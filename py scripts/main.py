import sys
import pygame
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((1080,720))
pygame.display.set_caption('Ball Game')

FPS = pygame.time.Clock()
FPS.tick(60)

title_image = pygame.image.load("./limace.jpg")

imagerect = title_image.get_rect()

posx = screen.get_rect().centerx
posy= screen.get_rect().centery

dutronc=pygame.image.load("./dutronc_cigare.jpg")
kino=pygame.image.load("kino.jpg")

# program.display.update()
gamestate = "Title"

first_frame=True

while True:
    pygame.display.flip()
    if gamestate == "Title":
        if first_frame:
            screen.fill((86, 150, 0))
            screen.blit(title_image, title_image.get_rect(center=(posx,posy)))
    elif gamestate == "Level Selection":
        if first_frame:
            screen.fill((255, 255, 255))
            kino=pygame.transform.smoothscale(kino, (0.9*kino.get_width(),0.9*kino.get_height()))
            dutronc = pygame.transform.smoothscale(dutronc, (0.5*dutronc.get_width(),0.1*dutronc.get_height()))
            screen.blit(dutronc, dutronc.get_rect(center=(posx + 700, posy - 30)))
            screen.blit(kino, kino.get_rect(center=(posx, posy)))
            first_frame=False


    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == MOUSEBUTTONDOWN:
            if (title_image.get_rect().collidepoint(event.pos)) and (gamestate == "Title"):
                gamestate="Level Selection"
                first_frame=True


            elif gamestate == "Level Selection" :
                pass