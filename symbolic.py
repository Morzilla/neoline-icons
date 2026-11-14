# SPDX-License-Identifier: MIT
"""NeoLine's symbolic icons: the small monochrome ones that panels, bars and GTK applications ask for by a name
ending in "-symbolic" (network, battery, volume, window buttons...).

GTK recolours a symbolic icon by forcing the *fill* of its shapes, and NeoLine is drawn with strokes: a stroked path
would come out as a blob or in the wrong colour. So every drawing is turned into filled outlines once, with Inkscape
("stroke to path", headless), and the result is kept in symbolic-paths.json: the theme can be rebuilt without Inkscape
as long as no symbolic drawing changes.

    ./make-icons.py --symbolic     converts the drawings that are not in symbolic-paths.json yet (needs inkscape)

A symbolic icon is a list of layers; a layer is some paths, an opacity (the dim part of a level icon) and a mode:
"stroke" (the usual outline), "fill" (a plain filled shape, as the level inside a battery), "solid" (filled and stroked).
"""
import hashlib
import json
import os
import re
import subprocess
import tempfile

WIDTH = 2.0       # a little heavier than the 1.7 of the big icons: these are shown at 16 px
DIM = 0.35        # the part of a level icon that is "off"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symbolic-paths.json")


def L(paths, opacity=1.0, mode="stroke"):
    return (tuple(paths), opacity, mode)


