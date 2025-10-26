#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: Sudoku (PyGame)
File: game.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-26
Updated: 2025-10-26
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
Module entrypoint. Parses `--difficulty` and starts the PyGame UI.
===========================================================================
"""
from __future__ import annotations

import argparse

from .ui import SudokuUI


def main() -> None:
    parser = argparse.ArgumentParser(description="Sudoku (PyGame)")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard", "expert"], default="medium")
    args = parser.parse_args()

    ui = SudokuUI(difficulty=args.difficulty)
    ui.run()


if __name__ == "__main__":
    main()