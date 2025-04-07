import time
start_time = time.time()

import sys
import pygame
from pygame.locals import *
import os
from math import sin


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

bckgroundsand=pygame.image.load(path+"bckgroundsand.png")
bckgroundsand_dim=(0,0,640,480)

bckgroundice=pygame.image.load(path+"bckgroundice.png")
bckgroundice_dim=(0,0,640,480)

buttons=pygame.image.load(path+"Buttons.png")
buttons = pygame.transform.scale(buttons, (3 * buttons.get_width(), 3 * buttons.get_height()))
w1lvl1off=(0,96,48,48)
w1lvl1on=(48,96,48,48)
w1lvl2off=(96,96,48,48)
w1lvl2on=(144,96,48,48)

w1lvl3off=(0,144,48,48)
w1lvl3on=(48,144,48,48)
w1lvl4off=(96,144,48,48)
w1lvl4on=(144,144,48,48)

w1lvl5off=(0,192,48,48)
w1lvl5on=(48,192,48,48)


w2lvl1off=(0,240,48,48)
w2lvl1on=(48,240,48,48)
w2lvl2off=(96,240,48,48)
w2lvl2on=(144,240,48,48)

w2lvl3off=(0,288,48,48)
w2lvl3on=(48,288,48,48)
w2lvl4off=(96,288,48,48)
w2lvl4on=(144,288,48,48)

w2lvl5off=(0,336,48,48)
w2lvl5on=(48,336,48,48)


w3lvl1off=(0,384,48,48)
w3lvl1on=(48,384,48,48)
w3lvl2off=(96,384,48,48)
w3lvl2on=(144,384,48,48)

w3lvl3off=(0,432,48,48)
w3lvl3on=(48,432,48,48)
w3lvl4off=(96,432,48,48)
w3lvl4on=(144,432,48,48)

w3lvl5off=(0,480,48,48)
w3lvl5on=(48,480,48,48)

path=path[:-12]+"Levels//"
E1M1=path+"grass_level_1.csv"
E1M2=path+"grass_level_2.csv"
E1M3=path+"grass_level_3.csv"
E1M4=path+"grass_level_4.csv"
E1M5=path+"grass_level_5.csv"
E2M1=path+"ice_level_1.csv"
E2M2=path+"ice_level_2.csv"
E2M3=path+"ice_level_3.csv"
E2M4=path+"ice_level_4.csv"
E2M5=path+"ice_level_5.csv"
E3M1=path+"sand_level_1.csv"
E3M2=path+"sand_level_2.csv"
E3M3=path+"sand_level_3.csv"
E3M4=path+"sand_level_4.csv"
E3M5=path+"sand_level_5.csv"

levels ={"grass":{1:(E1M1,(500,300)),2:(E1M2,(353,277)),3:(E1M3,(109,266)),4:(E1M4,(177,180)),5:(E1M5,(518,37))},
         "desert":{1:(E2M1,(530,302)),2:(E2M2,(96,238)),3:(E2M3,(244,200)),4:(E2M4,(378,295)),5:(E2M5,(330,54))},
         "ice":{1:(E3M1,(500,395)),2:(E3M2,(470,275)),3:(E3M3,(25,310)),4:(E3M4,(350,45)),5:(E3M5,(45,45))}}

"""Getting the center of the screen, for better image printing"""
posx = screen.get_rect().centerx
posy= screen.get_rect().centery

print(posx,posy)

first_frame=False
scene = "Title"
print("Build time : %.5s seconds" % (time.time() - start_time))

