"""Graphical Tic-Tac-Toe game on an N×N grid.

This module implements a configurable two-player Tic-Tac-Toe variant with a
Tkinter GUI. Players can choose their names, board size, and the required
length of a winning sequence before starting a game.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox


class TicTacToeApp:
    """Main application class that manages settings and gameplay windows."""

    MIN_BOARD_SIZE = 3
    MAX_BOARD_SIZE = 15
    MIN_WIN_LENGTH = 3
    MAX_WIN_LENGTH = 5

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Tic-Tac-Toe N×N")

        self.settings_frame: tk.Frame | None = None
        self.game_frame: tk.Frame | None = None
        self.board_frame: tk.Frame | None = None

        self.player_names: list[str] = ["", ""]
        self.player_symbols: list[str] = ["X", "O"]
        self.scores: list[int] = [0, 0]
        self.games_played = 0

        self.board_size = self.MIN_BOARD_SIZE
        self.win_length = self.MIN_WIN_LENGTH
        self.board: list[list[str | None]] = []
        self.buttons: list[list[tk.Button]] = []
        self.current_player_index = 0
        self.moves_made = 0

        self.turn_label_var = tk.StringVar()
        self.score_label_var = tk.StringVar()

        self._create_settings_window()

    def run(self) -> None:
        """Start the Tkinter event loop."""
        self.root.mainloop()

    # ------------------------------------------------------------------
    # Settings window
    # ------------------------------------------------------------------
    def _create_settings_window(self) -> None:
        """Render the initial configuration window."""
        if self.game_frame is not None:
            self.game_frame.destroy()
            self.game_frame = None

        self.settings_frame = tk.Frame(self.root, padx=20, pady=20)
        self.settings_frame.pack()

        tk.Label(self.settings_frame, text="Настройки игры", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 10)
        )

        tk.Label(self.settings_frame, text="Имя первого игрока:").grid(row=1, column=0, sticky="w", pady=2)
        player1_entry = tk.Entry(self.settings_frame)
        player1_entry.grid(row=1, column=1, pady=2)

        tk.Label(self.settings_frame, text="Имя второго игрока:").grid(row=2, column=0, sticky="w", pady=2)
        player2_entry = tk.Entry(self.settings_frame)
        player2_entry.grid(row=2, column=1, pady=2)

        tk.Label(self.settings_frame, text="Размер поля (N):").grid(row=3, column=0, sticky="w", pady=2)
        board_size_spin = tk.Spinbox(
            self.settings_frame,
            from_=self.MIN_BOARD_SIZE,
            to=self.MAX_BOARD_SIZE,
            width=5,
        )
        board_size_spin.delete(0, tk.END)
        board_size_spin.insert(0, self.MIN_BOARD_SIZE)
        board_size_spin.grid(row=3, column=1, pady=2)

        tk.Label(self.settings_frame, text="Фишек в ряд для победы (K):").grid(
            row=4, column=0, sticky="w", pady=2
        )
        win_length_spin = tk.Spinbox(
            self.settings_frame,
            from_=self.MIN_WIN_LENGTH,
            to=self.MAX_WIN_LENGTH,
            width=5,
        )
        win_length_spin.delete(0, tk.END)
        win_length_spin.insert(0, self.MIN_WIN_LENGTH)
        win_length_spin.grid(row=4, column=1, pady=2)

        def start_game() -> None:
            player1 = player1_entry.get().strip() or "Игрок 1"
            player2 = player2_entry.get().strip() or "Игрок 2"

            try:
                board_size = int(board_size_spin.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Размер поля должен быть целым числом.")
                return

            try:
                win_length = int(win_length_spin.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Количество фишек в ряд должно быть целым числом.")
                return

            if not (self.MIN_BOARD_SIZE <= board_size <= self.MAX_BOARD_SIZE):
                messagebox.showerror(
                    "Ошибка",
                    f"Размер поля должен быть в диапазоне от {self.MIN_BOARD_SIZE} до {self.MAX_BOARD_SIZE}.",
                )
                return

            if not (self.MIN_WIN_LENGTH <= win_length <= self.MAX_WIN_LENGTH):
                messagebox.showerror(
                    "Ошибка",
                    f"Количество фишек в ряд должно быть в диапазоне от {self.MIN_WIN_LENGTH} до {self.MAX_WIN_LENGTH}.",
                )
                return

            if win_length > board_size:
                messagebox.showerror("Ошибка", "K не может быть больше N.")
                return

            self.player_names = [player1, player2]
            self.board_size = board_size
            self.win_length = win_length
            self.scores = [0, 0]
            self.games_played = 0

            self._start_game_window()

        tk.Button(self.settings_frame, text="Начать игру", command=start_game).grid(
            row=5, column=0, columnspan=2, pady=(10, 0)
        )

    # ------------------------------------------------------------------
    # Game window
    # ------------------------------------------------------------------
    def _start_game_window(self) -> None:
        """Initialize the main gameplay interface."""
        if self.settings_frame is not None:
            self.settings_frame.destroy()
            self.settings_frame = None

        if self.game_frame is not None:
            self.game_frame.destroy()

        self.game_frame = tk.Frame(self.root, padx=20, pady=20)
        self.game_frame.pack()

        header_frame = tk.Frame(self.game_frame)
        header_frame.pack(fill="x")

        self.turn_label_var.set(self._turn_text())
        tk.Label(header_frame, textvariable=self.turn_label_var, font=("Arial", 12)).pack(anchor="w")

        self.score_label_var.set(self._score_text())
        tk.Label(header_frame, textvariable=self.score_label_var, font=("Arial", 12)).pack(anchor="w", pady=(5, 10))

        self.board_frame = tk.Frame(self.game_frame)
        self.board_frame.pack()

        self._initialize_board()

        control_frame = tk.Frame(self.game_frame)
        control_frame.pack(fill="x", pady=(10, 0))

        tk.Button(control_frame, text="Новая партия", command=self._reset_board).pack(side="left")
        tk.Button(control_frame, text="Настройки", command=self._create_settings_window).pack(side="left", padx=(10, 0))
        tk.Button(control_frame, text="Выход", command=self.root.destroy).pack(side="right")

    def _initialize_board(self) -> None:
        """Create the button grid representing the game board."""
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.buttons = []
        self.current_player_index = 0
        self.moves_made = 0
        self.turn_label_var.set(self._turn_text())

        if self.board_frame is None:
            return

        for child in self.board_frame.winfo_children():
            child.destroy()

        for row in range(self.board_size):
            button_row: list[tk.Button] = []
            for col in range(self.board_size):
                button = tk.Button(
                    self.board_frame,
                    text="",
                    width=3,
                    height=1,
                    font=("Arial", 16, "bold"),
                    command=lambda r=row, c=col: self._handle_move(r, c),
                )
                button.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
                button_row.append(button)
            self.buttons.append(button_row)

        for i in range(self.board_size):
            self.board_frame.grid_rowconfigure(i, weight=1)
            self.board_frame.grid_columnconfigure(i, weight=1)

    # ------------------------------------------------------------------
    # Gameplay helpers
    # ------------------------------------------------------------------
    def _handle_move(self, row: int, col: int) -> None:
        """Process a player's attempt to make a move."""
        if self.board[row][col] is not None:
            messagebox.showerror("Некорректный ход", "Эта клетка уже занята.")
            return

        symbol = self.player_symbols[self.current_player_index]
        self.board[row][col] = symbol
        self.moves_made += 1

        button = self.buttons[row][col]
        button.config(text=symbol, state=tk.DISABLED)

        if self._check_for_win(row, col, symbol):
            self._handle_win()
            return

        if self.moves_made == self.board_size * self.board_size:
            self._handle_draw()
            return

        self._switch_player()

    def _check_for_win(self, row: int, col: int, symbol: str) -> bool:
        """Check all directions for a winning sequence."""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in directions:
            if self._count_in_direction(row, col, dr, dc, symbol) + self._count_in_direction(row, col, -dr, -dc, symbol) - 1 >= self.win_length:
                return True
        return False

    def _count_in_direction(self, row: int, col: int, dr: int, dc: int, symbol: str) -> int:
        """Count consecutive symbols in a given direction starting from (row, col)."""
        count = 0
        r, c = row, col
        while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == symbol:
            count += 1
            r += dr
            c += dc
        return count

    def _handle_win(self) -> None:
        """Handle game completion when a player wins."""
        winner = self.player_names[self.current_player_index]
        messagebox.showinfo("Победа", f"Победил игрок: {winner}!")
        self.scores[self.current_player_index] += 1
        self.games_played += 1
        self.score_label_var.set(self._score_text())
        self._disable_board()

    def _handle_draw(self) -> None:
        """Handle a drawn game."""
        messagebox.showinfo("Ничья", "Ничья! Все клетки заполнены.")
        self.games_played += 1
        self.score_label_var.set(self._score_text())
        self._disable_board()

    def _disable_board(self) -> None:
        """Disable all board buttons until a new game starts."""
        for row_buttons in self.buttons:
            for button in row_buttons:
                button.config(state=tk.DISABLED)

    def _switch_player(self) -> None:
        """Switch to the next player's turn."""
        self.current_player_index = 1 - self.current_player_index
        self.turn_label_var.set(self._turn_text())

    def _reset_board(self) -> None:
        """Start a new game round with the same settings."""
        self._initialize_board()
        for row_buttons in self.buttons:
            for button in row_buttons:
                button.config(text="", state=tk.NORMAL)

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------
    def _turn_text(self) -> str:
        current_player = self.player_names[self.current_player_index]
        symbol = self.player_symbols[self.current_player_index]
        return f"Ходит: {current_player} ({symbol})"

    def _score_text(self) -> str:
        player1, player2 = self.player_names
        score1, score2 = self.scores
        return f"Счёт — {player1}: {score1} | {player2}: {score2} | Партии: {self.games_played}"


def main() -> None:
    app = TicTacToeApp()
    app.run()


if __name__ == "__main__":
    main()
