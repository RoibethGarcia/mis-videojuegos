import sys
from pathlib import Path

import pygame


pygame.init()

ANCHO, ALTO = 800, 600
FPS = 60

GRAVEDAD = 0.5
VEL_MOV = 6
FUERZA_SALTO = -13

COLOR_CIELO = (150, 210, 255)
COLOR_PLATAFORMA = (90, 60, 30)
COLOR_MONO = (160, 110, 50)
COLOR_BANANA = (255, 220, 60)
COLOR_ENEMIGO = (200, 50, 50)
COLOR_TEXTO = (20, 30, 40)

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
SOUNDS_DIR = ASSETS_DIR / "sounds"

POSICION_INICIAL_MONO = (100, 300)
TAMANIO_MONO = (40, 40)
VIDAS_INICIALES = 3
TIEMPO_INVULNERABLE_MS = 1000

pantalla = pygame.display.set_mode((ANCHO, ALTO))
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont(None, 36)


def iniciar_audio():
    """Inicializa el mixer, pero permite jugar aunque no haya salida de audio."""
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        return True
    except pygame.error:
        return False


AUDIO_ACTIVO = iniciar_audio()


def cargar_imagen(nombre, tamanio=None):
    """Carga una imagen desde assets/images y devuelve None si no existe."""
    ruta = IMAGES_DIR / nombre

    try:
        imagen = pygame.image.load(ruta).convert_alpha()
    except (FileNotFoundError, pygame.error):
        return None

    if tamanio is not None:
        imagen = pygame.transform.scale(imagen, tamanio)

    return imagen


def cargar_sonido(nombre):
    """Carga un efecto de sonido y devuelve None si no se puede reproducir."""
    if not AUDIO_ACTIVO:
        return None

    ruta = SOUNDS_DIR / nombre

    try:
        return pygame.mixer.Sound(ruta)
    except (FileNotFoundError, pygame.error):
        return None


def reproducir_sonido(sonido):
    if sonido is not None:
        sonido.play()


def iniciar_musica():
    """Reproduce música de fondo en loop si el archivo está disponible."""
    if not AUDIO_ACTIVO:
        return

    ruta = SOUNDS_DIR / "music.wav"

    try:
        pygame.mixer.music.load(ruta)
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play(-1)
    except (FileNotFoundError, pygame.error):
        pass


imagenes = {
    "fondo": cargar_imagen("background.png", (ANCHO, ALTO)),
    "mono": cargar_imagen("player.png", TAMANIO_MONO),
    "banana": cargar_imagen("coin.png", (20, 20)),
    "enemigo": cargar_imagen("enemy.png", (35, 35)),
    "plataforma": cargar_imagen("platform.png"),
}

sonidos = {
    "salto": cargar_sonido("jump.wav"),
    "banana": cargar_sonido("banana.wav"),
    "golpe": cargar_sonido("hit.wav"),
    "victoria": cargar_sonido("win.wav"),
}

plataformas = [
    pygame.Rect(0, ALTO - 40, ANCHO, 40),  # piso
    pygame.Rect(200, 450, 180, 25),
    pygame.Rect(450, 360, 180, 25),
    pygame.Rect(600, 250, 180, 25),
]

posiciones_bananas = [
    (250, 420),
    (500, 330),
    (650, 220),
]

datos_enemigos = [
    (320, 415, 35, 35, 2, 200, 380),
    (570, 325, 35, 35, 3, 450, 630),
]


def crear_bananas():
    """Crea las bananas en sus posiciones iniciales."""
    return [pygame.Rect(x, y, 20, 20) for x, y in posiciones_bananas]


def crear_mono():
    """Crea al mono en la posición inicial."""
    return pygame.Rect(*POSICION_INICIAL_MONO, *TAMANIO_MONO)


def crear_enemigos():
    """Crea enemigos simples que se mueven de izquierda a derecha."""
    return [
        {
            "rect": pygame.Rect(x, y, ancho, alto),
            "vel_x": vel_x,
            "min_x": min_x,
            "max_x": max_x,
        }
        for x, y, ancho, alto, vel_x, min_x, max_x in datos_enemigos
    ]


def reiniciar_intento():
    """Reinicia al mono, las bananas y los enemigos cuando cae al vacío."""
    return (
        crear_mono(),
        0,
        0,
        False,
        crear_bananas(),
        crear_enemigos(),
        0,
        pygame.time.get_ticks(),
    )


def reiniciar_mono():
    """Reinicia solo al mono después de tocar un enemigo."""
    return crear_mono(), 0, 0, False


def dibujar_texto(texto, posicion):
    superficie = fuente.render(texto, True, COLOR_TEXTO)
    pantalla.blit(superficie, posicion)


def dibujar_fondo():
    if imagenes["fondo"] is not None:
        pantalla.blit(imagenes["fondo"], (0, 0))
    else:
        pantalla.fill(COLOR_CIELO)


