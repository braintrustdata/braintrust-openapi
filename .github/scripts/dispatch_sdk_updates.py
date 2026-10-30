#!/usr/bin/env python3
"""Notify registered SDK repositories of a published OpenAPI commit."""

import argparse
import json
import os
from pathlib import Path
import re
import urllib.request

SOURCE = "braintrustdata/braintrust-openapi"
EVENT = "braintrust-openapi-updated"
REGISTRY = Path(__file__).resolve().parents[1] / "sdk-consumers.json"


def repositories(path=REGISTRY):
    values = json.loads(path.read_text())["repositories"]
    if not isinstance(values, list) or not values or any(
        not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value)
        for value in values
    ) or len(set(values)) != len(values):
        raise ValueError("SDK registry must contain unique repository names in braintrustdata")
    return values


def request_for(repository, spec_sha, token):
    if repository not in repositories():
        raise ValueError("repository is not registered as a spec consumer")
    if not re.fullmatch(r"[0-9a-f]{40}", spec_sha):
        raise ValueError("expected a full commit SHA")
    payload = {
        "event_type": EVENT,
        "client_payload": {
            "spec_sha": spec_sha,
        },
    }
    return urllib.request.Request(
        f"https://api.github.com/repos/braintrustdata/{repository}/dispatches",
        data=json.dumps(payload).encode(), method="POST",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json", "X-GitHub-Api-Version": "2022-11-28"},
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--repository")
    parser.add_argument("--spec-sha")
    args = parser.parse_args()
    if args.list:
        print(json.dumps(repositories()))
        return
    if not args.repository or not args.spec_sha:
        parser.error("--repository and --spec-sha are required when dispatching")
    request = request_for(args.repository, args.spec_sha, os.environ["GH_TOKEN"])
    with urllib.request.urlopen(request, timeout=30) as response:
        response.read()
    print(f"Notified {args.repository} of {SOURCE}@{args.spec_sha}")


if __name__ == "__main__":
    main()
