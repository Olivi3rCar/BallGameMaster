import time
import sys
import pygame
from pygame.locals import *
import os
from math import *
clock = pygame.time.Clock()
from SAT_algorithm_collision import collision_check
from tiles import *

from physics import gameplay, Ball, on_button

"""Initialization of the game window and the target frames per second"""
screen = pygame.display.set_mode((640,480))
pygame.display.set_caption('Ball Game')

"""Getting the path to the sprites folder"""
path=os.path.abspath(os.path.join("./main.py", os.pardir))
path=str(path)[:-10]+"Sprites png\\"

"""Loading all the images, some with there "dimensions" which are their positions in composite or carousel sprites"""
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
bckground_dim=(0,0,640,480)

bckgroundsand=pygame.image.load(path+"bckgroundsand.png")

bckgroundice=pygame.image.load(path+"bckgroundice.png")

buttons=pygame.image.load(path+"Buttons.png")
buttons = pygame.transform.scale(buttons, (3 * buttons.get_width(), 3 * buttons.get_height()))
gobackbuttonoff=(0,0,48,48)
gobackbuttonon=(48,0,48,48)
disable_back=False

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

bckE1M1=bckgroundgrass.subsurface((640,0,640,480))
bckE1M2=bckgroundgrass.subsurface((1280,0,640,480))
bckE1M3=bckgroundgrass.subsurface((1920,0,640,480))
bckE1M4=bckgroundgrass.subsurface((2560,0,640,480))
bckE1M5=bckgroundgrass.subsurface((3200,0,640,480))

bckE2M1=bckgroundsand.subsurface((640,0,640,480))
bckE2M2=bckgroundsand.subsurface((1280,0,640,480))
bckE2M3=bckgroundsand.subsurface((1920,0,640,480))
bckE2M4=bckgroundsand.subsurface((2560,0,640,480))
bckE2M5=bckgroundsand.subsurface((3200,0,640,480))

bckE3M1=bckgroundice.subsurface((640,0,640,480))
bckE3M2=bckgroundice.subsurface((1280,0,640,480))
bckE3M3=bckgroundice.subsurface((1920,0,640,480))
bckE3M4=bckgroundice.subsurface((2560,0,640,480))
bckE3M5=bckgroundice.subsurface((3200,0,640,480))

"""Storing the path to every level"""
path=path[:-12]+"Levels\\"
E1M1=path+"grass_level_1.csv"
E1M2=path+"grass_level_2.csv"
E1M3=path+"grass_level_3.csv"
E1M4=path+"grass_level_4.csv"
E1M5=path+"grass_level_5.csv"
E2M1=path+"sand_level_1.csv"
E2M2=path+"sand_level_2.csv"
E2M3=path+"sand_level_3.csv"
E2M4=path+"sand_level_4.csv"
E2M5=path+"sand_level_5.csv"
E3M1=path+"ice_level_1.csv"
E3M2=path+"ice_level_2.csv"
E3M3=path+"ice_level_3.csv"
E3M4=path+"ice_level_4.csv"
E3M5=path+"ice_level_5.csv"

path=path[:-7]+"Sprites png\\"

levels ={"grass":{1:(E1M1,(500,300)),2:(E1M2,(353,277)),3:(E1M3,(109,266)),4:(E1M4,(177,180)),5:(E1M5,(518,37))},
         "desert":{1:(E2M1,(530,302)),2:(E2M2,(96,238)),3:(E2M3,(244,200)),4:(E2M4,(378,295)),5:(E2M5,(330,54))},
         "ice":{1:(E3M1,(500,395)),2:(E3M2,(470,275)),3:(E3M3,(25,310)),4:(E3M4,(350,45)),5:(E3M5,(145,45))}}

"""Getting the center of the screen, for better image printing"""
posx = screen.get_rect().centerx
posy= screen.get_rect().centery

first_frame=False
scene = "Title"