# ---- drawings made for the symbolic set (24 x 24 grid, as everywhere)
SLASH = ["M4 4l16 16"]
SPEAKER = ["M4.5 9.5h3l4-3.5v12l-4-3.5h-3z"]
WAVE1, WAVE2 = ["M15 9a4 4 0 0 1 0 6"], ["M17.5 6.5a7.5 7.5 0 0 1 0 11"]
MIC = ["M12 3.5a2.5 2.5 0 0 1 2.5 2.5v5.5a2.5 2.5 0 0 1-5 0V6A2.5 2.5 0 0 1 12 3.5z", "M6.5 11.5a5.5 5.5 0 0 0 11 0", "M12 17v3.5M9 20.5h6"]
WIFI_DOT = ["M12 18.5h.01"]
WIFI_ARCS = [["M9.2 15.7a4 4 0 0 1 5.6 0"], ["M6.3 12.8a8 8 0 0 1 11.4 0"], ["M3.5 10a12 12 0 0 1 17 0"]]
BARS = [["M5 19.5v-3"], ["M9.7 19.5v-7"], ["M14.3 19.5v-11"], ["M19 19.5v-15"]]
BLUETOOTH = ["M7 7.5l10 9-5 4v-17l5 4-10 9"]
PLANE = ["M12 3.5c.8 0 1.5.7 1.5 1.5v4.5l7 4v2l-7-2v4l2 1.5v1.5L12 19.5l-3.5 1v-1.5l2-1.5v-4l-7 2v-2l7-4V5c0-.8.7-1.5 1.5-1.5z"]
BATTERY = ["M3.5 8h14.5a1.5 1.5 0 0 1 1.5 1.5v5a1.5 1.5 0 0 1-1.5 1.5H3.5A1.5 1.5 0 0 1 2 14.5v-5A1.5 1.5 0 0 1 3.5 8z", "M22 10.5v3"]
BOLT = ["M13 5l-4 7h5l-4 7"]
SUN = ["M12 8.5a3.5 3.5 0 1 0 0 7a3.5 3.5 0 1 0 0-7z"]
RAYS_MAIN = ["M12 3v2.5M12 18.5V21M3 12h2.5M18.5 12H21"]
RAYS_DIAG = ["M5.6 5.6l1.8 1.8M16.6 16.6l1.8 1.8M5.6 18.4l1.8-1.8M16.6 7.4l1.8-1.8"]
MOON = ["M19.5 14.5A8 8 0 0 1 9.5 4.5a8 8 0 1 0 10 10z"]
BELL = ["M6.5 16.5V11a5.5 5.5 0 0 1 11 0v5.5l1.5 1.5H5z", "M10 20.5a2.2 2.2 0 0 0 4 0"]
POWER = ["M12 3.5v8", "M7.5 6.5a7.5 7.5 0 1 0 9 0"]
LOGOUT = ["M14 4.5H6v15h8", "M10.5 12h10M17 8.5l3.5 3.5-3.5 3.5"]
LOCK = ["M6.5 11h11v9h-11z", "M8.5 11V8a3.5 3.5 0 0 1 7 0v3"]
UNLOCK = ["M6.5 11h11v9h-11z", "M8.5 11V8a3.5 3.5 0 0 1 7 0"]
PERSON = ["M12 4.5a3.5 3.5 0 1 0 0 7a3.5 3.5 0 1 0 0-7z", "M5 19.5a7 7 0 0 1 14 0"]
PEOPLE = ["M9 5.5a3 3 0 1 0 0 6a3 3 0 1 0 0-6z", "M3 19a6 6 0 0 1 12 0", "M16 6a3 3 0 0 1 0 5.5M17.5 14a6 6 0 0 1 3.5 5"]
CAMERA = ["M4 7.5h3l1.5-2h7l1.5 2h3v11H4z", "M12 9.5a3.5 3.5 0 1 0 0 7a3.5 3.5 0 1 0 0-7z"]
VIDEOCAM = ["M3.5 7h11v10h-11z", "M14.5 10.5l6-3v9l-6-3"]
PRINTER = ["M7.5 8.5v-4h9v4", "M7.5 16.5h-3v-8h15v8h-3", "M7.5 13.5h9v6h-9z"]
KEYBOARD = ["M3.5 7h17v10h-17z", "M7 10.5h.01M10.5 10.5h.01M14 10.5h.01M17 10.5h.01M8 13.5h8"]
MOUSE = ["M12 3.5a5.5 5.5 0 0 1 5.5 5.5v6a5.5 5.5 0 0 1-11 0V9A5.5 5.5 0 0 1 12 3.5z", "M12 7v3"]
TOUCHPAD = ["M4.5 5h15v14h-15z", "M4.5 14.5h15M12 14.5V19"]
LAPTOP = ["M5.5 5.5h13v9h-13z", "M3 18.5h18"]
NOTE = ["M9.5 17.5V5.5l9-2v12", "M9.5 17.5a2.5 2.5 0 1 1-5 0a2.5 2.5 0 1 1 5 0z", "M18.5 15.5a2.5 2.5 0 1 1-5 0a2.5 2.5 0 1 1 5 0z"]
CLOCK = ["M12 3.5a8.5 8.5 0 1 0 0 17a8.5 8.5 0 1 0 0-17z", "M12 7.5V12l3 2"]
ALARM = ["M12 6.5a7 7 0 1 0 0 14a7 7 0 1 0 0-14z", "M12 10v3.5l2.5 1.5", "M5 4.5l-2 2M19 4.5l2 2"]
QUESTION = ["M12 3.5a8.5 8.5 0 1 0 0 17a8.5 8.5 0 1 0 0-17z", "M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1 1-1 1.7M12 16.5h.01"]
PIN = ["M12 20.5s6-5.5 6-10a6 6 0 0 0-12 0c0 4.5 6 10 6 10z", "M12 8.5a2 2 0 1 0 0 4a2 2 0 1 0 0-4z"]
CLIP = ["M19.5 11.5l-7.8 7.8a4.5 4.5 0 0 1-6.4-6.4l8.5-8.5a3 3 0 0 1 4.2 4.2l-8.5 8.5a1.5 1.5 0 0 1-2.1-2.1l7.8-7.8"]
ARROWS_UPDOWN = ["M8 19.5v-15M4.5 8L8 4.5 11.5 8", "M16 4.5v15M12.5 16l3.5 3.5 3.5-3.5"]
UPDATE = ["M12 4v10.5M8 10.5l4 4 4-4", "M5 19.5h14"]
SHUFFLE = ["M4 7.5h3.5l8 9H20", "M4 16.5h3.5l2.2-2.5", "M13.3 10l2.2-2.5H20", "M17.5 5l2.5 2.5-2.5 2.5", "M17.5 14l2.5 2.5-2.5 2.5"]
CHEVRON = {"down": ["M7 10l5 5 5-5"], "up": ["M7 14l5-5 5 5"], "end": ["M10 7l5 5-5 5"], "start": ["M14 7l-5 5 5 5"]}
STAR = ["m12 3.5 2.6 5.3 5.9.9-4.3 4.1 1 5.9L12 17l-5.2 2.7 1-5.9-4.3-4.1 5.9-.9z"]
RECORD = ["M12 6.5a5.5 5.5 0 1 0 0 11a5.5 5.5 0 1 0 0-11z"]
SIDEBAR = ["M3.5 5h17v14h-17z", "M9 5v14"]


