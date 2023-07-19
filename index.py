import pygame
from threading import Thread
import random
from database import Database


db = Database('pacman.db')
db.connect()


# setting rgb color codes to be used later
green = (1,255,1)
red = (255,1,1)
purple = (255,1,255)
yellow   = ( 255, 255,   1)
black = (1,1,1)
white = (255,255,255)
blue = (1,1,255)

# setting an icon for the game window
game_icon=pygame.image.load('C:/Users/USER/Desktop/Django/minePy/pacman/images/pacman.png')
pygame.display.set_icon(game_icon)

# adding background music for the game
def playSound(path, loop, bg):
  if bg:
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(loop, 0.0)
  else:
    sound_effect = pygame.mixer.Sound(path)
    sound_effect.play()



rainbow_colors = [(148, 0, 211), (75, 0, 130), (0, 0, 255), (0, 255, 0), (255, 255, 0), (255, 127, 0), (255, 0, 0)]
current_rainbow_color = 0

# This class represents is the blueprint for the obstacles/walls in our game
class Obstacle(pygame.sprite.Sprite):
    # Constructor function which is executed upon calling the  class
    def __init__(self,x,y,width,height, color):
        # Call the parent's constructor
        pygame.sprite.Sprite.__init__(self)
  
        # Make a blue wall, of the size specified in the parameters
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
  
        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x

# This creates all the walls in room 1 and adds them to 2 lists. One for walls and one for all sprites in the game to be used later
def createLevel(all_sprites_list):
    # Make the walls. (x_pos, y_pos, width, height)
    obstacle_list=pygame.sprite.RenderPlain()
     
    # This is a list of wall dimensions. Each is in the form [x, y, width, height]
    obstacles = [
              [0,0,6,600],
              [0,0,600,6],
              [0,600,606,6],
              [600,0,6,606],
              [300,0,6,66],
              [60,60,186,6],
              [360,60,186,6],
              [60,120,66,6],
              [60,120,6,126],
              [180,120,246,6],
              [300,120,6,66],
              [480,120,66,6],
              [540,120,6,126],
              [120,180,126,6],
              [120,180,6,126],
              [360,180,126,6],
              [480,180,6,126],
              [180,240,6,126],
              [180,360,246,6],
              [420,240,6,126],
              [240,240,42,6],
              [324,240,42,6],
              [240,240,6,66],
              [240,300,126,6],
              [360,240,6,66],
              [0,300,66,6],
              [540,300,66,6],
              [60,360,66,6],
              [60,360,6,186],
              [480,360,66,6],
              [540,360,6,186],
              [120,420,366,6],
              [120,420,6,66],
              [480,420,6,66],
              [180,480,246,6],
              [300,480,6,66],
              [120,540,126,6],
              [360,540,126,6]
            ]
    
     
    # iterate and add created obstacles to list
    for thing in obstacles:
      obstacle=Obstacle(thing[0],thing[1],thing[2],thing[3], colorChange())
      obstacle_list.add(obstacle)
      all_sprites_list.add(obstacle)
         
    # output list of obstacles
    return obstacle_list

# uses wall class to create gate that monsters come from
def createGate(sprite_list):
      gate_object = pygame.sprite.RenderPlain()
      gate_object.add(Obstacle(283,243,41,2,white))
      sprite_list.add(gate_object)
      return gate_object

# Class for little yellow balls that pacman has to eat to gain points that is created
class YellowBall(pygame.sprite.Sprite):
    # Class takes x, y position and color of block to constructor
    def __init__(self, color, w, h):
        # inherit the constructor of the parent
        pygame.sprite.Sprite.__init__(self) 
 
        # this creates a picture for the yellow balls, fills the ball with color and makes it transparentr for the monsters to be seen clearly through it when passing
        self.image = pygame.Surface([w, h])
        self.image.fill(white)
        self.image.set_colorkey(white)
        pygame.draw.ellipse(self.image,color,[1,1,w,h])
 
        # creates a rectangle object wrapped around the yellow balls for collision detection and positioning
        self.rect = self.image.get_rect() 

