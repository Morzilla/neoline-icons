#!/usr/bin/env python3
"""NeoLine: an outline icon theme in the style of the Dolphin NG mockups.

Every icon is drawn on a 24 x 24 grid with a 1.7 px round stroke. Action icons are monochrome and follow the
colour scheme (KIconLoader recolours the ColorScheme-Text class); places and file types are drawn in the
colour of their kind with a faint fill of the same colour. Names follow the freedesktop / Breeze names, so the
theme can inherit Breeze for everything it does not draw.

    ./make-icons.py            writes the theme into ./NeoLine and installs it in ~/.local/share/icons/NeoLine
    ./make-icons.py --sheet    also writes preview.html with every icon
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "NeoLine")
INSTALL = os.path.expanduser("~/.local/share/icons/NeoLine")

# ---- the palette of kinds (as in Dolphin NG's cards)
C = {
    "dir": "#4f93d9", "img": "#5b7bb0", "vid": "#a66b9c", "aud": "#c98a4b", "arc": "#c0894b", "doc": "#8f99a6",
    "sheet": "#5e9c6a", "pres": "#d08457", "code": "#c9a24d", "pdf": "#d06060", "pkg": "#8a6fc9", "exe": "#6aa0b8",
    "text": "#9aa3ad", "gif": "#c86f6f", "web": "#4fa3c9", "font": "#b48ead", "disk": "#8fa0b3", "trash": "#8f99a6", "net": "#5ba3a3",
}

# ---- the drawings: SVG path data on the 24 grid (stroke only; "fill" entries are drawn filled)
P = {
    # places
    "folder": ["M3 6.5A1.5 1.5 0 0 1 4.5 5h4l2 2h9A1.5 1.5 0 0 1 21 8.5v9a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17.5z"],
    "folder-open": ["M3 6.5A1.5 1.5 0 0 1 4.5 5h4l2 2h8.5A1.5 1.5 0 0 1 19.5 8.5V10", "M3 17.5V10.5h17.2a1 1 0 0 1 .95 1.3l-1.9 6A1.5 1.5 0 0 1 17.8 19H4.5A1.5 1.5 0 0 1 3 17.5z"],
    "home": ["M3.5 10.5 12 3.5l8.5 7", "M5.5 9v10.5h13V9", "M10 19.5v-6h4v6"],
    "documents": ["M6.5 3.5h7l4 4v13h-11z", "M13.5 3.5v4h4", "M9 12h6M9 15.5h6"],
    "download": ["M12 3.5v11", "m8 10.5 4 4 4-4", "M4 15.5v3A1.5 1.5 0 0 0 5.5 20h13a1.5 1.5 0 0 0 1.5-1.5v-3"],
    "pictures": ["M3.5 4.5h17v15h-17z", "M9 9.5m-1.6 0a1.6 1.6 0 1 0 3.2 0a1.6 1.6 0 1 0-3.2 0", "m4 17 5-5 4 4 3-3 4 4"],
    "music": ["M9 18.5V6l11-2.5v12", "M9 18.5a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0z", "M20 15.5a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0z"],
    "videos": ["M3.5 5.5h13v13h-13z", "m16.5 10 4-2.5v9l-4-2.5z"],
    "desktop": ["M3.5 4.5h17v11h-17z", "M9 20h6M12 15.5V20"],
    "templates": ["M6.5 3.5h7l4 4v13h-11z", "M13.5 3.5v4h4", "M9 12h3M9 15.5h6"],
    "public": ["M12 3.5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17z", "M3.5 12h17M12 3.5c3 3 3 14 0 17M12 3.5c-3 3-3 14 0 17"],
    "trash": ["M4 6.5h16", "M9.5 6.5V4.5h5v2", "M6 6.5l1 13h10l1-13", "M10 10v6M14 10v6"],
    "trash-full": ["M4 6.5h16", "M9.5 6.5V4.5h5v2", "M6 6.5l1 13h10l1-13", "M9 10.5h6M9 13.5h6M9.5 16.5h5"],
    "network": ["M4.5 15.5h15v5h-15z", "M9.5 3.5h5v5h-5z", "M12 8.5v4M7 15.5v-3h10v3"],
    "server": ["M4 4.5h16v6H4zM4 13.5h16v6H4z", "M7.5 7.5h.01M7.5 16.5h.01"],
    "remote": ["M3 6.5A1.5 1.5 0 0 1 4.5 5h4l2 2h9A1.5 1.5 0 0 1 21 8.5v9a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17.5z", "M9 14.5a4.5 4.5 0 0 1 6 0M7 12.5a7 7 0 0 1 10 0M12 16.5h.01"],
    "recent": ["M12 3.5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17z", "M12 7.5V12l3 2"],
    "root": ["M12 3.5 4 8v8l8 4.5 8-4.5V8z", "M4 8l8 4.5L20 8M12 12.5v8"],
    "cloud": ["M7.5 18.5h10a4 4 0 0 0 .5-8 6 6 0 0 0-11.5 1.5A3.3 3.3 0 0 0 7.5 18.5z"],
    "git": ["M12 4v16", "M12 8a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM12 20a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM18 11a2 2 0 1 0 0-4 2 2 0 0 0 0 4z", "M18 11c0 3-3 3-6 5"],
    "drive": ["M3.5 11.5h17v8h-17z", "M5 11.5l2.5-7h9l2.5 7", "M16.5 15.5h.01M7 15.5h6"],
    "removable": ["M7.5 3.5h9v6h-9z", "M5.5 9.5h13v11h-13z", "M9.5 3.5v3M14.5 3.5v3"],
    "optical": ["M12 3.5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17z", "M12 9.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5z", "M5.5 10a7 7 0 0 1 3-4"],
    "phone": ["M7.5 3.5h9a1.5 1.5 0 0 1 1.5 1.5v14a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 6 19V5a1.5 1.5 0 0 1 1.5-1.5z", "M11 17.5h2"],
    # file types
    "file": ["M6.5 3.5h7l4 4v13h-11z", "M13.5 3.5v4h4"],
    "file-text": ["M6.5 3.5h7l4 4v13h-11z", "M13.5 3.5v4h4", "M9 12h6M9 15.5h6"],
    "file-image": ["M3.5 4.5h17v15h-17z", "M9 9.5m-1.6 0a1.6 1.6 0 1 0 3.2 0a1.6 1.6 0 1 0-3.2 0", "m4 17 5-5 4 4 3-3 4 4"],
    "file-gif": ["M3.5 4.5h17v15h-17z", "M9.5 10.5H8a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1h1.5v-1.5H9M12 10.5v3M15 13.5v-3h2.5M15 12h2"],
    "file-video": ["M3.5 5.5h13v13h-13z", "m16.5 10 4-2.5v9l-4-2.5z"],
    "file-audio": ["M9 18.5V6l11-2.5v12", "M9 18.5a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0z", "M20 15.5a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0z"],
    "file-archive": ["M4.5 3.5h15v17h-15z", "M10 3.5v3h2v2h-2v2h2v2h-2v2h2", "M9.5 15.5h3v3h-3z"],
    "file-pdf": ["M6.5 3.5h7l4 4v13h-11z", "M13.5 3.5v4h4", "M8.5 17v-5h1.5a1.5 1.5 0 0 1 0 3H8.5M12.5 17v-5h1a2.5 2.5 0 0 1 0 5h-1M16.5 17v-5h2M16.5 14.5h1.5"],
    "file-sheet": ["M3.5 4.5h17v15h-17z", "M3.5 10h17M3.5 15h17M9.5 4.5v15"],
    "file-pres": ["M3.5 4.5h17v11h-17z", "M9 20h6M12 15.5V20", "M7.5 12l3-3 2.5 2 3.5-3.5"],
    "file-code": ["M9 4.5c-2 0-2.5 1-2.5 2.5v3C6.5 11.5 5 12 4 12c1 0 2.5.5 2.5 2v3C6.5 18.5 7 19.5 9 19.5", "M15 4.5c2 0 2.5 1 2.5 2.5v3c0 1.5 1.5 2 2.5 2-1 0-2.5.5-2.5 2v3c0 1.5-.5 2.5-2.5 2.5"],
    "file-script": ["M4.5 4.5h15v15h-15z", "m8 9 3 3-3 3M13 15h4"],
    "file-source": ["m8.5 8-4 4 4 4M15.5 8l4 4-4 4", "m13.5 5-3 14"],
    "file-web": ["M12 3.5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17z", "M3.5 12h17M12 3.5c3 3 3 14 0 17M12 3.5c-3 3-3 14 0 17"],
    "file-package": ["M12 3.5 4 8v8l8 4.5 8-4.5V8z", "M4 8l8 4.5L20 8M12 12.5v8M8 6l8 4.5"],
    "file-exe": ["M4.5 4.5h15v15h-15z", "M4.5 8.5h15", "M7 6.5h.01M9.5 6.5h.01", "m9 12 2.5 2.5L9 17"],
    "file-iso": ["M12 3.5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17z", "M12 9.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5z"],
    "file-font": ["M5 19.5 11 5h2l6 14.5", "M8 13h8", "M4 19.5h3M17 19.5h3"],
    "file-markdown": ["M3.5 5.5h17v13h-17z", "M6.5 15.5v-7l2.5 3 2.5-3v7", "M16 8.5v7M13.5 13l2.5 2.5 2.5-2.5"],
    "file-unknown": ["M6.5 3.5h7l4 4v13h-11z", "M13.5 3.5v4h4", "M10.3 11a1.8 1.8 0 1 1 2.6 1.6c-.6.3-.9.7-.9 1.4M12 16.5h.01"],
    "file-log": ["M6.5 3.5h7l4 4v13h-11z", "M13.5 3.5v4h4", "M9 11h2M9 13.5h4M9 16h6"],
    "file-config": ["M6.5 3.5h7l4 4v13h-11z", "M13.5 3.5v4h4", "M12 11.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5z", "M12 9.5v2M12 16.5v2M9.5 14h2M12.5 14h2"],
    "file-desktop": ["M4.5 4.5h15v15h-15z", "M8 8.5h3v3H8zM13 8.5h3v3h-3zM8 13.5h3v3H8z"],
    "file-vector": ["M4.5 4.5h3v3h-3zM16.5 16.5h3v3h-3z", "M7.5 6C14 6 18 10 18 16.5", "M6 7.5c0 6.5 4 10.5 10.5 10.5"],
    "file-ebook": ["M4.5 4.5h13a2 2 0 0 1 2 2v13h-13a2 2 0 0 1-2-2z", "M6.5 16.5h13", "M8 8.5h7M8 11.5h5"],
    "file-disk-image": ["M12 3.5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17z", "M12 9.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5z", "M5.5 10a7 7 0 0 1 3-4"],
    "file-torrent": ["M12 3.5v9", "m8.5 9 3.5 3.5L15.5 9", "M4.5 15.5a7.5 7.5 0 0 0 15 0"],
    "file-mail": ["M3.5 5.5h17v13h-17z", "m3.5 7 8.5 6 8.5-6"],
    "file-calendar": ["M4.5 5.5h15v14h-15z", "M4.5 10h15M8.5 3.5v4M15.5 3.5v4"],
    "file-sub": ["M4.5 5.5h15v13h-15z", "M7.5 12h9M7.5 15h5"],
    # actions (monochrome)
    "view-grid": ["M4.5 4.5h6v6h-6zM13.5 4.5h6v6h-6zM4.5 13.5h6v6h-6zM13.5 13.5h6v6h-6z"],
    "view-list-icons": ["M4.5 4.5h4v4h-4zM10 4.5h4v4h-4zM15.5 4.5h4v4h-4zM4.5 10h4v4h-4zM10 10h4v4h-4zM15.5 10h4v4h-4zM4.5 15.5h4v4h-4zM10 15.5h4v4h-4zM15.5 15.5h4v4h-4z"],
    "view-list-details": ["M4.5 6.5h2v2h-2zM9.5 7.5h10M4.5 11h2v2h-2zM9.5 12h10M4.5 15.5h2v2h-2zM9.5 16.5h10"],
    "view-list-tree": ["M4.5 5.5h4v4h-4z", "M6.5 9.5v8h3M6.5 13.5h3", "M12 10.5h7.5M12 15.5h7.5M12 6h7.5"],
    "view-list-text": ["M4.5 7h15M4.5 12h15M4.5 17h15"],
    "view-sort-ascending": ["M5.5 19.5V5", "m9 8.5-3.5-3.5L2 8.5", "M11 7h3M11 12h5.5M11 17h8"],
    "view-sort-descending": ["M5.5 4.5V19", "m9 15.5-3.5 3.5L2 15.5", "M11 7h8M11 12h5.5M11 17h3"],
    "view-filter": ["M3.5 5.5h17l-6.5 7.5v5l-4 2v-7z"],
    "view-refresh": ["M4 12a8 8 0 0 1 13.7-5.6L20 8.5", "M20 3.5v5h-5", "M20 12a8 8 0 0 1-13.7 5.6L4 15.5", "M4 20.5v-5h5"],
    "view-preview": ["M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6z", "M12 9.4a2.6 2.6 0 1 0 0 5.2 2.6 2.6 0 0 0 0-5.2z"],
    "view-hidden": ["M3 3l18 18", "M10 10.6a2.6 2.6 0 0 0 3.5 3.5", "M6.5 6.9C4 8.5 2.5 12 2.5 12s3.5 6 9.5 6c1.6 0 3-.4 4.2-1", "M9.5 6.3c.8-.2 1.6-.3 2.5-.3 6 0 9.5 6 9.5 6s-.9 1.6-2.6 3.1"],
    "go-up": ["M12 19.5v-15", "m6 10.5 6-6 6 6"],
    "go-down": ["M12 4.5v15", "m6 13.5 6 6 6-6"],
    "go-previous": ["M19.5 12h-15", "m10.5 6-6 6 6 6"],
    "go-next": ["M4.5 12h15", "m13.5 6 6 6-6 6"],
    "go-home": ["M3.5 10.5 12 3.5l8.5 7", "M5.5 9v10.5h13V9", "M10 19.5v-6h4v6"],
    "go-jump": ["M4.5 17.5c0-5 3-8 8-8h5", "m14 5.5 4 4-4 4"],
    "edit-find": ["M10.5 4a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13z", "m15.5 15.5 5 5"],
    "folder-new": ["M3 6.5A1.5 1.5 0 0 1 4.5 5h4l2 2h9A1.5 1.5 0 0 1 21 8.5v9a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17.5z", "M12 10.5v6M9 13.5h6"],
    "document-new": ["M6.5 3.5h7l4 4v13h-11z", "M13.5 3.5v4h4", "M12 10.5v6M9 13.5h6"],
    "document-open": ["M3 6.5A1.5 1.5 0 0 1 4.5 5h4l2 2h8.5A1.5 1.5 0 0 1 19.5 8.5V10", "M3 17.5V10.5h17.2a1 1 0 0 1 .95 1.3l-1.9 6A1.5 1.5 0 0 1 17.8 19H4.5A1.5 1.5 0 0 1 3 17.5z"],
    "document-save": ["M4.5 4.5h12l3 3v12h-15z", "M8 4.5v5h7v-5M8 19.5v-5h8v5"],
    "document-properties": ["M6.5 3.5h7l4 4v13h-11z", "M13.5 3.5v4h4", "M9 12h6M9 15.5h3"],
    "edit-copy": ["M9.5 9.5h10v10h-10z", "M14.5 9.5v-5h-10v10h5"],
    "edit-cut": ["M6.5 14a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM6.5 5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5z", "M20 4 8.3 15.7M20 20 8.3 8.3"],
    "edit-paste": ["M8.5 5.5h-2a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h11a1 1 0 0 0 1-1v-12a1 1 0 0 0-1-1h-2", "M9 3.5h6v4H9z"],
    "edit-delete": ["M4 6.5h16", "M9.5 6.5V4.5h5v2", "M6 6.5l1 13h10l1-13", "M10 10v6M14 10v6"],
    "edit-rename": ["M4 20h16", "m14.5 4.5 5 5L9 20H4v-5z", "m12 7 5 5"],
    "edit-select-all": ["M4.5 4.5h15v15h-15z", "m8 12 3 3 5-6"],
    "edit-undo": ["M9 14 4 9l5-5", "M4 9h10a6 6 0 0 1 0 12h-4"],
    "edit-redo": ["m15 14 5-5-5-5", "M20 9H10a6 6 0 0 0 0 12h4"],
    "list-add": ["M12 5v14M5 12h14"],
    "list-remove": ["M5 12h14"],
    "dialog-close": ["M6 6l12 12M18 6 6 18"],
    "dialog-ok": ["m4.5 12.5 5 5 10-11"],
    "window-close": ["M6 6l12 12M18 6 6 18"],
    "tab-new": ["M3.5 7.5h8l2 2h7v10h-17z", "M12 11.5v5M9.5 14h5"],
    "view-split-left-right": ["M3.5 4.5h17v15h-17z", "M12 4.5v15"],
    "view-split-top-bottom": ["M3.5 4.5h17v15h-17z", "M3.5 12h17"],
    "application-menu": ["M4.5 7h15M4.5 12h15M4.5 17h15"],
    "configure": ["M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7z", "M12 3.5v2.5M12 18v2.5M3.5 12H6M18 12h2.5M6 6l1.8 1.8M16.2 16.2 18 18M6 18l1.8-1.8M16.2 7.8 18 6"],
    "zoom-in": ["M10.5 4a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13z", "m15.5 15.5 5 5", "M10.5 8v5M8 10.5h5"],
    "zoom-out": ["M10.5 4a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13z", "m15.5 15.5 5 5", "M8 10.5h5"],
    "zoom-original": ["M10.5 4a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13z", "m15.5 15.5 5 5", "M9 13V8l-1.2 1M12.5 8.5v4.5"],
    "view-fullscreen": ["M4.5 9.5v-5h5M19.5 9.5v-5h-5M4.5 14.5v5h5M19.5 14.5v5h-5"],
    "bookmarks": ["M6.5 3.5h11v17l-5.5-4-5.5 4z"],
    "help-about": ["M12 3.5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17z", "M12 11v5M12 8h.01"],
    "dialog-information": ["M12 3.5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17z", "M12 11v5M12 8h.01"],
    "dialog-warning": ["M12 3.5 2.5 20h19z", "M12 10v4M12 17h.01"],
    "dialog-error": ["M12 3.5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17z", "m9 9 6 6M15 9l-6 6"],
    "media-playback-start": ["M8 5.5v13l10-6.5z"],
    "media-playback-pause": ["M7.5 5.5h3v13h-3zM13.5 5.5h3v13h-3z"],
    "media-playback-stop": ["M6 6h12v12H6z"],
    "audio-volume-high": ["M4.5 9.5h3l4-3.5v12l-4-3.5h-3z", "M15 9a4 4 0 0 1 0 6M17.5 6.5a7.5 7.5 0 0 1 0 11"],
    "audio-volume-muted": ["M4.5 9.5h3l4-3.5v12l-4-3.5h-3z", "m15 9.5 5 5M20 9.5l-5 5"],
    "mail-send": ["m3.5 11 17-7.5-4 17-5-6.5z", "m11.5 14 9-10.5"],
    "link": ["M10 14a4 4 0 0 0 5.6.4l2.9-2.9a4 4 0 0 0-5.6-5.6l-1.4 1.4", "M14 10a4 4 0 0 0-5.6-.4l-2.9 2.9a4 4 0 0 0 5.6 5.6l1.4-1.4"],
    "emblem-symbolic-link": ["M10 14a4 4 0 0 0 5.6.4l2.9-2.9a4 4 0 0 0-5.6-5.6l-1.4 1.4", "M14 10a4 4 0 0 0-5.6-.4l-2.9 2.9a4 4 0 0 0 5.6 5.6l1.4-1.4"],
    "view-choose": ["M4.5 4.5h6v6h-6zM13.5 4.5h6v6h-6zM4.5 13.5h6v6h-6zM13.5 13.5h6v6h-6z"],
    "show-menu": ["M4.5 7h15M4.5 12h15M4.5 17h15"],
    "overflow-menu": ["M6 12h.01M12 12h.01M18 12h.01"],
    "dots": ["M6 12h.01M12 12h.01M18 12h.01"],
    "process-stop": ["M12 3.5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17z", "m9 9 6 6M15 9l-6 6"],
    "kt-show-statusbar": ["M3.5 4.5h17v15h-17z", "M3.5 15.5h17"],
    "view-sidetree": ["M3.5 4.5h17v15h-17z", "M9 4.5v15", "M5.5 8h1.5M5.5 11h1.5M5.5 14h1.5"],
    "window-new": ["M3.5 4.5h17v15h-17z", "M3.5 8.5h17"],
    "system-run": ["M4.5 4.5h15v15h-15z", "m9 12 2.5 2.5L9 17M13 17h4"],
    "preferences-system": ["M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7z", "M12 3.5v2.5M12 18v2.5M3.5 12H6M18 12h2.5M6 6l1.8 1.8M16.2 16.2 18 18M6 18l1.8-1.8M16.2 7.8 18 6"],
    "tag": ["M3.5 12.5v-9h9l8 8-9 9z", "M8 8h.01"],
    "flag": ["M5.5 20.5v-16", "M5.5 4.5h12l-3 4 3 4h-12"],
    "rating": ["m12 3.5 2.6 5.3 5.9.9-4.3 4.1 1 5.9L12 17l-5.2 2.7 1-5.9-4.3-4.1 5.9-.9z"],
    "edit-clear": ["M4.5 12 10 5.5h9.5v13H10z", "m13 9.5 4 4M17 9.5l-4 4"],
    "image-x-generic-symbolic": ["M3.5 4.5h17v15h-17z", "M9 9.5m-1.6 0a1.6 1.6 0 1 0 3.2 0a1.6 1.6 0 1 0-3.2 0", "m4 17 5-5 4 4 3-3 4 4"],
}

# ---- which icon names map to which drawing, and their colour
PLACES = {
    "folder": ("folder", "dir"), "inode-directory": ("folder", "dir"), "folder-open": ("folder-open", "dir"),
    "user-home": ("home", "dir"), "folder-home": ("home", "dir"), "folder-documents": ("documents", "dir"),
    "folder-download": ("download", "dir"), "folder-downloads": ("download", "dir"), "folder-pictures": ("pictures", "dir"),
    "folder-images": ("pictures", "dir"), "folder-music": ("music", "dir"), "folder-sound": ("music", "dir"),
    "folder-videos": ("videos", "dir"), "folder-video": ("videos", "dir"), "folder-desktop": ("desktop", "dir"),
    "user-desktop": ("desktop", "dir"), "folder-templates": ("templates", "dir"), "folder-publicshare": ("public", "dir"),
    "folder-public": ("public", "dir"), "user-trash": ("trash", "trash"), "user-trash-full": ("trash-full", "trash"),
    "network-workgroup": ("network", "net"), "network-server": ("server", "net"), "folder-remote": ("remote", "net"),
    "folder-network": ("network", "net"), "folder-cloud": ("cloud", "net"), "document-open-recent": ("recent", "dir"),
    "folder-recent": ("recent", "dir"), "folder-root": ("root", "dir"), "folder-git": ("git", "dir"), "folder-gitignored": ("git", "dir"),
    "drive-harddisk": ("drive", "disk"), "drive-harddisk-root": ("drive", "disk"), "drive-removable-media": ("removable", "disk"),
    "drive-removable-media-usb": ("removable", "disk"), "media-optical": ("optical", "disk"), "media-removable": ("removable", "disk"),
    "smartphone": ("phone", "disk"), "phone": ("phone", "disk"), "computer": ("desktop", "disk"), "folder-favorites": ("rating", "dir"),
    "folder-tar": ("file-archive", "arc"), "folder-script": ("file-script", "code"), "folder-code": ("file-code", "code"),
    "folder-text": ("file-text", "dir"), "folder-print": ("documents", "dir"),
}
MIMES = {
    "image-x-generic": ("file-image", "img"), "image-png": ("file-image", "img"), "image-jpeg": ("file-image", "img"),
    "image-webp": ("file-image", "img"), "image-bmp": ("file-image", "img"), "image-tiff": ("file-image", "img"),
    "image-x-xcf": ("file-image", "img"), "image-avif": ("file-image", "img"), "image-heif": ("file-image", "img"),
    "image-gif": ("file-gif", "gif"), "image-apng": ("file-gif", "gif"), "image-svg+xml": ("file-vector", "img"),
    "video-x-generic": ("file-video", "vid"), "video-mp4": ("file-video", "vid"), "video-x-matroska": ("file-video", "vid"),
    "video-webm": ("file-video", "vid"), "video-quicktime": ("file-video", "vid"), "video-x-msvideo": ("file-video", "vid"),
    "video-mpeg": ("file-video", "vid"), "audio-x-generic": ("file-audio", "aud"), "audio-mpeg": ("file-audio", "aud"),
    "audio-flac": ("file-audio", "aud"), "audio-x-wav": ("file-audio", "aud"), "audio-x-vorbis+ogg": ("file-audio", "aud"),
    "audio-ogg": ("file-audio", "aud"), "audio-mp4": ("file-audio", "aud"), "audio-x-opus+ogg": ("file-audio", "aud"), "audio-aac": ("file-audio", "aud"),
    "application-zip": ("file-archive", "arc"), "application-x-tar": ("file-archive", "arc"), "application-x-compressed-tar": ("file-archive", "arc"),
    "application-x-bzip-compressed-tar": ("file-archive", "arc"), "application-x-xz-compressed-tar": ("file-archive", "arc"),
    "application-x-zstd-compressed-tar": ("file-archive", "arc"), "application-x-7z-compressed": ("file-archive", "arc"),
    "application-vnd.rar": ("file-archive", "arc"), "application-x-rar": ("file-archive", "arc"), "application-gzip": ("file-archive", "arc"),
    "application-x-bzip": ("file-archive", "arc"), "application-x-xz": ("file-archive", "arc"), "application-zstd": ("file-archive", "arc"),
    "application-x-archive": ("file-archive", "arc"), "application-x-lzma": ("file-archive", "arc"), "application-x-cpio": ("file-archive", "arc"),
    "application-pdf": ("file-pdf", "pdf"), "application-epub+zip": ("file-ebook", "pdf"), "application-postscript": ("file-pdf", "pdf"),
    "text-plain": ("file-text", "text"), "text-x-generic": ("file-text", "text"), "text-x-readme": ("file-text", "text"),
    "text-x-log": ("file-log", "text"), "text-markdown": ("file-markdown", "text"), "text-csv": ("file-sheet", "sheet"),
    "text-html": ("file-web", "web"), "application-xhtml+xml": ("file-web", "web"), "text-xml": ("file-code", "code"), "application-xml": ("file-code", "code"),
    "application-json": ("file-code", "code"), "application-yaml": ("file-code", "code"), "application-x-yaml": ("file-code", "code"), "application-toml": ("file-code", "code"),
    "text-x-python": ("file-source", "code"), "text-x-python3": ("file-source", "code"), "text-x-script": ("file-script", "code"),
    "application-x-shellscript": ("file-script", "code"), "text-x-c++src": ("file-source", "code"), "text-x-csrc": ("file-source", "code"),
    "text-x-chdr": ("file-source", "code"), "text-x-c++hdr": ("file-source", "code"), "text-x-java": ("file-source", "code"),
    "text-x-rust": ("file-source", "code"), "text-x-go": ("file-source", "code"), "text-javascript": ("file-source", "code"),
    "application-javascript": ("file-source", "code"), "text-x-typescript": ("file-source", "code"), "text-css": ("file-code", "code"),
    "text-x-cmake": ("file-script", "code"), "text-x-makefile": ("file-script", "code"), "text-x-patch": ("file-source", "code"),
    "text-x-ini": ("file-config", "text"), "application-x-ini": ("file-config", "text"), "text-x-conf": ("file-config", "text"),
    "application-x-desktop": ("file-desktop", "exe"), "application-x-executable": ("file-exe", "exe"), "application-x-sharedlib": ("file-exe", "exe"),
    "application-x-ms-dos-executable": ("file-exe", "exe"), "application-x-msdownload": ("file-exe", "exe"), "application-x-pie-executable": ("file-exe", "exe"),
    "application-vnd.appimage": ("file-exe", "exe"), "application-x-object": ("file-exe", "exe"),
    "application-x-rpm": ("file-package", "pkg"), "application-vnd.debian.binary-package": ("file-package", "pkg"), "application-x-deb": ("file-package", "pkg"),
    "application-vnd.flatpak": ("file-package", "pkg"), "application-vnd.flatpak.ref": ("file-package", "pkg"), "application-vnd.snap": ("file-package", "pkg"),
    "application-x-iso9660-image": ("file-disk-image", "disk"), "application-x-cd-image": ("file-disk-image", "disk"), "application-x-raw-disk-image": ("file-disk-image", "disk"),
    "application-x-qemu-disk": ("file-disk-image", "disk"), "application-x-bittorrent": ("file-torrent", "net"),
    "application-vnd.ms-excel": ("file-sheet", "sheet"), "application-vnd.openxmlformats-officedocument.spreadsheetml.sheet": ("file-sheet", "sheet"),
    "application-vnd.oasis.opendocument.spreadsheet": ("file-sheet", "sheet"), "x-office-spreadsheet": ("file-sheet", "sheet"),
    "application-msword": ("file-text", "doc"), "application-vnd.openxmlformats-officedocument.wordprocessingml.document": ("file-text", "doc"),
    "application-vnd.oasis.opendocument.text": ("file-text", "doc"), "application-rtf": ("file-text", "doc"), "x-office-document": ("file-text", "doc"),
    "application-vnd.ms-powerpoint": ("file-pres", "pres"), "application-vnd.openxmlformats-officedocument.presentationml.presentation": ("file-pres", "pres"),
    "application-vnd.oasis.opendocument.presentation": ("file-pres", "pres"), "x-office-presentation": ("file-pres", "pres"),
    "font-x-generic": ("file-font", "font"), "font-ttf": ("file-font", "font"), "font-otf": ("file-font", "font"), "font-woff": ("file-font", "font"), "application-x-font-ttf": ("file-font", "font"),
    "message-rfc822": ("file-mail", "doc"), "text-calendar": ("file-calendar", "doc"), "text-vcard": ("file-text", "doc"),
    "application-x-subrip": ("file-sub", "vid"), "text-x-ssa": ("file-sub", "vid"), "unknown": ("file-unknown", "text"),
    "application-octet-stream": ("file-unknown", "text"), "application-x-zerosize": ("file", "text"), "inode-symlink": ("link", "text"),
    "application-x-trash": ("trash", "trash"), "application-x-kgetlist": ("file-torrent", "net"),
}
ACTIONS = [k for k in P if k.startswith(("view-", "go-", "edit-", "folder-new", "document-", "list-", "dialog-", "window-", "tab-", "application-menu",
                                          "configure", "zoom-", "bookmarks", "help-", "media-", "audio-", "mail-", "link", "emblem-", "show-menu", "overflow-menu",
                                          "process-stop", "kt-", "system-run", "preferences-", "tag", "flag", "rating", "image-x-generic-symbolic"))]

HEAD = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">'
STYLE_MONO = ('<defs><style type="text/css" id="current-color-scheme">.ColorScheme-Text { color:#dfdfdf; }</style></defs>')


def svg(paths, colour=None):
    """A stroke drawing; colour None = monochrome, follows the colour scheme."""
    stroke = "currentColor" if colour is None else colour
    cls = ' class="ColorScheme-Text"' if colour is None else ""
    fill = "none" if colour is None else colour
    fill_opacity = "" if colour is None else ' fill-opacity="0.16"'
    body = "".join(f'<path d="{d}" fill="{fill}"{fill_opacity} stroke="{stroke}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"{cls}/>' for d in paths)
    # small circles written as "h.01" need a visible dot: the round cap does it
    return HEAD + (STYLE_MONO if colour is None else "") + body + "</svg>\n"


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    sheet = []
    for name in ACTIONS:
        write(os.path.join(OUT, "scalable", "actions", name + ".svg"), svg(P[name]))
        sheet.append(("actions", name, svg(P[name]).replace("currentColor", "#dfdfdf")))
    for name, (drawing, kind) in PLACES.items():
        write(os.path.join(OUT, "scalable", "places", name + ".svg"), svg(P[drawing], C[kind]))
        sheet.append(("places", name, svg(P[drawing], C[kind])))
    for name, (drawing, kind) in MIMES.items():
        write(os.path.join(OUT, "scalable", "mimetypes", name + ".svg"), svg(P[drawing], C[kind]))
        sheet.append(("mimetypes", name, svg(P[drawing], C[kind])))
    for name in ("drive-harddisk", "drive-removable-media", "media-optical", "smartphone", "computer", "network-server"):
        drawing, kind = PLACES[name]
        write(os.path.join(OUT, "scalable", "devices", name + ".svg"), svg(P[drawing], C[kind]))
    dirs = ["scalable/actions", "scalable/places", "scalable/mimetypes", "scalable/devices"]
    index = ["[Icon Theme]", "Name=NeoLine", "Comment=Outline icons in the style of the Dolphin NG cards",
             "Inherits=breeze-dark-mod-outline-places,breeze-dark,breeze,hicolor", "Example=folder", "FollowsColorScheme=true",
             "Directories=" + ",".join(dirs), ""]
    for d in dirs:
        index += [f"[{d}]", "Size=24", "Type=Scalable", "MinSize=8", "MaxSize=512", "Context=" + d.split("/")[1].capitalize(), ""]
    write(os.path.join(OUT, "index.theme"), "\n".join(index))

    if os.path.islink(INSTALL) or os.path.isdir(INSTALL):
        if os.path.islink(INSTALL):
            os.unlink(INSTALL)
        else:
            shutil.rmtree(INSTALL)
    os.makedirs(os.path.dirname(INSTALL), exist_ok=True)
    shutil.copytree(OUT, INSTALL)
    print(f"{len(sheet)} icons -> {OUT} and {INSTALL}")

    if "--sheet" in sys.argv:
        cells = "".join(f'<figure title="{n}"><div class="ic">{s}</div><figcaption>{n}</figcaption></figure>' for _, n, s in sheet)
        html = ("<title>NeoLine Icons</title><style>:root{color-scheme:dark}body{margin:0;background:#1b1d20;color:#9ea2a8;font:12px/1.3 'Noto Sans',sans-serif;"
                "padding:24px max(16px,env(safe-area-inset-right,0px)) 48px max(16px,env(safe-area-inset-left,0px))}h1{color:#dfdfdf;font-size:20px;font-weight:600;margin:0 0 4px}"
                "p{max-width:70ch}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(118px,1fr));gap:8px;margin-top:18px}"
                "figure{margin:0;background:rgba(255,255,255,.05);border-radius:10px;padding:10px 6px 8px;display:flex;flex-direction:column;align-items:center;gap:6px;min-width:0}"
                "figure:hover{background:rgba(255,255,255,.1)}.ic svg{width:40px;height:40px}figcaption{font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%}"
                "</style><h1>NeoLine · icone</h1><p>Contorni 1,7 px su griglia 24, come nei mockup delle card. Le azioni seguono il colore del tema, luoghi e tipi di file hanno il colore della loro categoria. "
                "Il tema eredita Breeze dark per tutto il resto.</p><div class=\"grid\">" + cells + "</div>")
        with open(os.path.join(HERE, "preview.html"), "w") as f:
            f.write(html)
        print("preview.html written")


if __name__ == "__main__":
    main()
