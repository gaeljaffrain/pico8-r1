import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pico8_to_r1 as p


def test_label_added_when_missing():
    with tempfile.TemporaryDirectory() as d:
        cart = Path(d) / "a.p8"
        cart.write_text("pico-8 cartridge // x\nversion 41\n__lua__\nprint(1)\n")
        patched, label = p.with_label(cart, Path(d) / "w") if (Path(d) / "w").mkdir() is None else None
        rows = patched.read_text().split("__label__\n")[1].strip().split("\n")
        assert len(rows) == 128 and all(len(r) == 128 for r in rows)
        assert label == [[0] * 128 for _ in range(128)]


def test_existing_label_is_read():
    row = "0123456789abcdef" * 8
    text = "__lua__\nprint(1)\n__label__\n" + "\n".join([row] * 128) + "\n__gfx__\n00\n"
    label = p.read_label_from_p8(text)
    assert label[5][:3] == [0, 1, 2] and label[127][15] == 15


if __name__ == "__main__":
    test_label_added_when_missing(); test_existing_label_is_read(); print("ok")
