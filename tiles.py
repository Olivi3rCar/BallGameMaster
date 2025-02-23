import pygame
import csv
import os

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


# Classe Tile
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_index, x, y, spritesheet):
        pygame.sprite.Sprite.__init__(self)
        self.image = spritesheet.get_tile(tile_index)  # Extrait la bonne tile
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y


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