while True:
    """Capping the fps to 120"""
    clock.tick(120)

    if scene == "Title":
        screen.fill((86, 150, 0))

        """Messing with the size of the splash text to make it bouncy"""
        splashscale=0.4*sin(x)+2.5
        x+=1/40
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
            """Printing the background and buttons only on the first frame"""
            screen.blit(bckgroundgrass, (0,0), bckground_dim)
            screen.blit(buttons, (500,300), w1lvl1off)
            screen.blit(buttons, (353,277), w1lvl2off)
            screen.blit(buttons, (109,266), w1lvl3off)
            screen.blit(buttons, (177,180), w1lvl4off)
            screen.blit(buttons, (518,37), w1lvl5off)
            first_frame=False

        """Checking if the cursor in on any of the buttons, then changing one of them is the mouse is hovering one"""
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
        """Printing the background and buttons only on the first frame"""
        if first_frame:
            screen.blit(bckgroundsand, (0,0), bckground_dim)
            screen.blit(buttons,(530,302) , w2lvl1off)
            screen.blit(buttons,(96,238) , w2lvl2off)
            screen.blit(buttons, (244,200), w2lvl3off)
            screen.blit(buttons, (378,295) , w2lvl4off)
            screen.blit(buttons, (330,54), w2lvl5off)
            first_frame=False

        """Checking if the cursor in on any of the buttons, then changing one of them is the mouse is hovering one"""
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
        """Printing the background and buttons only on the first frame"""
        if first_frame:
            screen.blit(bckgroundice, (0,0), bckground_dim)
            screen.blit(buttons, (500,395), w3lvl1off)
            screen.blit(buttons, (470,275), w3lvl2off)
            screen.blit(buttons, (25,310), w3lvl3off)
            screen.blit(buttons, (350,45), w3lvl4off)
            screen.blit(buttons, (145,45), w3lvl5off)
            first_frame=False

        """Checking if the cursor in on any of the buttons, then changing one of them is the mouse is hovering one"""
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

                        if on_button((145,45), (193, 93)):
                            screen.blit(buttons, (145,45), w3lvl5on)
                        else:
                            screen.blit(buttons, (145,45), w3lvl5off)

    if scene!="Title":
        """Setting up the sprite of a button to go back in the menus"""
        screen.blit(buttons, (0,0), gobackbuttonoff)

        if on_button((0,0),(48,48)):
            screen.blit(buttons, (0,0), gobackbuttonon)
        else:
            screen.blit(buttons, (0,0), gobackbuttonoff)

    for event in pygame.event.get():

        """Setting up the logic for exiting the game, by pressing the escape or exiting the window manually"""
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

        elif event.type == MOUSEBUTTONDOWN:
            """Changing scenes if the related button has been pressed"""
            if (scene == "Title") and on_button( (200, 380),(440,440)):
                scene="World Selection"
                first_frame=True

            elif scene == "World Selection":
                if on_button((0,0),(640,160)) and not(on_button((0,0),(48,48))):
                    scene="Forest"
                    first_frame = True
                elif on_button((0,160),(640,320)):
                    scene="Desert"
                    first_frame = True
                elif on_button((0,320),(640,480)):
                    scene="Ice"
                    first_frame = True



                """Setting up the transtition between the level selection and the levels themselves"""
            elif scene=="Forest":
                spritesheet = Spritesheet(os.path.join("C:/Users/victo/PycharmProjects/BallGameMaster/Sprites png/groundtiles.png"),
                    tile_size=32, columns=9)
                ball = Ball(pygame.math.Vector2(400, 150), 7, 0.5, 0.6, pygame.math.Vector2(0, 0),"forest")

                if on_button((levels["grass"][1][1][0],levels["grass"][1][1][1]),
                                 (levels["grass"][1][1][0]+48,levels["grass"][1][1][1]+48)):
                    scene="GrassLevel"

                    gameplay(screen, ball, Tilemap(E1M1, spritesheet), bckE1M1)
                elif on_button((levels["grass"][2][1][0],levels["grass"][2][1][1]),
                                 (levels["grass"][2][1][0]+48,levels["grass"][2][1][1]+48)):
                    gameplay(screen, ball, Tilemap(E1M2, spritesheet), bckE1M2)
                    scene="GrassLevel"

                elif on_button((levels["grass"][3][1][0],levels["grass"][3][1][1]),
                                 (levels["grass"][3][1][0]+48,levels["grass"][3][1][1]+48)):
                    gameplay(screen, ball, Tilemap(E1M3, spritesheet), bckE1M3)
                    scene="GrassLevel"

                elif on_button((levels["grass"][4][1][0],levels["grass"][4][1][1]),
                                 (levels["grass"][4][1][0]+48,levels["grass"][4][1][1]+48)):
                    gameplay(screen, ball, Tilemap(E1M4, spritesheet), bckE1M4)
                    scene="GrassLevel"

                elif on_button((levels["grass"][5][1][0],levels["grass"][5][1][1]),
                                 (levels["grass"][5][1][0]+48,levels["grass"][5][1][1]+48)):
                    gameplay(screen, ball, Tilemap(E1M5, spritesheet), bckE1M5)
                    scene="GrassLevel"

            elif scene=="Desert":
                spritesheet = Spritesheet(
                    os.path.join("C:/Users/victo/PycharmProjects/BallGameMaster/Sprites png/sandtiles.png"),
                    tile_size=32, columns=9)
                ball = Ball(pygame.math.Vector2(400, 150), 7, 0.5, 0.6, pygame.math.Vector2(0, 0),"desert")

                if on_button((levels["desert"][1][1][0], levels["desert"][1][1][1]),
                             (levels["desert"][1][1][0] + 48, levels["desert"][1][1][1] + 48)):
                    gameplay(screen, ball, Tilemap(E2M1, spritesheet), bckE2M1)
                    scene = "SandLevel"
                elif on_button((levels["desert"][2][1][0], levels["desert"][2][1][1]),
                               (levels["desert"][2][1][0] + 48, levels["desert"][2][1][1] + 48)):
                    gameplay(screen, ball, Tilemap(E2M2, spritesheet), bckE2M2)
                    scene = "SandLevel"

                elif on_button((levels["desert"][3][1][0], levels["desert"][3][1][1]),
                               (levels["desert"][3][1][0] + 48, levels["desert"][3][1][1] + 48)):
                    gameplay(screen, ball, Tilemap(E2M3, spritesheet), bckE2M3)
                    scene = "SandLevel"

                elif on_button((levels["desert"][4][1][0], levels["desert"][4][1][1]),
                               (levels["desert"][4][1][0] + 48, levels["desert"][4][1][1] + 48)):
                    gameplay(screen, ball, Tilemap(E2M4, spritesheet), bckE2M4)
                    scene = "SandLevel"

                elif on_button((levels["desert"][5][1][0], levels["desert"][5][1][1]),
                               (levels["desert"][5][1][0] + 48, levels["desert"][5][1][1] + 48)):
                    gameplay(screen, ball, Tilemap(E2M5, spritesheet), bckE2M5)
                    scene = "SandLevel"

            elif scene=="Ice":
                spritesheet = Spritesheet(
                    os.path.join("C:/Users/victo/PycharmProjects/BallGameMaster/Sprites png/icetiles.png"),
                    tile_size=32, columns=11)
                ball = Ball(pygame.math.Vector2(400, 150), 7, 0.5, 0.6, pygame.math.Vector2(0, 0),"iceland")

                if on_button((levels["ice"][1][1][0], levels["ice"][1][1][1]),
                             (levels["ice"][1][1][0] + 48, levels["ice"][1][1][1] + 48)):
                    gameplay(screen, ball, Tilemap(E3M1, spritesheet), bckE3M1)
                    scene = "IceLevel"
                elif on_button((levels["ice"][2][1][0], levels["ice"][2][1][1]),
                               (levels["ice"][2][1][0] + 48, levels["ice"][2][1][1] + 48)):
                    gameplay(screen, ball, Tilemap(E3M2, spritesheet), bckE3M2)
                    scene = "IceLevel"

                elif on_button((levels["ice"][3][1][0], levels["ice"][3][1][1]),
                               (levels["ice"][3][1][0] + 48, levels["ice"][3][1][1] + 48)):
                    gameplay(screen, ball, Tilemap(E3M3, spritesheet), bckE3M3)
                    scene = "IceLevel"

                elif on_button((levels["ice"][4][1][0], levels["ice"][4][1][1]),
                               (levels["ice"][4][1][0] + 48, levels["ice"][4][1][1] + 48)):
                    gameplay(screen, ball, Tilemap(E3M4, spritesheet), bckE3M4)
                    scene = "IceLevel"

                elif on_button((levels["ice"][5][1][0], levels["ice"][5][1][1]),
                               (levels["ice"][5][1][0] + 48, levels["ice"][5][1][1] + 48)):
                    gameplay(screen, ball, Tilemap(E3M5, spritesheet), bckE3M5)
                    scene = "IceLevel"

                """Setting up the logic of the button to go back in the menus"""
            if on_button((0,0),(48,48)) and disable_back==False:
                if scene=="Forest" or scene=="Desert" or scene=="Ice":
                    scene="World Selection"

                elif scene=="GrassLevel":
                    scene="Forest"

                elif scene=="SandLevel":
                    scene="Desert"

                elif scene=="IceLevel":
                    scene="Ice"

                elif scene=="World Selection":
                    scene="Title"

                first_frame = True
                disable_back=True

            """Stopping the user from going back multiple menus in one click"""
        elif event.type == MOUSEBUTTONUP:
            disable_back=False

    pygame.display.flip()