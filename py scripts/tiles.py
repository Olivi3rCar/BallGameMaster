import pygame
import csv
import os

def grow_hitbox(vertices, factor=1.0):
    """Artificially grows or shrinks the hitbox of the tiles"""
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
        """Creation of the spritesheet from the png image"""
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
        """Creation of the tiles"""
        pygame.sprite.Sprite.__init__(self)
        self.image = spritesheet.get_tile(tile_index)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.x, self.y = x, y
        self.vertices = []
        self.index = tile_index #So we know which kind of tiles we have
        self.attribution() #Absolute pain
        self.broken = 0

    def attribution(self):
        """Pain, eternal pain
        Creates the hitbox of each tile, I had to count myself each pixel of the sides"""
        x, y = self.rect.x, self.rect.y

        """We shrink the squares, while growing the slopes, so squares under the slope
        will not interfere with the ball's movement"""
        tile_vertices = {
            0: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),
            27: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),
            54: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),
            1: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),
            28: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),
            55: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),
            2: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),
            29: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),
            56: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),
            3: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),
            30: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),
            57: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),
            4: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),
            31: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),
            58: grow_hitbox([(x + 32, y), (x + 32, y + 32),
                            (x, y + 32), (x, y)], 0.9),

            # À partir de 5, on applique un facteur > 1.0 pour grossir la hitbox
            5: grow_hitbox([(x + 32, y + 32), (x, y + 32),
                             (x + 34, y)], 1.1),
            32: grow_hitbox([(x + 32, y + 32), (x, y + 32),
                            (x + 34, y)], 1.1),
            59: grow_hitbox([(x + 32, y + 32), (x, y + 32),
                            (x + 34, y)], 1.1),
            6: grow_hitbox([(x, y + 32), (x + 32, y + 32),
                            (x + 32, y + 17)], 1.1),
            33: grow_hitbox([(x, y + 32), (x + 32, y + 32),
                            (x + 32, y + 17)], 1.1),
            60: grow_hitbox([(x, y + 32), (x + 32, y + 32),
                            (x + 32, y + 17)], 1.1),
            7: grow_hitbox([(x, y + 16), (x, y + 32),
                            (x + 32, y + 32), (x + 32, y)], 1.1),
            34: grow_hitbox([(x, y + 16), (x, y + 32),
                            (x + 32, y + 32), (x + 32, y)], 1.1),
            61: grow_hitbox([(x, y + 16), (x, y + 32),
                            (x + 32, y + 32), (x + 32, y)], 1.1),
            8: grow_hitbox([(x + 32, y + 32), (x, y + 32),
                            (x + 32, y + 23)], 1.1),
            35: grow_hitbox([(x + 32, y + 32), (x, y + 32),
                            (x + 32, y + 23)], 1.1),
            62: grow_hitbox([(x + 32, y + 32), (x, y + 32),
                            (x + 32, y + 23)], 1.1),
            9: grow_hitbox([(x + 32, y + 32), (x + 32, y + 12),
                            (x, y + 22), (x, y + 32)], 1.1),
            36: grow_hitbox([(x + 32, y + 32), (x + 32, y + 12),
                            (x, y + 22), (x, y + 32)], 1.1),
            63: grow_hitbox([(x + 32, y + 32), (x + 32, y + 12),
                            (x, y + 22), (x, y + 32)], 1.1),
            10: grow_hitbox([(x, y + 11), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y)], 1.1),
            37: grow_hitbox([(x, y + 11), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y)], 1.1),
            64: grow_hitbox([(x, y + 11), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y)], 1.1),
            11: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 17, y + 32)], 1.1),
            38: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 17, y + 32)], 1.1),
            65: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 17, y + 32)], 1.1),
            12: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 15, y), (x, y + 32)], 1.1),
            39: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 15, y), (x, y + 32)], 1.1),
            66: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 15, y), (x, y + 32)], 1.1),
            13: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 23, y + 32)], 1.1),
            40: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 23, y + 32)], 1.1),
            67: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 23, y + 32)], 1.1),
            14: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 22, y), (x + 12, y + 32)], 1.1),
            41: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 22, y), (x + 12, y + 32)], 1.1),
            68: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 22, y), (x + 12, y + 32)], 1.1),
            15: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 10, y), (x, y + 32)], 1.1),
            42: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 10, y), (x, y + 32)], 1.1),
            69: grow_hitbox([(x + 32, y + 32), (x + 32, y),
                             (x + 10, y), (x, y + 32)], 1.1),
            16: grow_hitbox([(x + 32, y + 32), (x, y),
                             (x, y + 32)], 1.1),
            43: grow_hitbox([(x + 32, y + 32), (x, y),
                             (x, y + 32)], 1.1),
            70: grow_hitbox([(x + 32, y + 32), (x, y),
                             (x, y + 32)], 1.1),
            17: grow_hitbox([(x + 32, y + 32), (x, y + 32),
                             (x, y + 17)], 1.1),
            44: grow_hitbox([(x + 32, y + 32), (x, y + 32),
                             (x, y + 17)], 1.1),
            71: grow_hitbox([(x + 32, y + 32), (x, y + 32),
                             (x, y + 17)], 1.1),
            18: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y + 16)], 1.1),
            45: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y + 16)], 1.1),
            72: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y + 16)], 1.1),
            19: grow_hitbox([(x + 32, y + 32), (x, y + 32),
                             (x, y + 23)], 1.1),
            46: grow_hitbox([(x + 32, y + 32), (x, y + 32),
                             (x, y + 23)], 1.1),
            73: grow_hitbox([(x + 32, y + 32), (x, y + 32),
                             (x, y + 23)], 1.1),
            20: grow_hitbox([(x, y + 12), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y + 22)], 1.1),
            47: grow_hitbox([(x, y + 12), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y + 22)], 1.1),
            74: grow_hitbox([(x, y + 12), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y + 22)], 1.1),
            21: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y + 11)], 1.1),
            48: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y + 11)], 1.1),
            75: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y + 11)], 1.1),
            22: grow_hitbox([(x, y), (x, y + 32),
                             (x + 15, y + 32)], 1.1),
            49: grow_hitbox([(x, y), (x, y + 32),
                             (x + 15, y + 32)], 1.1),
            76: grow_hitbox([(x, y), (x, y + 32),
                             (x + 15, y + 32)], 1.1),
            23: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 17, y)], 1.1),
            50: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 17, y)], 1.1),
            77: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 17, y)], 1.1),
            24: grow_hitbox([(x, y), (x, y + 32),
                             (x + 10, y + 32)], 1.1),
            51: grow_hitbox([(x, y), (x, y + 32),
                             (x + 10, y + 32)], 1.1),
            78: grow_hitbox([(x, y), (x, y + 32),
                             (x + 10, y + 32)], 1.1),
            25: grow_hitbox([(x, y), (x, y + 32),
                             (x + 21, y + 32), (x + 11, y)], 1.1),
            52: grow_hitbox([(x, y), (x, y + 32),
                             (x + 21, y + 32), (x + 11, y)], 1.1),
            79: grow_hitbox([(x, y), (x, y + 32),
                             (x + 21, y + 32), (x + 11, y)], 1.1),
            26: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 23, y)], 1.1),
            53: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 23, y)], 1.1),
            80: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 23, y)], 1.1),

            #ice slabs (to be broken)
            81: grow_hitbox([(x, y), (x, y + 16),
                             (x + 32, y + 16), (x + 32, y)], 1.1),
            82: grow_hitbox([(x, y), (x, y + 16),
                             (x + 32, y + 16), (x + 32, y)], 1.1),
            83: grow_hitbox([(x, y), (x, y + 16),
                             (x + 32, y + 16), (x + 32, y)], 1.1),
            84: grow_hitbox([(x, y), (x, y + 16),
                             (x + 32, y + 16), (x + 32, y)], 1.1),
            85: grow_hitbox([(x, y), (x, y + 16),
                             (x + 32, y + 16), (x + 32, y)], 1.1),

            #brick
            86: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y)], 0.9),

            #water
            87: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y)], 0.9),
            88: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y)], 0.9),
            89: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y)], 0.9),
            90: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y)], 0.9),
            91: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y)], 0.9),
            92: grow_hitbox([(x, y), (x, y + 32),
                             (x + 32, y + 32), (x + 32, y)], 0.9)
        }

        # Assign the vertices
        self.vertices = tile_vertices[self.index]

# ---------------------------
# Class Tilemap
# ---------------------------
class Tilemap:
    """Creates the tilemap """
    def __init__(self, filename, spritesheet):
        self.tile_size = 32
        self.tiles = self.load_tiles(filename, spritesheet)

    def read_csv(self, filename):
        """Reads the data of the level in a csv file"""
        map_data = []
        with open(filename) as data:
            reader = csv.reader(data, delimiter=',')
            for row in reader:
                map_data.append(list(row))
        return map_data

    def load_tiles(self, filename, spritesheet):
        """Creation of the tilemap"""
        tiles = []
        tile_map = self.read_csv(filename)
        y = 0
        for row in tile_map:
            x = 0
            for tile in row:
                tile_index = int(tile)
                if tile_index != -1 and tile_index < 94:
                    tiles.append(Tile(tile_index, x * self.tile_size, y * self.tile_size, spritesheet))
                x += 1
            y += 1
        return tiles

    def draw(self, surface):
        """Drawing the tilemap"""
        for tile in self.tiles:
            surface.blit(tile.image, (tile.rect.x, tile.rect.y))