def build_set(P, ACTIONS, PLACES):
    """name (without "-symbolic") -> (context, layers). P, ACTIONS and PLACES are the big icons' drawings: every action
    and place gets a symbolic twin, then come the names only symbolic icons have."""
    sym = {}

    def add(context, name, *layers):
        sym[name] = (context, list(layers))

    def many(context, names, *layers):
        for name in names.split():
            add(context, name, *layers)

    devices = {"computer", "drive-harddisk", "drive-harddisk-root", "drive-removable-media", "drive-removable-media-usb", "media-optical",
               "media-removable", "phone", "smartphone", "network-server"}
    for name in ACTIONS:
        if not name.endswith("-symbolic"):
            add("actions", name, L(P[name]))
    for name, (drawing, _kind) in PLACES.items():
        add("devices" if name in devices else "places", name, L(P[drawing]))

    # other names for drawings the theme already has (the names GTK applications and GNOME-like shells use)
    for names, drawing in (("open-menu", "application-menu"), ("view-more-horizontal content-loading", "overflow-menu"), ("system-search edit-find-replace", "edit-find"),
                           ("emblem-system applications-system preferences-system preferences-other", "configure"), ("emblem-ok object-select checkmark", "dialog-ok"),
                           ("help-browser help-faq help-contents", "help-about"), ("dialog-password", "app-key"), ("mail-unread mail-read mail-message-new", "app-mail"),
                           ("insert-link", "link"), ("bookmark-new user-bookmarks", "bookmarks"), ("view-list", "view-list-text"), ("edit-clear-all", "edit-clear"),
                           ("value-increase", "list-add"), ("value-decrease", "list-remove"), ("zoom-fit-best", "zoom-original"), ("view-reveal", "view-preview"),
                           ("view-conceal", "view-hidden"), ("document-edit", "edit-rename"), ("document-save-as", "document-save"), ("document-send", "mail-send"),
                           ("system-reboot system-restart media-playlist-repeat", "view-refresh"), ("emblem-important", "dialog-warning"),
                           ("video-display tv", "desktop"), ("tablet", "phone"), ("folder-saved-search", "edit-find"), ("emblem-synchronizing", "view-refresh"),
                           ("non-starred semi-starred", "rating"), ("emblem-favorite", "rating"), ("user-trash-full", "trash-full"), ("network-workgroup", "network")):
        for name in names.split():
            add("actions", name, L(P[drawing]))
    add("actions", "view-more", L(["M12 6h.01M12 12h.01M12 18h.01"]))
    add("actions", "starred", L(STAR, 1.0, "solid"))
    for side, d in CHEVRON.items():
        add("actions", "pan-" + side, L(d))
    add("actions", "window-maximize", L(["M5.5 5.5h13v13h-13z"]))
    add("actions", "window-minimize", L(["M6 17.5h12"]))
    add("actions", "window-restore", L(["M8.5 8.5h10v10h-10z", "M5.5 15.5v-10h10"]))
    add("actions", "view-restore", L(["M9 4.5V9H4.5M15 4.5V9h4.5M9 19.5V15H4.5M15 19.5V15h4.5"]))
    many("actions", "sidebar-show sidebar-hide view-sidebar-start", L(SIDEBAR))
    many("actions", "sidebar-show-right view-sidebar-end", L(["M3.5 5h17v14h-17z", "M15 5v14"]))
    add("actions", "dialog-question", L(QUESTION))
    many("actions", "find-location mark-location", L(PIN))
    add("actions", "mail-attachment", L(CLIP))
    many("actions", "software-update-available software-update-urgent system-software-update emblem-downloads", L(UPDATE))
    add("actions", "media-playlist-shuffle", L(SHUFFLE))
    add("actions", "media-skip-forward", L(["M6 6l8 6-8 6z", "M17.5 6v12"]))
    add("actions", "media-skip-backward", L(["M18 6l-8 6 8 6z", "M6.5 6v12"]))
    add("actions", "media-seek-forward", L(["M4.5 7l6.5 5-6.5 5zM12.5 7l6.5 5-6.5 5z"]))
    add("actions", "media-seek-backward", L(["M19.5 7l-6.5 5 6.5 5zM11.5 7l-6.5 5 6.5 5z"]))
    add("actions", "media-record", L(RECORD, 1.0, "solid"))
    add("actions", "media-eject", L(["M12 5.5l6.5 8h-13z", "M5.5 17.5h13"]))
    many("actions", "system-shutdown", L(POWER))
    add("actions", "system-log-out", L(LOGOUT))
    many("actions", "system-lock-screen changes-prevent lock channel-secure security-high network-vpn", L(LOCK))
    many("actions", "changes-allow channel-insecure security-low", L(UNLOCK))
    many("actions", "system-suspend system-hibernate night-light weather-clear-night", L(MOON))
    many("actions", "avatar-default user-info contact-new user-available", L(PERSON))
    many("actions", "system-users system-switch-user", L(PEOPLE))
    many("actions", "appointment-soon preferences-system-time", L(CLOCK))
    add("actions", "alarm", L(ALARM))
    add("actions", "document-print", L(PRINTER))

    # devices
    add("devices", "printer", L(PRINTER))
    add("devices", "input-keyboard", L(KEYBOARD))
    add("devices", "input-mouse", L(MOUSE))
    add("devices", "input-touchpad", L(TOUCHPAD))
    many("devices", "computer-laptop laptop", L(LAPTOP))
    many("devices", "camera-photo camera", L(CAMERA))
    many("devices", "camera-video camera-web", L(VIDEOCAM))
    add("devices", "camera-disabled", L(VIDEOCAM), L(SLASH))
    many("devices", "audio-input-microphone", L(MIC))
    add("devices", "audio-x-generic", L(NOTE))
    add("devices", "audio-card", L(SPEAKER + WAVE1 + WAVE2))

    # status: volume, microphone
    many("status", "audio-volume-high audio-volume-overamplified", L(SPEAKER + WAVE1 + WAVE2))
    add("status", "audio-volume-medium", L(SPEAKER + WAVE1), L(WAVE2, DIM))
    add("status", "audio-volume-low", L(SPEAKER), L(WAVE1 + WAVE2, DIM))
    add("status", "audio-volume-muted", L(SPEAKER), L(["m15 9.5 5 5M20 9.5l-5 5"]))
    many("status", "microphone-sensitivity-high microphone-sensitivity-medium microphone-sensitivity-low", L(MIC))
    many("status", "microphone-sensitivity-muted microphone-disabled", L(MIC), L(SLASH))

    # status: networks
    wifi_all = WIFI_DOT + [d for arc in WIFI_ARCS for d in arc]
    many("status", "network-wireless network-wireless-connected network-wireless-signal-excellent network-wireless-hotspot", L(wifi_all))
    for level, name in enumerate(("none", "weak", "ok", "good")):
        on = WIFI_DOT + [d for arc in WIFI_ARCS[:level] for d in arc]
        off = [d for arc in WIFI_ARCS[level:] for d in arc]
        add("status", "network-wireless-signal-" + name, *([L(on)] + ([L(off, DIM)] if off else [])))
    many("status", "network-wireless-acquiring network-wireless-no-route", L(wifi_all, DIM))
    many("status", "network-wireless-offline network-wireless-disabled network-wireless-hardware-disabled", L(wifi_all, DIM), L(SLASH))
    many("status", "network-wired network-wired-connected", L(P["network"]))
    many("status", "network-wired-acquiring network-wired-no-route", L(P["network"], DIM))
    many("status", "network-wired-disconnected network-wired-offline network-offline network-error", L(P["network"], DIM), L(SLASH))
    add("status", "network-vpn-acquiring", L(LOCK, DIM))
    many("status", "network-vpn-disconnected network-vpn-disabled", L(LOCK, DIM), L(SLASH))
    many("status", "network-transmit-receive network-idle", L(ARROWS_UPDOWN))
    all_bars = [d for bar in BARS for d in bar]
    many("status", "network-cellular network-cellular-connected network-cellular-signal-excellent", L(all_bars))
    for level, name in enumerate(("none", "weak", "ok", "good")):
        on = [d for bar in BARS[:level] for d in bar]
        off = [d for bar in BARS[level:] for d in bar]
        layers = ([L(on)] if on else []) + [L(off, DIM)]
        add("status", "network-cellular-signal-" + name, *layers)
    many("status", "network-cellular-offline network-cellular-disabled network-cellular-hardware-disabled", L(all_bars, DIM), L(SLASH))
    add("status", "network-cellular-acquiring", L(all_bars, DIM))
    many("status", "bluetooth bluetooth-active bluetooth-connected bluetooth-paired", L(BLUETOOTH))
    many("status", "bluetooth-acquiring bluetooth-disconnected", L(BLUETOOTH, DIM))
    many("status", "bluetooth-disabled bluetooth-hardware-disabled", L(BLUETOOTH, DIM), L(SLASH))
    add("status", "airplane-mode", L(PLANE))
    add("status", "airplane-mode-disabled", L(PLANE, DIM), L(SLASH))

    # status: battery, by tens and by the names of the older scheme; charging = a bolt over a dimmed level
    def battery(level, charging):
        layers = [L(BATTERY)]
        if level > 0:
            w = round(max(1.5, 12.5 * level / 100), 2)
            layers.append(L([f"M4.5 10.5h{w}v3h-{w}z"], DIM + 0.1 if charging else 1.0, "fill"))
        if charging:
            layers.append(L(BOLT))
        return layers
    for level in range(0, 101, 10):
        add("status", f"battery-level-{level}", *battery(level, False))
        add("status", f"battery-level-{level}-charging", *battery(level, True))
    add("status", "battery-level-100-charged", *battery(100, False))
    for name, level in (("empty", 0), ("caution", 10), ("low", 30), ("good", 70), ("full", 100)):
        add("status", f"battery-{name}", *battery(level, False))
        add("status", f"battery-{name}-charging", *battery(level, True))
    many("status", "battery battery-full-charged", *battery(100, False))
    add("status", "battery-missing", L(BATTERY, DIM), L(SLASH))

    # status: brightness, notifications
    many("status", "display-brightness display-brightness-high weather-clear", L(SUN + RAYS_MAIN + RAYS_DIAG))
    add("status", "display-brightness-medium", L(SUN + RAYS_MAIN), L(RAYS_DIAG, DIM))
    add("status", "display-brightness-low", L(SUN), L(RAYS_MAIN + RAYS_DIAG, DIM))
    add("status", "display-brightness-off", L(SUN + RAYS_MAIN + RAYS_DIAG, DIM))
    many("status", "notifications notification preferences-system-notifications bell notification-new", L(BELL))
    many("status", "notifications-disabled notification-disabled", L(BELL, DIM), L(SLASH))
    return sym


