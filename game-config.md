# Game Configuration Reference

All tunable constants for the Street Fighter game. These live in the `CONFIG` object at the top of `index.html`.

## Movement

| Constant | Default | Description |
|----------|---------|-------------|
| MOVE_SPEED | 5 | Horizontal walk speed (px/frame) |
| GROUND_Y | 500 | Y position of the ground line |
| STAGE_LEFT | 40 | Left stage boundary |
| STAGE_RIGHT | 1240 | Right stage boundary |
| PUSH_BACK | 8 | Knockback distance on hit |

## Punch

| Constant | Default | Description |
|----------|---------|-------------|
| PUNCH_STARTUP | 4 | Frames before hitbox activates |
| PUNCH_ACTIVE | 3 | Frames hitbox stays active |
| PUNCH_RECOVERY | 8 | Cooldown frames after attack |
| PUNCH_DAMAGE | 8 | Damage dealt |
| PUNCH_RANGE | 70 | Hitbox reach from character edge |

## Kick

| Constant | Default | Description |
|----------|---------|-------------|
| KICK_STARTUP | 6 | Frames before hitbox activates |
| KICK_ACTIVE | 4 | Frames hitbox stays active |
| KICK_RECOVERY | 10 | Cooldown frames after attack |
| KICK_DAMAGE | 12 | Damage dealt |
| KICK_RANGE | 90 | Hitbox reach from character edge |

## Fireball

| Constant | Default | Description |
|----------|---------|-------------|
| FIREBALL_STARTUP | 12 | Casting animation frames |
| FIREBALL_SPEED | 7 | Projectile horizontal speed (px/frame) |
| FIREBALL_DAMAGE | 14 | Damage on hit |
| FIREBALL_COOLDOWN | 45 | Minimum frames between fireballs |

## Combat

| Constant | Default | Description |
|----------|---------|-------------|
| HIT_STUN | 15 | Stun frames when hit (unblocked) |
| BLOCK_DAMAGE_MULT | 0.2 | Chip damage ratio when blocking |

## Round

| Constant | Default | Description |
|----------|---------|-------------|
| ROUND_TIME | 99 | Round duration in seconds |
| ROUNDS_TO_WIN | 2 | Rounds needed for match victory |

## Balancing Tips

- A full health bar is 100 HP
- Punch: fast but weak (100 / 8 = ~13 punches to KO)
- Kick: medium (100 / 12 = ~9 kicks to KO)
- Fireball: strong but slow startup (100 / 14 = ~7 fireballs to KO)
- Blocking reduces damage to 20% (chip), so a blocked fireball deals 2.8 damage
- HIT_STUN of 15 frames = 0.25 seconds at 60fps — enough to feel punishing but recoverable
