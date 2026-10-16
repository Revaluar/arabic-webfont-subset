# Contributing

Thanks for taking an interest. Bug reports, fixes and small improvements are welcome.

- **Bugs:** open an issue with the command you ran, the output, and if you can, a
  font whose licence allows you to share it (or the shaping difference you saw).
  Never attach a font you are not allowed to redistribute.
- **Changes:** keep them small and focused, and keep the single-file design:
  `subset.py` should stay readable in one sitting.
- **The check is the point.** Any change must keep the guarantee that a font is
  replaced only when every sample string shapes identically, and must keep the exit
  code `1` when it is not. Before opening a pull request, run the tool on at least one
  font with `--dry-run` and include the output.
- **Dependencies:** please do not add new ones; fontTools, uharfbuzz and brotli cover
  the job.

Security problems: see [SECURITY.md](SECURITY.md), not the issue tracker.

By contributing you agree that your contribution is licensed under the MIT licence
in [LICENSE](LICENSE).
