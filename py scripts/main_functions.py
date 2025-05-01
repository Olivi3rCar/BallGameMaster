import sys
from pygame.locals import *
from math import *
from tiles import *
from physics import gameplay, Ball, on_button
from random import randint



class GameState:
    """Class to store the game state and resources, such as sprites and their coordinates"""

    def __init__(self):
        # Game screens
        self.screen = None
        self.clock = None
        self.scene = "Title"
        self.first_frame = True
        self.disable_back = False

        # Screen positioning
        self.center_x = None
        self.center_y = None

        # Paths to background sprites, doing it here because we need it later

        self.sprite_path = None
        self.level_path = None

        # UI images and resources
        self.title_image = None
        self.splash = None
        self.play = None
        self.worldselect = None
        self.bckgroundgrass = None
        self.bckgroundsand = None
        self.bckgroundice = None
        self.buttons = None
        self.endlevel = None
        self.numbers = None
        self.reactions = None

        # Button dimensions
        self.button_rects = {
            'play': {
                'off': (0, 0, 80 * 3, 20 * 3),
                'on': (80 * 3, 0, 160 * 3, 20 * 3)
            },
            'back': {
                'off': (0, 0, 48, 48),
                'on': (48, 0, 48, 48)
            },
            'w1': {
                'lvl1': {'off': (0, 96, 48, 48), 'on': (48, 96, 48, 48)},
                'lvl2': {'off': (96, 96, 48, 48), 'on': (144, 96, 48, 48)},
                'lvl3': {'off': (0, 144, 48, 48), 'on': (48, 144, 48, 48)},
                'lvl4': {'off': (96, 144, 48, 48), 'on': (144, 144, 48, 48)},
                'lvl5': {'off': (0, 192, 48, 48), 'on': (48, 192, 48, 48)}
            },
            'w2': {
                'lvl1': {'off': (0, 240, 48, 48), 'on': (48, 240, 48, 48)},
                'lvl2': {'off': (96, 240, 48, 48), 'on': (144, 240, 48, 48)},
                'lvl3': {'off': (0, 288, 48, 48), 'on': (48, 288, 48, 48)},
                'lvl4': {'off': (96, 288, 48, 48), 'on': (144, 288, 48, 48)},
                'lvl5': {'off': (0, 336, 48, 48), 'on': (48, 336, 48, 48)}
            },
            'w3': {
                'lvl1': {'off': (0, 384, 48, 48), 'on': (48, 384, 48, 48)},
                'lvl2': {'off': (96, 384, 48, 48), 'on': (144, 384, 48, 48)},
                'lvl3': {'off': (0, 432, 48, 48), 'on': (48, 432, 48, 48)},
                'lvl4': {'off': (96, 432, 48, 48), 'on': (144, 432, 48, 48)},
                'lvl5': {'off': (0, 480, 48, 48), 'on': (48, 480, 48, 48)}
            }
        }

        # Button positions for all levels
        self.level_positions = {
            'grass': {
                1: (500, 300), 2: (353, 277), 3: (109, 266),
                4: (177, 180), 5: (518, 37)
            },
            'sand': {
                1: (530, 302), 2: (96, 238), 3: (244, 200),
                4: (378, 295), 5: (330, 54)
            },
            'ice': {
                1: (500, 395), 2: (470, 275), 3: (25, 310),
                4: (350, 45), 5: (145, 45)
            }
        }

        # Background dimensions
        self.background_dim = (0, 0, 640, 480)
        
        # World to button transition
        self.world_button_map = {
            'grass': 'w1',
            'sand': 'w2',
            'ice': 'w3'
        }


        # Level backgrounds
        self.backgrounds = {
            'grass': {},
            'sand': {},
            'ice': {}
        }

        # Dimensions for the end level screen
        self.number_rects = {"0123456789:"[i]: (14 * i, 0, 14, 25) for i in range(11)}
        self.reaction_rects = [(139 * i * 2, 0, 139 * 2, 30 * 2) for i in range(4)]
        self.endlevel_rects = {f"w{i}" : (640 * (i-1), 0, 640, 480) for i in range(1,4)}

        # Level files
        self.level_files = {
            'grass': {},
            'sand': {},
            'ice': {}
        }

        # Level data (position of buttons)
        self.levels = {}

        # Sprite sheet columns
        self.tile_columns = {
            'grass': 9,
            'sand': 9,
            'ice': 11
        }

        # Scene to world mapping
        self.scene_to_world = {
            'Forest': 'grass',
            'Desert': 'sand',
            'Ice': 'ice',
            'GrassLevel': 'grass',
            'SandLevel': 'sand',
            'IceLevel': 'ice'
        }

        # World to level scene mapping
        self.world_to_level_scene = {
            'grass': 'GrassLevel',
            'sand': 'SandLevel',
            'ice': 'IceLevel'
        }

        # Level file naming templates
        self.level_file_templates = {
            'grass': "grass_level_{}.csv",
            'sand': "sand_level_{}.csv",
            'ice': "ice_level_{}.csv"
        }


