from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from typing import Any

from .analysis import AnalysisResult


def emit_json(payload: Any, output_path: str | None) -> None:
    serialized = json.dumps(payload, indent=2, sort_keys=True)
    if output_path is None:
        print(serialized)
        return

    Path(output_path).write_text(serialized + "\n", encoding="utf-8")


def emit_png(
    result: AnalysisResult,
    output_path: str | None,
    *,
    title: str,
    metric: str,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(12, 6))
    hours = list(range(24))
    bottoms = [0] * 24

    for member, counts in result.counts_by_member.items():
        ax.bar(hours, counts, width=0.95, bottom=bottoms, label=member)
        bottoms = [bottoms[index] + counts[index] for index in range(24)]

    ax.set_xticks(hours)
    ax.set_xlabel("Hour of day")
    if metric == "lines_changed":
        ax.set_ylabel("Lines changed")
    else:
        ax.set_ylabel("Commit count")
    ax.set_title(title)
    if result.counts_by_member:
        ax.legend(loc="upper right")

    fig.tight_layout()

    if output_path is None:
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png")
        sys.stdout.buffer.write(buffer.getvalue())
    else:
        fig.savefig(output_path, format="png")

    plt.close(fig)
