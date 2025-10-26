#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================================================
Project: Sudoku (PyGame)
File: ui.py
Author: Mobin Yousefi (GitHub: github.com/mobinyousefi-cs)
Created: 2025-10-26
Updated: 2025-10-26
License: MIT License (see LICENSE file for details)
===========================================================================

Description:
PyGame rendering & input handling for Sudoku. Supports:
- Mouse/keyboard input, pencil notes, highlighting peers & conflicts
- Toolbar buttons (New, Check, Hint, Undo, Redo, Save, Load, Pencil)
- Timer and difficulty selection
===========================================================================
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Optional, Tuple

import pygame

from .board import Board
from .colors import *  # noqa
from .generator import generate_puzzle
from .settings import DIFFICULTY_CLUES, GAME, UI

Cell = Tuple[int, int]
SAVE_PATH = os.path.join(os.getcwd(), "savegame.json")


@dataclass
class ToolbarButton:
    rect: pygame.Rect
    label: str
    action: str


class SudokuUI:
    def __init__(self, difficulty: str = "medium") -> None:
        pygame.init()
        pygame.display.set_caption(UI.title)
        self.screen = pygame.display.set_mode((UI.width, UI.height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(UI.font_name, 28)
        self.small = pygame.font.Font(UI.font_name, 20)
        self.tiny = pygame.font.Font(UI.font_name, 14)

        self.selected: Optional[Cell] = None
        self.pencil_mode = False
        self.started_at = time.time()
        self.paused = False
        self.pause_time = 0.0

        self.new_game(difficulty)

    # --- Game state management ---
    def new_game(self, difficulty: str) -> None:
        clues = DIFFICULTY_CLUES.get(difficulty, 33)
        puzzle, solution = generate_puzzle(clues=clues)
        self.board = Board.from_puzzle(puzzle, solution)
        self.selected = None
        self.started_at = time.time()
        self.pause_time = 0.0
        self.difficulty = difficulty
        self._build_toolbar()

    def _build_toolbar(self) -> None:
        buttons = [
            ("New E", "new_easy"), ("New M", "new_medium"), ("New H", "new_hard"), ("New X", "new_expert"),
            ("Check", "check"), ("Hint", "hint"), ("Undo", "undo"), ("Redo", "redo"),
            ("Pencil", "pencil"), ("Save", "save"), ("Load", "load"), ("Quit", "quit"),
        ]
        x, y, w, h, pad = 10, 10, 84, 32, 8
        self.toolbar: list[ToolbarButton] = []
        for label, action in buttons:
            rect = pygame.Rect(x, y, w, h)
            self.toolbar.append(ToolbarButton(rect, label, action))
            x += w + pad

    # --- Rendering helpers ---
    def draw(self) -> None:
        self.screen.fill(WHITE)
        self._draw_toolbar()
        self._draw_grid()
        self._draw_info()
        pygame.display.flip()

    def _draw_toolbar(self) -> None:
        for btn in self.toolbar:
            pygame.draw.rect(self.screen, PRIMARY_DARK if btn.action == "pencil" and self.pencil_mode else PRIMARY, btn.rect, border_radius=8)
            label = self.small.render(btn.label, True, WHITE)
            self.screen.blit(label, (btn.rect.x + (btn.rect.w - label.get_width()) // 2, btn.rect.y + 6))

    def _grid_rect(self) -> pygame.Rect:
        g = pygame.Rect(UI.margin, UI.grid_offset_y, UI.grid_size, UI.grid_size)
        # center horizontally
        g.x = (UI.width - g.w) // 2
        return g

    def _cell_rect(self, r: int, c: int) -> pygame.Rect:
        g = self._grid_rect()
        s = g.w // 9
        return pygame.Rect(g.x + c * s, g.y + r * s, s, s)

    def _draw_grid(self) -> None:
        g = self._grid_rect()
        s = g.w // 9

        # peer/selection highlights
        if self.selected:
            rs, cs = self.selected
            for k in range(9):
                pygame.draw.rect(self.screen, PEER_BG, self._cell_rect(rs, k))
                pygame.draw.rect(self.screen, PEER_BG, self._cell_rect(k, cs))
            br, bc = 3 * (rs // 3), 3 * (cs // 3)
            for r in range(br, br + 3):
                for c in range(bc, bc + 3):
                    pygame.draw.rect(self.screen, PEER_BG, self._cell_rect(r, c))
            pygame.draw.rect(self.screen, SELECT_BG, self._cell_rect(rs, cs))

        # cells
        conflicts = self.board.conflicts() if GAME.show_conflicts else set()
        for r in range(9):
            for c in range(9):
                rect = self._cell_rect(r, c)
                pygame.draw.rect(self.screen, LIGHT_GRAY, rect)
                val = self.board.values[r][c]
                if self.board.is_given(r, c):
                    text = self.font.render(str(val), True, LOCKED)
                    self.screen.blit(text, (rect.x + (s - text.get_width()) // 2, rect.y + (s - text.get_height()) // 2))
                else:
                    if val != 0:
                        color = WARN if (r, c) in conflicts else BLACK
                        text = self.font.render(str(val), True, color)
                        self.screen.blit(text, (rect.x + (s - text.get_width()) // 2, rect.y + (s - text.get_height()) // 2))
                    else:
                        # draw pencil notes
                        notes = self.board.notes.get((r, c))
                        if notes:
                            for v in notes:
                                rr = (v - 1) // 3
                                cc = (v - 1) % 3
                                nx = rect.x + 6 + cc * (s // 3)
                                ny = rect.y + 4 + rr * (s // 3)
                                t = self.tiny.render(str(v), True, DARK_GRAY)
                                self.screen.blit(t, (nx, ny))

        # grid lines
        for k in range(10):
            lw = 3 if k % 3 == 0 else 1
            # horizontal
            pygame.draw.line(self.screen, BOX_LINE if lw == 3 else GRID_LINE, (g.x, g.y + k * s), (g.x + g.w, g.y + k * s), lw)
            # vertical
            pygame.draw.line(self.screen, BOX_LINE if lw == 3 else GRID_LINE, (g.x + k * s, g.y), (g.x + k * s, g.y + g.h), lw)

    def _draw_info(self) -> None:
        # timer & status
        elapsed = self._elapsed()
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        t = self.small.render(f"{self.difficulty.title()}  |  Time: {mins:02d}:{secs:02d}", True, BLACK)
        self.screen.blit(t, (UI.margin, UI.grid_offset_y + UI.grid_size + 12))

        # footer hint
        hint = self.tiny.render("Keys: 1-9 input | 0/Del clear | Arrows move | P pencil | Space hint | U/R undo/redo", True, DARK_GRAY)
        self.screen.blit(hint, (UI.margin, UI.height - 26))

    def _elapsed(self) -> float:
        if self.paused:
            return self.pause_time
        return time.time() - self.started_at

    # --- Input handling ---
    def handle_event(self, e: pygame.event.Event) -> bool:
        if e.type == pygame.QUIT:
            return False
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self._handle_toolbar_click(e.pos):
                return True
            self._handle_grid_click(e.pos)
            return True
        if e.type == pygame.KEYDOWN:
            return self._handle_key(e.key)
        return True

    def _handle_toolbar_click(self, pos) -> bool:
        for b in self.toolbar:
            if b.rect.collidepoint(pos):
                return self._dispatch_action(b.action)
        return False

    def _dispatch_action(self, action: str) -> bool:
        if action.startswith("new_"):
            diff = action.split("_", 1)[1]
            self.new_game(diff)
            return True
        if action == "check":
            if self.board.is_complete():
                pygame.display.set_caption(f"{UI.title} — Completed! 🎉")
            else:
                pygame.display.set_caption(f"{UI.title} — Not solved yet")
            return True
        if action == "hint":
            self.board.hint()
            return True
        if action == "undo":
            self.board.undo()
            return True
        if action == "redo":
            self.board.redo()
            return True
        if action == "pencil":
            self.pencil_mode = not self.pencil_mode
            return True
        if action == "save":
            self.save()
            return True
        if action == "load":
            self.load()
            return True
        if action == "quit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return True
        return False

    def _handle_grid_click(self, pos) -> None:
        g = self._grid_rect()
        if not g.collidepoint(pos):
            return
        s = g.w // 9
        c = (pos[0] - g.x) // s
        r = (pos[1] - g.y) // s
        self.selected = (int(r), int(c))

    def _handle_key(self, key: int) -> bool:
        if key in (pygame.K_p,):
            self.pencil_mode = not self.pencil_mode
            return True
        if key in (pygame.K_u,):
            self.board.undo(); return True
        if key in (pygame.K_r,):
            self.board.redo(); return True
        if key in (pygame.K_SPACE,):
            self.board.hint(); return True
        if not self.selected:
            return True
        r, c = self.selected
        # movement
        if key in (pygame.K_LEFT, pygame.K_a):
            self.selected = (r, max(0, c - 1)); return True
        if key in (pygame.K_RIGHT, pygame.K_d):
            self.selected = (r, min(8, c + 1)); return True
        if key in (pygame.K_UP, pygame.K_w):
            self.selected = (max(0, r - 1), c); return True
        if key in (pygame.K_DOWN, pygame.K_s):
            self.selected = (min(8, r + 1), c); return True

        # input
        if key in (pygame.K_DELETE, pygame.K_BACKSPACE, pygame.K_0, pygame.K_KP0):
            self.board.clear_cell(r, c); return True
        for n in range(1, 10):
            if key in (getattr(pygame, f"K_{n}"), getattr(pygame, f"K_KP{n}")):
                if self.pencil_mode:
                    self.board.toggle_note(r, c, n)
                else:
                    self.board.set_value(r, c, n)
                return True
        return True

    # --- Save/Load ---
    def save(self) -> None:
        data = {
            "difficulty": self.difficulty,
            "board": self.board.to_dict(),
            "elapsed": self._elapsed(),
        }
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f)
        pygame.display.set_caption(f"{UI.title} — Saved to savegame.json")

    def load(self) -> None:
        if not os.path.exists(SAVE_PATH):
            pygame.display.set_caption(f"{UI.title} — No save found")
            return
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.difficulty = data.get("difficulty", "medium")
        self.board = Board.from_dict(data["board"])
        self.started_at = time.time() - float(data.get("elapsed", 0.0))
        self.pause_time = 0.0
        pygame.display.set_caption(f"{UI.title} — Loaded savegame.json")

    # --- Loop ---
    def run(self) -> None:
        running = True
        while running:
            for e in pygame.event.get():
                running = self.handle_event(e)
            self.draw()
            self.clock.tick(60)
        pygame.quit()