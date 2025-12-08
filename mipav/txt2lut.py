#!/usr/bin/env python3
"""
Convert MIPAV-style colormap .txt files into NiiVue .json colormaps.

Usage:
    python txt2json.py <src_folder> <dst_folder> [precision]

- <src_folder>: folder containing MIPAV txt colormaps (256 lines of "R G B")
- <dst_folder>: folder to write NiiVue JSON colormaps
- precision   : optional max per-channel error allowed (default=2)

Each MIPAV txt file:
    Line i contains:  R G B   (0..255)
Representing the i-th color in a 256-entry palette.

NiiVue JSON format:
    {"R": [...], "G": [...], "B": [...], "A": [...], "I": [...]}

Alpha rule:
    alpha = round(index / 2)

Precision rule:
    Colors between nodes must be reconstructible with <= precision
    error in each channel 0..255.

This script also normalizes colormap names by replacing spaces with underscores.
"""

import os
import sys
import json
import numpy as np

# ---------------------------------------------------------------------
# Utility: read MIPAV txt file (256 lines, each "R G B")
# ---------------------------------------------------------------------
def read_mipav_txt(path: str) -> np.ndarray:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.replace(",", " ").split()
            if len(parts) < 3:
                raise ValueError(f"Invalid line in {path}: {line}")
            r, g, b = map(int, parts[:3])
            rows.append((r, g, b))

    if len(rows) != 256:
        raise ValueError(f"{path}: Expected 256 rows, found {len(rows)}")

    return np.array(rows, dtype=int)

# ---------------------------------------------------------------------
# Node-error calculation (same idea as your previous README)
# ---------------------------------------------------------------------
def max_error_in_interval(cols, i0, i1):
    if i1 <= i0 + 1:
        return 0, -1
    c0 = cols[i0].astype(float)
    c1 = cols[i1].astype(float)
    best_err = -1
    best_idx = -1
    denom = i1 - i0
    for j in range(i0 + 1, i1):
        t = (j - i0) / denom
        interp = c0 + t * (c1 - c0)
        interp_rounded = np.round(interp).astype(int)
        actual = cols[j]
        err = int(np.max(np.abs(interp_rounded - actual)))
        if err > best_err:
            best_err = err
            best_idx = j
    return best_err, best_idx

def reduce_nodes(cols, tol=2):
    n = cols.shape[0]
    kept = [0, n - 1]
    while True:
        global_best_err = -1
        global_best_idx = -1
        for a, b in zip(kept[:-1], kept[1:]):
            err, idx = max_error_in_interval(cols, a, b)
            if err > global_best_err:
                global_best_err = err
                global_best_idx = idx
        if global_best_err <= tol:
            break
        kept.append(global_best_idx)
        kept.sort()
    return kept

# ---------------------------------------------------------------------
# Write NiiVue JSON
# ---------------------------------------------------------------------
def write_niivue_json(path, kept, cols):
    R, G, B, A, I = [], [], [], [], []
    for idx in kept:
        r, g, b = map(int, cols[idx])
        alpha = int(round(idx / 2.0))  # same rule as README
        R.append(r)
        G.append(g)
        B.append(b)
        A.append(alpha)
        I.append(idx)

    out = {"R": R, "G": G, "B": B, "A": A, "I": I}

    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))
        f.write("\n")

# ---------------------------------------------------------------------
# Main conversion routine
# ---------------------------------------------------------------------
def convert_folder(src, dst, tol):
    os.makedirs(dst, exist_ok=True)
    count = 0

    for fname in os.listdir(src):
        if not fname.lower().endswith(".txt"):
            continue

        in_path = os.path.join(src, fname)
        name = os.path.splitext(fname)[0].replace(" ", "_")
        out_path = os.path.join(dst, name + ".json")

        try:
            cols = read_mipav_txt(in_path)
        except Exception as e:
            print(f"Skipping {fname}: {e}")
            continue

        kept = reduce_nodes(cols, tol=tol)
        write_niivue_json(out_path, kept, cols)

        print(f"Wrote {out_path}   (nodes={len(kept)})")
        count += 1

    print(f"\nConverted {count} colormap(s).")

# ---------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------
def main():
    if len(sys.argv) < 3:
        print("Usage: python txt2json.py <src_folder> <dst_folder> [precision]")
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2]
    tol = int(sys.argv[3]) if len(sys.argv) > 3 else 2

    convert_folder(src, dst, tol)

if __name__ == "__main__":
    main()
