# Phase 0 AWS access review

Date: October 11, 2026, America/New_York. UTC report filenames use October 12. Status: **required developer access checks passed** using `default`, `us-east-1`, account ending 2072.

The user approved creating isolated resources and running the remaining Phase 0 tests. Exactly eight targets were created with the [scratch template](../../infrastructure/phase0/scratch-stack.json): three DynamoDB tables, SQS queue and DLQ, a generated dummy secret, EventBridge bus and CloudWatch log group. No application deployment, IAM changes, real GitHub credentials or unrelated resource writes were involved.

| Layer / operation | Result | Evidence and boundary |
|---|---|---|
| Identity/account/Region | PASS | STS account matched the pinned local manifest before each live operation |
| Local template schema validation | PASS | cfn-lint 1.57.2; zero findings in us-east-1 |
| Project security rules | PASS | Guard 3.2.1 official release digest verified; five project rules, zero violations. This is a scoped policy check, not the entire AWS managed registry |
| Audit configuration | PASS | Existing organization trail actively logs all management events, without excluded management sources; integrity validation enabled |
| AWS pre-deployment validation | PASS | CREATE change set completed; exactly eight additions; DescribeEvents had no validation findings |
| Resource provisioning | PASS | All eight resources reached CREATE_COMPLETE; exact output identifiers saved to ignored mode-600 manifest |
| Three DynamoDB roles | PASS | DescribeTable; two-item conditional transactions and consistent readback per table |
| DynamoDB application operations | PASS | Conditional PutItem, Query, BatchGet, three-table transaction; deliberately failed condition rolled back the entire transaction and preserved the existing guard |
| Job queue and DLQ | PASS | Exact attributes; correlated send, receive, visibility change and delete on each exclusive queue; no purge |
| Dummy Secrets Manager value | PASS | Describe/Get; generated synthetic marker verified, hash compared in memory; no credential value retained or printed |
| EventBridge | PASS | DescribeEventBus and PutEvents with zero failed entries on a bus with no rules, targets or archive; ingestion only |
| CloudWatch Logs | PASS | Create stream, PutLogEvents, exact GetLogEvents readback, delete owned stream |
| Canary cleanup | PASS | Ten cleanup checks in the canary report; subsequent strongly consistent Queries found both run partitions empty in every table, both queues reported zero visible/in-flight/delayed messages, and the owned log stream was absent |
| Runtime roles / production deployment | NOT_TESTED | Separate later-phase permissions and configuration; developer success does not establish runtime least privilege |

The final canary report contains **28 PASS**, **0 FAIL**, **0 BLOCKED**, and one future-runtime-role NOT_TESTED row. The cleanup audit adds seven PASS rows. The resource creation and inspection gates that previously lacked named targets are closed for this scratch configuration.

Protected evidence in ignored `docs/validation/private/`:

- `aws-template-validation-20261012T015416400638Z.md`: local, policy, audit and service validation.
- `aws-provisioning-20261012T014748343262Z.md`: prepared eight-addition change set.
- `aws-provisioning-20261012T015129822088Z.md`: successful resource creation.
- `aws-20261012T015236612645Z.md`: inspection before writes.
- `aws-20261012T015337713274Z.md`: operation-level canaries and cleanup.
- `aws-cleanup-20261012T015521625619Z.md`: subsequent independent artifact audit.
- `aws-scratch.local.json`: stack ownership, template digest, expiry and target-manifest location; no credential values.

Earlier sandbox network failures and the initial overly strict ownership check remain in the evidence history. The ownership check stopped before execution because a new REVIEW_IN_PROGRESS stack has not applied the change set's tags yet. It was corrected to verify tags, exact stack ARN and remote template on the prepared change set; execution then succeeded. These were not AWS service-access denials.

Optional customer-managed KMS, S3, Bedrock/model invocation, Lambda, ECS/ECR and hosting are not selected for this scratch phase. Service-managed encryption was exercised through DynamoDB, SQS and Secrets Manager. Automatic SQS redrive, EventBridge delivery, Scheduler execution, GSIs, load/concurrency and deployed-role access remain future configuration tests. None is represented as passing here.

The synthetic canary artifacts are removed. The user requested retaining the eight tagged resources for further testing, with a UTC review/expiry tag of October 13; tags do not trigger deletion. The under-USD-1 one-day estimate in the [scratch scope](../planning/phase-0-aws-scratch-proposal.md) is a planning estimate, not an observed bill or spending cap. Preserve the Markdown reports after resource teardown.
