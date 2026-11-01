"""
Wireless Transmitter Placement Visualizer
DAA Assignment 2 | Backtracking algorithm | Python + Tkinter

Run:
    python wireless_transmitter_visualizer.py

Run built-in tests:
    python wireless_transmitter_visualizer.py --test

Model:
- Each grid cell is a possible transmitter location.
- A user-selected minimum separation distance is enforced.
- Two transmitters conflict if their Euclidean grid distance is smaller
  than the minimum separation.
- Backtracking searches for a set of locations that satisfies the constraint.
This is an educational simplified model, not a radio-frequency propagation simulator.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
from math import hypot
from typing import Generator, List, Tuple, Optional

BG = "#0b1120"
PANEL = "#111c31"
PANEL_LIGHT = "#17243b"
TEXT = "#edf3ff"
MUTED = "#9aabc7"
ACCENT = "#60a5fa"
GREEN = "#34d399"
RED = "#fb7185"
YELLOW = "#fbbf24"
LIGHT_CELL = "#dbeafe"
DARK_CELL = "#647da5"
TX_COLOR = "#082f49"

Location = Tuple[int, int]  # (row, column), zero-based


class WirelessPlacementApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Wireless Transmitter Placement | Backtracking Visualizer")
        self.root.geometry("1160x800")
        self.root.minsize(960, 700)
        self.root.configure(bg=BG)

        self.grid_var = tk.IntVar(value=6)
        self.tx_var = tk.IntVar(value=4)
        self.distance_var = tk.StringVar(value="2.0")
        self.mode_var = tk.StringVar(value="First solution")
        self.speed_var = tk.StringVar(value="Normal")

        self.status_var = tk.StringVar(value="Configure the grid and press Start.")
        self.step_var = tk.StringVar(value="0")
        self.candidate_var = tk.StringVar(value="0")
        self.solution_var = tk.StringVar(value="0")
        self.state_var = tk.StringVar(value="Ready")
        self.explanation_var = tk.StringVar(
            value="Each cell represents a possible transmitter site. The algorithm adds a site "
                  "only if it respects the minimum separation from all selected sites."
        )

        self.selected: List[Location] = []
        self.generator: Optional[Generator] = None
        self.running = False
        self.after_id = None
        self.finished = False
        self.step_count = 0
        self.candidate_checks = 0
        self.solution_count = 0
        self.current_cell: Optional[Location] = None
        self.current_action = "idle"
        self.cell_size = 52
        self.origin_x = 20
        self.origin_y = 20

        self._style()
        self._build_ui()
        self._draw_grid()

    def _style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "TCombobox", fieldbackground=PANEL_LIGHT, background=PANEL_LIGHT,
            foreground=TEXT, arrowcolor=TEXT, padding=6
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", PANEL_LIGHT)],
            foreground=[("readonly", TEXT)],
            selectbackground=[("readonly", PANEL_LIGHT)],
            selectforeground=[("readonly", TEXT)]
        )

    def _build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=24, pady=(18, 12))
        tk.Label(
            header, text="WIRELESS PLACEMENT", bg=BG, fg=TEXT,
            font=("Segoe UI", 23, "bold")
        ).pack(anchor="w")
        tk.Label(
            header, text="Backtracking visualizer for constrained transmitter locations",
            bg=BG, fg=MUTED, font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(3, 0))

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=24, pady=(0, 14))

        left = tk.Frame(main, bg=PANEL, highlightthickness=1, highlightbackground="#24334d")
        left.pack(side="left", fill="both", expand=True, padx=(0, 14))

        right = tk.Frame(main, bg=BG, width=320)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        board_header = tk.Frame(left, bg=PANEL)
        board_header.pack(fill="x", padx=18, pady=(15, 8))
        tk.Label(board_header, text="Candidate site grid", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(board_header, text="TX = transmitter", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="right")

        self.canvas = tk.Canvas(left, bg=PANEL, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.canvas.bind("<Configure>", lambda _event: self._draw_grid())

        self.status_label = tk.Label(
            left, textvariable=self.status_var, bg=PANEL_LIGHT, fg=TEXT,
            font=("Segoe UI", 10), anchor="w", justify="left",
            padx=12, pady=10, wraplength=700
        )
        self.status_label.pack(fill="x", padx=14, pady=(0, 14))

        stats = self._card(right, "LIVE STATISTICS")
        stat_grid = tk.Frame(stats, bg=PANEL)
        stat_grid.pack(fill="x")
        self._stat(stat_grid, "STEPS", self.step_var, 0, 0)
        self._stat(stat_grid, "CANDIDATE CHECKS", self.candidate_var, 0, 1)
        self._stat(stat_grid, "SOLUTIONS", self.solution_var, 1, 0)
        self._stat(stat_grid, "STATUS", self.state_var, 1, 1)


        setup = self._card(right, "PLACEMENT SETTINGS")
        self._setting_row(setup, "Grid size", self.grid_var, [4, 5, 6, 7, 8], "grid")
        self._setting_row(setup, "Transmitters", self.tx_var, list(range(1, 9)), "tx")

        tk.Label(setup, text="Minimum separation (grid units)", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 4))
        self.distance_combo = ttk.Combobox(
            setup, textvariable=self.distance_var,
            values=["1.0", "1.5", "2.0", "2.5", "3.0"], state="readonly"
        )
        self.distance_combo.pack(fill="x", pady=(0, 10))
        self.distance_combo.bind("<<ComboboxSelected>>", lambda _e: self.reset())

        tk.Label(setup, text="Search mode", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        self.mode_combo = ttk.Combobox(
            setup, textvariable=self.mode_var,
            values=["First solution", "All solutions"], state="readonly"
        )
        self.mode_combo.pack(fill="x", pady=(0, 10))
        self.mode_combo.bind("<<ComboboxSelected>>", lambda _e: self.reset())

        tk.Label(setup, text="Animation speed", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 4))
        self.speed_combo = ttk.Combobox(
            setup, textvariable=self.speed_var,
            values=["Slow", "Normal", "Fast"], state="readonly"
        )
        self.speed_combo.pack(fill="x", pady=(0, 12))

        self._button(setup, "▶  Start / Resume", self.start, "#2563eb").pack(fill="x", pady=3)
        self._button(setup, "Ⅱ  Pause", self.pause, "#334155").pack(fill="x", pady=3)
        self._button(setup, "›  Next Step", self.next_step, "#1d4ed8").pack(fill="x", pady=3)
        self._button(setup, "↻  Reset", self.reset, "#334155").pack(fill="x", pady=3)

        explain = self._card(right, "ALGORITHM EXPLANATION")
        tk.Label(
            explain, textvariable=self.explanation_var, bg=PANEL, fg=MUTED,
            font=("Segoe UI", 9), justify="left", anchor="nw", wraplength=280
        ).pack(fill="x")

        legend = self._card(right, "VISUAL LEGEND")
        self._legend(legend, GREEN, "Accepted transmitter site")
        self._legend(legend, RED, "Rejected / conflicting site")
        self._legend(legend, YELLOW, "Current search position")
        self._legend(legend, "#38bdf8", "Minimum-separation guide")

        tk.Label(
            self.root,
            text="Educational model: separation is measured as straight-line distance between grid cells.",
            bg=BG, fg="#7284a2", font=("Segoe UI", 9)
        ).pack(fill="x", padx=24, pady=(0, 12))

    def _card(self, parent, title):
        frame = tk.Frame(parent, bg=PANEL, highlightthickness=1, highlightbackground="#24334d")
        frame.pack(fill="x", pady=(0, 12))
        tk.Label(frame, text=title, bg=PANEL, fg=ACCENT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(12, 8))
        inner = tk.Frame(frame, bg=PANEL)
        inner.pack(fill="x", padx=14, pady=(0, 13))
        return inner

    def _setting_row(self, parent, label, variable, values, kind):
        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill="x", pady=(0, 9))
        tk.Label(row, text=label, bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left")
        combo = ttk.Combobox(row, textvariable=variable, values=values,
                             width=7, state="readonly")
        combo.pack(side="right")
        combo.bind("<<ComboboxSelected>>", lambda _e: self.reset())
        if kind == "grid":
            self.grid_combo = combo
        else:
            self.tx_combo = combo

    def _button(self, parent, text, command, color):
        return tk.Button(
            parent, text=text, command=command, bg=color, fg="white",
            activebackground=ACCENT, activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            font=("Segoe UI", 10, "bold"), padx=10, pady=9
        )

    def _stat(self, parent, label, variable, row, col):
        box = tk.Frame(parent, bg=PANEL_LIGHT, padx=8, pady=8)
        box.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
        parent.grid_columnconfigure(col, weight=1)
        tk.Label(box, text=label, bg=PANEL_LIGHT, fg=MUTED,
                 font=("Segoe UI", 7, "bold")).pack(anchor="w")
        tk.Label(box, textvariable=variable, bg=PANEL_LIGHT, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(3, 0))

    def _legend(self, parent, color, text):
        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill="x", pady=3)
        tk.Label(row, text="   ", bg=color).pack(side="left", padx=(0, 8))
        tk.Label(row, text=text, bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left")

    @staticmethod
    def _distance(a: Location, b: Location) -> float:
        return hypot(a[0] - b[0], a[1] - b[1])

    @classmethod
    def _is_safe(cls, selected: List[Location], candidate: Location, minimum: float) -> bool:
        return all(cls._distance(site, candidate) >= minimum for site in selected)

    def _draw_grid(self):
        if not hasattr(self, "canvas"):
            return
        self.canvas.delete("all")
        n = int(self.grid_var.get())
        width = max(self.canvas.winfo_width(), 300)
        height = max(self.canvas.winfo_height(), 300)
        available = min(width - 46, height - 46)
        self.cell_size = max(24, int(available / n))
        board_size = self.cell_size * n
        self.origin_x = (width - board_size) / 2
        self.origin_y = (height - board_size) / 2
        x0, y0 = self.origin_x, self.origin_y

        # Draw cells first.
        for r in range(n):
            for c in range(n):
                x1, y1 = x0 + c * self.cell_size, y0 + r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                fill = LIGHT_CELL if (r + c) % 2 == 0 else DARK_CELL
                if self.current_cell == (r, c):
                    fill = {"reject": RED, "backtrack": YELLOW, "place": GREEN,
                            "solution": YELLOW}.get(self.current_action, fill)
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=fill)

        # Optional distance rings around accepted sites (visual guide only).
        try:
            minimum = float(self.distance_var.get())
        except ValueError:
            minimum = 2.0
        radius = minimum * self.cell_size
        for r, c in self.selected:
            cx = x0 + (c + 0.5) * self.cell_size
            cy = y0 + (r + 0.5) * self.cell_size
            self.canvas.create_oval(
                cx - radius, cy - radius, cx + radius, cy + radius,
                outline="#38bdf8", width=1, dash=(3, 4)
            )

        # Draw transmitter markers over cells and rings.
        for index, (r, c) in enumerate(self.selected, start=1):
            cx = x0 + (c + 0.5) * self.cell_size
            cy = y0 + (r + 0.5) * self.cell_size
            radius_icon = max(10, self.cell_size * 0.29)
            self.canvas.create_oval(
                cx - radius_icon, cy - radius_icon, cx + radius_icon, cy + radius_icon,
                fill=TX_COLOR, outline=GREEN, width=2
            )
            self.canvas.create_text(
                cx, cy, text=f"T{index}", fill="white",
                font=("Segoe UI", max(8, int(self.cell_size * 0.20)), "bold")
            )

        # Row and column labels.
        for i in range(n):
            self.canvas.create_text(
                x0 - 12, y0 + (i + 0.5) * self.cell_size, text=str(i + 1),
                fill=MUTED, font=("Segoe UI", 8), anchor="e"
            )
            self.canvas.create_text(
                x0 + (i + 0.5) * self.cell_size, y0 + board_size + 12,
                text=chr(65 + i), fill=MUTED, font=("Segoe UI", 8), anchor="n"
            )

    def _make_generator(self):
        n = int(self.grid_var.get())
        target = int(self.tx_var.get())
        minimum = float(self.distance_var.get())
        mode = self.mode_var.get()
        selected: List[Location] = []
        total_cells = n * n
        stats = {"checks": 0, "solutions": 0, "stop": False}

        def search(start_index: int):
            if len(selected) == target:
                stats["solutions"] += 1
                yield (selected.copy(), selected[-1] if selected else None, "solution",
                       stats["checks"], stats["solutions"],
                       f"Valid placement {stats['solutions']} found: {target} transmitters satisfy the minimum separation of {minimum:g} grid units.")
                if mode == "First solution":
                    stats["stop"] = True
                return

            # Not enough remaining cells to fill all remaining transmitter slots.
            if total_cells - start_index < target - len(selected):
                return

            for index in range(start_index, total_cells):
                if stats["stop"]:
                    return
                row, col = divmod(index, n)
                candidate = (row, col)
                stats["checks"] += 1

                if self._is_safe(selected, candidate, minimum):
                    selected.append(candidate)
                    yield (selected.copy(), candidate, "place", stats["checks"], stats["solutions"],
                           f"Candidate row {row + 1}, column {col + 1} is at least {minimum:g} grid units from every selected transmitter. Accept it and search for the next site.")
                    yield from search(index + 1)
                    if stats["stop"]:
                        return
                    selected.pop()
                    yield (selected.copy(), candidate, "backtrack", stats["checks"], stats["solutions"],
                           f"Undo the choice at row {row + 1}, column {col + 1} and try a different candidate. Backtracking explores another combination.")
                else:
                    yield (selected.copy(), candidate, "reject", stats["checks"], stats["solutions"],
                           f"Reject row {row + 1}, column {col + 1}: it is closer than {minimum:g} grid units to an already selected transmitter.")

        yield from search(0)

    def _validate(self):
        n = int(self.grid_var.get())
        target = int(self.tx_var.get())
        if target > n * n:
            messagebox.showerror("Invalid settings", "The number of transmitters cannot exceed the number of grid cells.")
            return False
        try:
            if float(self.distance_var.get()) < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid distance", "Choose a valid minimum separation of at least 1 grid unit.")
            return False
        return True

    def start(self):
        if not self._validate():
            return
        if self.finished:
            self.reset()
        if self.generator is None:
            self.generator = self._make_generator()
        self.running = True
        self.state_var.set("Running")
        self.status_var.set("Searching for valid transmitter locations…")
        self._schedule()

    def pause(self):
        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        if not self.finished:
            self.state_var.set("Paused")
            self.status_var.set("Paused. Resume the search or advance one event at a time.")

    def next_step(self):
        if not self._validate() or self.finished:
            return
        if self.generator is None:
            self.generator = self._make_generator()
        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self._advance()

    def _schedule(self):
        if not self.running:
            return
        delay = {"Slow": 700, "Normal": 280, "Fast": 80}.get(self.speed_var.get(), 280)
        self.after_id = self.root.after(delay, self._advance)

    def _advance(self):
        if self.finished:
            return
        try:
            selected, current, action, checks, solutions, explanation = next(self.generator)
        except StopIteration:
            self.finished = True
            self.running = False
            self.after_id = None
            self.state_var.set("Complete")
            self.status_var.set(
                f"Search complete: {self.solution_count} valid placement(s), "
                f"{self.candidate_checks} candidate checks."
            )
            self.explanation_var.set(
                "Search finished. The first-solution mode stops after one valid configuration; "
                "all-solutions mode counts every combination that meets the selected distance constraint."
            )
            self._draw_grid()
            return

        self.selected = selected
        self.current_cell = current
        self.current_action = action
        self.candidate_checks = checks
        self.solution_count = solutions
        self.step_count += 1
        self.step_var.set(str(self.step_count))
        self.candidate_var.set(str(self.candidate_checks))
        self.solution_var.set(str(self.solution_count))
        self.explanation_var.set(explanation)
        self._draw_grid()

        labels = {
            "place": "Site accepted",
            "reject": "Candidate rejected",
            "backtrack": "Backtracking",
            "solution": "Valid placement found",
        }
        self.status_var.set(f"Step {self.step_count}: {labels[action]}. {explanation}")
        self.state_var.set("Running" if self.running else "Step mode")

        if self.running:
            self._schedule()

    def reset(self):
        self.pause()
        self.generator = None
        self.selected = []
        self.finished = False
        self.step_count = 0
        self.candidate_checks = 0
        self.solution_count = 0
        self.current_cell = None
        self.current_action = "idle"
        self.step_var.set("0")
        self.candidate_var.set("0")
        self.solution_var.set("0")
        self.state_var.set("Ready")
        self.status_var.set("Configure the grid and press Start, or use Next Step to inspect the search.")
        self.explanation_var.set(
            "Each cell represents a possible transmitter site. The algorithm adds a site only if it "
            "respects the minimum separation from all selected sites."
        )
        self._draw_grid()


def run_tests():
    def is_safe(selected, candidate, minimum):
        return all(hypot(a[0] - candidate[0], a[1] - candidate[1]) >= minimum
                   for a in selected)

    # Boundary/logic tests for separation and solution counts.
    assert is_safe([], (0, 0), 2.0)
    assert is_safe([(0, 0)], (0, 2), 2.0)  # exactly the minimum distance is allowed
    assert not is_safe([(0, 0)], (1, 1), 2.0)  # sqrt(2) < 2
    assert is_safe([(0, 0)], (2, 0), 2.0)
    print("PASS: empty placement accepts a candidate.")
    print("PASS: candidates exactly at minimum distance are allowed.")
    print("PASS: candidates closer than minimum distance are rejected.")
    print("PASS: candidates beyond minimum distance are allowed.")

    def count_placements(n, target, minimum):
        selected = []
        count = 0

        def visit(start):
            nonlocal count
            if len(selected) == target:
                count += 1
                return
            for index in range(start, n * n):
                candidate = divmod(index, n)
                if is_safe(selected, candidate, minimum):
                    selected.append(candidate)
                    visit(index + 1)
                    selected.pop()

        visit(0)
        return count

    assert count_placements(2, 1, 2.0) == 4
    assert count_placements(2, 2, 2.0) == 0
    assert count_placements(3, 2, 2.0) > 0
    print("PASS: 2x2 grid with 1 transmitter has 4 configurations.")
    print("PASS: 2x2 grid cannot fit 2 transmitters with separation 2.0.")
    print("PASS: 3x3 grid can fit 2 transmitters with separation 2.0.")
    print("All tests passed.")


if __name__ == "__main__":
    if "--test" in sys.argv:
        run_tests()
    else:
        window = tk.Tk()
        app = WirelessPlacementApp(window)
        window.mainloop()
