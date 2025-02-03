import sys
import pygame
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((1080,720))
pygame.display.set_caption('Putt It In')

FPS = pygame.time.Clock()
FPS.tick(60)

title_image = pygame.image.load("./sea-slug-3-3956079983.jpg")
t_w=title_image.get_width()
t_h=title_image.get_height()


imagerect = title_image.get_rect()
pos = screen.get_rect().center


def on_play_button(gamestate,pos,t_w,t_h):
    if gamestate!="Title":
        return False
    mouse_x, mouse_y = pygame.mouse.get_pos()
    print(mouse_x)
    print(pos[0]+(t_w/2), pos[0]-(t_w/2))

    print('\n', mouse_y)
    print(pos[1]+(t_h/2), pos[1]-(t_h/2))

    print('\n')

    print((pos[0]+(t_w/2)<=mouse_x<=pos[0]-(t_w/2)),(pos[1]+(t_h/2)<=mouse_y<=pos[1]-(t_h/2)))
    if (pos[0]+(t_w/2)<=mouse_x<=pos[0]-(t_w/2)) and (pos[1]+(t_h/2)<mouse_y<pos[1]-(t_h/2)):
        return True



while True:
    gamestate="Title"
    # print(gamestate,'\n',pos)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            break
        elif event.type == MOUSEBUTTONUP :
            print("click!")
            if on_play_button(gamestate,pos,t_w,t_h):
                gamestate="Level Selection"
                pygame.quit()
                sys.exit()
                break

    screen.fill((86,150,0))
    screen.blit(title_image, title_image.get_rect(center=pos))
    pygame.display.flip()
    #program.display.update()
