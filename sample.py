import pygame
import random
from threading import Thread

# Screen constants
SCREEN_WIDTH = 606
SCREEN_HEIGHT = 606
BLOCK_SIZE = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Other colors for the rainbow effect
RAINBOW_COLORS = [(148, 0, 211), (75, 0, 130), (0, 0, 255), (0, 255, 0), (255, 255, 0), (255, 127, 0), (255, 0, 0)]
current_rainbow_color = 0

# Initialize pygame
pygame.init()

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Pacman Space Rainbow Edition')

# Load images
pacman_image = pygame.image.load('C:/Users/USER/Desktop/Django/minePy/pacman/images/pacman.png')
blinky_image = pygame.image.load('C:/Users/USER/Desktop/Django/minePy/pacman/images/Blinky.png')
pinky_image = pygame.image.load('C:/Users/USER/Desktop/Django/minePy/pacman/images/Pinky.png')
inky_image = pygame.image.load('C:/Users/USER/Desktop/Django/minePy/pacman/images/Inky.png')
clyde_image = pygame.image.load('C:/Users/USER/Desktop/Django/minePy/pacman/images/Clyde.png')

# Sound effects and music
def play_sound(path, loop=False):
    if loop:
        pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)
    else:
        sound_effect = pygame.mixer.Sound(path)
        sound_effect.play()

def play_game_music():
    play_sound('C:/Users/USER/Desktop/Django/minePy/pacman/b2moon.mp3', True)

def play_collision_sound():
    play_sound('C:/Users/USER/Desktop/Django/minePy/pacman/hit_sound.mp3')

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.change_x = 0
        self.change_y = 0
        self.prev_x = x
        self.prev_y = y
        self.collided = False

    def change_speed(self, x, y):
        self.change_x += x
        self.change_y += y

    def update(self, walls, gate):
        old_x = self.rect.left
        old_y = self.rect.top

        new_x = old_x + self.change_x
        new_y = old_y + self.change_y

        self.rect.left = new_x
        self.rect.top = new_y

        x_collide = pygame.sprite.spritecollide(self, walls, False)
        if x_collide:
            self.rect.left = old_x
        else:
            y_collide = pygame.sprite.spritecollide(self, walls, False)
            if y_collide:
                self.rect.top = old_y

        if gate:
            gate_hit = pygame.sprite.spritecollide(self, gate, False)
            if gate_hit:
                self.rect.left = old_x
                self.rect.top = old_y

    def reset_position(self, x, y):
        self.rect.left = x
        self.rect.top = y

# Wall class
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# Block class for yellow balls
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([BLOCK_SIZE, BLOCK_SIZE])
        self.image.fill(WHITE)
        pygame.draw.ellipse(self.image, YELLOW, [0, 0, BLOCK_SIZE, BLOCK_SIZE])
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# Ghost class
class Ghost(Player):
    def __init__(self, x, y, image, directions):
        super().__init__(x, y, image)
        self.directions = directions
        self.turn = 0
        self.steps = 0

    def update(self, walls, gate):
        returned = self.change_speed(self.directions, self.turn, self.steps)
        self.turn = returned[0]
        self.steps = returned[1]
        super().update(walls, gate)

    def change_speed(self, directions, turn, steps):
        try:
            direction = directions[turn]
            if steps < direction[2]:
                self.change_x = direction[0]
                self.change_y = direction[1]
                steps += 1
            else:
                if turn < len(directions) - 1:
                    turn += 1
                else:
                    turn = 0
                direction = directions[turn]
                self.change_x = direction[0]
                self.change_y = direction[1]
                steps = 0
            return [turn, steps]
        except IndexError:
            return [0, 0]

# Function to generate a rainbow color
def get_rainbow_color():
    global current_rainbow_color
    color = RAINBOW_COLORS[current_rainbow_color]
    current_rainbow_color = (current_rainbow_color + 1) % len(RAINBOW_COLORS)
    return color

# Function to create all walls in room 1 and add them to sprite groups
def setup_room_one(all_sprites_list):
    wall_list = pygame.sprite.Group()
    walls = [
        [0, 0, 6, SCREEN_HEIGHT],
        [0, 0, SCREEN_WIDTH, 6],
        [0, SCREEN_HEIGHT - 6, SCREEN_WIDTH, 6],
        [SCREEN_WIDTH - 6, 0, 6, SCREEN_HEIGHT],
        # Other wall dimensions here ...
    ]

    for item in walls:
        wall = Wall(item[0], item[1], item[2], item[3], get_rainbow_color())
        wall_list.add(wall)
        all_sprites_list.add(wall)

    return wall_list

# Function to create the gate
def setup_gate(all_sprites_list):
    gate = pygame.sprite.Group()
    gate.add(Wall(282, 242, 42, 2, WHITE))
    all_sprites_list.add(gate)
    return gate

