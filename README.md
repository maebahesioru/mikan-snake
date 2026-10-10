# 🐍 Mikan Snake

A classic snake game built with **pygame** for [Hack Club Snek](https://snek.hackclub.com/).

**All graphics are drawn with code** — no image assets, no AI-generated art. Sound effects are generated with math (sine waves), not audio files.

## Features (5)

1. **Classic snake gameplay** — grow, score, speed increases as you eat
2. **Wrap-around walls** — snake wraps around edges (strategic depth)
3. **Particle effects** — burst of particles when eating food
4. **Pause** — P key to pause/resume
5. **High score persistence** — saved to JSON, survives restarts
6. **Generated sound effects** — eat/die beeps synthesized with numpy

## How to run

```bash
# From source
python3 game.py

# Or the standalone binary (no Python needed)
./dist/MikanSnake
```

## Controls

| Key | Action |
|---|---|
| Arrow keys / WASD | Move |
| P | Pause |
| Space | Restart (after game over) |

## Build (standalone executable)

```bash
python3 -m venv buildenv
./buildenv/bin/pip install pygame pyinstaller
./buildenv/bin/pyinstaller --onefile --windowed --name MikanSnake game.py
# → dist/MikanSnake
```

## Verified (2026-10-10)

```
✅ Logic: 300 steps simulated without crash
✅ Rendering: HUD/snake/food/particles draw without errors
✅ High score: save/load round-trip (123 → 123)
✅ Binary: dist/MikanSnake launches and exits cleanly (exit 0)
✅ Screenshot: captured from headless run
```

## Design notes

- **Zero external assets**: the entire visual identity (orange cat-snake, dark theme) is drawn with `pygame.draw` primitives — circles, rounded rects, lines
- **Generated audio**: sine-wave synthesis with exponential decay envelope, so no .wav files ship with the game
- **Deterministic grid**: 30×22 cells at 24px

## License

MIT

---

Built for [Snek](https://snek.hackclub.com/) (Hack Club) — learn pygame, ship a game, get plushies.
