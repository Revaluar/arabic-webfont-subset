# arabic-webfont-subset

Make Arabic (or any) web fonts smaller **without changing a single rendered glyph**, and prove it.

Large Arabic families ship stylistic sets, swashes and alternates that a browser never turns on unless your CSS asks for them. Removing them typically saves 15-25% per file while keeping every codepoint. The risk is that Arabic shaping is fragile: drop the wrong lookup and letters stop joining, marks drift, or a ligature disappears. You rarely notice that by eye.

This tool subsets each font, then shapes every string your site actually renders through **HarfBuzz** (the shaping engine Chrome, Firefox and Android use), once with the original font and once with the subset. Glyph IDs, advances and offsets must match exactly. If anything differs, the original file is kept and the run fails.

## Results

On a large Arabic type family (Sans and Serif Display) used by [revaluar.com](https://revaluar.com), with every string in the site's source as the sample:

| File | Before | After | Saved |
|---|---|---|---|
| Sans Regular (.woff2) | 77,776 B | 62,016 B | 20% |
| Serif Display Medium (.woff2) | 82,552 B | 68,784 B | 16% |

1,792 strings shaped identically for both, in Arabic and Latin. We built this for visitors on slow mobile connections, where every font file is a noticeable wait.

## Install

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

## Use

```bash
# Replace the fonts in place; sample text = every quoted string in your source
.venv/bin/python subset.py --strings-from 'src/**/*.jsx' 'public/fonts/**/*.woff2'

# Plain text sample (one string per line), write to another folder, check only
.venv/bin/python subset.py --text-file copy-ar.txt --out-dir dist/fonts --dry-run 'fonts/*.woff2'

# Your CSS uses font-feature-settings: "ss01"? Keep it, and check with it on
.venv/bin/python subset.py --strings-from 'src/**/*.tsx' --features ss01 'fonts/*.woff2'
```

Input format is kept: `.woff2` stays `.woff2`, `.ttf` stays `.ttf`. Running it on an already-subset file is a no-op. Exit code is `1` if any font was kept because shaping changed, so it works as a CI step.

## What is kept and what is dropped

- **Kept:** every codepoint in the font, and fontTools' default layout features: Arabic joining (`init`, `medi`, `fina`, `isol`), required ligatures (`rlig`), `ccmp`, `liga`, `calt`, `kern`, `mark`, `mkmk`, `locl` and the rest of the features a browser applies on its own. Name tables are kept intact.
- **Dropped:** discretionary features such as `ss01`-`ss20`, `salt`, `swsh`, `dlig`, `case`, `aalt`, and the glyphs that only they reach. Pass `--features` to keep any you use.

## Limits, honestly

- The check is only as good as the sample. Strings built at runtime (user names, CMS content) are not in your source; add representative text with `--text-file`.
- It shapes with default features plus `--features`. Shaping with CSS `font-variant-*` properties that map to other features is not checked unless you list those features.
- Variable fonts are subset fine, but shaping is checked at the default instance only.
- **Check your font licence.** Some licences forbid modification or subsetting, and the SIL OFL treats a subset as a modified version, which matters for fonts with a Reserved Font Name. This tool does not decide that for you.

## Licence

MIT. Built and maintained by [Revaluar](https://revaluar.com), an engineering company in Vancouver, Canada.