def dibujar_plataforma(plataforma):
    textura = imagenes["plataforma"]

    if textura is None:
        pygame.draw.rect(pantalla, COLOR_PLATAFORMA, plataforma)
        return

    textura_escalada = pygame.transform.scale(textura, plataforma.size)
    pantalla.blit(textura_escalada, plataforma)


def dibujar_mono(mono):
    if imagenes["mono"] is not None:
        pantalla.blit(imagenes["mono"], mono)
    else:
        pygame.draw.rect(pantalla, COLOR_MONO, mono)


def dibujar_banana(banana):
    if imagenes["banana"] is not None:
        pantalla.blit(imagenes["banana"], banana)
    else:
        pygame.draw.circle(pantalla, COLOR_BANANA, banana.center, 10)


def dibujar_enemigo(enemigo):
    rect = enemigo["rect"]

    if imagenes["enemigo"] is not None:
        pantalla.blit(imagenes["enemigo"], rect)
    else:
        pygame.draw.rect(pantalla, COLOR_ENEMIGO, rect)


def dibujar_mensaje_final(texto):
    dibujar_fondo()
    superficie = fuente.render(texto, True, COLOR_TEXTO)
    rect = superficie.get_rect(center=(ANCHO // 2, ALTO // 2))
    pantalla.blit(superficie, rect)
    pygame.display.flip()
    pygame.time.wait(2500)


def mover_enemigos(enemigos):
    for enemigo in enemigos:
        rect = enemigo["rect"]
        rect.x += enemigo["vel_x"]

        if rect.left <= enemigo["min_x"] or rect.right >= enemigo["max_x"]:
            enemigo["vel_x"] *= -1


def main():
    mono = crear_mono()
    vel_x, vel_y = 0, 0
    en_piso = False
    bananas = crear_bananas()
    enemigos = crear_enemigos()
    juntas = 0
    vidas = VIDAS_INICIALES
    ultimo_golpe = -TIEMPO_INVULNERABLE_MS
    inicio_tiempo = pygame.time.get_ticks()
    segundos_finales = 0
    mensaje_final = ""
    ejecutando = True

    iniciar_musica()

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE and en_piso:
                    vel_y = FUERZA_SALTO
                    en_piso = False
                    reproducir_sonido(sonidos["salto"])

        teclas = pygame.key.get_pressed()
        vel_x = (teclas[pygame.K_RIGHT] - teclas[pygame.K_LEFT]) * VEL_MOV

        vel_y += GRAVEDAD
        mono.x += vel_x

        borde_inferior_anterior = mono.bottom
        mono.y += vel_y

        en_piso = False
        for plataforma in plataformas:
            cae_sobre_plataforma = (
                mono.colliderect(plataforma)
                and vel_y >= 0
                and borde_inferior_anterior <= plataforma.top
            )

            if cae_sobre_plataforma:
                mono.bottom = plataforma.top
                vel_y = 0
                en_piso = True

        for banana in bananas[:]:
            if mono.colliderect(banana):
                bananas.remove(banana)
                juntas += 1
                reproducir_sonido(sonidos["banana"])

        if mono.top > ALTO:
            reproducir_sonido(sonidos["golpe"])
            (
                mono,
                vel_x,
                vel_y,
                en_piso,
                bananas,
                enemigos,
                juntas,
                inicio_tiempo,
            ) = reiniciar_intento()

        mover_enemigos(enemigos)

        ahora = pygame.time.get_ticks()
        puede_recibir_golpe = ahora - ultimo_golpe >= TIEMPO_INVULNERABLE_MS

        for enemigo in enemigos:
            if mono.colliderect(enemigo["rect"]) and puede_recibir_golpe:
                vidas -= 1
                ultimo_golpe = ahora
                reproducir_sonido(sonidos["golpe"])

                if vidas == 0:
                    mensaje_final = "Perdiste: te quedaste sin vidas"
                    ejecutando = False
                else:
                    mono, vel_x, vel_y, en_piso = reiniciar_mono()

                break

        segundos = (pygame.time.get_ticks() - inicio_tiempo) // 1000

        if len(bananas) == 0:
            segundos_finales = segundos
            mensaje_final = f"Ganaste en {segundos_finales} segundos"
            reproducir_sonido(sonidos["victoria"])
            ejecutando = False

        dibujar_fondo()

        for plataforma in plataformas:
            dibujar_plataforma(plataforma)

        dibujar_mono(mono)

        for banana in bananas:
            dibujar_banana(banana)

        for enemigo in enemigos:
            dibujar_enemigo(enemigo)

        dibujar_texto(f"Bananas: {juntas}", (20, 20))
        dibujar_texto(f"Vidas: {vidas}", (20, 55))
        dibujar_texto(f"Tiempo: {segundos}s", (20, 90))

        pygame.display.set_caption(
            f"El Mono - Bananas: {juntas} - Vidas: {vidas} - Tiempo: {segundos}s"
        )
        pygame.display.flip()
        reloj.tick(FPS)

    if AUDIO_ACTIVO:
        pygame.mixer.music.stop()

    if mensaje_final:
        dibujar_mensaje_final(mensaje_final)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
