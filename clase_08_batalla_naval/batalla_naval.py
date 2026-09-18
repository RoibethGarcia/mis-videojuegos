import random
import sys

import pygame


pygame.init()

TAM = 36
MARGEN = 10
SEPARACION = 40
FILAS = 10
COLUMNAS = 10
ANCHO_TABLERO = COLUMNAS * TAM
ALTO_TABLERO = FILAS * TAM
ANCHO = MARGEN * 2 + ANCHO_TABLERO * 2 + SEPARACION
ALTO = 520
FPS = 30

AGUA = "·"
BARCO = "B"
FALLADO = "X"
TOCADO = "T"
HUNDIDO = "H"
TAMANIOS_BARCOS = (5, 4, 3, 3, 2)

COLOR_FONDO = (15, 18, 30)
COLOR_AGUA = (30, 80, 150)
COLOR_AGUA_DISPARADA = (55, 65, 80)
COLOR_BARCO = (90, 170, 120)
COLOR_TOCADO = (225, 75, 65)
COLOR_HUNDIDO = (130, 35, 35)
COLOR_LINEA = (15, 30, 60)
COLOR_TEXTO = (240, 240, 240)
COLOR_AVISO = (255, 220, 120)

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Batalla naval contra IA")
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont("arial", 18)
fuente_grande = pygame.font.SysFont("arial", 30)

OX_JUGADOR = MARGEN
OY_TABLEROS = 55
OX_ENEMIGO = MARGEN + ANCHO_TABLERO + SEPARACION


def crear_tablero():
    """Crea una matriz de 10x10 llena de agua."""
    return [[AGUA] * COLUMNAS for _ in range(FILAS)]


def crear_juego():
    jugador = crear_tablero()
    enemigo = crear_tablero()
    barcos_jugador = colocar_barcos(jugador)
    barcos_enemigo = colocar_barcos(enemigo)

    return {
        "jugador": jugador,
        "enemigo": enemigo,
        "barcos_jugador": barcos_jugador,
        "barcos_enemigo": barcos_enemigo,
        "disparos_jugador": crear_tablero(),
        "disparos_enemigo": crear_tablero(),
        "turno_jugador": True,
        "disparos_realizados": 0,
        "mensaje": "Dispará en el tablero enemigo.",
        "finalizado": False,
        "ganador": "",
    }


def colocar_barcos(tablero, tamanios=TAMANIOS_BARCOS):
    """Coloca barcos aleatoriamente sin superponerlos y devuelve sus celdas."""
    barcos = []

    for tamanio in tamanios:
        colocado = False

        while not colocado:
            horizontal = random.choice([True, False])

            if horizontal:
                fila = random.randint(0, FILAS - 1)
                col = random.randint(0, COLUMNAS - tamanio)
                celdas = [(fila, col + i) for i in range(tamanio)]
            else:
                fila = random.randint(0, FILAS - tamanio)
                col = random.randint(0, COLUMNAS - 1)
                celdas = [(fila + i, col) for i in range(tamanio)]

            if all(tablero[fila][col] == AGUA for fila, col in celdas):
                for fila, col in celdas:
                    tablero[fila][col] = BARCO
                barcos.append(celdas)
                colocado = True

    return barcos


def quedan_barcos(tablero):
    """Indica si todavía queda alguna celda de barco en pie."""
    return any(BARCO in fila for fila in tablero)


def barco_hundido(barco, tablero):
    """Un barco está hundido cuando ninguna de sus celdas sigue marcada como B."""
    return all(tablero[fila][col] != BARCO for fila, col in barco)


def marcar_hundido(barco, tablero_disparos):
    for fila, col in barco:
        tablero_disparos[fila][col] = HUNDIDO


def revisar_hundimiento(fila, col, barcos, tablero, tablero_disparos):
    """Marca un barco como hundido si el disparo completó todas sus celdas."""
    for barco in barcos:
        if (fila, col) in barco and barco_hundido(barco, tablero):
            marcar_hundido(barco, tablero_disparos)
            return True
    return False


def disparar(tablero_objetivo, tablero_disparos, fila, col, barcos):
    """Procesa un disparo y devuelve el resultado textual."""
    if tablero_disparos[fila][col] != AGUA:
        return "repetido"

    if tablero_objetivo[fila][col] == BARCO:
        tablero_objetivo[fila][col] = TOCADO
        tablero_disparos[fila][col] = TOCADO

        if revisar_hundimiento(fila, col, barcos, tablero_objetivo, tablero_disparos):
            return "hundido"
        return "tocado"

    tablero_disparos[fila][col] = FALLADO
    return "agua"


def celda_desde_mouse(mx, my, ox, oy):
    col = (mx - ox) // TAM
    fila = (my - oy) // TAM

    if 0 <= fila < FILAS and 0 <= col < COLUMNAS:
        return fila, col

    return None


