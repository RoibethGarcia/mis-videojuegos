import sys
import pygame
pygame.init()
ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Mi primer juego")
reloj = pygame.time.Clock()
x, y = 100, 100 # posición del cuadrado
velocidad = 5
ejecutando = True
while ejecutando:
 # 1) LEER ENTRADA
 for evento in pygame.event.get():
    if evento.type == pygame.QUIT:
        ejecutando = False
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
        x -= velocidad
    if teclas[pygame.K_RIGHT]:
        x += velocidad
    if teclas[pygame.K_UP]:
        y -= velocidad
    if teclas[pygame.K_DOWN]:
        y += velocidad
 # 2) ACTUALIZAR (no hace falta en este juego tan simple)
 # 3) DIBUJAR
 pantalla.fill((20, 20, 40)) # fondo
 pygame.draw.rect(pantalla, (0, 200, 255), (x, y, 50, 50))
 pygame.display.flip()
 reloj.tick(60) # máximo 60 FPS
pygame.quit()
sys.exit()