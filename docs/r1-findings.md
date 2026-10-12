# R1 / PICO-8 findings (PICO-8 0.2.7, macOS)

Binary: /Applications/pico-8/PICO-8.app/Contents/MacOS/pico8

- Headless export works: `pico8 -export "out/index.html" cart.p8` -> out/index.html + out/index.js.
- `-f` writes a subfolder (out/index_html/...), not a flat layout: do not pass it.
- Export fails with "please capture a label first" if the cart has no __label__ section
  (a .p8.png cart already has one). Script must inject a label into .p8 carts that lack one.
- Default shell exposes `pico8_buttons[0]` bitfield: 1 left, 2 right, 4 up, 8 down, 16 O, 32 X, 64 menu.
  VERIFIED in a browser: setting bits drives btn()/btnp() in the running cart. Use this for touch/wheel/side.
- Synthesized KeyboardEvent dispatched on window did NOT register (not needed; use the bitfield).
- Start sequence that works: `p8_create_audio_context(); p8_run_cart();` (needs a user gesture for audio).
- Cart boot is slow in a throttled browser pane (~10 s); real R1 speed unknown.
- Canvas is 128x128 and the shell stretches it; audio context state was "running" after the call.

Still to check ON THE R1 (host tools/probe.html over https, scan a QR):
- real names of wheel / side button / long-press events
- audio after tap, WebView size (expect ~240x282)
- frame rate of the exported player (pico8_state.frame_number over time)

## Confirmed ON THE R1 (probe.html)
- Wheel turned physically UP   -> window 'scrollDown'   (inverted vs. intuition)
- Wheel turned physically DOWN -> window 'scrollUp'
- Side button click            -> window 'sideClick'
- Side button hold             -> window 'longPressStart', then 'longPressEnd' on release
- Touch                        -> 'pointerdown' then 'touchstart'
Unverified: `--orientation landscape` rotation direction (wheel down = page rotated -90deg; `--landscape-flip` for +90deg) and thumb reach on the device.

Not yet reported: audio state after tap, viewport size, creationStorage, keydown, fps.
Bridge mapping: physical wheel up = Up (bit 4) => handle 'scrollDown' as Up, 'scrollUp' as Down.
