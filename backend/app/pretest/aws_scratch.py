"""Provision only the reviewed eight-resource Phase 0 stack; no teardown or IAM changes."""

import argparse
import hashlib
import json
import os
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

from botocore.exceptions import BotoCoreError, ClientError

from app.config import REPO_ROOT
from app.pretest.aws_smoke import Manifest, Runner, Target, require
from app.pretest.report import write_report

TEMPLATE = REPO_ROOT / "infrastructure/phase0/scratch-stack.json"
DIRECTORY = REPO_ROOT / "docs/validation/private"
ALLOWED = {
    "CoreTable": "AWS::DynamoDB::Table",
    "OrganizationTable": "AWS::DynamoDB::Table",
    "IntelligenceTable": "AWS::DynamoDB::Table",
    "JobsQueue": "AWS::SQS::Queue",
    "JobsDlq": "AWS::SQS::Queue",
    "DummySecret": "AWS::SecretsManager::Secret",
    "ProbeBus": "AWS::Events::EventBus",
    "ProbeLogs": "AWS::Logs::LogGroup",
}
OUTPUTS = [
    ("core", "dynamodb", "Core"),
    ("organization", "dynamodb", "Organization"),
    ("intelligence", "dynamodb", "Intelligence"),
    ("jobs", "sqs", "Jobs"),
    ("jobs-dlq", "sqs", "JobsDlq"),
    ("oauth-dummy", "secretsmanager", "Dummy"),
    ("sync-schedule", "events", "Bus"),
    ("app-logs", "logs", "Logs"),
]


def save_private(path, data, *, exclusive=False):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    flags = os.O_WRONLY | os.O_CREAT | (os.O_EXCL if exclusive else os.O_TRUNC)
    with os.fdopen(os.open(path, flags, 0o600), "w") as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")


def reviewed_template():
    body = TEMPLATE.read_text()
    template = json.loads(body)
    require(len(body.encode()) <= 51200, "Template exceeds inline limit")
    require(
        {name: value["Type"] for name, value in template["Resources"].items()} == ALLOWED,
        "Template is outside the approved eight-resource scope",
    )
    require(not template.get("Transform"), "Transforms are outside scratch scope")
    return body, hashlib.sha256(body.encode()).hexdigest()


def prepare(runner, state_path):
    body, digest = reviewed_template()
    cf = runner.client("cloudformation")
    cf.validate_template(TemplateBody=body)
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    stack = f"ghm-phase0-{stamp}-{uuid.uuid4().hex[:6]}"
    state = {
        "profile": runner.manifest.profile,
        "region": runner.manifest.region,
        "expected_account": runner.account,
        "stack_name": stack,
        "template_sha256": digest,
        "expires": (datetime.now(UTC) + timedelta(days=1)).date().isoformat(),
        "stage": "preparing",
        "resource_teardown": "not executed; separate approval required",
    }
    # Reserve ownership before sending any mutation; never overwrite a previous run.
    save_private(state_path, state, exclusive=True)
    response = cf.create_change_set(
        StackName=stack,
        TemplateBody=body,
        ChangeSetName="phase0-access-preflight",
        ChangeSetType="CREATE",
        Description="Approved isolated Phase 0 access tests",
        Parameters=[{"ParameterKey": "Expires", "ParameterValue": state["expires"]}],
        Tags=[
            {"Key": "Project", "Value": "github-manager"},
            {"Key": "Purpose", "Value": "phase0"},
            {"Key": "Owner", "Value": "phase0-local-pretest"},
            {"Key": "Expires", "Value": state["expires"]},
        ],
    )
    state.update(stack_id=response["StackId"], change_set_id=response["Id"], stage="validating")
    save_private(state_path, state)
    cf.get_waiter("change_set_create_complete").wait(
        ChangeSetName=state["change_set_id"], WaiterConfig={"Delay": 3, "MaxAttempts": 60}
    )
    changes = cf.describe_change_set(ChangeSetName=state["change_set_id"])
    require(
        {change["ResourceChange"]["LogicalResourceId"] for change in changes["Changes"]}
        == set(ALLOWED),
        "Unexpected resource changes",
    )
    require(
        all(change["ResourceChange"]["Action"] == "Add" for change in changes["Changes"]),
        "Only new scratch resources may be added",
    )
    findings = [
        event
        for page in cf.get_paginator("describe_events").paginate(
            ChangeSetName=state["change_set_id"]
        )
        for event in page.get("OperationEvents", [])
        if event.get("EventType") == "VALIDATION_ERROR"
    ]
    require(not findings, "Service validation returned findings; review before execution")
    state["stage"] = "prepared"
    save_private(state_path, state)
    return "AWS template validation passed; exactly eight additions; no resource provisioning yet"


