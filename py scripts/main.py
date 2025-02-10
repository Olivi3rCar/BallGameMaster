import sys
import pygame
from pygame.locals import *
import os
from math import sin


path=(os.path.abspath(os.path.join("./main.py", os.pardir)))
path=str(path)[:-10]+"Sprites png\\"

#pygame.init()
screen = pygame.display.set_mode((960,720))
pygame.display.set_caption('Ball Game')

FPS = pygame.time.Clock()
FPS.tick(60)

title_image = pygame.image.load(path+"Title.png")
splash=pygame.image.load(path+"Putt_it_in.png")

play=pygame.image.load(path+"Let'sPlayButton.png")
playbuttonreac=pygame.Surface((80,20))

imagerect = title_image.get_rect()

posx = screen.get_rect().centerx
posy= screen.get_rect().centery-50

dutronc=pygame.image.load("./dutronc_cigare.jpg")
kino=pygame.image.load("kino.jpg")


scene = "Title"
first_frame=True

splashscale=3
print(splashscale * splash.get_width())
x=0

playbutton=playbuttonreac.blit(play, (0, 0), (0, 0, 80, 20))

while True:
    if scene == "Title":
        if first_frame:
            screen.fill((86, 150, 0))
            title_image = pygame.transform.scale(title_image,(3*title_image.get_width(),3*title_image.get_height()))
            screen.blit(title_image, title_image.get_rect(center=(posx,posy)))

            splashdisp=pygame.transform.scale(splash,(splashscale*splash.get_width(),splashscale*splash.get_height()))
            screen.blit(splashdisp, splashdisp.get_rect(center=(posx,posy+75)))

            screen.blit(playbutton, playbutton.get_rect(center=(posx,posy+75)))

            first_frame=False

        splashscale=0.3*sin(x)+2.5
        x+=0.1/30

        screen.fill((86, 0, 0))
        screen.blit(title_image, title_image.get_rect(center=(posx,posy)))
        splashdisp=pygame.transform.scale(splash,(splashscale*splash.get_width(),splashscale*splash.get_height()))
        screen.blit(splashdisp, splashdisp.get_rect(center=(posx,posy+75)))


    elif scene == "Level Selection":
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
            if (title_image.get_rect().collidepoint(event.pos)) and (scene == "Title"):
                scene="Level Selection"
                first_frame=True


            elif scene == "Level Selection" :
                pass
            
    pygame.display.flip()