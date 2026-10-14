# Taskly CLI

Taskly CLI is a beginner-friendly task manager written for Python 3 using only
the standard library. Tasks are stored in a local `tasks.json` file.

## Setup

No third-party packages are required. From this directory, run:

```bash
python3 taskly.py --help
```

Optionally make the command easier to invoke:

```bash
chmod +x taskly.py
./taskly.py --help
```

## Usage

Add tasks with a low, medium, or high priority:

```bash
python3 taskly.py add "Write project README" --priority high
python3 taskly.py add "Review pull request"
```

List tasks:

```bash
python3 taskly.py list
```

Example output:

```text
ID   Status     Priority Created              Title
------------------------------------------------------------------------
1    pending    high     2026-10-14 16:31:00  Write project README
2    pending    medium   2026-10-14 16:32:10  Review pull request
```

Complete or delete a task by ID:

```bash
python3 taskly.py complete 1
python3 taskly.py delete 2
```

Use a different data file when needed:

```bash
python3 taskly.py --file demo-tasks.json list
```

Run the test suite:

```bash
python3 -m unittest -v
```

## Features

- Add, list, complete, and delete tasks.
- Numeric task IDs, completion status, priority, and UTC creation timestamps.
- Persistent, human-readable JSON storage.
- Clear validation and error messages for empty titles, invalid IDs, missing
  files, invalid JSON, and invalid task data.
- Built-in `--help` text with command examples.
- Standard-library-only implementation and `unittest` coverage.

## Project structure

```text
taskly-cli/
├── taskly.py          # CLI parser, task operations, storage, and formatting
├── test_taskly.py     # Unit tests
├── README.md          # Setup and usage documentation
└── tasks.json         # Created automatically after the first add command
```
