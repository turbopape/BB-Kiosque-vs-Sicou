---
name: street-fighter-game
description: Build a Street Fighter 2-style 2D fighting game as a single-page HTML/JS application with SVG sprites. Use this skill when the user asks to build, modify, or extend the fighting game project. Covers character movement, attacks, fireballs, health bars, hit detection, animations, game loop, and asset integration. Trigger on any mention of "fighting game", "street fighter", "the game", "fighter sprites", "fireballs", "health bars", or references to characters/moves in this project.
---

# Street Fighter 2-Style Fighting Game

A complete 2D fighting game built as a single HTML file with JavaScript canvas rendering, SVG sprite support, keyboard controls, and full game loop with health management, projectiles, and win/loss conditions.

## Project Structure

```
street-fighter-game/
├── SKILL.md                  # This file — build instructions
├── assets/                   # ALL visual assets go here
│   ├── background.svg        # Stage background (1280×720 recommended)
│   ├── player1/              # Player 1 character sprites
│   │   ├── idle.svg          # Standing idle pose
│   │   ├── walk.svg          # Walking frame
│   │   ├── punch.svg         # Punch attack pose
│   │   ├── kick.svg          # Kick attack pose
│   │   ├── fireball-pose.svg # Fireball casting pose
│   │   ├── hit.svg           # Taking damage pose
│   │   ├── block.svg         # Blocking pose
│   │   └── victory.svg       # Win pose
│   ├── player2/              # Player 2 character sprites (same filenames)
│   │   ├── idle.svg
│   │   ├── walk.svg
│   │   ├── punch.svg
│   │   ├── kick.svg
│   │   ├── fireball-pose.svg
│   │   ├── hit.svg
│   │   ├── block.svg
│   │   └── victory.svg
│   └── fx/                   # Effects
│       ├── fireball-p1.svg   # Player 1 projectile
│       ├── fireball-p2.svg   # Player 2 projectile
│       └── hit-spark.svg     # Hit impact effect
├── references/
│   └── game-config.md        # Tunable constants reference
└── index.html                # THE GAME (single file)
```

## Build Workflow

### Step 0: Check for Assets

Before writing ANY game code, check the `assets/` folder:

```bash
echo "=== Checking assets ==="
for dir in assets assets/player1 assets/player2 assets/fx; do
  if [ -d "$dir" ]; then
    echo "✅ $dir/ exists"
    ls -1 "$dir"/*.svg 2>/dev/null || echo "   ⚠️  No SVGs found in $dir"
  else
    echo "❌ MISSING: $dir/"
  fi
done
```

**If assets are missing**, prompt the user:

> I need SVG assets before building the game. Please provide:
>
> **Required (minimum viable):**
> - `assets/background.svg` — Stage background (1280×720)
> - `assets/player1/idle.svg` — Player 1 standing pose
> - `assets/player2/idle.svg` — Player 2 standing pose
>
> **Recommended (full experience):**
> - `assets/player1/{idle,walk,punch,kick,fireball-pose,hit,block,victory}.svg`
> - `assets/player2/{idle,walk,punch,kick,fireball-pose,hit,block,victory}.svg`
> - `assets/fx/{fireball-p1,fireball-p2,hit-spark}.svg`
>
> Drop the files into the `assets/` folder and I'll wire them up.
> If you want placeholder rectangles to test mechanics first, just say "use placeholders".

**If user says "use placeholders"**, generate colored rectangle placeholders with labels so the game is playable immediately, and the user can swap in real SVGs later without code changes.

### Step 1: Game Canvas & Rendering Setup

Build `index.html` as a **single self-contained file** (HTML + CSS + JS, no external deps).

```
Canvas size: 1280 × 720 (16:9)
Rendering: HTML5 Canvas 2D context
Target FPS: 60 (use requestAnimationFrame)
Scaling: CSS object-fit: contain for responsive display
```

**Rendering pipeline (each frame):**
1. Draw background (SVG rendered to offscreen canvas once, then blitted)
2. Draw Player 1 sprite (current animation frame)
3. Draw Player 2 sprite (current animation frame, horizontally flipped if facing left)
4. Draw active fireballs
5. Draw hit spark effects
6. Draw HUD (health bars, round counter, timer)

**SVG Loading Strategy:**
- Preload ALL SVGs into `Image` objects at startup
- Show a loading screen with progress bar until all assets are ready
- Cache SVGs on offscreen canvases for performance
- Flip sprites horizontally via `ctx.scale(-1, 1)` when facing left

