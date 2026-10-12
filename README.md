# pico8-r1

Package a PICO-8 cart as a Rabbit R1 Creation: a folder of static web files plus the install QR code.

```
python3 pico8_to_r1.py cart.p8 --title "My Game" --base-url https://example.com/games/mygame/
```

The cart can be a `.p8` file or a `.p8.png` as distributed on the PICO-8 BBS (PICO-8 reads the PNG directly,
and the icon is cut from the cart's label).

Upload the contents of `dist/` to that URL (HTTPS), then scan `dist/qr.png` with the R1's Creations scanner.

## Installation

Requirements:

- **Python 3.8+**. The script itself uses only the standard library.
- **PICO-8 0.2.x**, your own licensed copy. The script looks for it in the usual install
  locations; otherwise pass `--pico8 /path/to/pico8` or set `PICO8`.
- **Pillow** and **qrcode** (optional): without them the script skips `icon.png` and `qr.png`.

```
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install pillow "qrcode[pil]"
```

Check that PICO-8 is found by running the packager on the included example:

```
python3 pico8_to_r1.py examples/btn_test.p8 --title "Button test" --base-url https://example.com/btntest/
```

The R1's scanner rejects a creation whose `description` is empty, so `--description` defaults to 
"`<title>` - PICO-8 game".

## Controls and Options

Controls on the R1: 
- touch d-pad and O/X buttons (multi-touch)
- scroll wheel = up/down (`--invert-wheel` swaps)
- side button = O
- hold side button = pause menu

Options: 
- `--layout overlay` draws the controls over the game instead of in their own strip under it
(bigger game, but covered)
- `--fps` shows a frame-rate and window-size readout.


### Extra files and info
`tools/probe.html` logs R1 events. 
`docs/r1-findings.md` records what was verified on a real R1.
