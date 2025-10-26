#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: Sudoku (PyGame)
File: board.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-26
Updated: 2025-10-26
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
Immutable givens + editable cells, pencil notes, conflict detection,
undo/redo stack, serialization for save/load.
===========================================================================
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

Grid = List[List[int]]
Cell = Tuple[int, int]


@dataclass
class Move:
    pos: Cell
    prev: int
    new: int
    was_note: bool = False


@dataclass
class Board:
    givens: Grid
    solution: Grid
    values: Grid
    notes: Dict[Cell, Set[int]] = field(default_factory=dict)
    undo_stack: List[Move] = field(default_factory=list)
    redo_stack: List[Move] = field(default_factory=list)

    @classmethod
    def from_puzzle(cls, puzzle: Grid, solution: Grid) -> "Board":
        return cls(
            givens=[row[:] for row in puzzle],
            solution=[row[:] for row in solution],
            values=[row[:] for row in puzzle],
        )

    def is_given(self, r: int, c: int) -> bool:
        return self.givens[r][c] != 0

    def set_value(self, r: int, c: int, v: int, record=True) -> None:
        if self.is_given(r, c):
            return
        prev = self.values[r][c]
        if prev == v:
            return
        self.values[r][c] = v
        if (r, c) in self.notes:
            self.notes.pop((r, c), None)
        if record:
            self.undo_stack.append(Move((r, c), prev, v))
            self.redo_stack.clear()

    def toggle_note(self, r: int, c: int, v: int, record=True) -> None:
        if self.is_given(r, c):
            return
        if self.values[r][c] != 0:
            return
        s = self.notes.setdefault((r, c), set())
        prev = set(s)
        if v in s:
            s.remove(v)
        else:
            s.add(v)
        if record:
            self.undo_stack.append(Move((r, c), 0, 0, was_note=True))
            self.redo_stack.clear()

    def clear_cell(self, r: int, c: int) -> None:
        if self.is_given(r, c):
            return
        prev = self.values[r][c]
        self.values[r][c] = 0
        self.notes.pop((r, c), None)
        self.undo_stack.append(Move((r, c), prev, 0))
        self.redo_stack.clear()

    def conflicts(self) -> Set[Cell]:
        bad: Set[Cell] = set()
        # rows
        for r in range(9):
            seen: Dict[int, List[int]] = {}
            for c in range(9):
                v = self.values[r][c]
                if v == 0:
                    continue
                seen.setdefault(v, []).append(c)
            for v, cols in seen.items():
                if len(cols) > 1:
                    for c in cols:
                        bad.add((r, c))
        # cols
        for c in range(9):
            seen: Dict[int, List[int]] = {}
            for r in range(9):
                v = self.values[r][c]
                if v == 0:
                    continue
                seen.setdefault(v, []).append(r)
            for v, rows in seen.items():
                if len(rows) > 1:
                    for r in rows:
                        bad.add((r, c))
        # boxes
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                seen: Dict[int, List[Cell]] = {}
                for r in range(br, br + 3):
                    for c in range(bc, bc + 3):
                        v = self.values[r][c]
                        if v == 0:
                            continue
                        seen.setdefault(v, []).append((r, c))
                for v, cells in seen.items():
                    if len(cells) > 1:
                        bad.update(cells)
        return bad

    def is_complete(self) -> bool:
        return all(self.values[r][c] == self.solution[r][c] for r in range(9) for c in range(9))

    def next_empty(self) -> Optional[Cell]:
        for r in range(9):
            for c in range(9):
                if self.values[r][c] == 0:
                    return r, c
        return None

    def hint(self) -> Optional[Move]:
        pos = self.next_empty()
        if not pos:
            return None
        r, c = pos
        val = self.solution[r][c]
        prev = self.values[r][c]
        self.set_value(r, c, val, record=False)
        m = Move((r, c), prev, val)
        self.undo_stack.append(m)
        self.redo_stack.clear()
        return m

    def undo(self) -> Optional[Move]:
        if not self.undo_stack:
            return None
        m = self.undo_stack.pop()
        r, c = m.pos
        self.values[r][c] = m.prev
        if m.was_note:
            # notes are not fully reversible in this simple model
            pass
        self.redo_stack.append(m)
        return m

    def redo(self) -> Optional[Move]:
        if not self.redo_stack:
            return None
        m = self.redo_stack.pop()
        r, c = m.pos
        self.values[r][c] = m.new
        self.undo_stack.append(m)
        return m

    # --- Serialization ---
    def to_dict(self) -> dict:
        return {
            "givens": self.givens,
            "solution": self.solution,
            "values": self.values,
            "notes": {f"{r},{c}": sorted(list(vs)) for (r, c), vs in self.notes.items()},
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Board":
        notes: Dict[Cell, Set[int]] = {}
        for k, vs in d.get("notes", {}).items():
            r, c = map(int, k.split(","))
            notes[(r, c)] = set(vs)
        return cls(d["givens"], d["solution"], d["values"], notes=notes)