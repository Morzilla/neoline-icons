# AGENTS.md

Guidance for coding agents (and people) working on the NeoLine icons.

## What this is

NeoLine is an outline icon theme for KDE Plasma in three variants (NeoLine, NeoLine White, NeoLine Yellow), part of
the NG desktop with [Dolphin NG](https://github.com/Morzilla/dolphin-ng) and Breeze NG. The icons are generated: the
drawings are path data in Python, and the scripts write the SVG files and the `index.theme` of each variant.

The development branch is `master`.

## Layout

```
make-icons.py               the coloured icons: the palette of kinds, the drawings on a 24 grid, the variants
symbolic.py                 the monochrome (symbolic) icons for panels, bars and GTK applications
symbolic-paths.json         their path data
NeoLine/, NeoLine-White/, NeoLine-Yellow/   generated themes (do not edit by hand)
preview/                    pictures for the README
packaging/neoline-icons.spec   the Fedora package (COPR morzilla/desktop-ng)
packaging/aur/              the AUR package (neoline-icons-git), its PKGBUILD
```

## Working on it

- Change a drawing or a colour in `make-icons.py` (or `symbolic.py`), then run `python3 make-icons.py`: it writes
  the three themes again and installs them into `~/.local/share/icons`. Commit the script and the regenerated files
  together.
- Never edit the generated SVG files by hand: the next run overwrites them.
- An icon belongs to a kind (folder, document, image, audio, video, archive, code…) and takes that kind's colour, as
  Dolphin NG's cards do; keep the two in step.
- Dolphin NG's bar and tabs ask for some icons by name (groups, search, tab close, copy to every folder, pin): keep
  those names when redrawing them, and give any new button of Dolphin NG its icon here.
- Check the icons at their real sizes (16, 22, 32, 48) on a dark and a light background.

## Commits and packages

- The subject of a commit says what changed for the user; the body says why.
- `packaging/neoline-icons.spec`: after pushing, set `commit` and `snapdate` and add a changelog line. The AUR
  package builds from git and needs no change for a new commit. Publishing packages is the maintainer's decision: ask
  first.
- Keep secrets and personal details out of the repository.