# ---- stroke to fill, cached
def _key(layer, soften):
    paths, _opacity, mode = layer
    return hashlib.sha1(json.dumps([[soften(d) for d in paths], mode, WIDTH]).encode()).hexdigest()[:16]


def load_cache():
    if os.path.exists(CACHE):
        with open(CACHE) as f:
            return json.load(f)
    return {}


def _round(d):
    return re.sub(r"-?\d+\.\d+", lambda m: ("%.3f" % float(m.group(0))).rstrip("0").rstrip("."), d)


def convert(sym, soften):
    """Fill symbolic-paths.json with the outlines of every layer that is not in it yet."""
    cache = load_cache()
    todo = {}
    for _context, layers in sym.values():
        for layer in layers:
            key = _key(layer, soften)
            if key not in cache and key not in todo:
                todo[key] = layer
    wanted = {_key(layer, soften) for _c, layers in sym.values() for layer in layers}
    cache = {k: v for k, v in cache.items() if k in wanted}  # drop what no icon uses any more
    if todo:
        with tempfile.TemporaryDirectory() as tmp:
            files = []
            for key, (paths, _opacity, mode) in todo.items():
                ds = " ".join(soften(d) for d in paths)
                if mode == "fill":
                    cache[key] = ds
                    continue
                fill = "#000" if mode == "solid" else "none"
                body = "".join(f'<path d="{soften(d)}" fill="{fill}" stroke="#000" stroke-width="{WIDTH}" stroke-linecap="round" stroke-linejoin="round"/>' for d in paths)
                path = os.path.join(tmp, key + ".svg")
                with open(path, "w") as f:
                    f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">{body}</svg>')
                files.append(path)
            if files:
                env = {k: v for k, v in os.environ.items() if k not in ("DISPLAY", "WAYLAND_DISPLAY")}  # headless: no window can open
                actions = "select-all;object-stroke-to-path;select-all;path-union;export-type:svg;export-plain-svg;export-overwrite;export-do"
                for i in range(0, len(files), 60):
                    subprocess.run(["inkscape", "--batch-process", "--actions=" + actions] + files[i:i + 60], env=env, check=True,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                for path in files:
                    with open(path) as f:
                        ds = re.findall(r'<path[^>]*?\sd="([^"]*)"', f.read(), re.S)
                    if not ds:
                        raise SystemExit("inkscape gave no path for " + path)
                    cache[os.path.basename(path)[:-4]] = _round(" ".join(" ".join(d.split()) for d in ds))
    with open(CACHE, "w") as f:
        json.dump(dict(sorted(cache.items())), f, indent=0)
    return len(todo)


def svg(layers, soften, cache, style):
    body = ""
    for layer in layers:
        d = cache.get(_key(layer, soften))
        if d is None:
            return None
        opacity = f' opacity="{layer[1]}"' if layer[1] < 1 else ""
        body += f'<path d="{d}" fill="currentColor" class="ColorScheme-Text"{opacity}/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">{style}{body}</svg>\n'
