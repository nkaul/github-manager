import json
from types import SimpleNamespace

import boto3
import pytest
from botocore.exceptions import ClientError
from botocore.stub import Stubber
from pydantic import ValidationError

from app.pretest.aws_smoke import Manifest, Runner, Target, template

ACCOUNT = "123456789012"


def session():
    return boto3.Session(
        aws_access_key_id="fixture", aws_secret_access_key="fixture", region_name="us-east-1"
    )


def test_manifest_blocks_wrong_account_region_and_unsafe_queue():
    for values in (
        {"targets": [{"alias": "core", "kind": "dynamodb", "required": False}]},
        {"targets": [{"alias": "jobs", "kind": "sqs", "identifier": "http://evil.example/q"}]},
        {"targets": [{"alias": "core", "kind": "dynamodb", "approved_canary": True}]},
        {
            "expected_account": ACCOUNT,
            "targets": [
                {
                    "alias": "key",
                    "kind": "kms",
                    "identifier": "arn:aws:kms:eu-west-1:123456789012:key/fixture",
                }
            ],
        },
        {
            "expected_account": ACCOUNT,
            "targets": [
                {
                    "alias": "key",
                    "kind": "kms",
                    "identifier": "arn:aws:kms:us-east-1:999999999999:key/fixture",
                }
            ],
        },
        {"targets": [{"alias": "core", "kind": "dynamodb"}, {"alias": "core", "kind": "dynamodb"}]},
    ):
        with pytest.raises(ValidationError):
            Manifest.model_validate(values)


def test_identity_is_not_service_access_and_omissions_stay_blocked():
    runner = Runner(Manifest(), session())
    client = runner.client("sts")
    with Stubber(client) as stub:
        stub.add_response(
            "get_caller_identity",
            {
                "Account": ACCOUNT,
                "Arn": f"arn:aws:iam::{ACCOUNT}:user/fixture",
                "UserId": "fixture",
            },
        )
        rows = runner.run()
        stub.assert_no_pending_responses()
    assert rows[0]["status"] == "PASS"
    assert sum(row["status"] == "BLOCKED" for row in rows) == 8
    assert len(runner.clients) == 1


def test_wrong_identity_stops_all_target_operations():
    runner = Runner(
        Manifest(
            expected_account="999999999999",
            targets=[Target(alias="core", kind="dynamodb", identifier="fixture-table")],
        ),
        session(),
    )
    with Stubber(runner.client("sts")) as stub:
        stub.add_response("get_caller_identity", {"Account": ACCOUNT})
        rows = runner.run()
    assert rows[0]["status"] == "FAIL" and len(runner.clients) == 1


def test_service_denial_report_omits_response_body():
    runner = Runner(template(), session())
    client = runner.client("kms")
    with Stubber(client) as stub:
        stub.add_client_error(
            "describe_key",
            "AccessDeniedException",
            "secret details",
            expected_params={"KeyId": "alias/fixture"},
        )
        assert not runner.check(
            "kms",
            lambda: runner.inspect(Target(alias="key", kind="kms", identifier="alias/fixture")),
        )
    assert runner.rows[0]["status"] == "FAIL"
    assert "secret details" not in json.dumps(runner.rows)


def test_canary_never_receives_shared_queue():
    runner = Runner(Manifest(expected_account=ACCOUNT), session())
    target = Target(
        alias="jobs",
        kind="sqs",
        identifier=f"https://sqs.us-east-1.amazonaws.com/{ACCOUNT}/fixture",
        approved_canary=True,
    )
    with Stubber(runner.client("sqs")):
        with pytest.raises(ValueError, match="exclusively"):
            runner.canary(target)


def test_sqs_unowned_message_restored_never_deleted():
    runner = Runner(Manifest(expected_account=ACCOUNT), session())
    url = f"https://sqs.us-east-1.amazonaws.com/{ACCOUNT}/fixture"
    target = Target(
        alias="jobs", kind="sqs", identifier=url, approved_canary=True, exclusive_scratch=True
    )
    with Stubber(runner.client("sqs")) as stub:
        stub.add_response(
            "get_queue_attributes",
            {
                "Attributes": {
                    "ApproximateNumberOfMessages": "0",
                    "ApproximateNumberOfMessagesNotVisible": "0",
                }
            },
        )
        stub.add_response("send_message", {"MessageId": "owned"})
        stub.add_response(
            "receive_message",
            {"Messages": [{"MessageId": "other", "Body": "foreign", "ReceiptHandle": "receipt"}]},
        )
        stub.add_response(
            "change_message_visibility",
            {},
            {"QueueUrl": url, "ReceiptHandle": "receipt", "VisibilityTimeout": 0},
        )
        with pytest.raises(ValueError, match="Unowned"):
            runner.canary(target)
        stub.assert_no_pending_responses()


def test_dynamodb_transaction_readback_and_cleanup_are_owner_bound():
    runner = Runner(Manifest(expected_account=ACCOUNT), session())
    calls = []

    class Table:
        key_schema = [{"AttributeName": "PK"}, {"AttributeName": "SK"}]
        attribute_definitions = [{"AttributeName": k, "AttributeType": "S"} for k in ("PK", "SK")]

        def get_item(self, **params):
            return {"Item": {**params["Key"], "probeOwner": runner.run_id}}

        def delete_item(self, **params):
            calls.append(params)
            assert params["ConditionExpression"].get_expression()["values"][-1] == runner.run_id

        meta = SimpleNamespace(
            client=SimpleNamespace(
                exceptions=SimpleNamespace(ConditionalCheckFailedException=ClientError)
            )
        )

    def transaction(**params):
        assert len(params["TransactItems"]) == 2
        for operation in params["TransactItems"]:
            put = operation["Put"]
            assert put["Item"]["probeOwner"] == runner.run_id
            assert put["ConditionExpression"].startswith("attribute_not_exists")

    runner.ddb = SimpleNamespace(
        Table=lambda name: Table(),
        meta=SimpleNamespace(client=SimpleNamespace(transact_write_items=transaction)),
    )
    assert "transaction" in runner.dynamodb_canary(
        Target(alias="core", kind="dynamodb", identifier="fixture")
    )
    assert len(calls) == 2 and all(row["status"] == "PASS" for row in runner.rows)
