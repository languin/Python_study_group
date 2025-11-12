"""Segment intersection analyzer.

This script reads segments from a text file, checks every consecutive pair
for intersections, and updates the file by appending the result ("Пересекается"
/ "Не пересекается") after the coordinates of each processed segment. A plot
visualizing all segments is also generated to satisfy the visualization
requirement.

Usage:
    python main.py path/to/segments.txt

Optional arguments:
    --plot-path PATH  Save the generated plot to PATH instead of the default
                      `<input_stem>_plot.png`.
    --skip-plot       Disable plot generation.

Input format:
    Each line must contain at least four numbers representing the coordinates
    of the segment endpoints: `x1 y1 x2 y2`. Additional tokens on the line are
    ignored. If the file contains an odd number of valid segment lines, the
    last line is ignored during pairwise intersection checks but still appears
    in the output without a result label.

The script is idempotent with respect to the coordinates: it rewrites each
processed line so that only the first four numeric tokens are preserved,
followed by the result label if available.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

try:  # pragma: no cover - optional dependency
    import matplotlib.pyplot as plt  # type: ignore[import]
except ImportError:  # pragma: no cover - optional dependency
    plt = None  # type: ignore[assignment]


@dataclass(frozen=True)
class Segment:
    """Represents a 2D segment defined by two endpoints."""

    start: Tuple[float, float]
    end: Tuple[float, float]

    def midpoint(self) -> Tuple[float, float]:
        """Return the midpoint of the segment."""

        return ((self.start[0] + self.end[0]) / 2, (self.start[1] + self.end[1]) / 2)


@dataclass
class LineEntry:
    """Stores data about a line in the input file."""

    original_text: str
    numbers: Optional[Tuple[float, float, float, float]] = None
    sanitized_text: Optional[str] = None
    output_text: Optional[str] = None
    color: str = "tab:gray"

    def ensure_sanitized(self) -> None:
        if self.numbers is None:
            return
        if self.sanitized_text is None:
            self.sanitized_text = " ".join(format_number(value) for value in self.numbers)


def format_number(value: float) -> str:
    """Format a float using the shortest representation."""

    if value.is_integer():
        return str(int(value))
    return f"{value:g}"


def parse_line(line: str) -> LineEntry:
    """Parse a single line of the input file."""

    tokens = line.strip().split()
    entry = LineEntry(original_text=line.rstrip("\n"))
    if len(tokens) < 4:
        return entry

    numbers: List[float] = []
    for token in tokens[:4]:
        try:
            numbers.append(float(token))
        except ValueError:
            return entry
    entry.numbers = tuple(numbers)  # type: ignore[assignment]
    entry.ensure_sanitized()
    return entry


def segments_intersect(first: Segment, second: Segment) -> bool:
    """Return True if the two segments intersect."""

    def orientation(p: Tuple[float, float], q: Tuple[float, float], r: Tuple[float, float]) -> float:
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    def on_segment(p: Tuple[float, float], q: Tuple[float, float], r: Tuple[float, float]) -> bool:
        return min(p[0], r[0]) - 1e-9 <= q[0] <= max(p[0], r[0]) + 1e-9 and min(p[1], r[1]) - 1e-9 <= q[1] <= max(p[1], r[1]) + 1e-9

    p1, q1 = first.start, first.end
    p2, q2 = second.start, second.end

    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    if (o1 > 0 and o2 < 0 or o1 < 0 and o2 > 0) and (o3 > 0 and o4 < 0 or o3 < 0 and o4 > 0):
        return True

    if abs(o1) < 1e-9 and on_segment(p1, p2, q1):
        return True
    if abs(o2) < 1e-9 and on_segment(p1, q2, q1):
        return True
    if abs(o3) < 1e-9 and on_segment(p2, p1, q2):
        return True
    if abs(o4) < 1e-9 and on_segment(p2, q1, q2):
        return True

    return False


def load_entries(file_path: Path) -> List[LineEntry]:
    """Load all lines from the input file and parse them."""

    lines = file_path.read_text(encoding="utf-8").splitlines()
    return [parse_line(line) for line in lines]


def analyze_pairs(entries: List[LineEntry]) -> None:
    """Check intersections for every consecutive pair of lines."""

    for index in range(0, len(entries) - 1, 2):
        first, second = entries[index], entries[index + 1]
        if first.numbers is None or second.numbers is None:
            continue

        segment_a = Segment(start=(first.numbers[0], first.numbers[1]), end=(first.numbers[2], first.numbers[3]))
        segment_b = Segment(start=(second.numbers[0], second.numbers[1]), end=(second.numbers[2], second.numbers[3]))
        intersects = segments_intersect(segment_a, segment_b)
        result_text = "Пересекается" if intersects else "Не пересекается"

        first.ensure_sanitized()
        second.ensure_sanitized()

        first.output_text = f"{first.sanitized_text} {result_text}" if first.sanitized_text else first.original_text
        second.output_text = f"{second.sanitized_text} {result_text}" if second.sanitized_text else second.original_text
        pair_color = "tab:red" if intersects else "tab:green"
        first.color = pair_color
        second.color = pair_color

    for entry in entries:
        if entry.output_text is None:
            if entry.sanitized_text is not None:
                entry.output_text = entry.sanitized_text
            else:
                entry.output_text = entry.original_text


def save_entries(file_path: Path, entries: Sequence[LineEntry]) -> None:
    """Overwrite the input file with updated lines."""

    content = "\n".join(entry.output_text for entry in entries)
    file_path.write_text(content + "\n", encoding="utf-8")


def create_plot(entries: Sequence[LineEntry], output_path: Path) -> bool:
    """Generate a plot of the segments and save it.

    Returns True if the plot was created, otherwise False.
    """

    if plt is None:
        print("Matplotlib не установлен: визуализация пропущена.")
        return False

    segments_to_plot = [entry for entry in entries if entry.numbers is not None]
    if not segments_to_plot:
        print("Недостаточно данных для визуализации отрезков.")
        return False

    fig, ax = plt.subplots(figsize=(8, 6))
    for index, entry in enumerate(segments_to_plot, start=1):
        x1, y1, x2, y2 = entry.numbers  # type: ignore[misc]
        segment = Segment(start=(x1, y1), end=(x2, y2))
        color = entry.color if entry.color else "tab:blue"
        ax.plot([segment.start[0], segment.end[0]], [segment.start[1], segment.end[1]], marker="o", color=color, linewidth=2)
        midpoint = segment.midpoint()
        ax.text(midpoint[0], midpoint[1], str(index), fontsize=9, ha="center", va="center", color="black")

    ax.set_title("Визуализация отрезков")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_aspect("equal", adjustable="datalim")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return True


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Анализ пересечения отрезков")
    parser.add_argument("input_path", type=Path, help="Путь к файлу с координатами")
    parser.add_argument("--plot-path", type=Path, help="Путь для сохранения визуализации")
    parser.add_argument("--skip-plot", action="store_true", help="Не создавать визуализацию")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    input_path: Path = args.input_path
    if not input_path.exists():
        raise FileNotFoundError(f"Файл {input_path} не найден")

    entries = load_entries(input_path)
    analyze_pairs(entries)
    save_entries(input_path, entries)

    if not args.skip_plot:
        plot_path = args.plot_path or input_path.with_name(f"{input_path.stem}_plot.png")
        if create_plot(entries, plot_path):
            print(f"Визуализация сохранена в {plot_path}")

    pair_count = sum(1 for _ in range(0, len(entries) - 1, 2))
    print(f"Обработано пар отрезков: {pair_count}")


if __name__ == "__main__":
    main()
