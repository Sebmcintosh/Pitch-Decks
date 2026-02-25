#!/usr/bin/env python3
"""
Nineteen58 Pitch Deck Generator
================================
Creates a client pitch page from a template + config file.

Usage:
    python3 generate.py <client-slug>

Example:
    python3 generate.py old-mutual
    python3 generate.py discovery-health

Output:
    clients/<slug>/index.html   (the pitch page)
    clients/<slug>/audio/       (copied from configs/<slug>/audio/)

GitHub Pages URL after pushing:
    https://sebmcintosh.github.io/Pitch-Decks/clients/<slug>/
"""

import json
import re
import os
import sys
import shutil


def flatten(d, prefix=""):
    """Flatten a nested dict to dot-notation keys.
    e.g. {"brand": {"primary": "#fff"}} → {"brand.primary": "#fff"}
    """
    result = {}
    for key, value in d.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            result.update(flatten(value, full_key))
        else:
            result[full_key] = str(value)
    return result


def generate(slug):
    config_path  = f"configs/{slug}.json"
    template_path = "template/TEMPLATE.html"
    out_dir      = f"clients/{slug}"
    out_path     = f"{out_dir}/index.html"
    audio_src    = f"configs/{slug}/audio"
    audio_dst    = f"{out_dir}/audio"

    # ── Validate inputs ──────────────────────────────
    if not os.path.exists(config_path):
        print(f"\n  Error: Config not found → {config_path}")
        print(f"  Create it first (copy configs/old-mutual.json as a starting point)\n")
        sys.exit(1)

    if not os.path.exists(template_path):
        print(f"\n  Error: Template not found → {template_path}\n")
        sys.exit(1)

    # ── Load & flatten config ─────────────────────────
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    flat = flatten(config)

    # ── Load template ─────────────────────────────────
    with open(template_path, encoding="utf-8") as f:
        html = f.read()

    # ── Replace placeholders ──────────────────────────
    for key, value in flat.items():
        html = html.replace("{{" + key + "}}", value)

    # ── Warn about any missed placeholders ────────────
    remaining = re.findall(r"\{\{[^}]+\}\}", html)
    if remaining:
        print(f"\n  Warning: {len(set(remaining))} unreplaced placeholder(s):")
        for p in sorted(set(remaining)):
            print(f"    {p}")

    # ── Write output ──────────────────────────────────
    os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    # ── Copy audio files ──────────────────────────────
    if os.path.exists(audio_src):
        if os.path.exists(audio_dst):
            shutil.rmtree(audio_dst)
        shutil.copytree(audio_src, audio_dst)
        mp3s = [f for f in os.listdir(audio_dst) if f.endswith(".mp3")]
        print(f"\n  Audio copied ({len(mp3s)} file(s)) → {audio_dst}/")
    else:
        print(f"\n  Note: No audio folder found at {audio_src}/")
        print(f"  Add audio files there and re-run to include them.")

    # ── Done ──────────────────────────────────────────
    print(f"\n  ✓ Generated → {out_path}")
    print(f"\n  Local preview:")
    print(f"    http://localhost:8080/clients/{slug}/")
    print(f"\n  GitHub Pages (after git push):")
    print(f"    https://sebmcintosh.github.io/Pitch-Decks/clients/{slug}/\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    # Run from the pitch-decks directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    generate(sys.argv[1])
