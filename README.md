# NeoLine

An outline icon theme for KDE Plasma: 24 px grid, 1.7 px round strokes. Action icons follow the colour scheme;
places and file types come in three variants:

- **NeoLine** – each kind in its own colour
- **NeoLine White** – all white
- **NeoLine Yellow** – all yellow

Everything it does not draw is inherited from Breeze Dark.

```
./make-icons.py            # writes the three themes here and installs them in ~/.local/share/icons
./make-icons.py --sheet    # also writes preview.html with every icon
```

Then pick one in System Settings › Colours & Themes › Icons, or `/usr/libexec/plasma-changeicons NeoLine-White`.
To add an icon, put its path data in the `P` dictionary of the script and its name in `PLACES`, `MIMES` or
the actions list, and run the script again. Licence: CC0.
