# Changelog

## [0.2.0] - 2026-03-04

### Added
- Sensei Jmal the karate camel referee — watches the fight, gets shocked on hits
- Roaring engine splash sound with two-note power chord finale
- Title screen 80s chiptune BGM
- Flapping birds in the sky and animated wave ripple on background
- Improved loading screen with splash backdrop and progress percentage
- BB. Kiosque cat head favicon
- Character credits on title screen (BB. Kiosque & Sensei Jmal by Elyes, Sicou by Sara)
- Mazinger Z-style flybot randomly flies across the sky with perspective scaling
- CSS preloader spinner visible during initial page load
- Match end returns to title screen instead of auto-restarting

### Fixed
- Anti-corner-trap: invincibility frames after hit recovery (45 frames with blinking)
- Corner push: blocked attacks near walls push attacker back
- Shorter hit stun (25 frames) for faster recovery

---

## [0.1.0] - 2026-03-04

### Added
- Single-file fighting game (`index.html`) with full game loop
- Two-player local multiplayer with keyboard controls
- Punch, close punch, kick, fireball, and block mechanics
- Jump with gravity physics and jump cross-ups (jump over opponent)
- Health bars, round timer, and round/match management
- Procedural retro sound effects (Web Audio API)
- PNG sprite loading with automatic placeholder fallback
- Screen shake and hit spark sprite particle effects
- Pause/help screen (Space bar) with controls overlay
- Fireball limit (3 per round) with fiery HUD token indicators
- Splash screen with fade-in/hold/fade-out on game start (skippable)
- Flashy yellow title menu replacing old text title
- Idle breathing animation via subtle sprite scaling
- Defeat and victory pose sprites
- Block stun and heavier hit stun for dramatic impact
- Longer round end pause (6 seconds)
- Player 2 (Sicou) custom ice-cream-cone rainbow character sprites
- Asset prompts documentation (`asset-prompts.md`)
- Game configuration reference (`game-config.md`)
- Background removal script (`green2alpha.py`) with luminosity normalization

### Fixed
- Asset loader preserves loaded PNGs instead of overwriting with placeholders
- Close punch triggers at short range (gap < 30px)
- Fireball hitbox smaller than visual for jumpable fireballs
- P2 sprite flipping corrected (P2 sprites face left by default)
- Damage flash isolated to offscreen canvas (no screen flicker)
- Hit spark sprite now visible (larger, longer life, upward drift)