def disparo_ia(juego):
    """La IA simple dispara a una celda aleatoria donde no haya disparado antes."""
    opciones = [
        (fila, col)
        for fila in range(FILAS)
        for col in range(COLUMNAS)
        if juego["disparos_jugador"][fila][col] == AGUA
    ]

    if not opciones:
        juego["turno_jugador"] = True
        return

    fila, col = random.choice(opciones)
    resultado = disparar(
        juego["jugador"],
        juego["disparos_jugador"],
        fila,
        col,
        juego["barcos_jugador"],
    )

    if resultado == "agua":
        juego["mensaje"] = "La IA falló. Tu turno."
        juego["turno_jugador"] = True
    elif resultado == "hundido":
        juego["mensaje"] = "La IA hundió uno de tus barcos. Sigue tirando."
    else:
        juego["mensaje"] = "La IA tocó un barco. Sigue tirando."

    if not quedan_barcos(juego["jugador"]):
        juego["finalizado"] = True
        juego["ganador"] = "ia"
        juego["mensaje"] = "Perdiste. La IA hundió todos tus barcos."


def color_celda(celda, mostrar_barcos=False, celda_real=AGUA):
    if celda == FALLADO:
        return COLOR_AGUA_DISPARADA
    if celda == TOCADO:
        return COLOR_TOCADO
    if celda == HUNDIDO:
        return COLOR_HUNDIDO
    if mostrar_barcos and celda_real == BARCO:
        return COLOR_BARCO
    return COLOR_AGUA


def dibujar_tablero(tablero_disparos, ox, oy, titulo, tablero_real=None, mostrar_barcos=False):
    pantalla.blit(fuente.render(titulo, True, COLOR_TEXTO), (ox, oy - 30))

    for fila in range(FILAS):
        for col in range(COLUMNAS):
            celda_disparo = tablero_disparos[fila][col]
            celda_real = tablero_real[fila][col] if tablero_real is not None else AGUA
            color = color_celda(celda_disparo, mostrar_barcos, celda_real)
            rect = pygame.Rect(ox + col * TAM, oy + fila * TAM, TAM - 2, TAM - 2)
            pygame.draw.rect(pantalla, color, rect)
            pygame.draw.rect(pantalla, COLOR_LINEA, rect, 1)

            if celda_disparo == FALLADO:
                dibujar_texto_centrado("X", rect, COLOR_TEXTO)
            elif celda_disparo == TOCADO:
                dibujar_texto_centrado("T", rect, COLOR_TEXTO)
            elif celda_disparo == HUNDIDO:
                dibujar_texto_centrado("H", rect, COLOR_TEXTO)


def dibujar_texto_centrado(texto, rect, color):
    superficie = fuente.render(texto, True, color)
    texto_rect = superficie.get_rect(center=rect.center)
    pantalla.blit(superficie, texto_rect)


def dibujar_info(juego):
    if juego["finalizado"]:
        if juego["ganador"] == "jugador":
            titulo = f"¡Ganaste en {juego['disparos_realizados']} disparos!"
        else:
            titulo = "Perdiste."
        superficie = fuente_grande.render(titulo, True, COLOR_AVISO)
        pantalla.blit(superficie, (MARGEN, 430))
        ayuda = "Presioná R para reiniciar o ESC para salir."
    else:
        turno = "Tu turno" if juego["turno_jugador"] else "Turno de la IA"
        ayuda = f"{turno} | Disparos: {juego['disparos_realizados']}"

    pantalla.blit(fuente.render(juego["mensaje"], True, COLOR_TEXTO), (MARGEN, 465))
    pantalla.blit(fuente.render(ayuda, True, COLOR_TEXTO), (MARGEN, 490))


def dibujar(juego):
    pantalla.fill(COLOR_FONDO)
    dibujar_tablero(
        juego["disparos_jugador"],
        OX_JUGADOR,
        OY_TABLEROS,
        "Tu tablero",
        juego["jugador"],
        mostrar_barcos=True,
    )
    dibujar_tablero(
        juego["disparos_enemigo"],
        OX_ENEMIGO,
        OY_TABLEROS,
        "Tablero enemigo",
    )
    dibujar_info(juego)
    pygame.display.flip()


def manejar_disparo_jugador(juego, fila, col):
    resultado = disparar(
        juego["enemigo"],
        juego["disparos_enemigo"],
        fila,
        col,
        juego["barcos_enemigo"],
    )

    if resultado == "repetido":
        juego["mensaje"] = "Ya disparaste a esa celda. Elegí otra."
        return

    juego["disparos_realizados"] += 1

    if resultado == "agua":
        juego["mensaje"] = "Agua. Ahora juega la IA."
        juego["turno_jugador"] = False
    elif resultado == "hundido":
        juego["mensaje"] = "¡Hundiste un barco! Volvés a tirar."
    else:
        juego["mensaje"] = "¡Tocado! Volvés a tirar."

    if not quedan_barcos(juego["enemigo"]):
        juego["finalizado"] = True
        juego["ganador"] = "jugador"
        juego["mensaje"] = "Hundiste todos los barcos enemigos."


def main():
    juego = crear_juego()
    ejecutando = True

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    ejecutando = False
                elif evento.key == pygame.K_r and juego["finalizado"]:
                    juego = crear_juego()
            elif (
                evento.type == pygame.MOUSEBUTTONDOWN
                and juego["turno_jugador"]
                and not juego["finalizado"]
            ):
                celda = celda_desde_mouse(*evento.pos, OX_ENEMIGO, OY_TABLEROS)
                if celda is not None:
                    manejar_disparo_jugador(juego, *celda)

        if not juego["turno_jugador"] and not juego["finalizado"]:
            pygame.time.wait(350)
            disparo_ia(juego)

        dibujar(juego)
        reloj.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
