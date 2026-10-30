import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

module_spec = importlib.util.spec_from_file_location("dispatch", Path(__file__).with_name("dispatch_sdk_updates.py"))
dispatch = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(dispatch)


class DispatchTests(unittest.TestCase):
    def test_notification_matches_the_sdk_contract(self):
        request = dispatch.request_for("braintrust-sdk-rust", "a" * 40, "test-token")
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.full_url, "https://api.github.com/repos/braintrustdata/braintrust-sdk-rust/dispatches")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-token")
        self.assertEqual(json.loads(request.data), {
            "event_type": "braintrust-openapi-updated",
            "client_payload": {"spec_sha": "a" * 40},
        })

    def test_unregistered_target_and_floating_ref_are_rejected(self):
        for repository, sha in [("other-sdk", "a" * 40), ("braintrust-sdk-rust", "main")]:
            with self.assertRaises(ValueError):
                dispatch.request_for(repository, sha, "test-token")

    def test_registry_rejects_duplicates_and_repository_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "consumers.json"
            for values in [["sdk", "sdk"], ["other/repo"], [], "sdk"]:
                path.write_text(json.dumps({"repositories": values}))
                with self.assertRaises(ValueError):
                    dispatch.repositories(path)


if __name__ == "__main__":
    unittest.main()
