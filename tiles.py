import pygame
import csv
import os

def grow_hitbox(vertices, factor=1.0):
    center_x = sum(v[0] for v in vertices) / len(vertices)
    center_y = sum(v[1] for v in vertices) / len(vertices)
    new_vertices = []
    for v in vertices:
        direction_x = v[0] - center_x
        direction_y = v[1] - center_y
        new_x = center_x + direction_x * factor
        new_y = center_y + direction_y * factor
        new_vertices.append((new_x, new_y))
    return new_vertices


# ---------------------------
# Class Spritesheet
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
# Class Tile
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

        # Pour les tuiles 0 à 4, on garde un factor=1.0 (ou la valeur par défaut)
        # Pour les autres (5 à 26), on applique factor=1.1 (ajustable) afin de "gonfler" la hitbox.
        tile_vertices = {
            0: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),
            1: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),
            2: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),
            3: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),
            4: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),

            # À partir de 5, on applique un facteur > 1.0 pour grossir la hitbox
            5: grow_hitbox([(x + 32, y + 32), (x, y + 32), (x + 34, y)], 1.1),
            6: grow_hitbox([(x, y + 32), (x + 32, y + 32),
                            (x + 32, y + 17)], 1.1),
            7: grow_hitbox([(x, y + 16), (x, y + 32),
                            (x + 32, y + 32), (x + 32, y)], 1.1),
            8: grow_hitbox([(x + 32, y + 32), (x, y + 32),
                            (x + 32, y + 23)], 1.1),
            9: grow_hitbox([(x + 32, y + 32), (x + 32, y + 12),
                            (x, y + 22), (x, y + 32)], 1.1),
            10: grow_hitbox([(x, y + 11), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y)], 1.1),
            11: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 17, y + 32)], 1.1),
            12: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 15, y), (x, y + 32)], 1.1),
            13: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 23, y + 32)], 1.1),
            14: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 22, y), (x + 12, y + 32)], 1.1),
            15: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 10, y), (x, y + 32)], 1.1),
            16: grow_hitbox([(x + 32, y + 32), (x, y),
                             (x, y + 32)], 1.1),
            17: grow_hitbox([(x + 32, y + 32), (x, y + 32),
                             (x, y + 17)], 1.1),
            18: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y + 16)], 1.1),
            19: grow_hitbox([(x + 32, y + 32), (x, y + 32),
                             (x, y + 23)], 1.1),
            20: grow_hitbox([(x, y + 12), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y + 22)], 1.1),
            21: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y + 11)], 1.1),
            22: grow_hitbox([(x, y), (x, y + 32),
                             (x + 15, y + 32)], 1.1),
            23: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 17, y)], 1.1),
            24: grow_hitbox([(x, y), (x, y + 32),
                             (x + 10, y + 32)], 1.1),
            25: grow_hitbox([(x, y), (x, y + 32),
                             (x + 21, y + 32), (x + 11, y)], 1.1),
            26: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 23, y)], 1.1),
            27: grow_hitbox([(x + 32, y), (x + 32, y + 15),
                            (x, y + 15), (x, y)], 0.9),
            28: grow_hitbox([(x + 32, y), (x + 32, y + 15),
                            (x, y + 15), (x, y)], 0.9),
            29: grow_hitbox([(x + 32, y), (x + 32, y + 15),
                            (x, y + 15), (x, y)], 0.9),
            30: grow_hitbox([(x + 32, y), (x + 32, y + 15),
                            (x, y + 15), (x, y)], 0.9),
            31: grow_hitbox([(x + 32, y), (x + 32, y + 15),
                            (x, y + 15), (x, y)], 0.9)
        }

        # Assigne ensuite la liste de sommets à self.vertices
        self.vertices = tile_vertices[self.index]
        # Par exemple, si tu veux toujours mettre priority=1
        # pour les tiles non 0..4 :
        if self.index not in [0, 1, 2, 3, 4]:
            self.priority = 1
        else:
            self.priority = 0

        self.vertices = tile_vertices[self.index]
        if self.index not in [0, 1, 2, 3, 4]:
            self.priority = 1
        else:
            self.priority = 0




# ---------------------------
# Class Tilemap
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
