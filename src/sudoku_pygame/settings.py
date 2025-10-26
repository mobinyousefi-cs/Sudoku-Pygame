#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: Sudoku (PyGame)
File: settings.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-26
Updated: 2025-10-26
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
Global configuration and tunables.
===========================================================================
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class UISettings:
    width: int = 600
    height: int = 740
    grid_offset_y: int = 80
    grid_size: int = 540  # square area for 9x9
    margin: int = 20
    font_name: str = "freesansbold.ttf"
    title: str = "Sudoku — mobinyousefi-cs"


@dataclass(frozen=True)
class GameSettings:
    max_undo: int = 500
    hint_limit: int = 81  # effectively unlimited
    show_conflicts: bool = True


UI = UISettings()
GAME = GameSettings()

DIFFICULTY_CLUES = {
    "easy": 40,
    "medium": 33,
    "hard": 28,
    "expert": 24,
}