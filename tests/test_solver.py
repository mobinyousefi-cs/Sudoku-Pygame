#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: Sudoku (PyGame)
File: tests/test_solver.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-26
Updated: 2025-10-26
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
Basic property tests for the solver & generator.
===========================================================================
"""
from sudoku_pygame.generator import count_solutions, generate_puzzle, make_full_grid


def test_full_grid_is_solved():
    g = make_full_grid()
    assert all(g[r][c] != 0 for r in range(9) for c in range(9))


def test_generated_puzzle_has_unique_solution():
    p, _ = generate_puzzle(clues=33, seed=42)
    assert count_solutions([row[:] for row in p]) == 1