```javascript
// SVG preloader pattern
const ASSETS = {
  bg: 'assets/background.svg',
  p1: {
    idle: 'assets/player1/idle.svg',
    walk: 'assets/player1/walk.svg',
    punch: 'assets/player1/punch.svg',
    kick: 'assets/player1/kick.svg',
    fireballPose: 'assets/player1/fireball-pose.svg',
    hit: 'assets/player1/hit.svg',
    block: 'assets/player1/block.svg',
    victory: 'assets/player1/victory.svg',
  },
  p2: { /* same keys, player2 paths */ },
  fx: {
    fireballP1: 'assets/fx/fireball-p1.svg',
    fireballP2: 'assets/fx/fireball-p2.svg',
    hitSpark: 'assets/fx/hit-spark.svg',
  }
};

function preloadAssets(assetMap) {
  const entries = flattenAssetMap(assetMap);
  let loaded = 0;
  return Promise.all(entries.map(([key, src]) =>
    new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => { loaded++; updateLoadingBar(loaded, entries.length); resolve([key, img]); };
      img.onerror = () => resolve([key, null]); // graceful fallback
      img.src = src;
    })
  ));
}
```

### Step 2: Character System

Each fighter is a state machine:

```
STATES: idle | walking | punching | kicking | fireball | hit | blocking | victory | defeat
```

**Character data structure:**
```javascript
const createFighter = (playerNum, startX, facingRight) => ({
  x: startX,
  y: GROUND_Y,             // ground level (canvas height - character height - floor offset)
  width: 120,              // hitbox width
  height: 200,             // hitbox height
  facingRight,
  velocityX: 0,
  velocityY: 0,

  // State
  state: 'idle',
  stateTimer: 0,           // frames remaining in current state
  health: 100,
  maxHealth: 100,

  // Combat
  canAct: true,            // false during attack recovery
  isAttacking: false,
  attackHitbox: null,       // {x, y, w, h} relative to character
  attackDamage: 0,
  hasHitThisAttack: false, // prevent multi-hit per attack

  // Animation
  currentSprite: 'idle',
  spriteFlash: 0,          // damage flash timer
});
```

**Movement constants (tune these for feel):**
```javascript
const CONFIG = {
  MOVE_SPEED: 5,           // pixels per frame
  GROUND_Y: 500,           // ground line Y position
  PUSH_BACK: 8,            // knockback on hit (pixels)
  STAGE_LEFT: 40,          // left boundary
  STAGE_RIGHT: 1240,       // right boundary

  // Attack frame data
  PUNCH_STARTUP: 4,        // frames before hitbox appears
  PUNCH_ACTIVE: 3,         // frames hitbox is active
  PUNCH_RECOVERY: 8,       // frames of cooldown
  PUNCH_DAMAGE: 8,
  PUNCH_RANGE: 70,         // hitbox reach

  KICK_STARTUP: 6,
  KICK_ACTIVE: 4,
  KICK_RECOVERY: 10,
  KICK_DAMAGE: 12,
  KICK_RANGE: 90,

  FIREBALL_STARTUP: 12,    // frames of casting animation
  FIREBALL_SPEED: 7,       // projectile speed
  FIREBALL_DAMAGE: 14,
  FIREBALL_COOLDOWN: 45,   // frames before next fireball

  HIT_STUN: 15,            // frames character is stunned when hit
  BLOCK_DAMAGE_MULT: 0.2,  // chip damage multiplier when blocking

  ROUND_TIME: 99,          // seconds per round
  ROUNDS_TO_WIN: 2,        // best of 3
};
```

### Step 3: Input Handling

**Control scheme:**

| Action       | Player 1     | Player 2       |
|------------- |------------- |--------------- |
| Move Left    | `A`          | `ArrowLeft`    |
| Move Right   | `D`          | `ArrowRight`   |
| Punch        | `F`          | `Numpad1` or `J`  |
| Kick         | `G`          | `Numpad2` or `K`  |
| Fireball     | `H`          | `Numpad3` or `L`  |
| Block        | `S`          | `ArrowDown`    |

