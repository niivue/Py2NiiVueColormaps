#!/usr/bin/env python3
"""
color2json.py

Usage:
    python color2json.py [<cmap_name>] [-o OUTDIR] [-t TOL]

If <cmap_name> is provided, create <cmap_name>.json in NiiVue format.
If no name is provided, convert the default list of colormap names.

This is derived from the original color2clut converter; sampling and node
reduction are unchanged. Alpha is computed the same way as before:
    alpha = round(node_intensity / 2)
Intensity is the original node index (0..255).
"""
import argparse
import os
import json
from cmap import Colormap
import numpy as np
from typing import List, Tuple, Any

def color_like_to_rgb(value: Any) -> Tuple[int, int, int]:
    if isinstance(value, str):
        s = value.lstrip('#')
        if len(s) >= 6:
            r = int(s[0:2], 16)
            g = int(s[2:4], 16)
            b = int(s[4:6], 16)
            return (r, g, b)
        raise ValueError(f"Unrecognized hex string: {value}")

    if hasattr(value, "hex"):
        try:
            hx = value.hex
            if isinstance(hx, str):
                return color_like_to_rgb(hx)
        except Exception:
            pass

    if hasattr(value, "rgba"):
        try:
            rgba = value.rgba
            if rgba is not None:
                arr = np.array(rgba)
                return _numeric_array_to_rgb(arr)
        except Exception:
            pass

    try:
        s = str(value)
        if s.startswith("#") or (len(s) >= 6 and all(c in "0123456789ABCDEFabcdef#" for c in s[:7])):
            return color_like_to_rgb(s)
    except Exception:
        pass

    if isinstance(value, (tuple, list, np.ndarray)):
        arr = np.array(value)
        return _numeric_array_to_rgb(arr)

    raise ValueError(f"Cannot interpret color value: {repr(value)}")


def _numeric_array_to_rgb(arr: np.ndarray) -> Tuple[int, int, int]:
    arr = np.asarray(arr).astype(float).flatten()
    if arr.size >= 3:
        if np.all(arr[:3] <= 1.0 + 1e-8):
            rgb = np.clip(np.round(arr[:3] * 255.0), 0, 255).astype(int)
        else:
            rgb = np.clip(np.round(arr[:3]), 0, 255).astype(int)
        return (int(rgb[0]), int(rgb[1]), int(rgb[2]))
    raise ValueError(f"Numeric color must have length >=3, got {arr}")


def sample_colormap(cmap_obj, n: int = 256) -> np.ndarray:
    cols = []
    for i in range(n):
        t = i / (n - 1)
        val = cmap_obj(t)
        r, g, b = color_like_to_rgb(val)
        cols.append((r, g, b))
    return np.array(cols, dtype=int)


def max_error_in_interval(cols: np.ndarray, i0: int, i1: int) -> Tuple[int,int]:
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
        err = np.max(np.abs(interp_rounded - actual))
        if err > best_err:
            best_err = int(err)
            best_idx = j
    return best_err, best_idx

def reduce_nodes(cols: np.ndarray, tol: int = 1) -> List[int]:
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

def write_niivue_json(filename: str, kept_indices: List[int], cols: np.ndarray, pretty: bool = False):
    """
    Write NiiVue JSON.
    - Compact (default): minimal whitespace, arrays inline, uses separators=(',',':')
    - pretty=True: readable, indented JSON
    """
    R = []
    G = []
    B = []
    A = []
    I = []
    for idx in kept_indices:
        r, g, b = int(cols[idx,0]), int(cols[idx,1]), int(cols[idx,2])
        alpha = int(round(idx / 2.0))
        R.append(r)
        G.append(g)
        B.append(b)
        A.append(alpha)
        I.append(int(idx))
    out = {"R": R, "G": G, "B": B, "A": A, "I": I}
    # compact form: no spaces after separators, arrays remain inline
    if pretty:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, sort_keys=False)
            f.write("\n")
    else:
        # separators=(',',':') removes spaces after commas and colons -> minimal bytes
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(out, f, separators=(',',':'), sort_keys=False)
            f.write("\n")

DEFAULT_CMAP_LIST = [
    "fake_parula", "inferno", "magma", "bordeaux", "amethyst", "gem",
    "panatel", "acton", "bamako", "batlow", "davos", "devon", "glasgow",
    "hawaii", "imola", "lipari", "nuuk", "oslo", "tokyo", "turku",
    "cubehelix", "mako", "rocket"
]

def process_one(name: str, outdir: str, tol: int, pretty: bool):
    outname = os.path.join(outdir, f"{name}.json")
    try:
        cmap = Colormap(name)
    except Exception as e:
        print(f"Skipping '{name}': cannot construct Colormap('{name}'): {e}")
        return False
    cols = sample_colormap(cmap, n=256)
    kept = reduce_nodes(cols, tol=tol)
    write_niivue_json(outname, kept, cols, pretty=pretty)
    print(f"Wrote {outname}  (sampled=256 -> nodes={len(kept)})")
    return True

def main():
    p = argparse.ArgumentParser(description="Create NiiVue JSON colormap from cmap.Colormap (single or batch)")
    p.add_argument("name", nargs="?", default=None, help="optional colormap name (e.g. davos). If omitted, process default list.")
    p.add_argument("-o", "--outdir", default=".", help="output directory for .json files (default: current dir)")
    p.add_argument("-t", "--tol", type=int, default=2, help="max allowed per-channel interpolation error (default: 2)")
    p.add_argument("--pretty", action="store_true", help="write human-readable pretty JSON (default: compact single-line arrays)")
    args = p.parse_args()

    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    if args.name:
        ok = process_one(args.name, outdir, args.tol, args.pretty)
        if not ok:
            raise SystemExit(2)
    else:
        print("No name provided — processing default colormap list.")
        for nm in DEFAULT_CMAP_LIST:
            process_one(nm, outdir, args.tol, args.pretty)

if __name__ == "__main__":
    main()