def execute(runner, state_path, manifest_path):
    state = json.loads(state_path.read_text())
    _, digest = reviewed_template()
    require(
        state["expected_account"] == runner.account
        and state["region"] == runner.manifest.region
        and state["profile"] == runner.manifest.profile,
        "Ownership manifest scope mismatch",
    )
    require(state["template_sha256"] == digest, "Template changed since preparation")
    require(state["stage"] == "prepared", "Only a prepared scratch change set may execute")
    cf = runner.client("cloudformation")
    stack = cf.describe_stacks(StackName=state["stack_id"])["Stacks"][0]
    require(stack["StackStatus"] == "REVIEW_IN_PROGRESS", "Existing stack cannot be adopted")
    # New stacks in REVIEW_IN_PROGRESS have no applied stack tags yet. Validate the
    # planned tags and exact stack ARN on the change set instead of weakening ownership.
    changes = cf.describe_change_set(ChangeSetName=state["change_set_id"])
    tags = {tag["Key"]: tag["Value"] for tag in changes.get("Tags", [])}
    require(
        changes["StackId"] == state["stack_id"]
        and tags.get("Project") == "github-manager"
        and tags.get("Purpose") == "phase0"
        and tags.get("Owner") == "phase0-local-pretest",
        "Change set ownership mismatch",
    )
    remote = cf.get_template(ChangeSetName=state["change_set_id"])["TemplateBody"]
    if isinstance(remote, str):
        remote = json.loads(remote)
    require(remote == json.loads(TEMPLATE.read_text()), "Remote change set template mismatch")
    require(not manifest_path.exists(), "Refusing to overwrite an existing target manifest")
    state["stage"] = "executing"
    save_private(state_path, state)
    cf.execute_change_set(ChangeSetName=state["change_set_id"])
    cf.get_waiter("stack_create_complete").wait(
        StackName=state["stack_id"], WaiterConfig={"Delay": 5, "MaxAttempts": 120}
    )
    stack = cf.describe_stacks(StackName=state["stack_id"])["Stacks"][0]
    outputs = {item["OutputKey"]: item["OutputValue"] for item in stack["Outputs"]}
    dummy = runner.client("secretsmanager").get_secret_value(SecretId=outputs["Dummy"])[
        "SecretString"
    ]
    content = json.loads(dummy)
    require(
        content.get("purpose") == "github-manager.phase0" and bool(content.get("canary")),
        "Generated secret is not the expected synthetic canary",
    )
    digest = hashlib.sha256(dummy.encode()).hexdigest()
    targets = [
        Target(
            alias=alias,
            kind=kind,
            identifier=outputs[output],
            approved_canary=True,
            exclusive_scratch=kind in {"sqs", "events"},
            dummy_sha256=digest if kind == "secretsmanager" else "",
        )
        for alias, kind, output in OUTPUTS
    ]
    manifest = Manifest(
        profile=runner.manifest.profile,
        region=runner.manifest.region,
        expected_account=runner.account,
        targets=targets,
    )
    save_private(manifest_path, manifest.model_dump(), exclusive=True)
    state.update(stage="created", manifest=str(manifest_path), stack_status=stack["StackStatus"])
    save_private(state_path, state)
    return (
        "CREATE_COMPLETE; eight owned scratch targets recorded; "
        "synthetic secret baseline hashed in memory"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["prepare", "execute"])
    parser.add_argument("--expected-account", required=True)
    parser.add_argument("--profile", default="default")
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--state", type=Path, default=DIRECTORY / "aws-scratch.local.json")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPO_ROOT / "infrastructure/phase0/resource-manifest.local.json",
    )
    args = parser.parse_args()
    runner = Runner(
        Manifest(profile=args.profile, region=args.region, expected_account=args.expected_account)
    )
    if runner.check("aws-identity", runner.identity):
        runner.check(
            "scratch/" + args.stage,
            lambda: (
                prepare(runner, args.state)
                if args.stage == "prepare"
                else execute(runner, args.state, args.manifest)
            ),
        )
    report = write_report(
        DIRECTORY,
        "aws-provisioning",
        "Phase 0 AWS scratch provisioning",
        runner.rows,
        [
            f"Profile: {args.profile}; Region: {args.region}.",
            "Only the reviewed eight scratch targets; no IAM changes.",
            "Resource teardown is separate; expiry tags do not delete resources.",
        ],
    )
    print(f"Markdown report: {report}")
    for row in runner.rows:
        print(f"{row['check']}: {row['status']}; {row['detail']}")
    return 1 if any(row["status"] != "PASS" for row in runner.rows) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, KeyError, ValueError, BotoCoreError, ClientError) as exc:
        print(
            f"Scratch operation stopped: {type(exc).__name__}; no raw response printed",
            file=sys.stderr,
        )
        sys.exit(2)