**Input implementation:**
```javascript
// Track pressed keys in a Set for simultaneous key support
const keysDown = new Set();
window.addEventListener('keydown', e => keysDown.add(e.code));
window.addEventListener('keyup', e => keysDown.delete(e.code));

// Read inputs each frame (NOT in event handlers)
function readInputs(playerNum) {
  if (playerNum === 1) {
    return {
      left: keysDown.has('KeyA'),
      right: keysDown.has('KeyD'),
      punch: keysDown.has('KeyF'),
      kick: keysDown.has('KeyG'),
      fireball: keysDown.has('KeyH'),
      block: keysDown.has('KeyS'),
    };
  } else {
    return {
      left: keysDown.has('ArrowLeft') ,
      right: keysDown.has('ArrowRight'),
      punch: keysDown.has('KeyJ') || keysDown.has('Numpad1'),
      kick: keysDown.has('KeyK') || keysDown.has('Numpad2'),
      fireball: keysDown.has('KeyL') || keysDown.has('Numpad3'),
      block: keysDown.has('ArrowDown'),
    };
  }
}
```

**Important: Prevent default on game keys** so the page doesn't scroll:
```javascript
window.addEventListener('keydown', e => {
  const gameKeys = ['KeyA','KeyD','KeyS','KeyF','KeyG','KeyH',
    'ArrowLeft','ArrowRight','ArrowDown','KeyJ','KeyK','KeyL',
    'Numpad1','Numpad2','Numpad3'];
  if (gameKeys.includes(e.code)) e.preventDefault();
});
```

### Step 4: State Machine & Actions

```javascript
function updateFighter(fighter, input, opponent, fireballs) {
  fighter.stateTimer--;

  // Auto-face opponent
  fighter.facingRight = fighter.x < opponent.x;

  switch (fighter.state) {
    case 'idle':
    case 'walking':
      fighter.canAct = true;
      // Movement
      if (input.left) { fighter.x -= CONFIG.MOVE_SPEED; fighter.state = 'walking'; }
      else if (input.right) { fighter.x += CONFIG.MOVE_SPEED; fighter.state = 'walking'; }
      else { fighter.state = 'idle'; }

      // Actions (priority: fireball > kick > punch > block)
      if (input.fireball && fighter.canAct) startFireball(fighter, fireballs);
      else if (input.kick && fighter.canAct) startKick(fighter);
      else if (input.punch && fighter.canAct) startPunch(fighter);
      else if (input.block) fighter.state = 'blocking';

      // Clamp to stage bounds
      fighter.x = Math.max(CONFIG.STAGE_LEFT, Math.min(CONFIG.STAGE_RIGHT - fighter.width, fighter.x));
      break;

    case 'punching':
      handleAttackFrames(fighter, 'punch');
      break;
    case 'kicking':
      handleAttackFrames(fighter, 'kick');
      break;
    case 'fireball':
      if (fighter.stateTimer <= 0) {
        fighter.state = 'idle';
        fighter.canAct = true;
      }
      break;
    case 'hit':
      if (fighter.stateTimer <= 0) { fighter.state = 'idle'; fighter.canAct = true; }
      break;
    case 'blocking':
      if (!input.block) fighter.state = 'idle';
      break;
  }

  // Update sprite key based on state
  fighter.currentSprite = stateToSprite(fighter.state);
}
```

### Step 5: Fireball System

```javascript
const fireballs = []; // shared array

function spawnFireball(fighter) {
  fireballs.push({
    x: fighter.x + (fighter.facingRight ? fighter.width : -30),
    y: fighter.y + fighter.height * 0.4,
    width: 60,
    height: 30,
    speed: fighter.facingRight ? CONFIG.FIREBALL_SPEED : -CONFIG.FIREBALL_SPEED,
    damage: CONFIG.FIREBALL_DAMAGE,
    owner: fighter,         // reference to avoid self-hit
    sprite: fighter === p1 ? 'fireballP1' : 'fireballP2',
    alive: true,
  });
}

function updateFireballs() {
  for (const fb of fireballs) {
    fb.x += fb.speed;
    // Off-screen kill
    if (fb.x < -100 || fb.x > 1380) fb.alive = false;
  }
  // Remove dead fireballs
  for (let i = fireballs.length - 1; i >= 0; i--) {
    if (!fireballs[i].alive) fireballs.splice(i, 1);
  }
}
```

### Step 6: Hit Detection

