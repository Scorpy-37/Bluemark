#!/usr/bin/env python3
"""
Plot 2‑D axis‑aligned boxes given centre + half‑extent.

Input format:
    boxes = [
        (px1, py1, sx1, sy1),
        (px2, py2, sx2, sy2),
        ...
    ]

Author: ChatGPT (OpenAI)
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

def plot_boxes(
    boxes,
    ax=None,
    facecolor="none",
    edgecolor="tab:blue",
    linewidth=1.5,
    alpha=0.7,
    label_fmt="{i}",
    show_axes=True,
):
    """
    Draws the supplied list of boxes on a Matplotlib Axes.

    Parameters
    ----------
    boxes : iterable of tuples (px, py, sx, sy)
        List/array of box specifications.
    ax : matplotlib.axes.Axes or None
        If None, a new figure & axes are created.
    facecolor : str or tuple
        Colour inside the rectangle.  Default is transparent.
    edgecolor : str or tuple
        Colour of the rectangle border.
    linewidth : float
        Width of the rectangle border line.
    alpha : float
        Transparency (0 = fully transparent, 1 = opaque).
    label_fmt : str
        Format string for optional per‑box labels. Use `{i}` for index,
        `{px}`, `{py}`, `{sx}`, `{sy}` to insert values.
    show_axes : bool
        Whether to display the x/y axes (default True).

    Returns
    -------
    ax : matplotlib.axes.Axes
        The Axes object containing the plot.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))

    # Ensure we have an array for vectorised operations
    boxes_arr = np.asarray(boxes)
    if boxes_arr.ndim != 2 or boxes_arr.shape[1] != 4:
        raise ValueError("boxes must be a sequence of (px, py, sx, sy) tuples")

    px, py, sx, sy = boxes_arr.T

    # Bottom‑left corner coordinates
    blx = px - sx
    bly = py - sy
    widths = 2 * sx
    heights = 2 * sy

    for i, (x, y, w, h) in enumerate(zip(blx, bly, widths, heights)):
        rect = Rectangle(
            (x, y),
            w,
            h,
            linewidth=linewidth,
            edgecolor=edgecolor,
            facecolor=facecolor,
            alpha=alpha,
        )
        ax.add_patch(rect)

        # Optional label
        if "{i}" in label_fmt or any(k in label_fmt for k in ("px", "py", "sx", "sy")):
            lbl = label_fmt.format(
                i=i, px=px[i], py=py[i], sx=sx[i], sy=sy[i]
            )
            ax.text(x + w / 2, y + h / 2, lbl,
                    ha="center", va="center",
                    fontsize=9, color=edgecolor)

    # Auto‑scale to fit all boxes nicely
    ax.autoscale_view()
    if show_axes:
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_aspect("equal")

    return ax

# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    boxes = eval(open("data/2d_boxes.txt").read())

    ax = plot_boxes(
        boxes,
        facecolor="lightgreen",
        edgecolor="darkgreen",
        linewidth=2.0,
        alpha=0.4,
        label_fmt="Box {i}",
    )
    plt.title("2D Box Layout")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.show()