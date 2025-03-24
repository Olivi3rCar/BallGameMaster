import sys
import pygame
from pygame.locals import *
import os
from math import sin


path=(os.path.abspath(os.path.join("./main.py", os.pardir)))
path=str(path)[:-10]+"Sprites png\\"

#pygame.init()
screen = pygame.display.set_mode((640,480))
pygame.display.set_caption('Ball Game')

FPS = pygame.time.Clock()
FPS.tick(60)

title_image = pygame.image.load(path+"Title.png")
splash=pygame.image.load(path+"Putt_it_in.png")

play=pygame.image.load(path+"Let'sPlayButton.png")

imagerect = title_image.get_rect()

posx = screen.get_rect().centerx
posy= screen.get_rect().centery

worldselect=pygame.image.load(path+"stageselect.png")

buttons=pygame.image.load(path+"Buttons.png")
bckgroundgrass=pygame.image.load(path+"bckgroundgrass.png")

scene = "Title"
first_frame=True

splashscale=1
x=0

playoff=(0,0,80*3,20*3)
playon=(80*3,0,160*3,20*3)
forest_bg_levelselect_dim=(0,0,640,160)
desert_bg_levelselect_dim=(0,0,640,160)
icesheet_bg_levelselect_dim=(0,0,640,160)
bckgroundgrass_dim=(0,0,640,480)

lvl1off=(0,96,48,48)
lvl1on=(48,96,48,48)
lvl2off=(96,96,48,48)
lvl2on=(144,96,48,48)

lvl3off=(0,144,48,48)
lvl3on=(48,144,48,48)
lvl4off=(96,144,48,48)
lvl4on=(144,144,48,48)

lvl5off=(0,144+48,48,48)
lvl5on=(48,144+48,48,48)

screen_center = screen.get_rect().center

buttons = pygame.transform.scale(buttons, (3 * buttons.get_width(), 3 * buttons.get_height()))


def on_button(gamestate,position,t_w,t_h):
    mouse_x, mouse_y = pygame.mouse.get_pos()

    if gamestate == "Title" and (position[0]+(t_w/2)>=int(mouse_x)>=position[0]-(t_w/2)) and (position[1]+(t_h/2)>=int(mouse_y)>=position[1]-(t_h/2)):
        return True
    elif (position[0]<mouse_x<t_w) and (position[1]<mouse_y<t_h):
        return True

while True:
    if scene == "Title":
        if first_frame:
            screen.fill((86, 150, 0))
            title_image = pygame.transform.scale(title_image,(2*title_image.get_width(),2*title_image.get_height()))
            splashdisp=pygame.transform.scale(splash,(splashscale*splash.get_width(),splashscale*splash.get_height()))
            play=pygame.transform.scale(play,(3*play.get_width(),3*play.get_height()))
            first_frame=False

        splashscale=0.4*sin(x)+2.5
        x+=0.1/40

        screen.fill((86, 150, 0))
        screen.blit(play, play.get_rect(center=(posx+(40*3), posy+170)),playoff)

        screen.blit(title_image, title_image.get_rect(center=(posx,posy-60)))

        splashdisp=pygame.transform.scale(splash,(splashscale*splash.get_width(),splashscale*splash.get_height()))
        screen.blit(splashdisp, splashdisp.get_rect(center=(posx,posy+2)))

        if on_button(scene, (posx, posy + 170),play.get_width()/2,play.get_height()):
            screen.blit(play, play.get_rect(center=(posx + (40 * 3), posy + 170)), playon)

    elif scene == "World Selection":
        if first_frame:
            screen.fill((255, 255, 255))

            screen.blit(worldselect, worldselect.get_rect(center=(posx, posy)), (0,0,680,480))
            first_frame=False

    elif scene == "Forest":
        if first_frame:
            screen.fill((255, 255, 255))
            screen.blit(bckgroundgrass, bckgroundgrass.get_rect(center=(posx+3*640+320, posy)), bckgroundgrass_dim)

            screen.blit(buttons, buttons.get_rect(center=(posx+270, posy+320)), lvl1off)
            screen.blit(buttons, buttons.get_rect(center=(posx+130, posy+300)), lvl2off)
            screen.blit(buttons, buttons.get_rect(center=(posx-120, posy+288)), lvl3off)
            screen.blit(buttons, buttons.get_rect(center=(posx-60, posy+200)), lvl4off)
            screen.blit(buttons, buttons.get_rect(center=(posx+290, posy+60)), lvl5off)

            first_frame=False

        if on_button(scene, (493,298), 541, 346):
            screen.blit(buttons, buttons.get_rect(center=(posx+270, posy+320)), lvl1on)
        else:
            screen.blit(buttons, buttons.get_rect(center=(posx + 270, posy + 320)), lvl1off)

        if on_button(scene, (357,279), 405, 327):
            screen.blit(buttons, buttons.get_rect(center=(posx + 130, posy + 300)), lvl2on)
        else:
            screen.blit(buttons, buttons.get_rect(center=(posx + 130, posy + 300)), lvl2off)

        if on_button(scene, (109,268), 157, 316):
            screen.blit(buttons, buttons.get_rect(center=(posx -120, posy + 288)), lvl3on)
        else:
            screen.blit(buttons, buttons.get_rect(center=(posx -120, posy + 288)), lvl3off)

        if on_button(scene, (170, 182), 218, 230):
            screen.blit(buttons, buttons.get_rect(center=(posx -60, posy + 200)), lvl4on)
        else:
            screen.blit(buttons, buttons.get_rect(center=(posx -60, posy + 200)), lvl4off)

        if on_button(scene, (519, 39), 567, 87):
            screen.blit(buttons, buttons.get_rect(center=(posx + 290, posy + 60)), lvl5on)
        else:
            screen.blit(buttons, buttons.get_rect(center=(posx + 290, posy + 60)), lvl5off)

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

        elif event.type == MOUSEBUTTONDOWN:
            if (scene == "Title") and on_button(scene, (posx, posy + 170),play.get_width()/2,play.get_height()):
                scene="World Selection"
                first_frame=True

            elif scene == "World Selection":
                if on_button(scene,(0,0),640,160):
                    scene="Forest"
                    first_frame = True
                elif on_button(scene,(0,160),640,160*2):
                    scene="Desert"
                    first_frame = True
                elif on_button(scene,(0,160*2),640,160*3):
                    scene="Ice"
                    first_frame = True

    pygame.display.flip()