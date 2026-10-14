"""A small command-line task manager."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TextIO


DEFAULT_TASKS_FILE = Path("tasks.json")
VALID_PRIORITIES = ("low", "medium", "high")


class TasklyError(Exception):
    """An expected error that can be shown to a CLI user."""


def load_tasks(path: Path) -> list[dict[str, Any]]:
    """Load tasks from JSON, treating a missing file as an empty task list."""
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as tasks_file:
            data = json.load(tasks_file)
    except json.JSONDecodeError as exc:
        raise TasklyError(f"Could not read {path}: invalid JSON ({exc.msg}).") from exc
    except OSError as exc:
        raise TasklyError(f"Could not read {path}: {exc}") from exc

    if not isinstance(data, list) or not all(isinstance(task, dict) for task in data):
        raise TasklyError(f"Could not read {path}: expected a JSON list of tasks.")
    return data


def save_tasks(path: Path, tasks: list[dict[str, Any]]) -> None:
    """Write tasks as readable JSON, creating the file if needed."""
    try:
        with path.open("w", encoding="utf-8") as tasks_file:
            json.dump(tasks, tasks_file, indent=2)
            tasks_file.write("\n")
    except OSError as exc:
        raise TasklyError(f"Could not save {path}: {exc}") from exc


def next_task_id(tasks: list[dict[str, Any]]) -> int:
    """Return one greater than the largest valid numeric task ID."""
    ids = [task.get("id", 0) for task in tasks]
    numeric_ids = [task_id for task_id in ids if isinstance(task_id, int) and task_id > 0]
    return max(numeric_ids, default=0) + 1


def add_task(tasks: list[dict[str, Any]], title: str, priority: str) -> dict[str, Any]:
    """Add and return a new task."""
    title = title.strip()
    if not title:
        raise TasklyError("Task title cannot be empty.")
    if priority not in VALID_PRIORITIES:
        raise TasklyError(f"Priority must be one of: {', '.join(VALID_PRIORITIES)}.")

    task = {
        "id": next_task_id(tasks),
        "title": title,
        "completed": False,
        "priority": priority,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    tasks.append(task)
    return task


def find_task(tasks: list[dict[str, Any]], task_id: int) -> dict[str, Any]:
    """Find a task by ID or raise a user-facing error."""
    for task in tasks:
        if task.get("id") == task_id:
            return task
    raise TasklyError(f"No task found with ID {task_id}.")


def format_tasks(tasks: list[dict[str, Any]]) -> str:
    """Format tasks as a readable table."""
    if not tasks:
        return "No tasks found."

    lines = [
        f"{'ID':<4} {'Status':<10} {'Priority':<8} {'Created':<20} Title",
        "-" * 72,
    ]
    for task in sorted(tasks, key=lambda item: item.get("id", 0)):
        status = "done" if task.get("completed", False) else "pending"
        created = str(task.get("created_at", ""))[:19].replace("T", " ")
        lines.append(
            f"{task.get('id', '?'):<4} {status:<10} {task.get('priority', '?'):<8} "
            f"{created:<20} {task.get('title', '')}"
        )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    examples = (
        "examples:\n"
        "  taskly add \"Write project README\" --priority high\n"
        "  taskly list\n"
        "  taskly complete 1\n"
        "  taskly delete 1"
    )
    parser = argparse.ArgumentParser(
        prog="taskly",
        description="A simple command-line task manager.",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_TASKS_FILE,
        help="path to the task data file (default: tasks.json)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="add a new task")
    add_parser.add_argument("title", help="task title")
    add_parser.add_argument(
        "--priority",
        choices=VALID_PRIORITIES,
        default="medium",
        help="task priority (default: medium)",
    )
    subparsers.add_parser("list", help="list all tasks")

    complete_parser = subparsers.add_parser("complete", help="mark a task as complete")
    complete_parser.add_argument("task_id", type=int, help="ID of the task")

    delete_parser = subparsers.add_parser("delete", help="delete a task")
    delete_parser.add_argument("task_id", type=int, help="ID of the task")
    return parser


def run(args: argparse.Namespace, output: TextIO, error: TextIO) -> int:
    """Execute parsed arguments and return a process-style exit code."""
    try:
        tasks = load_tasks(args.file)
        if args.command == "add":
            task = add_task(tasks, args.title, args.priority)
            save_tasks(args.file, tasks)
            print(f"Added task {task['id']}: {task['title']}", file=output)
        elif args.command == "list":
            print(format_tasks(tasks), file=output)
        elif args.command == "complete":
            task = find_task(tasks, args.task_id)
            if task.get("completed", False):
                print(f"Task {task['id']} is already complete.", file=output)
            else:
                task["completed"] = True
                save_tasks(args.file, tasks)
                print(f"Completed task {task['id']}: {task['title']}", file=output)
        elif args.command == "delete":
            task = find_task(tasks, args.task_id)
            tasks.remove(task)
            save_tasks(args.file, tasks)
            print(f"Deleted task {task['id']}: {task['title']}", file=output)
        return 0
    except TasklyError as exc:
        print(f"Error: {exc}", file=error)
        return 1


def main(argv: list[str] | None = None) -> int:
    """Parse command-line arguments and execute the requested command."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args, sys.stdout, sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