```javascript
function checkCollisions(attacker, defender, fireballs) {
  // Melee hit detection
  if (attacker.isAttacking && !attacker.hasHitThisAttack && attacker.attackHitbox) {
    const hb = getWorldHitbox(attacker);
    if (rectsOverlap(hb, getBodyBox(defender))) {
      applyHit(defender, attacker.attackDamage);
      attacker.hasHitThisAttack = true;
      spawnHitSpark(hb.x + hb.w / 2, hb.y + hb.h / 2);
    }
  }

  // Fireball hit detection
  for (const fb of fireballs) {
    if (fb.owner !== defender && fb.alive) {
      if (rectsOverlap(fb, getBodyBox(defender))) {
        applyHit(defender, fb.damage);
        fb.alive = false;
        spawnHitSpark(fb.x, fb.y);
      }
    }
  }
}

function applyHit(fighter, damage) {
  if (fighter.state === 'blocking') {
    damage *= CONFIG.BLOCK_DAMAGE_MULT;
    fighter.x += (fighter.facingRight ? -CONFIG.PUSH_BACK / 2 : CONFIG.PUSH_BACK / 2);
  } else {
    fighter.state = 'hit';
    fighter.stateTimer = CONFIG.HIT_STUN;
    fighter.canAct = false;
    fighter.x += (fighter.facingRight ? -CONFIG.PUSH_BACK : CONFIG.PUSH_BACK);
  }
  fighter.health = Math.max(0, fighter.health - damage);
  fighter.spriteFlash = 6; // frames of white flash
}

function rectsOverlap(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x &&
         a.y < b.y + b.h && a.y + a.h > b.y;
}
```

### Step 7: HUD — Health Bars, Timer, Rounds

```javascript
function drawHUD(ctx) {
  const BAR_W = 480, BAR_H = 30, BAR_Y = 30, BAR_MARGIN = 40;

  // Player 1 health bar (left-aligned, drains right-to-left)
  drawHealthBar(ctx, BAR_MARGIN, BAR_Y, BAR_W, BAR_H, p1.health, p1.maxHealth, '#e63946', false);

  // Player 2 health bar (right-aligned, drains left-to-right)
  drawHealthBar(ctx, 1280 - BAR_MARGIN - BAR_W, BAR_Y, BAR_W, BAR_H, p2.health, p2.maxHealth, '#457b9d', true);

  // Timer (center)
  ctx.fillStyle = '#fff';
  ctx.font = 'bold 48px monospace';
  ctx.textAlign = 'center';
  ctx.fillText(String(Math.ceil(roundTimer)), 640, 60);

  // Round indicators (dots under health bars)
  drawRoundDots(ctx, p1Wins, 200, 75);
  drawRoundDots(ctx, p2Wins, 1080, 75);

  // Player names
  ctx.font = 'bold 20px sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('PLAYER 1', BAR_MARGIN, BAR_Y - 8);
  ctx.textAlign = 'right';
  ctx.fillText('PLAYER 2', 1280 - BAR_MARGIN, BAR_Y - 8);
}

function drawHealthBar(ctx, x, y, w, h, health, max, color, rightAligned) {
  const ratio = health / max;
  // Background
  ctx.fillStyle = '#333';
  ctx.fillRect(x, y, w, h);
  // Health fill
  ctx.fillStyle = color;
  if (rightAligned) {
    ctx.fillRect(x + w * (1 - ratio), y, w * ratio, h);
  } else {
    ctx.fillRect(x, y, w * ratio, h);
  }
  // Border
  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 2;
  ctx.strokeRect(x, y, w, h);
}
```

### Step 8: Game Loop & Round Management

```javascript
// Game states: 'loading' | 'title' | 'roundStart' | 'fighting' | 'roundEnd' | 'matchEnd'
let gameState = 'loading';

function gameLoop(timestamp) {
  const dt = timestamp - lastTimestamp;
  lastTimestamp = timestamp;

  switch (gameState) {
    case 'loading':
      drawLoadingScreen();
      break;
    case 'title':
      drawTitleScreen(); // "PRESS START" / any key
      break;
    case 'roundStart':
      drawRoundAnnounce(); // "ROUND 1 — FIGHT!"
      if (announceTimer-- <= 0) gameState = 'fighting';
      break;
    case 'fighting':
      updateFighters();
      updateFireballs();
      checkAllCollisions();
      updateTimer(dt);
      drawEverything();
      checkRoundEnd();
      break;
    case 'roundEnd':
      drawRoundResult(); // "PLAYER 1 WINS" / "DRAW"
      if (resultTimer-- <= 0) startNextRound();
      break;
    case 'matchEnd':
      drawMatchResult(); // final victory screen
      // any key to restart
      break;
  }

  requestAnimationFrame(gameLoop);
}
```

