# Braintrust OpenAPI Specification

This repository contains [OpenAPI specifications](https://www.openapis.org/) for
Braintrust's API. JSON and YAML versions of the spec can be found in the
[`openapi`](/openapi) directory.

See the [Braintrust docs](https://www.braintrustdata.com/docs/api/spec) for
documentation of the spec and more resources.

## SDK update notifications

Every push to `main` notifies repositories registered in
[`.github/sdk-consumers.json`](.github/sdk-consumers.json). Each repository owns
its update workflow and PR structure. Initially only the Rust SDK is registered.
No change in spec content means the receiver has no update to propose.

The notification is a `repository_dispatch` event named
`braintrust-openapi-updated` with this versioned `client_payload`:

```json
{
  "contract_version": "1",
  "spec_repository": "braintrustdata/braintrust-openapi",
  "spec_sha": "<full published commit SHA>"
}
```

To add an SDK, merge its receiver on its default branch, then add its repository
name to the registry. Receivers should verify the source repository and commit,
handle duplicate/delayed notifications, and open or update one PR for changed
spec content. SDK CI should validate generation from the proposed revision.

The dispatcher uses `repository_dispatch` because the existing Braintrust bot
has Contents write permission; it does not require adding Actions write
permission to the app. `GH_BOT_APP_PRIVATE_KEY` must be available to this repo,
and the app must be installed on each recipient with Contents write access.
The public App ID defaults to `1394756`; override the repository variable
`GH_BOT_APP_ID` if another app is used. Receiver credentials for opening PRs
are configured separately in each SDK repo.

Install and configure the Rust receiver before merging the dispatcher. Configure
the bot credentials in both repositories before activation. Notifications run
independently per SDK, so a failure does not cancel the other recipients. The
workflow can be run manually on `main` to retry notification of the latest
published revision. No SDK releases or auto-merges are performed.
