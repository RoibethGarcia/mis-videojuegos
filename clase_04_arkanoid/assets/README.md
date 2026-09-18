# Assets de clase_04_arkanoid

Assets seleccionados para `arkanoid.py`, respetando las medidas actuales del juego:

- Ventana: 800x600
- Ladrillos: 70x20 en código; las texturas son 64x32 para escalar con `pygame.transform.scale`.
- Paleta: 120x15 en código; la textura base es 128x28 para escalar.
- Pelota: 16x16; la textura `ball.png` ya coincide con el tamaño actual.

## Texturas

Fuente principal: Tiny Break-em Pack — Screaming Brain Studios — CC0.
Fuente de fondo: Breakout graphics — Marcus/OpenGameArt — CC0.

- `textures/background.png`
- `textures/ball.png`
- `textures/paddle.png`
- `textures/brick_red.png`
- `textures/brick_orange.png`
- `textures/brick_yellow.png`
- `textures/brick_green.png`
- `textures/brick_texture_01.png`
- `textures/brick_texture_02.png`
- `textures/brick_stone_01.png`

## Sonidos

Fuente: Kenney Impact Sounds — Kenney — CC0.

- `sounds/bounce_wall.ogg` — rebote contra pared/techo.
- `sounds/bounce_paddle.ogg` — rebote con la paleta.
- `sounds/hit_brick.ogg` — destrucción de ladrillo.
- `sounds/lose_life.ogg` — pérdida de vida.
- `sounds/win.ogg` — victoria.

## Licencias

Todos los assets seleccionados son CC0. La atribución no es obligatoria, pero conviene mantener los archivos de licencia para documentar el origen.

- `licenses/tiny_breakem_pack_LICENSE.txt`
- `licenses/kenney_impact_sounds_LICENSE.txt`
- `licenses/breakout_graphics_background_SOURCE.txt`
