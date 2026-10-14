"""Named-resource preflight. No provisioning, policy changes or unrestricted discovery."""

import argparse
import hashlib
import json
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

import boto3
from boto3.dynamodb.conditions import Attr, ConditionExpressionBuilder, Key
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from app.config import REPO_ROOT
from app.pretest.report import write_report

Kind = Literal[
    "dynamodb", "sqs", "secretsmanager", "kms", "events", "logs", "s3", "bedrock", "lambda", "ecs"
]


class Target(BaseModel):
    model_config = ConfigDict(extra="forbid")
    alias: str = Field(pattern=r"^[a-z0-9-]{1,40}$")
    kind: Kind
    identifier: str = ""
    required: bool = True
    approved_canary: bool = False
    exclusive_scratch: bool = False
    partition_key: str = "PK"
    sort_key: str = "SK"
    dummy_sha256: str = ""


class Manifest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profile: str = "default"
    region: str = "us-east-1"
    expected_account: str = Field(default="", pattern=r"^(?:[0-9]{12})?$")
    targets: list[Target] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def safe_identifiers(self):
        if len({t.alias for t in self.targets}) != len(self.targets):
            raise ValueError("Target aliases must be unique")
        required_roles = dict(REQUIRED)
        named = [(t.kind, t.identifier) for t in self.targets if t.identifier]
        if len(named) != len(set(named)):
            raise ValueError("Distinct target roles require distinct resource identifiers")
        for target in self.targets:
            if target.alias in required_roles and (
                target.kind != required_roles[target.alias] or not target.required
            ):
                raise ValueError("Required target roles cannot be retyped or marked optional")
            if target.identifier.startswith("arn:"):
                parts = target.identifier.split(":", 5)
                if len(parts) != 6 or (parts[3] and parts[3] != self.region):
                    raise ValueError("Target Region must match manifest")
                if parts[4] and parts[4] != self.expected_account:
                    raise ValueError("Target account must match expected_account")
            if target.kind == "sqs" and target.identifier:
                url = urlsplit(target.identifier)
                if (
                    url.scheme != "https"
                    or url.netloc != f"sqs.{self.region}.amazonaws.com"
                    or url.query
                    or url.fragment
                    or url.username
                    or url.password
                    or not re.fullmatch(r"/[0-9]{12}/[A-Za-z0-9_-]+(?:\.fifo)?", url.path)
                ):
                    raise ValueError("Use a standard regional SQS queue URL")
                if self.expected_account and url.path.split("/")[1] != self.expected_account:
                    raise ValueError("Queue account mismatch")
            if target.approved_canary and not self.expected_account:
                raise ValueError("Canaries require expected_account")
        return self


REQUIRED = [
    ("core", "dynamodb"),
    ("organization", "dynamodb"),
    ("intelligence", "dynamodb"),
    ("jobs", "sqs"),
    ("jobs-dlq", "sqs"),
    ("oauth-dummy", "secretsmanager"),
    ("sync-schedule", "events"),
    ("app-logs", "logs"),
]
OPTIONAL = [
    ("encryption", "kms"),
    ("artifacts", "s3"),
    ("model", "bedrock"),
    ("api-function", "lambda"),
    ("worker-cluster", "ecs"),
]


