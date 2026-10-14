# Phase 0 AWS scratch-target proposal

Date: October 11, 2026. Status: **creation and canaries approved and completed**. All eight targets passed inspection and basic data-plane tests. See [AWS results](../validation/aws-access-review-2026-10-11.md).

The user authorized proceeding with fixture verification, resource creation and the remaining AWS tests using `default` / `us-east-1`. The [scratch template](../../infrastructure/phase0/scratch-stack.json) creates exactly eight isolated resources under a unique `ghm-phase0-<UTC timestamp>-<suffix>` stack. The ignored local manifest pins the account and resulting IDs. This CloudFormation choice is limited to Phase 0; it does not select production IaC for Phase 1.

## Proposed targets and allowed tests

The confirmed account ends in 2072. Targets carry `Project=github-manager`, `Purpose=phase0`, `Owner=phase0-local-pretest`, and `Expires=2026-10-13` (UTC review/teardown date). The expiry tag does not automatically delete resources. Names below are role illustrations; deployed names derive from the unique stack name. No existing target was adopted.

| Role | Proposed name | Configuration / allowed canary |
|---|---|---|
| Core table | `ghm-phase0-core` | DynamoDB Standard on-demand; string `PK`/`SK`; no backups, streams or GSIs for this basic access test. Two owner-tagged items in a conditional transaction, GetItem and guarded DeleteItem. |
| Organization table | `ghm-phase0-organization` | Same scratch schema and bounded operations; final application schema remains Phase 1. |
| Intelligence table | `ghm-phase0-intelligence` | Same scratch schema and bounded operations. |
| Job queue | `ghm-phase0-jobs` | Dedicated Standard SQS, no real consumers; send/receive/delete own message; no purge. Configure redrive to the scratch DLQ if separately testing routing. |
| Job DLQ | `ghm-phase0-jobs-dlq` | Dedicated Standard SQS, no real consumers; direct round trip. Direct use does not establish source-queue redrive. |
| Dummy secret | `github-manager/phase0/<stack>/dummy` | CloudFormation-generated synthetic value, verified purpose marker, in-memory SHA-256 baseline and read comparison. AWS managed encryption key; no real OAuth credentials. |
| Scratch event bus | `ghm-phase0` | No rules, targets, archive, real consumers or cross-account delivery. Describe and PutEvents acceptance only. |
| Scratch log group | `/github-manager/phase0` | Short retention, no subscription filters; create/put/delete only a run-owned stream. |

No VPC, NAT gateway, EC2/Fargate, Lambda, ECR, custom KMS key, S3 bucket, model invocation, IAM role/policy changes or application deployment is part of this proposal. Selected optional services require an amended target list. Future runtime-role, GSI, scheduling, redrive, encryption and deployment acceptance stay separate even if these basic canaries pass.

## Spend and lifetime

Planning estimate: **under USD 1 for one test day**, assuming only these targets, fewer than 100 small data operations per service, under 1 MB of synthetic stored/logged data, no real consumers, no paid optional features, and prompt teardown. This is a conservative planning inference from usage pricing, not an observed bill or a hard AWS spending cap; no Free Tier credits are assumed. Review actual prices and the precise provisioning configuration before approval.

The dummy secret is the main fixed-duration charge in this tiny set. The AWS pricing example uses USD 0.40/secret/month and USD 0.05/10,000 API calls. A deterministic Decimal calculation gives **USD 0.013833** for 24 hours plus 100 calls using the example's 720-hour month. Remaining tiny request/storage charges depend on actual usage. [Secrets Manager pricing](https://aws.amazon.com/secrets-manager/pricing/).

DynamoDB uses on-demand requests/storage; SQS and EventBridge charge by usage, and CloudWatch Logs by ingestion/storage/features. Avoid provisioned table capacity, event archives and paid monitoring additions. Recheck with the [AWS Pricing Calculator](https://calculator.aws/), [DynamoDB](https://aws.amazon.com/dynamodb/pricing/), [SQS](https://aws.amazon.com/sqs/pricing/), [EventBridge](https://aws.amazon.com/eventbridge/pricing/) and [CloudWatch](https://aws.amazon.com/cloudwatch/pricing/) pricing pages. Rates reviewed October 11, 2026.

## Review and execution boundary

The user's latest instruction approves creation and testing of this scratch set. The concrete template, local lint, project Guard checks and AWS change set were reviewed before execution. Only eight `Add` changes were executed; no IAM capabilities, external targets or application deployment were included. All resources reached `CREATE_COMPLETE`.

Inspection preceded canaries. The canaries additionally verified conditional PutItem, Query, BatchGet, a three-table transaction and atomic rollback on an expected failed condition, SQS visibility change, and exact log readback. Reports and protected ownership/run records were saved locally. A separate read-only audit confirmed empty canary partitions, zero queue counters and no owned log stream.

Canary cleanup is complete. The user explicitly requested retaining the eight scratch resources for further testing; their template uses `DeletionPolicy: Delete` and `UpdateReplacePolicy: Delete` because they contain disposable synthetic data only. Teardown must verify the recorded stack ID, account, ownership tags, template and eight-resource inventory first. Never delete shared or production targets as cleanup.

The live GitHub OAuth test is independent and can proceed without these resources.
