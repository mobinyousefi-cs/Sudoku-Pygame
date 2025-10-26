# Sudoku (PyGame)

A polished Sudoku game implemented with **PyGame**, featuring a clean architecture, an exact backtracking **solver**, a **unique-solution** puzzle **generator**, pencil notes, undo/redo, hints, and save/load.

> Author: **Mobin Yousefi** — [github.com/mobinyousefi-cs](https://github.com/mobinyousefi-cs)

---

## ✨ Features
- 9×9 grid with peer highlighting and conflict display
- Difficulty presets: **Easy**, **Medium**, **Hard**, **Expert** (clue targets: 40/33/28/24)
- Pencil mode notes (per-cell candidates)
- **Undo/Redo**, **Hint**, **Check**, **Save/Load**
- Keyboard controls + toolbar buttons
- Deterministic tests for solver/generator

## 🗂️ Project Structure
```
src/sudoku_pygame/  # game modules (UI, board, generator)
tests/              # unit tests
scripts/run.sh      # convenience launcher
```

## 🚀 Quickstart
```bash
# 1) Create venv (recommended)
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\\Scripts\\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Run the game (default: Medium)
python -m sudoku_pygame

# Or choose a difficulty
python -m sudoku_pygame --difficulty easy
python -m sudoku_pygame --difficulty hard
```

## 🎮 Controls
- **Mouse**: click a cell to select; click toolbar buttons
- **Numbers 1–9**: set value; with **P** toggled, add/remove pencil note
- **0 / Backspace / Delete**: clear cell
- **Arrows / WASD**: navigate
- **P**: toggle Pencil mode
- **Space**: hint (fills one correct cell)
- **U / R**: undo / redo

## 💾 Save/Load
Saves a `savegame.json` in the project directory (ignored by git). Use **Save** and **Load** toolbar buttons.

## 🧪 Tests
```bash
pip install pytest
pytest
```

## 📐 Design Notes
- **Generator**: create a full valid grid then iteratively remove numbers while preserving **unique** solution (checked via a solution counter).
- **Solver**: optimized backtracking with early validity checks.
- **Board**: keeps `givens`, `values`, `notes`, and move stacks for undo/redo.
- **UI**: separates rendering and input; configurable in `settings.py`.

## 🛠️ Development
- Code style: 4‑space indent, LF line endings (`.editorconfig` included)
- Packaging: `pyproject.toml` (PEP 621), importable package under `src/`
- License: MIT

---

**Enjoy solving!**