### Step 9: Visual Polish

**Screen shake on heavy hits:**
```javascript
let shakeIntensity = 0;
function applyScreenShake() {
  if (shakeIntensity > 0) {
    ctx.save();
    ctx.translate(
      (Math.random() - 0.5) * shakeIntensity,
      (Math.random() - 0.5) * shakeIntensity
    );
    shakeIntensity *= 0.85; // decay
    if (shakeIntensity < 0.5) shakeIntensity = 0;
  }
}
// call ctx.restore() after drawing
```

**Hit spark particles:**
```javascript
const particles = [];
function spawnHitSpark(x, y) {
  for (let i = 0; i < 8; i++) {
    particles.push({
      x, y,
      vx: (Math.random() - 0.5) * 10,
      vy: (Math.random() - 0.5) * 10,
      life: 12,
      color: ['#fff', '#ff0', '#f80'][Math.floor(Math.random() * 3)],
    });
  }
  shakeIntensity = 6;
}
```

**Damage flash:**
When `fighter.spriteFlash > 0`, draw the sprite normally, then overdraw with `ctx.globalCompositeOperation = 'source-atop'` using white at 50% opacity, then restore composite mode.

### Step 10: Sound (Optional Enhancement)

If the user wants sound, use the Web Audio API to generate retro sound effects procedurally (no external files needed):

```javascript
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function playHitSound() {
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = 'square';
  osc.frequency.setValueAtTime(200, audioCtx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(80, audioCtx.currentTime + 0.1);
  gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.15);
  osc.connect(gain).connect(audioCtx.destination);
  osc.start(); osc.stop(audioCtx.currentTime + 0.15);
}
```

Suggested sounds: `playHitSound()`, `playFireballSound()`, `playBlockSound()`, `playRoundAnnounce()`, `playKO()`.

## Asset Guidelines

### SVG Sprite Requirements

- **Recommended size**: 200×300px viewBox for characters, 100×50px for fireballs
- **Orientation**: All character sprites should face RIGHT; the engine flips for Player 2
- **Transparency**: Use transparent backgrounds (no `<rect>` fill behind character)
- **Consistent anchor**: Feet should be at the bottom of the viewBox so ground alignment works
- **Color coding**: Player 1 sprites in warm tones (reds/oranges), Player 2 in cool tones (blues/teals) is conventional but not required
- **Naming**: Must match the filenames listed in the project structure above exactly

### Placeholder Mode

When assets aren't available yet, the game generates colored rectangles:
- Player 1: Red rectangle with "P1" label
- Player 2: Blue rectangle with "P2" label
- Fireballs: Yellow (P1) / Cyan (P2) circles
- Background: Dark gradient with grid lines

Placeholders are replaced automatically when real SVGs are dropped into `assets/`.

## Customization Hooks

All gameplay constants live in the `CONFIG` object at the top of the file. To tune the game:

- **Faster gameplay**: Decrease startup frames, increase MOVE_SPEED
- **More strategic**: Increase recovery frames, reduce FIREBALL_SPEED
- **Beginner friendly**: Increase HIT_STUN, reduce FIREBALL_COOLDOWN
- **Arcade feel**: Add chip damage, increase PUSH_BACK, add corner pressure

## Extending the Game

Ideas the user may ask for — handle these within the same single-file architecture:

- **Jump / Crouch**: Add gravity, jump velocity, crouch state + low attacks
- **Special moves**: Motion input detection (e.g., down-forward + punch = uppercut)
- **AI opponent**: Simple state machine AI: approach, attack at range, block on reaction
- **Character select**: Title screen with character portraits, different CONFIG per character
- **Combos**: Cancel system — allow chaining punch → kick → fireball within frame windows
- **Mobile controls**: On-screen touch buttons (d-pad + action buttons)
- **Online multiplayer**: WebRTC data channel for peer-to-peer input sync

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| SVGs not showing | Path mismatch or CORS | Verify paths, serve via local HTTP server |
| Characters slide through each other | No push collision | Add body-to-body overlap check that pushes fighters apart |
| Fireball goes wrong direction | facingRight not set | Ensure auto-face runs before fireball spawn |
| Health doesn't update visually | Drawing stale value | Confirm drawHUD runs every frame after state update |
| Keys feel laggy | Using keypress instead of keydown | Use keydown/keyup with Set-based tracking |
| Game runs fast/slow on different monitors | Using setTimeout | Must use requestAnimationFrame + delta time |
