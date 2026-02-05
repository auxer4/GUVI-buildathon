# VS Code Workspace Setup

This folder contains VS Code configuration files for optimal development experience.

## Files Included

- **`extensions.json`** — Recommends essential extensions for Python, FastAPI, Docker, and Git workflows.
- **`settings.json`** — Workspace-wide settings for Python formatting, linting, testing, and YAML schemas.
- **`launch.json`** — Debug configurations for FastAPI dev server, pytest, and Python scripts.
- **`tasks.json`** — Automation tasks for running the server, tests, linting, and formatting.

## Quick Start

### 1. Install Recommended Extensions
Run the terminal command:
```powershell
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension redhat.vscode-yaml
code --install-extension eamodio.gitlens
code --install-extension ms-azuretools.vscode-docker
code --install-extension charliermarsh.ruff
```

Or, VS Code will prompt you to install from `extensions.json` on first folder open.

### 2. Create Virtual Environment
In Terminal, run:
```powershell
python -m venv venv
```

Then activate it:
- **Windows PowerShell:** `.\venv\Scripts\Activate.ps1`
- **Windows CMD:** `venv\Scripts\activate.bat`
- **macOS/Linux:** `source venv/bin/activate`

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Start Developing

**Run the FastAPI server** (auto-reload):
- Press `F5` (or Debug: Start Debugging) and select "FastAPI - Main App".

**Run tests**:
- Press `Ctrl+Shift+D` → select "Pytest - All Tests".
- Or use Terminal: `Task: Run Task` → "Tests: Run All".

**Format & Lint**:
- Terminal: `Task: Run Task` → "Format: Black" or "Lint: Flake8".
- Or on-save (Black is configured to format on save).

## Configuration Details

### settings.json
- **Python formatter**: Black (configured for 88-char line, ruler at 120).
- **Linting**: Flake8 with relaxed E203/W503 rules.
- **Testing**: Pytest integration with test discovery in `shreyas/tests`.
- **Type checking**: Pylance in "basic" mode.
- **YAML**: Red Hat YAML extension with schema hints.
- **Editor**: Auto-format on save, trim whitespace, final newline insertion.

### launch.json
Four debug configurations:
1. **FastAPI - Main App** — Run uvicorn with hot reload.
2. **Pytest - All Tests** — Run all tests in `shreyas/tests`.
3. **Pytest - Single File** — Debug the currently open test file.
4. **Python - Current File** — Run any Python script.

### tasks.json
Pre-configured tasks accessible via `Terminal: Run Task`:
- **FastAPI: Run Dev Server** — Starts uvicorn on `http://localhost:8000`.
- **Tests: Run All** — Pytest with coverage report.
- **Lint: Flake8** — Code quality check.
- **Format: Black** — Reformat all `.py` files.
- **Type Check: Mypy** — Static type verification.
- **Imports: Sort with isort** — Organize imports per Black profile.
- **Setup: Create Virtual Environment** — Initialize venv.
- **Setup: Install Dependencies** — Install from `requirements.txt`.

## Keyboard Shortcuts (Common)

| Action | Shortcut |
|--------|----------|
| Format Document | `Shift+Alt+F` |
| Run Current File | `Ctrl+F5` |
| Start Debugging | `F5` |
| Open Terminal | `` Ctrl+` `` |
| Open Command Palette | `Ctrl+Shift+P` |
| Go to Definition | `F12` |
| Find All References | `Shift+F12` |

## Notes

- **Interpreter Path**: Set to `${workspaceFolder}/venv/Scripts/python.exe` (Windows). Adjust if using a different venv location.
- **Python Path**: Added `${workspaceFolder}` to analysis extraPaths for proper module resolution across `rishi`, `saachi`, `shreyas`, `shared`.
- **Exclude Patterns**: `__pycache__`, `*.pyc`, `.pytest_cache`, and `venv` are excluded from file watchers and search.
- **Line Length**: 120 characters (Flake8 max, with Black at 88 as default formatter).

---

Happy coding! 🚀
