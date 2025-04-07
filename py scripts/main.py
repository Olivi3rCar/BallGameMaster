import sys
import pygame
from pygame.locals import *
import os
from math import sin
import time
start_time = time.time()


def on_button(top_left,bottom_right):
    """Getting the position of the mouse, then checking its position relative to the "hitbox" of the image
    :param top_left: int couple: the position of the top left corner of the image
    :param bottom_right: int couple: the position of the bottom right of the image
    :return: bool: if the mouse is on the image or not
    """
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if (top_left[0]<mouse_x<bottom_right[0]) and (top_left[1]<mouse_y<bottom_right[1]):
        return True

"""Initialization of the game window and the target frames per second"""
screen = pygame.display.set_mode((640,480))
pygame.display.set_caption('Ball Game')

FPS = pygame.time.Clock()
FPS.tick(60)

"""Getting the path to the sprites folder"""
path=(os.path.abspath(os.path.join("./main.py", os.pardir)))
path=str(path)[:-10]+"Sprites png\\"

"""Loading all the images, some with there "dimensions" which are their positions in more composite sprites"""
title_image = pygame.image.load(path+"Title.png")
title_image = pygame.transform.scale(title_image,(2*title_image.get_width(),2*title_image.get_height()))

splash=pygame.image.load(path+"Putt_it_in.png")
splashscale=1
x=0

play=pygame.image.load(path+"Let'sPlayButton.png")
play=pygame.transform.scale(play,(3*play.get_width(),3*play.get_height()))
playoff=(0,0,80*3,20*3)
playon=(80*3,0,160*3,20*3)

worldselect=pygame.image.load(path+"stageselect.png")

bckgroundgrass=pygame.image.load(path+"bckgroundgrass.png")
bckgroundgrass_dim=(0,0,640,480)

buttons=pygame.image.load(path+"Buttons.png")
buttons = pygame.transform.scale(buttons, (3 * buttons.get_width(), 3 * buttons.get_height()))
lvl1off=(0,96,48,48)
lvl1on=(48,96,48,48)
lvl2off=(96,96,48,48)
lvl2on=(144,96,48,48)

lvl3off=(0,144,48,48)
lvl3on=(48,144,48,48)
lvl4off=(96,144,48,48)
lvl4on=(144,144,48,48)

lvl5off=(0,192,48,48)
lvl5on=(48,192,48,48)

"""Getting the center of the screen, for better image printing"""
posx = screen.get_rect().centerx
posy= screen.get_rect().centery

first_frame=False
scene = "Title"
print("Build time : %.4s seconds" % (time.time() - start_time))


while True:
    if scene == "Title":
        screen.fill((86, 150, 0))

        """Messing with the size of the splash text to make it BoUnCy"""
        splashscale=0.4*sin(x)+2.5
        x+=0.3/40
        splashdisp=pygame.transform.scale(splash,(splashscale*splash.get_width(),splashscale*splash.get_height()))

        """Printing the images on the screen"""
        screen.blit(play, play.get_rect(center=(posx+(40*3), posy+170)),playoff)
        screen.blit(title_image, title_image.get_rect(center=(posx,posy-60)))
        screen.blit(splashdisp, splashdisp.get_rect(center=(posx,posy-8)))

        """Pressing the button if the cursor is on top of it"""
        if on_button((200, 380),(440,440)):
            screen.blit(play, play.get_rect(center=(posx + (40 * 3), posy + 170)), playon)

    elif scene == "World Selection":
        """Initialization of the World select screen"""
        screen.blit(worldselect, worldselect.get_rect(center=(posx, posy)), (0,0,680,480))

    elif scene == "Forest":
        if first_frame:
            screen.blit(bckgroundgrass, bckgroundgrass.get_rect(center=(posx+3*640+320, posy)), bckgroundgrass_dim)
            screen.blit(buttons, buttons.get_rect(center=(posx + 270, posy + 320)), lvl1off)
            screen.blit(buttons, buttons.get_rect(center=(posx + 130, posy + 300)), lvl2off)
            screen.blit(buttons, buttons.get_rect(center=(posx - 120, posy + 288)), lvl3off)
            screen.blit(buttons, buttons.get_rect(center=(posx - 60, posy + 200)), lvl4off)
            screen.blit(buttons, buttons.get_rect(center=(posx + 290, posy + 60)), lvl5off)
            first_frame=False


        """Checking if the cursor in on any of the buttons"""
        if on_button((493,298), (541, 346)):
            screen.blit(buttons, buttons.get_rect(center=(posx+270, posy+320)), lvl1on)
        else:
            screen.blit(buttons, buttons.get_rect(center=(posx + 270, posy + 320)), lvl1off)

            if on_button((357,279), (405, 327)):
                screen.blit(buttons, buttons.get_rect(center=(posx + 130, posy + 300)), lvl2on)
            else:
                screen.blit(buttons, buttons.get_rect(center=(posx + 130, posy + 300)), lvl2off)

                if on_button((109,268), (157, 316)):
                    screen.blit(buttons, buttons.get_rect(center=(posx -120, posy + 288)), lvl3on)
                else:
                    screen.blit(buttons, buttons.get_rect(center=(posx -120, posy + 288)), lvl3off)

                    if on_button((170, 182), (218, 230)):
                        screen.blit(buttons, buttons.get_rect(center=(posx -60, posy + 200)), lvl4on)
                    else:
                        screen.blit(buttons, buttons.get_rect(center=(posx -60, posy + 200)), lvl4off)

                        if on_button((519, 39), (567, 87)):
                            screen.blit(buttons, buttons.get_rect(center=(posx + 290, posy + 60)), lvl5on)
                        else:
                            screen.blit(buttons, buttons.get_rect(center=(posx + 290, posy + 60)), lvl5off)

    for event in pygame.event.get():

        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

        elif event.type == MOUSEBUTTONDOWN:
            """Changing scenes if the related button has been pressed"""
            if (scene == "Title") and on_button( (200, 380),(440,440)):
                scene="World Selection"
                first_frame=True

            elif scene == "World Selection":
                if on_button((0,0),(640,160)):
                    scene="Forest"
                    first_frame = True
                elif on_button((0,160),(640,160*2)):
                    scene="Desert"
                    first_frame = True
                elif on_button((0,160*2),(640,160*3)):
                    scene="Ice"
                    first_frame = True
    pygame.display.flip()