while True:
    if scene == "Title":
        screen.fill((86, 150, 0))

        """Messing with the size of the splash text to make it BoUnCy"""
        splashscale=0.4*sin(x)+2.5
        x+=0.15/40
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
            screen.blit(bckgroundgrass, (0,0), bckgroundgrass_dim)
            screen.blit(buttons, (500,300), w1lvl1off)
            screen.blit(buttons, (353,277), w1lvl2off)
            screen.blit(buttons, (109,266), w1lvl3off)
            screen.blit(buttons, (177,180), w1lvl4off)
            screen.blit(buttons, (518,37), w1lvl5off)
            first_frame=False

        """Checking if the cursor in on any of the buttons"""
        if on_button((500,300), (548, 348)):
            screen.blit(buttons, (500,300), w1lvl1on)
        else:
            screen.blit(buttons, (500,300), w1lvl1off)

            if on_button((353,277), (401, 325)):
                screen.blit(buttons, (353,277), w1lvl2on)
            else:
                screen.blit(buttons, (353,277), w1lvl2off)

                if on_button((109,266), (157, 314)):
                    screen.blit(buttons, (109,266), w1lvl3on)
                else:
                    screen.blit(buttons, (109,266), w1lvl3off)

                    if on_button((172, 180), (220, 228)):
                        screen.blit(buttons, (177,180), w1lvl4on)
                    else:
                        screen.blit(buttons, (177,180), w1lvl4off)

                        if on_button((518, 37), (566, 85)):
                            screen.blit(buttons, (518,37), w1lvl5on)
                        else:
                            screen.blit(buttons, (518,37), w1lvl5off)

    elif scene == "Desert":
        if first_frame:
            screen.blit(bckgroundsand, (0,0), bckgroundsand_dim)
            screen.blit(buttons,(530,302) , w2lvl1off)
            screen.blit(buttons,(96,238) , w2lvl2off)
            screen.blit(buttons, (244,200), w2lvl3off)
            screen.blit(buttons, (378,295) , w2lvl4off)
            screen.blit(buttons, (330,54), w2lvl5off)
            first_frame=False

        if on_button((530,302), (578, 350)):
            screen.blit(buttons, (530,302), w2lvl1on)
        else:
            screen.blit(buttons, (530,302), w2lvl1off)

            if on_button((96,238), (144, 286)):
                screen.blit(buttons, (96,238), w2lvl2on)
            else:
                screen.blit(buttons, (96,238), w2lvl2off)

                if on_button((244,200), (292, 248)):
                    screen.blit(buttons, (244,200), w2lvl3on)
                else:
                    screen.blit(buttons, (244,200), w2lvl3off)

                    if on_button((378,295), (426, 343)):
                        screen.blit(buttons, (378,295), w2lvl4on)
                    else:
                        screen.blit(buttons, (378,295), w2lvl4off)

                        if on_button((330,54), (378, 102)):
                            screen.blit(buttons, (330,54), w2lvl5on)
                        else:
                            screen.blit(buttons, (330,54), w2lvl5off)

    elif scene == "Ice":
        if first_frame:
            screen.blit(bckgroundice, (0,0), bckgroundice_dim)
            screen.blit(buttons, (500,395), w3lvl1off)
            screen.blit(buttons, (470,275), w3lvl2off)
            screen.blit(buttons, (25,310), w3lvl3off)
            screen.blit(buttons, (350,45), w3lvl4off)
            screen.blit(buttons, (45,45), w3lvl5off)
            first_frame=False

        """Checking if the cursor in on any of the buttons"""
        if on_button((500,395), (548, 443)):
            screen.blit(buttons, (500,395), w3lvl1on)
        else:
            screen.blit(buttons, (500,395), w3lvl1off)

            if on_button((470,275), (518, 323)):
                screen.blit(buttons, (470,275), w3lvl2on)
            else:
                screen.blit(buttons, (470,275), w3lvl2off)

                if on_button((25,310), (73, 358)):
                    screen.blit(buttons, (25,310), w3lvl3on)
                else:
                    screen.blit(buttons, (25,310), w3lvl3off)

                    if on_button((350,45), (398, 93)):
                        screen.blit(buttons, (350,45), w3lvl4on)
                    else:
                        screen.blit(buttons, (350,45), w3lvl4off)

                        if on_button((45,45), (93, 93)):
                            screen.blit(buttons, (45,45), w3lvl5on)
                        else:
                            screen.blit(buttons, (45,45), w3lvl5off)
    if scene!="Title":
        ...

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
                elif on_button((0,160),(640,320)):
                    scene="Desert"
                    first_frame = True
                elif on_button((0,320),(640,480)):
                    scene="Ice"
                    first_frame = True
    pygame.display.flip()