# Class for the player itself .i.e pacman character
class Gamer(pygame.sprite.Sprite):
  # variables for speed
  displace_x=0
  displace_y=0

  # Function that is called upon class initialization
  def __init__(self,x,y, filename):
      # call the inherited constructor
      pygame.sprite.Sprite.__init__(self)

      # this sets the image of the players character from a locally selected picture
      self.image = pygame.image.load(filename).convert()

      #checking collisions
      self.collided = False

      # x and y are the initial player's position
      # rect method is used to wrap around our character sprite to position and detect collisions
      self.rect = self.image.get_rect()
      # stores initial player position inside rect
      self.rect.top = y
      self.rect.left = x
      # these are used to store the previous position of pacman when a collision occurs
      self.prev_y = y
      self.prev_x = x


  # handle when player is speeding up or down
  def velocitychange(self, x, y):
      self.displace_x = self.displace_x + x
      self.displace_y = self.displace_y + y
        
  # handle updating players position
  def update(self,walls,gate):
    # save former coordinate for reference 
    former_x = self.rect.left
    update_x = former_x + self.displace_x
    self.rect.left = update_x
    former_y = self.rect.top
    update_y = former_y + self.displace_y

    # check if wall/obstacle is hit and if so go back to the old position
    x_collision = pygame.sprite.spritecollide(self, walls, False)
    if x_collision:
        self.rect.left = former_x
    else:
        self.rect.top = update_y

        collision_y = pygame.sprite.spritecollide(self, walls, False)
        if collision_y:
            self.rect.top = former_y

    # don't allow pacman into gate
    if gate is not False:
      obstacle_collide = pygame.sprite.spritecollide(self, gate, False)
      if obstacle_collide:
        self.rect.left = former_x
        self.rect.top = former_y

  def reset_position(self, x, y):
    self.rect.left = x
    self.rect.top = y

#This is a class representing each of the enemy monster sprites
class Monster(Gamer):
  # manipulate velocity of the monster
  def velocitychange(self, directions_list, monster, turn, steps, length):
    try:
        x, y, z = directions_list[turn]
        if steps < z:
            self.displace_x = x
            self.displace_y = y
            steps = steps + 1
        else:
            if turn < length:
                turn = turn + 1
            elif monster == "clyde":
                turn = 1 + 1
            else:
                turn = 2 % 1
            x, y, _ = directions_list[turn]
            self.displace_x = x
            self.displace_y = y
            steps = 0
        return [turn, steps]
    except IndexError:
        return [0, 0]
      
Pinky_directions = [
[0,-30,4],
[15,0,9],
[0,15,11],
[-15,0,23],
[0,15,7],
[15,0,3],
[0,-15,3],
[15,0,19],
[0,15,3],
[15,0,3],
[0,15,3],
[15,0,3],
[0,-15,15],
[-15,0,7],
[0,15,3],
[-15,0,19],
[0,-15,11],
[15,0,9]
]

Blinky_directions = [
[0,-15,4],
[15,0,9],
[0,15,11],
[15,0,3],
[0,15,7],
[-15,0,11],
[0,15,3],
[15,0,15],
[0,-15,15],
[15,0,3],
[0,-15,11],
[-15,0,3],
[0,-15,11],
[-15,0,3],
[0,-15,3],
[-15,0,7],
[0,-15,3],
[15,0,15],
[0,15,15],
[-15,0,3],
[0,15,3],
[-15,0,3],
[0,-15,7],
[-15,0,3],
[0,15,7],
[-15,0,11],
[0,-15,7],
[15,0,5]
]

Inky_directions = [
[30,0,2],
[0,-15,4],
[15,0,10],
[0,15,7],
[15,0,3],
[0,-15,3],
[15,0,3],
[0,-15,15],
[-15,0,15],
[0,15,3],
[15,0,15],
[0,15,11],
[-15,0,3],
[0,-15,7],
[-15,0,11],
[0,15,3],
[-15,0,11],
[0,15,7],
[-15,0,3],
[0,-15,3],
[-15,0,3],
[0,-15,15],
[15,0,15],
[0,15,3],
[-15,0,15],
[0,15,11],
[15,0,3],
[0,-15,11],
[15,0,11],
[0,15,3],
[15,0,1],
]

Clyde_directions = [
[-30,0,2],
[0,-15,4],
[15,0,5],
[0,15,7],
[-15,0,11],
[0,-15,7],
[-15,0,3],
[0,15,7],
[-15,0,7],
[0,15,15],
[15,0,15],
[0,-15,3],
[-15,0,11],
[0,-15,7],
[15,0,3],
[0,-15,11],
[15,0,9],
]

pl = len(Pinky_directions) - 1
bl = len(Blinky_directions) - 1
il = len(Inky_directions) - 1
cl = len(Clyde_directions) - 1

# Initialize pygame
pygame.init()
  
# set height and width of our screen
screen = pygame.display.set_mode([606, 606])


# Give our game a title
pygame.display.set_caption('Pacman Space Rainbow Edition')

# Define an area in the game window that can be drawn in
background = pygame.Surface(screen.get_size())

