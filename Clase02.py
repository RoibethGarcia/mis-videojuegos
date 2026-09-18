import random
import sys

import pygame


ANCHO, ALTO = 600, 600
CELDA = 30
COLUMNAS = ANCHO // CELDA
FILAS = ALTO // CELDA
FPS = 10

COLOR_FONDO = (10, 10, 15)
COLOR_SERPIENTE = (0, 220, 60)
COLOR_MANZANA = (230, 40, 40)


def manzana_nueva(serpiente):
    """Crea una manzana en una celda libre."""
    while True:
        manzana = (
            random.randint(0, COLUMNAS - 1),
            random.randint(0, FILAS - 1),
        )

        if manzana not in serpiente:
            return manzana


def dibujar_celda(pantalla, posicion, color):
    pygame.draw.rect(
        pantalla,
        color,
        (
            posicion[0] * CELDA,
            posicion[1] * CELDA,
            CELDA - 2,
            CELDA - 2,
        ),
    )


def main():
    pygame.init()

    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    reloj = pygame.time.Clock()

    # El cuerpo: lista de (columna, fila). La cabeza es el primer elemento.
    serpiente = [(5, 5)]
    direccion = (1, 0)  # (dx, dy) -> derecha
    manzana = manzana_nueva(serpiente)
    puntos = 0
    ejecutando = True

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.KEYDOWN:
                # No dejar que gire 180 grados: no puede ir directamente hacia atrás.
                if evento.key == pygame.K_UP and direccion != (0, 1):
                    direccion = (0, -1)
                elif evento.key == pygame.K_DOWN and direccion != (0, -1):
                    direccion = (0, 1)
                elif evento.key == pygame.K_LEFT and direccion != (1, 0):
                    direccion = (-1, 0)
                elif evento.key == pygame.K_RIGHT and direccion != (-1, 0):
                    direccion = (1, 0)

        # 1) Nueva cabeza.
        cabeza = (
            serpiente[0][0] + direccion[0],
            serpiente[0][1] + direccion[1],
        )
        serpiente.insert(0, cabeza)

        # 2) ¿Comió?
        if cabeza == manzana:
            puntos += 1
            manzana = manzana_nueva(serpiente)
        else:
            serpiente.pop()  # No comió: se achica por el final.

        # 3) ¿Chocó con el borde o consigo misma?
        choco_borde = (
            cabeza[0] < 0
            or cabeza[0] >= COLUMNAS
            or cabeza[1] < 0
            or cabeza[1] >= FILAS
        )
        choco_consigo_misma = cabeza in serpiente[1:]

        if choco_borde or choco_consigo_misma:
            ejecutando = False

        # 4) Dibujar.
        pantalla.fill(COLOR_FONDO)

        for segmento in serpiente:
            dibujar_celda(pantalla, segmento, COLOR_SERPIENTE)

        dibujar_celda(pantalla, manzana, COLOR_MANZANA)
        pygame.display.set_caption(f"Puntos: {puntos}")
        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()
    print(f"Fin del juego. Puntos: {puntos}")
    sys.exit()


if __name__ == "__main__":
    main()
