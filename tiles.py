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


# ---------------------------
# Classe Spritesheet
# ---------------------------
class Spritesheet:
    def __init__(self, filename, tile_size=32, columns=9):
        self.spritesheet = pygame.image.load(filename).convert_alpha()
        self.tile_size = tile_size
        self.columns = columns

    def get_tile(self, index):
        x = (index % self.columns) * self.tile_size
        y = (index // self.columns) * self.tile_size
        return self.spritesheet.subsurface((x, y, self.tile_size, self.tile_size))

# ---------------------------
# Classe Tile
# ---------------------------
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_index, x, y, spritesheet):
        pygame.sprite.Sprite.__init__(self)
        self.image = spritesheet.get_tile(tile_index)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.x, self.y = x, y
        self.vertices = []
        self.angle = 0
        self.index = tile_index
        self.attribution()
        self.priority = 0

    def attribution(self):
        x, y = self.rect.x, self.rect.y
        tile_vertices = {
            0: [(x, y), (x + 32, y + 32), (x + 32, y), (x, y + 32)],
            1: [(x, y), (x + 32, y + 32), (x + 32, y), (x, y + 32)],
            2: [(x, y), (x + 32, y + 32), (x + 32, y), (x, y + 32)],
            3: [(x, y), (x + 32, y + 32), (x + 32, y), (x, y + 32)],
            4: [(x, y), (x + 32, y + 32), (x + 32, y), (x, y + 32)],
            5: [(x + 32, y + 32), (x, y + 32), (x + 32, y)],
            6: [(x + 32, y + 32), (x, y + 32), (x + 32, y + 17)],
            7: [(x + 32, y + 32), (x + 32, y), (x, y + 32), (x, y + 16)],
            8: [(x + 32, y + 32), (x, y + 32), (x + 32, y + 23)],
            9: [(x + 32, y + 32), (x + 32, y + 26), (x, y + 32), (x, y + 12)],
            10: [(x + 32, y + 32), (x + 32, y), (x, y + 32), (x, y + 11)],
            11: [(x + 32, y + 32), (x + 32, y), (x + 17, y + 32)],
            12: [(x + 32, y + 32), (x + 32, y), (x, y + 32), (x + 15, y)],
            13: [(x + 32, y + 32), (x + 32, y), (x + 23, y + 32)],
            14: [(x + 32, y + 32), (x + 32, y), (x + 12, y + 32), (x + 22, y)],
            15: [(x + 32, y + 32), (x + 32, y), (x + 10, y), (x, y + 32)],
            16: [(x + 32, y + 32), (x, y), (x, y + 32)],
            17: [(x + 32, y + 32), (x, y + 32), (x, y + 17)],
            18: [(x + 32, y + 32), (x, y), (x, y + 32), (x + 32, y + 16)],
            19: [(x + 32, y + 32), (x, y + 32), (x + 32, y + 23)],
            20: [(x + 32, y + 32), (x + 32, y + 12), (x, y + 32), (x, y + 22)],
            21: [(x + 32, y + 32), (x, y), (x, y + 32), (x + 32, y + 11)],
            22: [(x, y), (x, y + 32), (x + 15, y + 32)],
            23: [(x + 32, y + 32), (x, y), (x, y + 32), (x + 17, y)],
            24: [(x, y + 32), (x, y), (x + 10, y + 32)],
            25: [(x, y), (x, y + 32), (x + 11, y), (x + 21, y + 32)],
            26: [(x + 32, y + 32), (x, y), (x + 10, y), (x + 23, y)],
        }
        self.vertices = tile_vertices[self.index]
        if self.vertices != [(x, y), (x + 32, y + 32), (x + 32, y), (x, y + 32)] :
            self.priority = 1
        else :
            self.priority = 0

# ---------------------------
# Classe Tilemap
# ---------------------------
class Tilemap:
    def __init__(self, filename, spritesheet):
        self.tile_size = 32
        self.tiles = self.load_tiles(filename, spritesheet)

    def read_csv(self, filename):
        map_data = []
        with open(filename) as data:
            reader = csv.reader(data, delimiter=',')
            for row in reader:
                map_data.append(list(row))
        return map_data

    def load_tiles(self, filename, spritesheet):
        tiles = []
        tile_map = self.read_csv(filename)
        y = 0
        for row in tile_map:
            x = 0
            for tile in row:
                tile_index = int(tile)
                if tile_index != -1:
                    tiles.append(Tile(tile_index, x * self.tile_size, y * self.tile_size, spritesheet))
                x += 1
            y += 1
        return tiles

    def draw(self, surface):
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