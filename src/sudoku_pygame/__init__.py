#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: Sudoku (PyGame)
File: __init__.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-26
Updated: 2025-10-26
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
Package initializer and CLI entry.

Usage:
python -m sudoku_pygame

Notes:
- Exposes `main()` for module execution.
===========================================================================
"""
from .game import main  # noqa: F401

__all__ = ["main"]