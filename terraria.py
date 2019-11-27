import numpy as np
from enum import Enum
from time import sleep, time
from random import randint, seed
from pyinput import mouse, controller, manager
from sense_hat import SenseHat
sense = SenseHat()

class Block(Enum): 
    AIR   = (  0,   0,   0)
    GRASS = (  0, 100,   0)
    DIRT  = (139,  69,  19)
    STONE = (100, 100, 100)
    BRICK = (100,   0,   0)

class Point:
    def __init__(self,x_init,y_init):
        self.x = x_init
        self.y = y_init

    def shift(self, x, y):
        self.x += x
        self.y += y

    def __repr__(self):
        return "".join(["(", str(self.x), ",", str(self.y), ")"])

class Player:
    def __init__(self, pos):
        self.pos = pos
        self.target = Point(0, 0)
        self.dir = Point(0, 0)
        self.facing = 1
        self.gravity = 1
        
    def move_towards(self, _dir):
        self.dir = Point(_dir.x, _dir.y)
        self.target = Point(_dir.x, _dir.y)

    def update(self, world):
        next_pos = Point(self.pos.x + sign(self.dir.x), self.pos.y + sign(self.dir.y))

        #print(f"next: {next_pos}")
        #print(f"dir: {self.dir}")
        #print(f"target: {self.target}")
        if world[next_pos.y, next_pos.x] == 0:
            self.pos = next_pos
            if self.target.x == 0 and self.target.y == 0:
                self.move_towards(Point(self.dir.x, self.gravity))
            else:
                self.target.x = self.target.x - sign(self.target.x)
                self.target.y = self.target.y - sign(self.target.y)
        elif self.dir.y == 1:
            self.move_towards(Point(0, self.gravity))
            next_pos = Point(self.pos.x + sign(self.dir.x), self.pos.y + sign(self.dir.y))
            if world[next_pos.y, next_pos.x] == 0:
                self.pos = next_pos
        self.facing = self.dir.x
WIDTH, HEIGHT = 8, 8
LAYERS = 3
LAYER_HEIGHT = 8
WORLD_WIDTH = 64
WORLD_HEIGHT = 64

