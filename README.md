# AXT

Automated Xml Transformation
TODO: Update descrption

## Requirements

- Python 3.11+
- I use VS Code, so install TODO

---

## Installation

### Option 1 - Development Setup (Poetry)

Clone the repository:

```bash
git clone <repo-url>
cd AXT
poetry install
poetry run axt --help
```

Install dependencies:

```bash
poetry install
```

Activate the virtual environment (Poetry 2.x):

```bash
eval $(poetry env activate)
```

Run the CLI:

```bash
axt --help
```

If you prefer not to activate the environment:

```bash
poetry run axt --help
```

### Option 2 - End User Installation (Wheel)

Build the package first (for developer):

```bash
poetry build
```

This creates something like:

```bash
dist/axt-0.1.0-py3-none-any.whl
```

Install (end user):

```bash
pip install dist/axt-0.1.0-py3-none-any.whl
```

Run:

```bash
axt --help
```

So Poetry is not required for end users.

## Makefile Shortcuts

The project provides a `Makefile` with common development commands.

Run them with:

```bash
make <command>
```