# Function to create yellow balls and add them to sprite groups
def setup_yellow_balls(all_sprites_list, walls, pacman_collide):
    block_list = pygame.sprite.Group()
    for row in range(19):
        for column in range(19):
            if (row == 7 or row == 8) and (column == 8 or column == 9 or column == 10):
                continue
            else:
                block = Block(column * BLOCK_SIZE + 6 + 26, row * BLOCK_SIZE + 6 + 26)

                b_collide = pygame.sprite.spritecollide(block, walls, False)
                p_collide = pygame.sprite.spritecollide(block, pacman_collide, False)

                if not b_collide and not p_collide:
                    block_list.add(block)
                    all_sprites_list.add(block)

    return block_list

# Function to show game over message
def game_over_message():
    font = pygame.font.Font(None, 74)
    text = font.render("Game Over", True, RED)
    screen.blit(text, [150, 300])
    pygame.display.flip()
    pygame.time.wait(2000)

# Main game loop
def game_loop():
    all_sprites_list = pygame.sprite.Group()

    pacman_collide = pygame.sprite.Group()
    blinky_collide = pygame.sprite.Group()
    pinky_collide = pygame.sprite.Group()
    inky_collide = pygame.sprite.Group()
    clyde_collide = pygame.sprite.Group()

    walls = setup_room_one(all_sprites_list)
    gate = setup_gate(all_sprites_list)
    pacman_collide.add(walls, gate)

    player = Player(287, 439, pacman_image)
    players_list = pygame.sprite.Group()
    players_list.add(player)
    all_sprites_list.add(player)

    blinky = Ghost(287, 259, blinky_image, [[0, -2, 20], [2, 0, 20], [0, 2, 20], [-2, 0, 20]])
    blinky_collide.add(walls, gate)
    players_list.add(blinky)
    all_sprites_list.add(blinky)

    pinky = Ghost(255, 299, pinky_image, [[0, -2, 20], [2, 0, 20], [0, 2, 20], [-2, 0, 20]])
    pinky_collide.add(walls, gate)
    players_list.add(pinky)
    all_sprites_list.add(pinky)

    inky = Ghost(319, 299, inky_image, [[2, 0, 20], [0, 2, 20], [-2, 0, 20], [0, -2, 20]])
    inky_collide.add(walls, gate)
    players_list.add(inky)
    all_sprites_list.add(inky)

    clyde = Ghost(287, 299, clyde_image, [[0, 2, 20], [-2, 0, 20], [0, -2, 20], [2, 0, 20]])
    clyde_collide.add(walls, gate)
    players_list.add(clyde)
    all_sprites_list.add(clyde)

    yellow_balls = setup_yellow_balls(all_sprites_list, walls, pacman_collide)

    score = 0
    player_direction = 0
    change_player_x = 0
    change_player_y = 0

    done = False
    clock = pygame.time.Clock()

    # Start background music thread
    bg_music_thread = Thread(target=play_game_music)
    bg_music_thread.start()

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    change_player_x = -2
                    change_player_y = 0
                    player_direction = 180
                elif event.key == pygame.K_RIGHT:
                    change_player_x = 2
                    change_player_y = 0
                    player_direction = 0
                elif event.key == pygame.K_UP:
                    change_player_y = -2
                    change_player_x = 0
                    player_direction = 90
                elif event.key == pygame.K_DOWN:
                    change_player_y = 2
                    change_player_x = 0
                    player_direction = 270

        player.change_speed(change_player_x, change_player_y)
        change_player_x = 0
        change_player_y = 0

        all_sprites_list.update(walls, gate)

        # Collide detection
        yellow_blocks_hit = pygame.sprite.spritecollide(player, yellow_balls, True)
        for block in yellow_blocks_hit:
            score += 1
            play_collision_sound()

        ghost_hit_list = pygame.sprite.spritecollide(player, blinky_collide, False)
        if ghost_hit_list:
            done = True

        ghost_hit_list = pygame.sprite.spritecollide(player, pinky_collide, False)
        if ghost_hit_list:
            done = True

        ghost_hit_list = pygame.sprite.spritecollide(player, inky_collide, False)
        if ghost_hit_list:
            done = True

        ghost_hit_list = pygame.sprite.spritecollide(player, clyde_collide, False)
        if ghost_hit_list:
            done = True

        # Clear the screen
        screen.fill(BLACK)

        all_sprites_list.draw(screen)

        # Draw the score
        font = pygame.font.Font(None, 34)
        text = font.render("Score: " + str(score), True, WHITE)
        screen.blit(text, [10, 10])

        # Update the screen
        pygame.display.flip()

        # Set the frame rate
        clock.tick(60)

    # Game over message
    game_over_message()

# Start the game
if __name__ == "__main__":
    game_loop()
    pygame.quit()
