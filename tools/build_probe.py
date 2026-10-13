#!/usr/bin/env python3
"""Build the R1 probe creation (dist-probe/) from tools/probe.html.

    tools/build_probe.py https://example.com/r1-probe/

Writes index.html, icon.png, manifest.json and qr.png. Upload the folder contents to the
URL (HTTPS), then scan qr.png with the R1's Creations scanner.
Pillow and qrcode are optional (icon and QR code).
"""
import argparse, json, shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base_url", help="HTTPS URL where the output folder will be hosted")
    ap.add_argument("--out", type=Path, default=HERE.parent / "dist-probe")
    ap.add_argument("--title", default="R1 probe")
    ap.add_argument("--description", default="R1 event and audio probe")
    ap.add_argument("--theme-color", default="#FE5000")
    a = ap.parse_args()

    out = a.out.resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    shutil.copy(HERE / "probe.html", out / "index.html")

    base = a.base_url.rstrip("/") + "/"
    icon_ok = False
    try:
        from PIL import Image
        Image.new("RGB", (96, 96), (0, 160, 0)).save(out / "icon.png")
        icon_ok = True
    except ImportError:
        print("note: Pillow not installed, skipping icon.png")

    payload = {"title": a.title, "url": base + "index.html", "description": a.description,
               "iconUrl": base + "icon.png" if icon_ok else "", "themeColor": a.theme_color}
    (out / "manifest.json").write_text(json.dumps(payload, indent=2) + "\n")
    try:
        import qrcode
        qrcode.make(json.dumps(payload, separators=(",", ":")), box_size=8, border=4).save(out / "qr.png")
    except ImportError:
        print("note: qrcode not installed, skipping qr.png")
    print("QR payload:", json.dumps(payload, separators=(",", ":")))
    print(f"built {out}")


if __name__ == "__main__":
    main()