# convert the surface background to the same pixel format as the display surface
background = background.convert()
  
# Make screen background black
background.fill(black)


# Used to control our games framerate
clock = pygame.time.Clock()

# Set a font variable to be used for text displays later on
pygame.font.init()
font = pygame.font.Font('C:/Users/USER/Desktop/Django/minePy/gg.ttf', 25)

#starting point for player and monsters
w = 287 #Width
p_h = 439 #Pacman height
m_h = 259 #Monster height
b_h = 199 #Blinky height
i_w = 255 #Inky width
c_w = 319 #Clyde width

#Give us a color from our previously defined rainbow_colors variable
def colorChange():
  global current_rainbow_color
  color = rainbow_colors[current_rainbow_color]
  current_rainbow_color = (current_rainbow_color + 1) % len(rainbow_colors)
  return color

def wallChange(obstacle_list, all_sprites_list):
  del obstacle_list
  createLevel(all_sprites_list)

def startGame():
  # run a thread for playing background music
  bg_music_thread = Thread(target=lambda: playSound('C:/Users/USER/Desktop/Django/minePy/pacman/b2moon.mp3', -1, True))
  bg_music_thread.start()

  #variable to control number of lives a player is given
  lives = 3

  #list containing all game sprites/elements
  all_sprites_list = pygame.sprite.RenderPlain()

  #list containing all game yellow ball sprites
  block_list = pygame.sprite.RenderPlain()

  #list containing all game monsters sprites
  monster_list = pygame.sprite.RenderPlain()

  # list recording each time pacman collides
  player_collision = pygame.sprite.RenderPlain()

  # function that returns list of all wall sprites created in function
  obstacle_list = createLevel(all_sprites_list)

  # function that returns list of all gate sprites created in function
  gate = createGate(all_sprites_list)


  # variables to be used in movement algorithm 
  pturn = 0
  psteps = 0

  bturn = 0
  bsteps = 0

  iturn = 0
  isteps = 0

  cturn = 0
  csteps = 0


  # Initialization of Player and monster Classes and adding them to lists for rendering
  Pacman = Gamer( w, p_h, "C:/Users/USER/Desktop/Django/minePy/pacman/images/pacman.png" )
  all_sprites_list.add(Pacman)
  player_collision.add(Pacman)
   
  Blinky=Monster( w, b_h, "C:/Users/USER/Desktop/Django/minePy/pacman/images/Blinky.png" )
  monster_list.add(Blinky)
  all_sprites_list.add(Blinky)

  Pinky=Monster( w, m_h, "C:/Users/USER/Desktop/Django/minePy/pacman/images/Pinky.png" )
  monster_list.add(Pinky)
  all_sprites_list.add(Pinky)
   
  Inky=Monster( i_w, m_h, "C:/Users/USER/Desktop/Django/minePy/pacman/images/Inky.png" )
  monster_list.add(Inky)
  all_sprites_list.add(Inky)
   
  Clyde=Monster( c_w, m_h, "C:/Users/USER/Desktop/Django/minePy/pacman/images/Clyde.png" )
  monster_list.add(Clyde)
  all_sprites_list.add(Clyde)

  # Draw the grid
  for row in range(19):
    for column in range(19):
        if (row == 7 or row == 8) and (8 <= column <= 10):
            continue
        else:
            block = YellowBall(yellow, 4, 4)

            # Put our block in a random spot
            block.rect.x = (30 * column + 6) + 26
            block.rect.y = (30 * row + 6) + 26

            # does yellow ball appear on a wall
            is_colliding_with_wall = pygame.sprite.spritecollide(block, obstacle_list, False)
            is_colliding_with_pacman = pygame.sprite.spritecollide(block, player_collision, False)

            if is_colliding_with_wall or is_colliding_with_pacman:
                continue
            else:
                # add our block to the list of all other sprites
                block_list.add(block)
                all_sprites_list.add(block)

  #count number of yellow balls pacman can possibly eat to know highest attainable score
  max_balls = len(block_list)
  score = 0
  done = False

  while done == False:

      for event in pygame.event.get():
          # game gets closed check
          if event.type == pygame.QUIT:
              db.disconnect()
              done=True
          # key is pressed while game running check
          if event.type == pygame.KEYDOWN:
              # Whenever key is pressed recreate our walls and give different color
              wallChange(createLevel(all_sprites_list), all_sprites_list)
              # pressed key is arrow left
              if event.key == pygame.K_LEFT:
                  Pacman.velocitychange(-30,0)
              # pressed key is arrow right
              if event.key == pygame.K_RIGHT:
                  Pacman.velocitychange(30,0)
              # pressed key is arrow up
              if event.key == pygame.K_UP:
                  Pacman.velocitychange(0,-30)
              # pressed key is arrow down
              if event.key == pygame.K_DOWN:
                  Pacman.velocitychange(0,30)

          # key is released while game running check
          if event.type == pygame.KEYUP:
              # released key is arrow left
              if event.key == pygame.K_LEFT:
                  Pacman.velocitychange(30,0)
              # released key is arrow right
              if event.key == pygame.K_RIGHT:
                  Pacman.velocitychange(-30,0)
              # released key is arrow up
              if event.key == pygame.K_UP:
                  Pacman.velocitychange(0,30)
              # released key is arrow left
              if event.key == pygame.K_DOWN:
                  Pacman.velocitychange(0,-30)
          
      
      # update player position and check  for collisions
      Pacman.update(obstacle_list,gate)

      # automated monster movement with direction list and parameters
      returned = Pinky.velocitychange(Pinky_directions,False,pturn,psteps,pl)
      pturn = returned[0]
      psteps = returned[1]
      Pinky.velocitychange(Pinky_directions,False,pturn,psteps,pl)
      Pinky.update(obstacle_list,False)

      returned = Blinky.velocitychange(Blinky_directions,False,bturn,bsteps,bl)
      bturn = returned[0]
      bsteps = returned[1]
      Blinky.velocitychange(Blinky_directions,False,bturn,bsteps,bl)
      Blinky.update(obstacle_list,False)

      returned = Inky.velocitychange(Inky_directions,False,iturn,isteps,il)
      iturn = returned[0]
      isteps = returned[1]
      Inky.velocitychange(Inky_directions,False,iturn,isteps,il)
      Inky.update(obstacle_list,False)

      returned = Clyde.velocitychange(Clyde_directions,"clyde",cturn,csteps,cl)
      cturn = returned[0]
      csteps = returned[1]
      Clyde.velocitychange(Clyde_directions,"clyde",cturn,csteps,cl)
      Clyde.update(obstacle_list,False)

      # checking pacmans collision with yellow balls. If so delete the yellow ball
      blocks_hit_list = pygame.sprite.spritecollide(Pacman, block_list, True)
       
      # compare collision list 
      if len(blocks_hit_list) > 0:
          score = score + len(blocks_hit_list)

      # make screen black
      screen.fill(black)
        
      # draw all sprites
      obstacle_list.draw(screen)
      gate.draw(screen)
      all_sprites_list.draw(screen)
      monster_list.draw(screen)

      # show score and life count on screen
      score_text = font.render(f"Score: {score}/{max_balls}", True, red)
      lives_text = font.render(f"Lives: {lives}", True, red)
      
      screen.blit(score_text, [10, 10])
      screen.blit(lives_text, [526, 10])

      if score == max_balls:
        finalAction("Good Job, Level Passed!", 145, score)
      
      #has pacman collided with any of the monsters? if so play sound,  deduct life and reposition
      if not Pacman.collided:
          if pygame.sprite.spritecollide(Pacman, monster_list, False):
            sound_effect_thread = Thread(target=lambda: playSound('C:/Users/USER/Desktop/Django/minePy/pacman/hit_sound.mp3', 0, False))
            sound_effect_thread.start()
            lives -= 1
            Pacman.reset_position(w, p_h)

          if lives == 0:
            finalAction("Game Over", 235, score)
      
      pygame.display.flip()
    
      clock.tick(10)

#generate random number to be used as id in database
def generateID():
    random_number = random.randint(1, 999999)
    return random_number

# do after lives are exhausted
def finalAction(message, left, score):
  # check if table exists in database. If not create
  db.table_exist('Highscores')

  score_id = generateID()
  name = 'BYRON'

  # Insert players score into database
  db.insert_data('Highscores', (score_id, name, score))

  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        db.disconnect()
        pygame.quit()
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          pygame.quit()
        if event.key == pygame.K_RETURN:
          startGame()

    # Set another Surface for game message(width, height)
    w = pygame.Surface((400,200))  
    w.set_alpha(10)              
    w.fill((128,128,128))          
    screen.blit(w, (100,200))    

    # After win or lose handling
    text1=font.render(message, True, white)
    screen.blit(text1, [left, 233])

    text2=font.render("Press Enter to Restart", True, white)
    screen.blit(text2, [195, 303])
    text3=font.render("Press Escape to Quit", True, white)
    screen.blit(text3, [195, 333])

    pygame.display.flip()

    # adjust frame rate to accomodate graphics
    clock.tick(10)

startGame()

db.disconnect()
pygame.quit()