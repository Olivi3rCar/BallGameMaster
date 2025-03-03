import sys
import pygame
from pygame.locals import *
import os
from math import sin


path=(os.path.abspath(os.path.join("./main.py", os.pardir)))
path=str(path)[:-10]+"Sprites png\\"

#pygame.init()
screen = pygame.display.set_mode((680,480))
pygame.display.set_caption('Ball Game')

FPS = pygame.time.Clock()
FPS.tick(5)

title_image = pygame.image.load(path+"Title.png")
splash=pygame.image.load(path+"Putt_it_in.png")

play=pygame.image.load(path+"Let'sPlayButton.png")

imagerect = title_image.get_rect()

posx = screen.get_rect().centerx
posy= screen.get_rect().centery-50

dutronc=pygame.image.load("./dutronc_cigare.jpg")
kino=pygame.image.load("kino.jpg")

forest_bg_levelselect=pygame.image.load("tout-savoir-sur-la-foret-1690461418.jpg")
desert_bg_levelselect=pygame.image.load("DATA_ART_11302929.JPG-1082602760.JPG")
icesheet_bg_levelselect=pygame.image.load("cold-fish-441151-35585082.jpg")

scene = "Title"
first_frame=True

splashscale=3
x=0

playoff=(0,0,80*3,20*3)
playon=(80*3,0,160*3,20*3)
forest_bg_levelselect_dim=(0,0,680,160)
desert_bg_levelselect_dim=(0,0,680,160)
icesheet_bg_levelselect_dim=(0,0,680,160)

screen_center = screen.get_rect().center

def on_button(gamestate,position,t_w,t_h):
    mouse_x, mouse_y = pygame.mouse.get_pos()

    if gamestate == "Title" and (position[0]+(t_w/2)>=int(mouse_x)>=position[0]-(t_w/2)) and (position[1]+(t_h/2)>=int(mouse_y)>=position[1]-(t_h/2)):
        return True
    elif gamestate=="World Selection" and (position[0]<mouse_x<t_w) and (position[1]<mouse_y<t_h):
        return True

while True:
    if scene == "Title":
        if first_frame:
            screen.fill((86, 150, 0))
            title_image = pygame.transform.scale(title_image,(3*title_image.get_width(),3*title_image.get_height()))
            splashdisp=pygame.transform.scale(splash,(splashscale*splash.get_width(),splashscale*splash.get_height()))
            play=pygame.transform.scale(play,(3*play.get_width(),3*play.get_height()))
            first_frame=False

        splashscale=0.3*sin(x)+2.5
        x+=0.1/25

        screen.fill((86, 150, 0))
        screen.blit(play, play.get_rect(center=(posx+(40*3), posy+180)),playoff)

        screen.blit(title_image, title_image.get_rect(center=(posx,posy-60)))

        splashdisp=pygame.transform.scale(splash,(splashscale*splash.get_width(),splashscale*splash.get_height()))
        screen.blit(splashdisp, splashdisp.get_rect(center=(posx,posy+15)))

        if on_button(scene, (posx, posy + 180),play.get_width()/2,play.get_height()):
            screen.blit(play, play.get_rect(center=(posx + (40 * 3), posy + 180)), playon)

    elif scene == "World Selection":
        if first_frame:
            screen.fill((255, 255, 255))

            screen.blit(forest_bg_levelselect, forest_bg_levelselect.get_rect(center=(posx+260, posy+125)), forest_bg_levelselect_dim)
            screen.blit(desert_bg_levelselect, desert_bg_levelselect.get_rect(center=(posx+160,posy+251)), desert_bg_levelselect_dim)
            screen.blit(icesheet_bg_levelselect, icesheet_bg_levelselect.get_rect(center=(posx+460,posy+708)), icesheet_bg_levelselect_dim)
            first_frame=False


    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

        elif event.type == MOUSEBUTTONDOWN:
            if (scene == "Title") and on_button(scene, (posx, posy + 180),play.get_width()/2,play.get_height()):
                scene="World Selection"
                first_frame=True

            elif scene == "World Selection":
                if on_button(scene,(0,0),680,160):
                    scene="Forest"
                    first_frame = True
                elif on_button(scene,(0,160),680,160*2):
                    scene="Desert"
                    first_frame = True
                elif on_button(scene,(0,160*2),680,160*3):
                    scene="Ice"
                    first_frame = True

    pygame.display.flip()