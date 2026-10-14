import io
import json
import tempfile
import unittest
from pathlib import Path

import taskly


class TasklyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tasks_file = Path(self.temp_dir.name) / "tasks.json"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_cli(self, *arguments: str) -> tuple[int, str, str]:
        output = io.StringIO()
        error = io.StringIO()
        args = taskly.build_parser().parse_args(["--file", str(self.tasks_file), *arguments])
        code = taskly.run(args, output, error)
        return code, output.getvalue(), error.getvalue()

    def test_add_persists_task_with_expected_fields(self) -> None:
        code, output, error = self.run_cli("add", "Learn argparse", "--priority", "high")

        self.assertEqual(code, 0)
        self.assertIn("Added task 1", output)
        self.assertEqual(error, "")
        tasks = json.loads(self.tasks_file.read_text(encoding="utf-8"))
        self.assertEqual(tasks[0]["title"], "Learn argparse")
        self.assertEqual(tasks[0]["priority"], "high")
        self.assertFalse(tasks[0]["completed"])
        self.assertTrue(tasks[0]["created_at"])

    def test_list_handles_missing_file(self) -> None:
        code, output, error = self.run_cli("list")

        self.assertEqual(code, 0)
        self.assertEqual(output.strip(), "No tasks found.")
        self.assertEqual(error, "")

    def test_complete_and_delete_task(self) -> None:
        self.run_cli("add", "Temporary task")

        code, output, error = self.run_cli("complete", "1")
        self.assertEqual(code, 0)
        self.assertIn("Completed task 1", output)
        self.assertEqual(error, "")

        code, output, error = self.run_cli("delete", "1")
        self.assertEqual(code, 0)
        self.assertIn("Deleted task 1", output)
        self.assertEqual(error, "")
        self.assertEqual(json.loads(self.tasks_file.read_text(encoding="utf-8")), [])

    def test_invalid_id_is_reported_without_changing_file(self) -> None:
        self.run_cli("add", "Keep me")
        before = self.tasks_file.read_text(encoding="utf-8")

        code, output, error = self.run_cli("complete", "99")

        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("No task found with ID 99", error)
        self.assertEqual(self.tasks_file.read_text(encoding="utf-8"), before)

    def test_corrupted_json_is_reported(self) -> None:
        self.tasks_file.write_text("{not valid json", encoding="utf-8")

        code, output, error = self.run_cli("list")

        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("invalid JSON", error)

    def test_empty_title_is_rejected(self) -> None:
        code, output, error = self.run_cli("add", "   ")

        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("Task title cannot be empty", error)
        self.assertFalse(self.tasks_file.exists())


if __name__ == "__main__":
    unittest.main()