ID_TO_BLOCKS = {0: Block.AIR, 1: Block.GRASS, 2: Block.DIRT, 3: Block.STONE, 4: Block.BRICK}
BLOCKS_TO_ID = {Block.AIR: 0, Block.GRASS: 1, Block.DIRT: 2, Block.STONE: 3, Block.BRICK: 4}
world = np.zeros( (WORLD_HEIGHT, WORLD_WIDTH), int)
player = Player(Point(WORLD_WIDTH // 2, 0))
pointer = Point(0, 0)
has_pointer = False
spectate = False
controller.max_cooldown = 15
controller.cooldown = 0

world_seed = int(time())

#world_seed = 1570883613
# tall seed: 1569530493
# mountain: 1569531073

def main():
    sense.stick.direction_left = move_left
    sense.stick.direction_right =  move_right
    sense.stick.direction_up = move_up
    sense.stick.direction_down = move_down

    mouse.set_right_click(right_click)
    mouse.set_left_click(left_click)
    mouse.set_move(mouse_move)

    controller.set_move_joystick(controller_move)
    controller.set_press_button(controller_press)
    controller.set_move_trigger(controller_trigger)

    player.move_towards(Point(0, 1))
    seed(world_seed)
    initalize()
    while True:
        #if world[player.pos.y + 1, player.pos.x] == 1:
        #    player.move_towards(Point(1, -1))
        player.update(world)
        draw_world()
        #print_world()
        #print("")
        #print(f"{player.pos.x}, {player.pos.y}")
        sleep(0.2)

def initalize():
    # Sky layer:
    for x in range(0, WORLD_WIDTH):
        for y in range(0, LAYER_HEIGHT):
            world[y, x] = BLOCKS_TO_ID[Block.AIR]
             
    # Mid level:
    level = LAYER_HEIGHT + LAYER_HEIGHT // 2
    has_stayed_in_level = 1
    for x in range(0, WORLD_WIDTH):
        for y in range(LAYER_HEIGHT, 3 * LAYER_HEIGHT):
            if y - level >= 4:
                world[y, x] = BLOCKS_TO_ID[Block.STONE]
                continue
            if y < level:
                world[y, x] = BLOCKS_TO_ID[Block.AIR]
            elif y == level:
                world[y, x] = BLOCKS_TO_ID[Block.GRASS]
            else:
                world[y, x] = BLOCKS_TO_ID[Block.DIRT]
            
        # Increase level:
        if has_stayed_in_level == 0:
            if level <= 2 * LAYER_HEIGHT and randint(0, 2) == 0:
                level += 1
                has_stayed_in_level = 1
                continue
            if level >= 0 and randint(0, 2) == 0:
                level -= 1
                has_stayed_in_level = 1
                continue
        else:
            has_stayed_in_level -= 1

    for x in range(0, WORLD_WIDTH):
        for y in range(3 * LAYER_HEIGHT, WORLD_HEIGHT):
            world[y, x] = BLOCKS_TO_ID[Block.STONE]

def draw_world():
    offset = player.pos.x - WIDTH // 2, player.pos.y - HEIGHT // 2
    yi = 0
    for y in range(offset[1], offset[1] + HEIGHT):
        xi = 0
        for x in range(offset[0], offset[0] + WIDTH):
            if has_pointer and xi == pointer.x and yi == pointer.y:
                pass
            elif xi == WIDTH // 2 and yi == HEIGHT // 2:
                pass
            elif 0 < x < WORLD_WIDTH and 0 < y < WORLD_HEIGHT:
                sense.set_pixel(xi, yi, ID_TO_BLOCKS[world[y, x]].value)
            else:
                sense.set_pixel(xi, yi, (0, 0, 0))
            xi += 1
        yi += 1
    sense.set_pixel(WIDTH // 2, HEIGHT // 2, (255,255,255))

def print_world():
    print(f"Seed: {world_seed}")
    for y in range(0, 3 * LAYER_HEIGHT):
        for x in range(0, WORLD_WIDTH):
            a = world[y, x]
            if player.pos.x == x and player.pos.y == y:
                print("X", end=" ")
            elif a == 0:
                print(" ", end=" ")
            elif a == 1:
                print("$", end=" ")
            elif a == 2:
                print("%", end=" ")
            elif a == 3:
                print("#", end=" ")
        print("")

def mouse_move(): 
    pointer = Point(mouse.get_pixel_x(), mouse.get_pixel_y())
    draw_world()
    sense.set_pixel(mouse.get_pixel_x(), mouse.get_pixel_y(), (50, 50, 50))
    
def right_click():
    global world, player
    offset = player.pos.x - WIDTH // 2, player.pos.y - HEIGHT // 2
    world[offset[1] + pointer.y, offset[0] + pointer.x] = BLOCKS_TO_ID[Block.BRICK]

def left_click():
    global world, player
    offset = player.pos.x - WIDTH // 2, player.pos.y - HEIGHT // 2
    world[offset[1] + pointer.y, offset[0] + pointer.x] = BLOCKS_TO_ID[Block.AIR]

def controller_trigger(direction, percent):
    if abs(percent) > 0.3:
        if direction == "R":
            right_click()
        else:
            left_click()

def controller_move(joystick, direction, percent):
    global has_pointer
    if abs(percent) > 0.4:
        if joystick == "L" and direction == "X":
            if sign(percent) == 1:
                move_right()
            else:
                move_left()
        if joystick == "L" and direction == "Y":
            if sign(percent) == 1:
                move_down()
            else:
                move_up()
    if controller.cooldown == 0:
        if abs(percent) > 0.4:
            if joystick == "R" and direction == "Y":
                if not has_pointer: has_pointer = True
                pointer.x = int(max(min(pointer.x + sign(percent), WIDTH - 1), 0))
                draw_world()
                sense.set_pixel(pointer.x, pointer.y,  (50, 50, 50))

            if joystick == "R" and direction == "X":
                if not has_pointer: has_pointer = True
                pointer.y = int(max(min(pointer.y + sign(percent), HEIGHT - 1), 0))
                draw_world()            
                sense.set_pixel(pointer.x, pointer.y, (50, 50, 50))
            controller.cooldown = controller.max_cooldown
    else:
        controller.cooldown -= 1

def controller_press(code, is_pressed):
    if is_pressed:
        if code == "A":
            move_up()

def move_left():
    if not player.dir.x == -1 and not player.dir.y == 0:
        player.move_towards(Point(-1, 0))

def move_right():
    if not player.dir.x == 1 and not player.dir.y == 0:
        player.move_towards(Point(1, 0))

def move_down():
    pass

def move_up():
    if not world[player.pos.y + 1, player.pos.x] == 0:
        player.move_towards(Point(sign(player.facing), -1))

def sign(x):
    if x < 0:
        return -1
    if x == 0:
        return 0
    if x > 0:
        return 1

if __name__ == "__main__":
    main()