# Create global game state
game = GameState()


def init_game():
    """Initialize the game, load resources and set up global variables"""
    global game

    # Initialize pygame and create game window
    pygame.init()
    game.clock = pygame.time.Clock()
    game.screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Ball Game')

    game.sprite_path = os.path.abspath(os.path.join("./main.py", os.pardir))
    game.sprite_path = str(game.sprite_path)[:-10] + "Sprites png\\"

    # Resource paths for spritesheets
    game.tile_paths = {
        'grass': game.sprite_path + "groundtiles.png",
        'sand': game.sprite_path + "sandtiles.png",
        'ice': game.sprite_path + "icetiles.png"
    }

    # Load all images
    game.title_image = pygame.image.load(game.sprite_path + "Title.png")
    game.title_image = pygame.transform.scale(game.title_image,
                                              (2 * game.title_image.get_width(),
                                               2 * game.title_image.get_height()))

    game.splash = pygame.image.load(game.sprite_path + "Putt_it_in.png")

    game.play = pygame.image.load(game.sprite_path + "Let'sPlayButton.png")
    game.play = pygame.transform.scale(game.play, (3 * game.play.get_width(), 3 * game.play.get_height()))

    game.worldselect = pygame.image.load(game.sprite_path + "stageselect.png")

    game.bckgroundgrass = pygame.image.load(game.sprite_path + "bckgroundgrass.png")
    game.bckgroundsand = pygame.image.load(game.sprite_path + "bckgroundsand.png")
    game.bckgroundice = pygame.image.load(game.sprite_path + "bckgroundice.png")

    game.buttons = pygame.image.load(game.sprite_path + "Buttons.png")
    game.buttons = pygame.transform.scale(game.buttons,
                                          (3 * game.buttons.get_width(), 3 * game.buttons.get_height()))

    game.endlevel = pygame.image.load(game.sprite_path + "endlevel.png")
    game.numbers = pygame.image.load(game.sprite_path + "numbers.png")
    game.reactions = pygame.image.load(game.sprite_path + "reactions.png")
    game.reactions = pygame.transform.scale(game.reactions,
                                              (2 * game.reactions.get_width(),
                                               2 * game.reactions.get_height()))

    # Set up background images for levels
    backgrounds_data = {
        'grass': game.bckgroundgrass,
        'sand': game.bckgroundsand,
        'ice': game.bckgroundice
    }

    # Load backgrounds for each level
    for world, background in backgrounds_data.items():
        for i in range(1, 6):
            game.backgrounds[world][i] = background.subsurface((640 * i, 0, 640, 480))

    # Store paths to level files
    game.level_path = game.sprite_path[:-12] + "Levels\\"

    # Initialize level csv with file name templates
    for world, template in game.level_file_templates.items():
        for i in range(1, 6):
            game.level_files[world][i] = game.level_path + template.format(i)

    #Restoring path to sprites
    game.sprite_path = game.level_path[:-7] + "Sprites png\\"

    # Assemble level data by combining level files and positions dictionnaries defined uptop
    for world in ['grass', 'sand', 'ice']:
        game.levels[world] = {}
        for level in range(1, 6):
            game.levels[world][level] = (game.level_files[world][level], game.level_positions[world][level])

    # Get screen center
    game.center_x = game.screen.get_rect().centerx
    game.center_y = game.screen.get_rect().centery

