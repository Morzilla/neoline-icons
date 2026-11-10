# NeoLine

![NeoLine White](preview/neoline-2-white.png)

An outline icon theme for KDE Plasma: 24 px grid, 1.7 px round strokes. Action icons follow the colour scheme;
places and file types come in three variants:

- **NeoLine** – each kind in its own colour
- **NeoLine White** – places and devices in white, file types in colour
- **NeoLine Yellow** – places and devices in yellow, file types in colour

Everything it does not draw is inherited from Breeze Dark.

```
./make-icons.py            # writes the three themes here and installs them in ~/.local/share/icons
./make-icons.py --sheet    # also writes preview.html with every icon
```

Then pick one in System Settings › Colours & Themes › Icons, or `/usr/libexec/plasma-changeicons NeoLine-White`.
To add an icon, put its path data in the `P` dictionary of the script and its name in `PLACES`, `MIMES` or
the actions list, and run the script again. Licence: MIT (see LICENSE). Drawn with Claude (Anthropic).

## Part of the NG desktop

- [Breeze NG](https://github.com/Morzilla/breeze-ng) – widget style and window decoration ([KDE Store](https://store.kde.org/p/2381557/))
- [Dolphin NG](https://github.com/Morzilla/dolphin-ng) – the file manager ([KDE Store](https://store.kde.org/p/2381561/))
- NeoLine on the KDE Store: https://store.kde.org/p/2381562/

The other variants: [colour](preview/neoline-1-colour.png), [yellow](preview/neoline-3-yellow.png).
