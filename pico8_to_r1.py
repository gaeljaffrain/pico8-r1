#!/usr/bin/env python3
"""Package a PICO-8 cart as a Rabbit R1 Creation (a folder of static web files + install QR code).

    pico8_to_r1.py cart.p8 --title "My Game" --base-url https://example.com/games/mygame/

Writes dist/ (index.html, index.js, r1-input.js, icon.png, manifest.json, qr.png).
Upload dist/ to any HTTPS host, then scan qr.png with the R1's Creations scanner.
Requires a licensed PICO-8 install. Pillow and qrcode are optional (icon and QR code).
"""
import argparse, json, os, platform, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLATE_NAME = "r1_creation"
PALETTE = ["000000", "1d2b53", "7e2553", "008751", "ab5236", "5f574f", "c2c3c7", "fff1e8",
           "ff004d", "ffa300", "ffec27", "00e436", "29adff", "83769c", "ff77a8", "ffccaa"]
PICO8_CANDIDATES = [
    "/Applications/pico-8/PICO-8.app/Contents/MacOS/pico8",
    "/Applications/PICO-8.app/Contents/MacOS/pico8",
    "/usr/local/bin/pico8",
    "C:/Program Files (x86)/PICO-8/pico8.exe",
]


def find_pico8(arg):
    for c in [arg, os.environ.get("PICO8"), *PICO8_CANDIDATES, shutil.which("pico8")]:
        if c and Path(c).is_file():
            return str(c)
    sys.exit("PICO-8 not found: pass --pico8 PATH or set $PICO8")


def plates_dir():
    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Library/Application Support/pico-8/plates"
    if system == "Windows":
        return Path(os.environ["APPDATA"]) / "pico-8/plates"
    return Path.home() / ".lexaloffle/pico-8/plates"


def read_label_from_p8(text):
    """Return a 128x128 list of palette indices from a .p8 __label__ section, or None."""
    if "__label__" not in text:
        return None
    rows = text.split("__label__\n", 1)[1].split("\n__", 1)[0].strip().split("\n")
    if len(rows) < 128 or any(len(r) < 128 for r in rows[:128]):
        return None
    return [[int(ch, 16) for ch in r[:128]] for r in rows[:128]]


def with_label(cart, workdir):
    """PICO-8 refuses to export a .p8 cart without a label; add a black one if missing."""
    if cart.suffix == ".png":
        return cart, None
    text = cart.read_text()
    label = read_label_from_p8(text)
    if label is not None:
        return cart, label
    blank = [[0] * 128 for _ in range(128)]
    if "__label__" in text:
        text = text.split("__label__")[0].rstrip("\n")
    text += "\n__label__\n" + "\n".join("0" * 128 for _ in range(128)) + "\n"
    patched = workdir / cart.name
    patched.write_text(text)
    return patched, blank


def make_icon(cart, label, dest):
    try:
        from PIL import Image
    except ImportError:
        print("note: Pillow not installed, skipping icon.png"); return False
    if cart.suffix == ".png":                      # .p8.png: label sits at (16,24) in the 160x205 image
        img = Image.open(cart).convert("RGB").crop((16, 24, 144, 152))
    else:
        img = Image.new("RGB", (128, 128))
        px = img.load()
        for y, row in enumerate(label):
            for x, v in enumerate(row):
                px[x, y] = tuple(int(PALETTE[v][i:i + 2], 16) for i in (0, 2, 4))
    img.resize((96, 96), Image.NEAREST).save(dest)
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cart", type=Path, help=".p8 or .p8.png cartridge")
    ap.add_argument("--title", help="creation title (default: cart name)")
    ap.add_argument("--description", help="creation description (default: \"<title> - PICO-8 game\"); the R1 rejects an empty one")
    ap.add_argument("--base-url", help="HTTPS URL where dist/ will be hosted (needed for the QR code)")
    ap.add_argument("--out", type=Path, default=Path("dist"))
    ap.add_argument("--pico8", help="path to the pico8 binary")
    ap.add_argument("--invert-wheel", action="store_true", help="swap wheel up/down")
    ap.add_argument("--layout", choices=["strip", "overlay"], default="strip",
                    help="strip: controls in their own area under the game (default); overlay: controls over the game")
    ap.add_argument("--orientation", choices=["portrait", "landscape"], default="portrait",
                    help="landscape: hold the R1 sideways, wheel down; controls move to the corners")
    ap.add_argument("--landscape-flip", action="store_true",
                    help="rotate the landscape page the other way (wheel up)")
    ap.add_argument("--fps", action="store_true", help="show an fps / window-size readout")
    ap.add_argument("--theme-color", default="#FE5000")
    ap.add_argument("--serve", type=int, nargs="?", const=8000, metavar="PORT", help="serve dist/ locally after building")
    a = ap.parse_args()

    if not a.cart.is_file():
        sys.exit(f"cart not found: {a.cart}")
    pico8 = find_pico8(a.pico8)
    title = a.title or a.cart.name.split(".")[0]
    description = a.description or f"{title} - PICO-8 game"
    out = a.out.resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        cart, label = with_label(a.cart.resolve(), tmp)

        plates = plates_dir()
        plates.mkdir(parents=True, exist_ok=True)
        shutil.copy(HERE / "templates/r1.html", plates / f"{PLATE_NAME}.html")

        stage = tmp / "export"
        stage.mkdir()
        res = subprocess.run([pico8, "-export", f"{stage}/index.html -p {PLATE_NAME}", str(cart)],
                             capture_output=True, text=True)
        if not (stage / "index.html").is_file() or not (stage / "index.js").is_file():
            sys.exit(f"PICO-8 export failed:\n{res.stdout}{res.stderr}")
        for f in ("index.html", "index.js"):
            shutil.copy(stage / f, out / f)

    cfg = "window.R1_CONFIG=" + json.dumps({"invertWheel": a.invert_wheel, "layout": a.layout, "fps": a.fps,
                                            "orientation": a.orientation, "flip": a.landscape_flip}) + ";\n"
    (out / "r1-input.js").write_text(cfg + (HERE / "templates/r1-input.js").read_text())

    if label is None and a.cart.suffix != ".png":
        label = read_label_from_p8(a.cart.read_text())
    icon_ok = make_icon(a.cart, label, out / "icon.png")

    base = a.base_url.rstrip("/") + "/" if a.base_url else None
    if base:
        payload = {"title": title, "url": base + "index.html", "description": description,
                   "iconUrl": base + "icon.png" if icon_ok else "", "themeColor": a.theme_color}
        (out / "manifest.json").write_text(json.dumps(payload, indent=2) + "\n")
        try:
            import qrcode
            qrcode.make(json.dumps(payload, separators=(",", ":")), box_size=8, border=4).save(out / "qr.png")
        except ImportError:
            print("note: qrcode not installed, skipping qr.png")
        print("QR payload:", json.dumps(payload, separators=(",", ":")))
    else:
        print("note: no --base-url, so no manifest.json / qr.png")

    kb = (out / "index.js").stat().st_size // 1024
    print(f"built {out} ({kb} KB, of which about 1600 KB is the PICO-8 player)")
    print("upload the folder contents to your HTTPS host, then scan qr.png from the R1's Creations scanner")

    if a.serve:
        os.chdir(out)
        print(f"serving http://localhost:{a.serve}/ (Ctrl-C to stop)")
        subprocess.run([sys.executable, "-m", "http.server", str(a.serve)])


if __name__ == "__main__":
    main()
