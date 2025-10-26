#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: Sudoku (PyGame)
File: generator.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-26
Updated: 2025-10-26
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
Sudoku solver and puzzle generator with uniqueness enforcement.

Usage:
from sudoku_pygame.generator import generate_puzzle
board, solution = generate_puzzle(clues=33)

Notes:
- Backtracking solver with counter to ensure unique solutions.
- Generator builds a full grid then digs holes respecting clue count.
===========================================================================
"""
from __future__ import annotations

import random
from typing import List, Optional, Tuple

Grid = List[List[int]]


def find_empty(grid: Grid) -> Optional[Tuple[int, int]]:
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                return r, c
    return None


def is_valid(grid: Grid, r: int, c: int, v: int) -> bool:
    if any(grid[r][x] == v for x in range(9)):
        return False
    if any(grid[x][c] == v for x in range(9)):
        return False
    br, bc = 3 * (r // 3), 3 * (c // 3)
    for rr in range(br, br + 3):
        for cc in range(bc, bc + 3):
            if grid[rr][cc] == v:
                return False
    return True


def solve(grid: Grid) -> bool:
    pos = find_empty(grid)
    if not pos:
        return True
    r, c = pos
    nums = list(range(1, 10))
    random.shuffle(nums)
    for v in nums:
        if is_valid(grid, r, c, v):
            grid[r][c] = v
            if solve(grid):
                return True
            grid[r][c] = 0
    return False


def count_solutions(grid: Grid, limit: int = 2) -> int:
    # backtracking counter with early exit
    pos = find_empty(grid)
    if not pos:
        return 1
    r, c = pos
    total = 0
    for v in range(1, 10):
        if is_valid(grid, r, c, v):
            grid[r][c] = v
            total += count_solutions(grid, limit)
            if total >= limit:
                grid[r][c] = 0
                return total
            grid[r][c] = 0
    return total


def make_full_grid() -> Grid:
    grid = [[0] * 9 for _ in range(9)]
    solve(grid)
    return grid


def generate_puzzle(clues: int = 33, seed: Optional[int] = None) -> Tuple[Grid, Grid]:
    if seed is not None:
        random.seed(seed)
    full = make_full_grid()
    puzzle = [row[:] for row in full]

    # cells in random order
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    # dig while keeping at least `clues` cells
    holes_target = 81 - max(17, min(81, clues))
    holes = 0
    for r, c in cells:
        if holes >= holes_target:
            break
        backup = puzzle[r][c]
        if backup == 0:
            continue
        puzzle[r][c] = 0
        # uniqueness check
        work = [row[:] for row in puzzle]
        if count_solutions(work, limit=2) != 1:
            puzzle[r][c] = backup
        else:
            holes += 1

    return puzzle, full