import sys

import pygame


pygame.init()

ANCHO, ALTO = 800, 600
FPS = 60

COLOR_FONDO = (15, 15, 30)
COLOR_PALETA = (90, 180, 255)
COLOR_PELOTA = (255, 255, 255)
COLORES_LADRILLOS = [
    (255, 100, 100),
    (255, 150, 90),
    (255, 210, 90),
    (120, 220, 120),
]
COLOR_TEXTO = (240, 240, 240)

pantalla = pygame.display.set_mode((ANCHO, ALTO))
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont(None, 48)

pala = pygame.Rect(ANCHO // 2 - 60, ALTO - 40, 120, 15)
pelota = pygame.Rect(ANCHO // 2 - 8, ALTO // 2, 16, 16)
vel_x, vel_y = 5, -5

FILAS, COLS = 4, 10
ladrillos = []

for fila in range(FILAS):
    for col in range(COLS):
        ladrillo = pygame.Rect(col * 80 + 5, fila * 30 + 40, 70, 20)
        ladrillos.append(ladrillo)

vidas = 3
puntaje = 0
ladrillos_destruidos = 0
mensaje_final = ""
ejecutando = True


def reiniciar_pelota():
    """Devuelve la pelota al centro después de perder una vida."""
    pelota.center = (ANCHO // 2, ALTO // 2)
    return 5, -5


def aumentar_velocidad(valor):
    """Aumenta la velocidad conservando la dirección actual."""
    if valor > 0:
        return valor + 1
    return valor - 1


def mostrar_mensaje(texto):
    """Muestra un mensaje final por un momento antes de cerrar."""
    pantalla.fill(COLOR_FONDO)
    superficie_texto = fuente.render(texto, True, COLOR_TEXTO)
    rect_texto = superficie_texto.get_rect(center=(ANCHO // 2, ALTO // 2))
    pantalla.blit(superficie_texto, rect_texto)
    pygame.display.flip()
    pygame.time.wait(2000)


while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    # La paleta sigue al mouse.
    pala.x = pygame.mouse.get_pos()[0] - pala.width // 2
    pala.x = max(0, min(ANCHO - pala.width, pala.x))

    # Mover la pelota.
    pelota.x += vel_x
    pelota.y += vel_y

    # Rebotes con paredes y techo.
    if pelota.left <= 0 or pelota.right >= ANCHO:
        vel_x *= -1

    if pelota.top <= 0:
        vel_y *= -1

    # Rebote con la paleta.
    if pelota.colliderect(pala) and vel_y > 0:
        vel_y *= -1
        pelota.bottom = pala.top

    # Destruir ladrillos.
    for ladrillo in ladrillos[:]:
        if pelota.colliderect(ladrillo):
            ladrillos.remove(ladrillo)
            vel_y *= -1
            puntaje += 10
            ladrillos_destruidos += 1

            if ladrillos_destruidos % 5 == 0:
                vel_x = aumentar_velocidad(vel_x)
                vel_y = aumentar_velocidad(vel_y)

            break

    # Condición de victoria.
    if len(ladrillos) == 0:
        mensaje_final = "¡Ganaste!"
        ejecutando = False

    # Perder vida.
    if pelota.bottom >= ALTO:
        vidas -= 1

        if vidas == 0:
            mensaje_final = "Perdiste"
            ejecutando = False
        else:
            vel_x, vel_y = reiniciar_pelota()

    # Dibujar.
    pantalla.fill(COLOR_FONDO)
    pygame.draw.rect(pantalla, COLOR_PALETA, pala)
    pygame.draw.rect(pantalla, COLOR_PELOTA, pelota)

    for indice, ladrillo in enumerate(ladrillos):
        color = COLORES_LADRILLOS[indice // COLS]
        pygame.draw.rect(pantalla, color, ladrillo)

    pygame.display.set_caption(
        f"Arkanoid - Vidas: {vidas} - Puntaje: {puntaje} - Ladrillos: {len(ladrillos)}"
    )
    pygame.display.flip()
    reloj.tick(FPS)

if mensaje_final:
    mostrar_mensaje(mensaje_final)

pygame.quit()
sys.exit()
