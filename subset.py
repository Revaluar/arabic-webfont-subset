#!/usr/bin/env python3
"""Subset web fonts and prove, with HarfBuzz, that your text still renders the same.

pyftsubset's default layout features keep everything a browser turns on by itself
(Arabic joining, ligatures, kerning, marks) and drop what it never does unless the CSS
asks: stylistic sets, swashes, salt, dlig, case, aalt, plus the glyphs only they reach.
On a large Arabic family that is often 15-25% of the file, with every codepoint kept.

The check: every sample string is shaped through the original and the subset font, and
the glyph names, advances and offsets must match exactly. If anything differs, the
original file is left alone and the run exits 1.

    python subset.py --strings-from 'src/**/*.jsx' 'fonts/*.woff2'
    python subset.py --text-file copy.txt --features ss01 --out-dir dist/ 'fonts/*.woff2'
"""
import argparse, glob, os, re, shutil, sys, tempfile

import uharfbuzz as hb
from fontTools import subset
from fontTools.ttLib import TTFont

BASE_TEXT = "0123456789 ٠١٢٣٤٥٦٧٨٩ ?!.,;:()[]{}«»“”‘’…→·©×- ؟،؛ ‎‏‌‍"
LITERAL = re.compile(r'"((?:[^"\\]|\\.)*)"|\'((?:[^\'\\]|\\.)*)\'|`([^`]*)`')


def collect(args):
    texts = {BASE_TEXT}
    for pattern in args.strings_from:
        for path in glob.glob(pattern, recursive=True):
            src = open(path, encoding="utf8").read()
            texts |= {s for groups in LITERAL.findall(src) for s in groups if s.strip()}
    for pattern in args.text_file:
        for path in glob.glob(pattern, recursive=True):
            texts |= {line for line in open(path, encoding="utf8").read().splitlines() if line.strip()}
    return sorted(texts)


def shaped(path, texts, features):
    face = hb.Face(hb.Blob.from_file_path(path))
    font = hb.Font(face)
    out = []
    for text in texts:
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font, buf, features)
        out.append([(font.glyph_to_string(i.codepoint), p.x_advance, p.x_offset, p.y_offset)
                    for i, p in zip(buf.glyph_infos, buf.glyph_positions)])
    return out


def as_sfnt(path, tmp):
    """HarfBuzz reads TTF/OTF; decompress WOFF/WOFF2 to a temp file first."""
    font = TTFont(path)
    if not font.flavor:
        return path
    font.flavor = None
    out = os.path.join(tmp, os.path.basename(path) + ".sfnt")
    font.save(out)
    return out


def subset_one(src, dst, keep_features):
    opts = subset.Options()
    opts.flavor = TTFont(src).flavor  # woff2 stays woff2, ttf stays ttf
    opts.name_IDs = ["*"]
    opts.name_languages = ["*"]
    opts.notdef_outline = True
    opts.layout_features += keep_features
    font = subset.load_font(src, opts)
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=font.getBestCmap().keys())  # keep every codepoint
    sub.subset(font)
    subset.save_font(font, dst, opts)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("fonts", nargs="+", help="font files or globs (.woff2, .woff, .ttf, .otf)")
    ap.add_argument("--strings-from", action="append", default=[], metavar="GLOB",
                    help="source files whose quoted string literals are the sample text "
                         "(JS, JSX, TS, JSON, Python); repeat the flag for more globs")
    ap.add_argument("--text-file", action="append", default=[], metavar="GLOB",
                    help="plain text files, every non-empty line is a sample; repeatable")
    ap.add_argument("--features", action="append", default=[], metavar="TAG",
                    help="an OpenType feature your CSS turns on (font-feature-settings), kept AND checked; repeatable")
    ap.add_argument("--out-dir", help="write subsets here instead of replacing the originals")
    ap.add_argument("--dry-run", action="store_true", help="check and report sizes, write nothing")
    args = ap.parse_args()

    texts = collect(args)
    features = {tag: True for tag in args.features}
    paths = sorted({p for pattern in args.fonts for p in glob.glob(pattern, recursive=True)})
    if not paths:
        sys.exit("no font files matched")
    if args.out_dir:
        os.makedirs(args.out_dir, exist_ok=True)

    failed = False
    with tempfile.TemporaryDirectory() as tmp:
        for src in paths:
            dst = os.path.join(tmp, os.path.basename(src))
            subset_one(src, dst, args.features)
            if shaped(as_sfnt(src, tmp), texts, features) != shaped(as_sfnt(dst, tmp), texts, features):
                print(f"KEPT  {src}: shaping changed, original left alone")
                failed = True
                continue
            before, after = os.path.getsize(src), os.path.getsize(dst)
            print(f"OK    {src}: {before} -> {after} bytes ({100 * (before - after) // before}% smaller, "
                  f"{len(texts)} strings identical)")
            if args.dry_run or after >= before:
                continue
            shutil.copyfile(dst, os.path.join(args.out_dir, os.path.basename(src)) if args.out_dir else src)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