def draw_nbr_string(nbr : str, pos : tuple):
    """
    Displays a string of numbers using sprites
    :param nbr: the string to be displayed (can contain numbers 0-9 and colon ':')
    :param pos: tuple of position for the upper left of the string
    """
    global game
    for i in range(len(nbr)):
        game.screen.blit(game.numbers, (pos[0]+ i*15, pos[1]), game.number_rects[nbr[i]])

def time_to_string(elapsed):
    return str(elapsed // 60) + ":" + '0'*(int(elapsed%60 <=10) + int(elapsed%60 == 0)) + str(elapsed % 60)

def draw_lvl_end_screen(w : str, lvl : int, time : int, strokes : int):
    """
    Displays the level end screen
    :param w: world ID (as 'wi', where i is the world ID)
    :param lvl: level
    :param time: time
    :param strokes: strokes
    """
    global game
    # Display the 'level beat' background

    game.screen.blit(game.endlevel,
                    game.worldselect.get_rect(center=(game.center_x, game.center_y)), game.endlevel_rects[w])
    # Display the level info
    draw_nbr_string(w[1]+':'+str(lvl), (290, 197))
    # Display the number of strokes to beat the level
    draw_nbr_string(str(strokes), (290, 233))
    # Display the time took to finish the level
    draw_nbr_string(time_to_string(time), (290, 270))
    # Display a funny message for the player's enjoyment
    game.screen.blit(game.reactions, (335,313), game.reaction_rects[(lvl+time+strokes)%4])




def draw_title_screen(x):
    """
    Draw the title screen with animated splash
    :param x: spash screen size scalar
    """

    global game

    #Required every frame, else the previous splash texts remain on screen (it's not the artist's vision)
    game.screen.fill((86, 150, 0))

    # Animate splash text
    splashscale = 0.4 * sin(x) + 2.5
    splashdisp = pygame.transform.scale(game.splash, (
        splashscale * game.splash.get_width(),
        splashscale * game.splash.get_height()
    ))

    # Draw elements
    game.screen.blit(game.play,
                     game.play.get_rect(center=(game.center_x + (40 * 3), game.center_y + 170)),
                     game.button_rects['play']['off'])
    game.screen.blit(game.title_image,
                     game.title_image.get_rect(center=(game.center_x, game.center_y - 60)))
    game.screen.blit(splashdisp,
                     splashdisp.get_rect(center=(game.center_x, game.center_y - 8)))

    # Change "Play" button appearance if mouse is over it
    if on_button((200, 380), (440, 440)):
        game.screen.blit(game.play,
                         game.play.get_rect(center=(game.center_x + (40 * 3), game.center_y + 170)),
                         game.button_rects['play']['on'])


def draw_world_selection():
    """Draw the world selection screen"""
    global game

    game.screen.blit(game.worldselect,
                     game.worldselect.get_rect(center=(game.center_x, game.center_y)),
                     (0, 0, 680, 480))


    draw_lvl_end_screen('w3', 4, 125, 644654684)


def draw_level_selection(world):
    """Draw the level selection screen for a specific world
    :param world: The world selected by the player
    :return: first_frame: returns False if this is the first frame the level selection screen is drawn
    """
    global game
    # Map world to button set and background
    button_set = game.world_button_map[world]
    background = getattr(game, f"bckground{world}")

    if game.first_frame:
        # Initialize screen on first frame
        game.screen.blit(background, (0, 0), game.background_dim)

        # Draw all level buttons
        for level in range(1, 6):
            position = game.level_positions[world][level]
            game.screen.blit(game.buttons, position,
                             game.button_rects[button_set][f'lvl{level}']['off'])

        game.first_frame = False

    # Find the button that's being hovered (if any)
    hovered_level = None
    for level in range(1, 6):
        position = game.level_positions[world][level]
        button_width, button_height = 48, 48
        if on_button(position, (position[0] + button_width, position[1] + button_height)):
            hovered_level = level
            break

    # Draw buttons with appropriate state (on if hovered, off if not)
    for level in range(1, 6):
        position = game.level_positions[world][level]
        state = 'on' if level == hovered_level else 'off'
        game.screen.blit(game.buttons, position,
                         game.button_rects[button_set][f'lvl{level}'][state])

    return game.first_frame


def draw_back_button():
    """Draw the back button for navigation"""
    global game

    game.screen.blit(game.buttons, (0, 0), game.button_rects['back']['off'])

    if on_button((0, 0), (48, 48)):
        game.screen.blit(game.buttons, (0, 0), game.button_rects['back']['on'])
    else:
        game.screen.blit(game.buttons, (0, 0), game.button_rects['back']['off'])


def handle_events():
    """Handle all pygame events and return the updated scene"""
    global game

    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

        elif event.type == MOUSEBUTTONDOWN:
            # Title screen button
            if (game.scene == "Title") and on_button((200, 380), (440, 440)):
                game.scene = "World Selection"
                game.first_frame = True

            # World selection buttons
            elif game.scene == "World Selection":
                if on_button((0, 0), (640, 160)) and not (on_button((0, 0),
                                                                    (48, 48))):
                    game.scene = "Forest"
                    game.first_frame = True
                elif on_button((0, 160), (640, 320)):
                    game.scene = "Desert"
                    game.first_frame = True
                elif on_button((0, 320), (640, 480)):
                    game.scene = "Ice"
                    game.first_frame = True

            # Level selection for any world
            elif game.scene in ["Forest", "Desert", "Ice"]:
                world = game.scene_to_world[game.scene]

                # Create appropriate spritesheet for the world
                spritesheet = Spritesheet(
                    os.path.join(game.tile_paths[world]),
                    tile_size=32, columns=game.tile_columns[world]
                )

                # Create appropriate ball for the world
                ball = Ball(pygame.math.Vector2(400, 150), 7, 0.5, 0.6,
                            pygame.math.Vector2(0, 0), world)

                # Check if any level button was clicked
                for level in range(1, 6):
                    position = game.level_positions[world][level]
                    if on_button(
                            position,
                            (position[0] + 48, position[1] + 48)
                    ):
                        # Start gameplay for that level
                        gameplay(
                            game.screen,
                            ball,
                            Tilemap(game.level_files[world][level], spritesheet),
                            game.backgrounds[world][level]
                        )
                        game.scene = game.world_to_level_scene[world]
                        break

            # Back button logic
            if on_button((0, 0), (48, 48)) and game.disable_back == False:
                if game.scene in ["Forest", "Desert", "Ice"]:
                    game.scene = "World Selection"
                elif game.scene in ["GrassLevel", "SandLevel", "IceLevel"]:
                    # Map level scene back to world scene
                    world = game.scene_to_world[game.scene]
                    world_scenes = {
                        'grass': 'Forest',
                        'sand': 'Desert',
                        'ice': 'Ice'
                    }
                    game.scene = world_scenes[world]
                elif game.scene == "World Selection":
                    game.scene = "Title"

                game.first_frame = True
                game.disable_back = True

        # Reset the back button state when mouse button is released,
        # so that the player can't go back multiple scenes in one click
        elif event.type == MOUSEBUTTONUP:
            game.disable_back = False

    return game.scene


def game_loop():
    """Main game loop"""
    global game
    # Animation counter for title screen
    x = 0

    while True:
        # Cap fps to 120
        game.clock.tick(120)

        # Draw the appropriate scene
        if game.scene == "Title":
            draw_title_screen(x)
            # Update animation counter
            x += 1 / 40
        elif game.scene == "World Selection":
            draw_world_selection()
        elif game.scene == "Forest":
            game.first_frame = draw_level_selection('grass')
        elif game.scene == "Desert":
            game.first_frame = draw_level_selection('sand')
        elif game.scene == "Ice":
            game.first_frame = draw_level_selection('ice')

        # Draw back button for all scenes except title
        if game.scene != "Title":
            draw_back_button()

        # Handle events (input, buttons, etc.)
        game.scene = handle_events()

        # Update display
        pygame.display.flip()


def main():
    """Main function to start the game"""
    pygame.init()
    init_game()
    game_loop()