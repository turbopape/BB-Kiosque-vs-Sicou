# Nano Banana — Street Fighter Style Fighting Game

A 2D fighting game built as a single HTML file with JavaScript canvas rendering, PNG sprite support, and procedural retro sound effects. Two players battle it out locally with punches, kicks, fireballs, and blocks.

## How to Play

Open `index.html` in a browser (serve via a local HTTP server for asset loading).

### Controls

| Action     | Player 1 | Player 2         |
|------------|----------|------------------|
| Move Left  | A        | Arrow Left       |
| Move Right | D        | Arrow Right      |
| Jump       | W        | Arrow Up         |
| Block      | S        | Arrow Down       |
| Punch      | F        | J / Numpad 1     |
| Kick       | G        | K / Numpad 2     |
| Fireball   | H        | L / Numpad 3     |

### Rules

- Each round lasts 99 seconds
- First to win 2 rounds wins the match
- Blocking reduces damage to 20% (chip damage)

## Assets

Drop PNG sprites into the `assets/` folder. The game falls back to colored placeholders for any missing assets. See `asset-prompts.md` for the full list and generation prompts.

```
assets/
├── background.png
├── player1/
│   ├── idle.png, walk.png, punch.png, close-punch.png
│   ├── kick.png, fireball-pose.png, hit.png, block.png, victory.png
├── player2/
│   └── (same as player1)
└── fx/
    ├── fireball-p1.png, fireball-p2.png, hit-spark.png
```

## Configuration

All gameplay constants are in the `CONFIG` object at the top of `index.html`. See `game-config.md` for the full reference.

## Tech

- Single HTML file, no dependencies
- HTML5 Canvas 2D rendering at 1280x720
- 60 FPS via requestAnimationFrame
- Procedural retro sound effects (Web Audio API)
- Automatic placeholder sprites when assets are missing
