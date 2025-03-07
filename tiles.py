import pygame
import csv
import os
from pytmx import *
# Initialisation de Pygame
pygame.init()

# Taille de la fenêtre
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tilemap Loader")

# Couleurs
WHITE = (255, 255, 255)


# Classe Spritesheet pour extraire les tiles
class Spritesheet:
    def __init__(self, filename, tile_size=32, columns=9):
        self.spritesheet = pygame.image.load(filename).convert_alpha()
        self.tile_size = tile_size
        self.columns = columns  # Nombre de colonnes dans la spritesheet

    def get_tile(self, index):
        """Retourne une surface correspondant à la tile avec l'index donné"""
        x = (index % self.columns) * self.tile_size
        y = (index // self.columns) * self.tile_size
        return self.spritesheet.subsurface((x, y, self.tile_size, self.tile_size))

#We need to modify the tile creation and get_tile so we can get what we want

# Classe Tile
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_index, x, y, spritesheet):
        pygame.sprite.Sprite.__init__(self)
        self.image = spritesheet.get_tile(tile_index)  # Extrait la bonne tile
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.vertices = []
        self.angle = 0

    def attribution(self):
        x,y = self.x,self.y
        if self.index in [1,2,3,4,0] :
            self.angle = 0
            self.vertices = [(x,y),(x+32,y+32),(x+32,y),(x,y+32)]
        elif self.index == 5:
            self.angle = 45
            self.vertices = [(x+32,y+32),(x,y+32),(x+32,y)]
        elif self.index in [6,7] :
            self.angle = 22.5
            if self.index == 6:
                self.vertices = [(x+32,y+32),(x,y+32),(x+32,y+17)]
            else :
                self.vertices = [(x+32,y+32),(x+32,y),(x,y+32),(x,y+16)]
        elif self.index in [8,9,10] :
            self.angle = 11.25
            if self.index == 8:
                self.vertices = [(x+32,y+32),(x,y+32),(x+32,y+23)]
            elif self.index == 9:
                self.vertices = [(x+32,y+32),(x+32,y+26),(x,y+32),(x,y+12)]
            else :
                self.vertices = [(x+32,y+32),(x+32,y),(x,y+32),(x,y+11)]
        elif self.index in [11,12] :
            self.angle = 63.4
            if self.index == 11 :
                self.vertices = [(x + 32, y + 32), (x + 32, y), (x + 17, y + 32)]
            else :
                self.vertices = [(x+32,y+32),(x+32,y),(x,y+32),(x+15,y)]
        elif self.index in [13,14,15] :
            self.angle = 72.6
            if self.index == 13:
                self.vertices = [(x+32,y+32),(x+32,y),(x+23,y+32)]
            elif self.index == 14:
                self.vertices = [(x+32,y+32),(x+32,y),(x+12,y+32),(x+22,y)]
            else :
                self.vertices = [(x+32,y+32),(x+32,y),(x+10,y),(x,y+32)]
        elif self.index == 16 :
            self.angle = 135
            self.vertices = [(x+32,y+32),(x,y),(x,y+32)]
        elif self.index in [17,18] :
            self.angle = 157.5
            if self.index == 17:
                self.vertices = [(x+32,y+32),(x,y+32),(x,y+17)]
            else:
                self.vertices = [(x+32,y+32),(x,y),(x,y+32),(x+32,y+16)]
        elif self.index in [19,20,21] :
            self.angle = 101.25
            if self.index == 19:
                self.vertices = [(x+32,y+32),(x,y+32),(x+32,y+23)]
            elif self.index == 20:
                self.vertices = [(x+32,y+32),(x+32,y+12),(x,y+32),(x,y+22)]
            else :
                self.vertices = [(x+32,y+32),(x,y),(x,y+32),(x+32,y+11)]
        elif self.index in [22,23] :
            self.angle = 116.6
            if self.index == 22 :
                self.vertices = [(x,y),(x,y+32),(x+15,y+32)]
            else :
                self.vertices = [(x+32,y+32),(x,y),(x,y+32),(x+17,y)]
        else : #24,25,26
            self.angle = 107.4
            if self.index == 24:
                self.vertices = [(x,y+32),(x,y),(x+10,y+32)]
            elif self.index == 25:
                self.vertices = [(x,y),(x,y+32),(x+11,y),(x+21,y+32)]
            else :
                self.vertices = [(x+32,y+32),(x,y),(x+10,y),(x+23,y)]



# Classe Tilemap
class Tilemap:
    def __init__(self, filename, spritesheet):
        self.tile_size = 32
        self.tiles = self.load_tiles(filename, spritesheet)

    def read_csv(self, filename):
        """Lit le fichier CSV et retourne une liste contenant la carte"""
        map_data = []
        with open(filename) as data:
            reader = csv.reader(data, delimiter=',')
            for row in reader:
                map_data.append(list(row))
        return map_data

    def load_tiles(self, filename, spritesheet):
        """Charge les tiles à partir du fichier CSV"""
        tiles = []
        tile_map = self.read_csv(filename)
        y = 0
        for row in tile_map:
            x = 0
            for tile in row:
                tile_index = int(tile)  # Convertir en entier
                if tile_index != -1:  # -1 = espace vide
                    tiles.append(Tile(tile_index, x * self.tile_size, y * self.tile_size, spritesheet))
                x += 1
            y += 1
        return tiles # Our array of tiles

    def draw(self, surface):
        """Dessine toutes les tiles sur l'écran"""
        for tile in self.tiles:
            surface.blit(tile.image, (tile.rect.x, tile.rect.y))


# Charger la spritesheet
spritesheet = Spritesheet(os.path.join("Sprites png/sandtiles.png"), tile_size=32, columns=9)  # Chemin à adapter

# Charger la tilemap
tilemap = Tilemap("tiles_maps/test_map.csv", spritesheet)  # Chemin à adapter

# Boucle de jeu
running = True
while running:
    screen.fill((0,0,0))  # Fond blanc

    tilemap.draw(screen)  # Affiche la tilemap

    pygame.display.flip()  # Rafraîchir l'écran

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()