def template() -> Manifest:
    return Manifest(
        targets=[Target(alias=a, kind=k) for a, k in REQUIRED]
        + [Target(alias=a, kind=k, required=False) for a, k in OPTIONAL]
    )


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Runner:
    def __init__(self, manifest: Manifest, session=None):
        self.manifest = manifest
        self.session = session or boto3.Session(
            profile_name=manifest.profile, region_name=manifest.region
        )
        self.config = Config(
            retries={"total_max_attempts": 2, "mode": "standard"},
            connect_timeout=5,
            read_timeout=10,
        )
        self.clients = {}
        self.rows = []
        self.run_id = "phase0-" + uuid.uuid4().hex
        self.ddb = None
        self.account = ""

    def client(self, kind):
        if kind not in self.clients:
            self.clients[kind] = self.session.client(kind, config=self.config)
        return self.clients[kind]

    def record(self, check, status, detail, evidence="LIVE"):
        self.rows.append({"check": check, "evidence": evidence, "status": status, "detail": detail})

    def check(self, label, call):
        # CLI/report boundary: errors become explicit failed/blocked evidence, never a false PASS.
        try:
            detail = call()
            self.record(label, "PASS", detail or "Operation succeeded")
            return True
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "ClientError")
            request_id = exc.response.get("ResponseMetadata", {}).get("RequestId", "unavailable")
            self.record(label, "FAIL", f"{code}; request ID {request_id}; no response body saved")
        except BotoCoreError as exc:
            self.record(
                label, "BLOCKED", type(exc).__name__ + "; check profile, session, TLS and network"
            )
        except (ValueError, AssertionError) as exc:
            self.record(label, "FAIL", str(exc))
        return False

    def identity(self):
        value = self.client("sts").get_caller_identity()
        self.account = value["Account"]
        if self.manifest.expected_account and self.account != self.manifest.expected_account:
            raise ValueError("Wrong AWS account; no target operations attempted")
        return (
            f"Profile {self.manifest.profile}; account ending {self.account[-4:]}; "
            f"Region {self.manifest.region}; identity only, not service permission"
        )

    def inspect(self, target):
        kind, ident = target.kind, target.identifier
        client = self.client(kind)
        if kind == "dynamodb":
            table = client.describe_table(TableName=ident)["Table"]
            require(table["TableArn"].split(":")[4] == self.account, "Table account mismatch")
            return (
                f"DescribeTable; status {table['TableStatus']}; data read/write and GSIs not tested"
            )
        if kind == "sqs":
            attrs = client.get_queue_attributes(
                QueueUrl=ident,
                AttributeNames=[
                    "QueueArn",
                    "RedrivePolicy",
                    "ApproximateNumberOfMessages",
                    "ApproximateNumberOfMessagesNotVisible",
                ],
            )["Attributes"]
            require(attrs["QueueArn"].split(":")[4] == self.account, "Queue account mismatch")
            return "GetQueueAttributes; send/receive/redrive not tested"
        if kind == "secretsmanager":
            client.describe_secret(SecretId=ident)
            return "DescribeSecret only; dummy value read requires an approved canary"
        if kind == "kms":
            client.describe_key(KeyId=ident)
            return "DescribeKey only; encrypt/decrypt not tested"
        if kind == "events":
            client.describe_event_bus(Name=ident)
            return "DescribeEventBus; event delivery and Scheduler role not tested"
        if kind == "logs":
            pages = client.get_paginator("describe_log_groups").paginate(
                logGroupNamePrefix=ident, PaginationConfig={"MaxItems": 100, "PageSize": 50}
            )
            require(
                any(
                    group["logGroupName"] == ident for page in pages for group in page["logGroups"]
                ),
                "Exact log group not found within bounded lookup",
            )
            return "Exact log group found; stream/event writes not tested"
        if kind == "s3":
            client.head_bucket(Bucket=ident, ExpectedBucketOwner=self.account)
            return "HeadBucket; object operations not tested"
        if kind == "bedrock":
            client.get_foundation_model(modelIdentifier=ident)
            return (
                "Model metadata only; invocation entitlement, quota and runtime access not tested"
            )
        if kind == "lambda":
            client.get_function_configuration(FunctionName=ident)
            return "GetFunctionConfiguration; invocation/deployment not tested"
        value = client.describe_clusters(clusters=[ident])
        require(value.get("clusters") and not value.get("failures"), "Cluster missing or denied")
        return "DescribeClusters; task execution, ECR and runtime role not tested"

    def dynamodb_canary(self, target):
        if self.ddb is None:
            self.ddb = self.session.resource("dynamodb", config=self.config)
        table = self.ddb.Table(target.identifier)
        expected_keys = {target.partition_key, target.sort_key}
        require(
            {key["AttributeName"] for key in table.key_schema} == expected_keys,
            "Scratch table key schema mismatch",
        )
        require(
            all(
                attr["AttributeType"] == "S"
                for attr in table.attribute_definitions
                if attr["AttributeName"] in expected_keys
            ),
            "Scratch table keys must be strings",
        )
        keys = [
            {target.partition_key: self.run_id, target.sort_key: f"probe-{index}"}
            for index in (1, 2)
        ]
        expression = ConditionExpressionBuilder().build_expression(
            Attr(target.partition_key).not_exists()
        )
        try:
            self.ddb.meta.client.transact_write_items(
                ClientRequestToken=uuid.uuid4().hex,
                TransactItems=[
                    {
                        "Put": {
                            "TableName": target.identifier,
                            "Item": {**key, "probeOwner": self.run_id},
                            "ConditionExpression": expression.condition_expression,
                            "ExpressionAttributeNames": expression.attribute_name_placeholders,
                        }
                    }
                    for key in keys
                ],
            )
            for key in keys:
                value = table.get_item(Key=key, ConsistentRead=True).get("Item")
                require(
                    value and value.get("probeOwner") == self.run_id,
                    "Conditional transaction readback mismatch",
                )
            return "Two-item conditional transaction and strongly consistent GetItem passed"
        finally:
            for index, key in enumerate(keys):

                def cleanup(key=key):
                    try:
                        table.delete_item(
                            Key=key, ConditionExpression=Attr("probeOwner").eq(self.run_id)
                        )
                    except table.meta.client.exceptions.ConditionalCheckFailedException:
                        value = table.get_item(Key=key, ConsistentRead=True).get("Item")
                        require(value is None, "Cleanup ownership conflict; row preserved")
                    return "Owned probe item removed or confirmed absent"

                self.check(f"{target.alias}/cleanup-{index + 1}", cleanup)

    def canary(self, target):
        if target.kind == "dynamodb":
            return self.dynamodb_canary(target)
        kind, ident = target.kind, target.identifier
        client = self.client(kind)
        if kind == "kms":
            value = uuid.uuid4().bytes
            context = {"phase0Run": self.run_id}
            encrypted = client.encrypt(KeyId=ident, Plaintext=value, EncryptionContext=context)
            decrypted = client.decrypt(
                KeyId=ident, CiphertextBlob=encrypted["CiphertextBlob"], EncryptionContext=context
            )
            require(decrypted["Plaintext"] == value, "KMS round trip mismatch")
            return "Encrypt/Decrypt round trip; no persisted artifacts"
        if kind == "secretsmanager":
            require(
                re.fullmatch(r"[a-f0-9]{64}", target.dummy_sha256),
                "Dummy secret requires an expected SHA-256",
            )
            value = client.get_secret_value(SecretId=ident)
            content = (
                value.get("SecretString", "").encode()
                if "SecretString" in value
                else value["SecretBinary"]
            )
            require(
                hashlib.sha256(content).hexdigest() == target.dummy_sha256,
                "Dummy value hash mismatch; value omitted",
            )
            return "Approved dummy secret read and hash matched; value discarded"
        if kind == "sqs":
            require(target.exclusive_scratch, "Receive requires an exclusively owned scratch queue")
            attrs = client.get_queue_attributes(
                QueueUrl=ident,
                AttributeNames=[
                    "ApproximateNumberOfMessages",
                    "ApproximateNumberOfMessagesNotVisible",
                ],
            )["Attributes"]
            require(
                all(int(value) == 0 for value in attrs.values()),
                "Scratch queue is not empty; no messages touched",
            )
            params = {"QueueUrl": ident, "MessageBody": self.run_id}
            if ident.endswith(".fifo"):
                params.update(MessageGroupId=self.run_id, MessageDeduplicationId=self.run_id)
            sent = client.send_message(**params)
            for _ in range(3):
                value = client.receive_message(
                    QueueUrl=ident, MaxNumberOfMessages=1, WaitTimeSeconds=2, VisibilityTimeout=5
                )
                for message in value.get("Messages", []):
                    if (
                        message.get("MessageId") != sent["MessageId"]
                        or message.get("Body") != self.run_id
                    ):
                        client.change_message_visibility(
                            QueueUrl=ident,
                            ReceiptHandle=message["ReceiptHandle"],
                            VisibilityTimeout=0,
                        )
                        raise ValueError(
                            "Unowned message returned; restored visibility and stopped"
                        )
                    client.change_message_visibility(
                        QueueUrl=ident, ReceiptHandle=message["ReceiptHandle"], VisibilityTimeout=5
                    )
                    client.delete_message(QueueUrl=ident, ReceiptHandle=message["ReceiptHandle"])
                    return (
                        "Own send/receive/visibility-change/delete passed; "
                        "no purge; redrive untested"
                    )
            raise ValueError(
                "Own message was not received; possible residual message requires cleanup by run ID"
            )
        if kind == "events":
            require(
                target.exclusive_scratch,
                "Event probe requires a scratch bus with no real consumers",
            )
            value = client.put_events(
                Entries=[
                    {
                        "Source": "github-manager.phase0",
                        "DetailType": "AccessProbe",
                        "Detail": json.dumps({"run": self.run_id}),
                        "EventBusName": ident,
                    }
                ]
            )
            require(value["FailedEntryCount"] == 0, "Event entry rejected")
            return "Scratch event accepted; delivery/Scheduler untested; event not retractable"
        if kind == "logs":
            stream = self.run_id
            client.create_log_stream(logGroupName=ident, logStreamName=stream)
            try:
                result = client.put_log_events(
                    logGroupName=ident,
                    logStreamName=stream,
                    logEvents=[
                        {
                            "timestamp": int(time.time() * 1000),
                            "message": "Phase 0 access probe " + self.run_id,
                        }
                    ],
                )
                require(not result.get("rejectedLogEventsInfo"), "Log event rejected")
                expected = "Phase 0 access probe " + self.run_id
                for attempt in range(6):
                    events = client.get_log_events(
                        logGroupName=ident, logStreamName=stream, startFromHead=True, limit=10
                    )["events"]
                    if any(event["message"] == expected for event in events):
                        return "Owned log stream/event write and exact readback passed"
                    if attempt < 5:
                        time.sleep(2)
                raise ValueError("Log event readback not observed in bounded retry window")
            finally:
                self.check(
                    target.alias + "/cleanup",
                    lambda: (
                        client.delete_log_stream(logGroupName=ident, logStreamName=stream)
                        and "Owned stream removed"
                    ),
                )
        if kind == "s3":
            key = f"phase0/{self.run_id}/probe.txt"
            put = client.put_object(
                Bucket=ident,
                Key=key,
                Body=self.run_id.encode(),
                ExpectedBucketOwner=self.account,
                IfNoneMatch="*",
            )
            version = {"VersionId": put["VersionId"]} if put.get("VersionId") else {}
            try:
                result = client.get_object(
                    Bucket=ident, Key=key, ExpectedBucketOwner=self.account, **version
                )
                with result["Body"] as body:
                    require(body.read(100) == self.run_id.encode(), "Object readback mismatch")
                return "Owned object put/get passed"
            finally:
                self.check(
                    target.alias + "/cleanup",
                    lambda: (
                        client.delete_object(
                            Bucket=ident, Key=key, ExpectedBucketOwner=self.account, **version
                        )
                        and "Owned object version removed"
                    ),
                )
        raise ValueError(
            "Invocation/deployment canaries are intentionally outside this Phase 0 probe"
        )

    def cross_table_canary(self, targets):
        """Check application-relevant operations and atomic failure on owned synthetic rows."""
        tables = [self.ddb.Table(target.identifier) for target in targets]
        pk = self.run_id + "-cross"
        key = {"PK": pk, "SK": "transaction"}
        guard = {"PK": pk, "SK": "guard"}
        sentinel = {"PK": pk, "SK": "must-not-exist"}
        owner = Attr("probeOwner").eq(self.run_id)
        condition = {"ConditionExpression": "attribute_not_exists(PK)"}
        try:
            tables[0].put_item(Item={**guard, "probeOwner": self.run_id}, **condition)
            self.ddb.meta.client.transact_write_items(
                ClientRequestToken=uuid.uuid4().hex,
                TransactItems=[
                    {
                        "Put": {
                            "TableName": table.name,
                            "Item": {**key, "probeOwner": self.run_id},
                            **condition,
                        }
                    }
                    for table in tables
                ],
            )
            values = self.ddb.batch_get_item(
                RequestItems={
                    table.name: {"Keys": [key], "ConsistentRead": True} for table in tables
                }
            )
            require(not values.get("UnprocessedKeys"), "BatchGet returned unprocessed keys")
            for table in tables:
                items = values["Responses"].get(table.name, [])
                require(
                    len(items) == 1 and items[0].get("probeOwner") == self.run_id,
                    "Cross-table BatchGet mismatch",
                )
                queried = table.query(KeyConditionExpression=Key("PK").eq(pk), ConsistentRead=True)
                require(
                    any(item == items[0] for item in queried["Items"]), "Query readback mismatch"
                )
            try:
                self.ddb.meta.client.transact_write_items(
                    ClientRequestToken=uuid.uuid4().hex,
                    TransactItems=[
                        {
                            "Put": {
                                "TableName": tables[0].name,
                                "Item": {**guard, "probeOwner": self.run_id, "unexpected": True},
                                **condition,
                            }
                        },
                        {
                            "Put": {
                                "TableName": tables[1].name,
                                "Item": {**sentinel, "probeOwner": self.run_id},
                                **condition,
                            }
                        },
                    ],
                )
            except self.ddb.meta.client.exceptions.TransactionCanceledException as exc:
                codes = [
                    reason.get("Code") for reason in exc.response.get("CancellationReasons", [])
                ]
                require(
                    "ConditionalCheckFailed" in codes
                    and all(code in {None, "None", "ConditionalCheckFailed"} for code in codes),
                    "Transaction cancellation was not the expected condition failure",
                )
            else:
                raise ValueError("Expected conditional transaction rejection did not occur")
            require(
                tables[0].get_item(Key=guard, ConsistentRead=True)["Item"]
                == {**guard, "probeOwner": self.run_id},
                "Rejected transaction changed guard",
            )
            require(
                "Item" not in tables[1].get_item(Key=sentinel, ConsistentRead=True),
                "Rejected transaction partially committed",
            )
            return (
                "Conditional PutItem, Query, BatchGet, three-table transaction "
                "and failed-condition rollback passed"
            )
        finally:
            for index, table in enumerate(tables):
                keys = [key] + ([guard] if index == 0 else [sentinel] if index == 1 else [])

                def cleanup(table=table, keys=keys):
                    for owned_key in keys:
                        try:
                            table.delete_item(Key=owned_key, ConditionExpression=owner)
                        except table.meta.client.exceptions.ConditionalCheckFailedException:
                            require(
                                "Item" not in table.get_item(Key=owned_key, ConsistentRead=True),
                                "Cross-table cleanup ownership conflict; preserved",
                            )
                        require(
                            "Item" not in table.get_item(Key=owned_key, ConsistentRead=True),
                            "Cross-table cleanup readback found a residual",
                        )
                    return "Owned records removed and strongly consistent absence verified"

                self.check(targets[index].alias + "/cross-cleanup", cleanup)

    def run(self, mode="inspect"):
        if not self.check("aws-identity", self.identity):
            self.record(
                "named-resource-probes",
                "BLOCKED",
                "Identity/account validation failed; no targets attempted",
                "POLICY",
            )
            return self.rows
        # Omitting a required target from a local manifest cannot silently close a gate.
        present = {(t.alias, t.kind) for t in self.manifest.targets}
        targets = self.manifest.targets + [
            Target(alias=a, kind=k) for a, k in REQUIRED if (a, k) not in present
        ]
        for target in targets:
            if not target.identifier:
                self.record(
                    target.alias + "/inspect",
                    "BLOCKED" if target.required else "NOT_APPLICABLE",
                    "No named target supplied"
                    if target.required
                    else "Optional service not selected",
                    "POLICY",
                )
                continue
            if not self.check(target.alias + "/inspect", lambda t=target: self.inspect(t)):
                continue
            if mode != "canary" or not target.approved_canary:
                self.record(
                    target.alias + "/data-plane",
                    "NOT_TESTED",
                    "Inspect mode or canary not approved in manifest",
                    "POLICY",
                )
                continue
            self.check(target.alias + "/canary", lambda t=target: self.canary(t))
        ddb_targets = [
            next((t for t in targets if t.alias == alias), None)
            for alias in ("core", "organization", "intelligence")
        ]
        if mode == "canary" and all(
            target
            and target.identifier
            and target.approved_canary
            and target.partition_key == "PK"
            and target.sort_key == "SK"
            and any(
                row["check"] == target.alias + "/canary" and row["status"] == "PASS"
                for row in self.rows
            )
            for target in ddb_targets
        ):
            self.check(
                "dynamodb/cross-table-atomicity", lambda: self.cross_table_canary(ddb_targets)
            )
        self.record(
            "future-runtime-role",
            "NOT_TESTED",
            "Developer identity does not prove deployed runtime-role access; "
            "scratch provisioning has a separate report",
            "POLICY",
        )
        return self.rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--mode", choices=["inspect", "canary"], default="inspect")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "docs/validation/private")
    args = parser.parse_args()
    run_id = "not started"
    try:
        manifest = (
            Manifest.model_validate_json(args.manifest.read_text()) if args.manifest else template()
        )
        if args.mode == "canary" and not args.manifest:
            parser.error("Canary mode requires an explicitly approved local manifest")
        runner = Runner(manifest)
        run_id = runner.run_id
        rows = runner.run(args.mode)
    except (ValidationError, OSError):
        print(
            "Invalid or unreadable manifest; no probes started. See the example schema.",
            file=sys.stderr,
        )
        return 2
    except BotoCoreError as exc:
        rows = [
            {
                "check": "aws-session",
                "evidence": "LIVE",
                "status": "BLOCKED",
                "detail": type(exc).__name__,
            }
        ]
    report = write_report(
        args.output,
        "aws",
        "Phase 0 AWS access report",
        rows,
        [
            f"Profile: {manifest.profile}; Region: {manifest.region}; mode: {args.mode}.",
            f"Canary owner/run ID: {run_id}.",
            "No provisioning or IAM changes. Inspection does not prove data-plane access.",
            "Disposition: required BLOCKED/NOT_TESTED results remain gates; optional targets open.",
        ],
    )
    print(f"Markdown report: {report}")
    for row in rows:
        print(f"{row['check']}: {row['status']}")
    return 1 if any(row["status"] in {"FAIL", "BLOCKED"} for row in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
