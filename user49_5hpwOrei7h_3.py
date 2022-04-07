# program template for Spaceship
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
rock_group = set([])
missile_group = set([])
started = False
explosion_group = set([])
# globals for control 
ship_angle_vel_inc = .2

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
#ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
ship_thrust_sound = simplegui.load_sound("https://www.dropbox.com/s/296i7mjk64iibmv/ship_thrust_sound_2.mp3?dl=1")
ship_thrust_sound.set_volume(.9)
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# alternative upbeat soundtrack by composer and former IIPP student Emiel Stopler
# please do not redistribute without permission from Emiel at http://www.filmcomposer.nl
soundtrack = simplegui.load_sound("https://storage.googleapis.com/codeskulptor-assets/ricerocks_theme.mp3")
soundtrack.set_volume(.2)
# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)


# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.image_lifespan = info.get_lifespan()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        if self.thrust == False:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
        else: 
            canvas.draw_image(self.image, [135,45], self.image_size, self.pos, self.image_size, self.angle)

    def update(self):
        self.angle += self.angle_vel
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]    
        #friction update
        self.vel[0] *= .9
        self.vel[1] *= .9
        #thrust update 
        if self.thrust == True: 
            self.vel[0] += angle_to_vector(self.angle)[0]
            self.vel[1] += angle_to_vector(self.angle)[1]
            
        #position update so the ship wraps around the screen    
        if not (self.radius < self.pos[0] < WIDTH - self.radius):
            self.pos[0] = WIDTH -self.pos[0]
        
        if not (self.radius < self.pos[1] < HEIGHT - self.radius):
            self.pos[1] = HEIGHT -self.pos[1]
    
    def thrust_sound(self, Isthruston):
        if Isthruston == True: 
            ship_thrust_sound.rewind()
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.pause()
    
    def shoot(self):
        global missile_group
        orient = angle_to_vector(self.angle)
        missile_vel = [self.vel[0] + orient[0]*4, self.vel[1] + orient[1]*4]
        missile_pos = [self.pos[0] + orient[0]*self.radius, 
                       self.pos[1] + orient[1]*self.radius]
        
        a_missile = Sprite(missile_pos, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound)
        missile_group.add(a_missile)

# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.image_lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
    

    def collide(self,other_object):
        return dist(self.pos, other_object.pos) <= (self.radius + other_object.radius)
            
    def draw(self, canvas):
        if self.animated:
            current_exp_index = (self.age % self.image_lifespan) // 1
            current_exp_center = [self.image_center[0] + current_exp_index * self.image_size[0], self.image_center[1]]
            canvas.draw_image(self.image, current_exp_center, self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
        
    def update(self):
        self.angle += self.angle_vel 
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        #position update so the Sprite wraps around the screen    
        if not (self.radius < self.pos[0] < WIDTH - self.radius):
            self.pos[0] = WIDTH -self.pos[0]
        
        if not (self.radius < self.pos[1] < HEIGHT - self.radius):
            self.pos[1] = HEIGHT -self.pos[1]
        
        #increment the age every time the update method is called. Check with the lifespan of this image
        self.age += 1
        if self.age < self.image_lifespan:
            return False
        else:
            return True

#######################           
#define a helper function.   
def process_sprite_group(canvas, sprite_set):
    
    for each_sprite in set(sprite_set):
        each_sprite.draw(canvas)
        if each_sprite.update():
            sprite_set.remove(each_sprite)  
    
    

def group_collide (group, other_object):
    
    for s in set(group): 
        if s.collide(other_object):
            group.remove(s)
            #At collision, create one explosion as Sprite(self, pos, vel, ang, ang_vel, image, info, sound = None)
            new_explosion = Sprite(s.pos, s.vel, s.angle, s.angle_vel, explosion_image, explosion_info, explosion_sound)
            explosion_group.add(new_explosion)
            return True
        else:
            return False

def group_group_collide(first_group, other_group):
    removed_sprite = set([])
    for s in set(first_group): 
        if group_collide(other_group, s):
            removed_sprite.add(s)
            first_group.discard(s)
    return len(removed_sprite)
        
def draw(canvas):
    global time, lives, score, rock_group, started, missile_group 
    
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw ship and sprites  
    my_ship.draw(canvas)

    #draw lives and scores
    canvas.draw_text("Lives = " + str(lives), [WIDTH/10, HEIGHT/10], 20, "White")
    canvas.draw_text("Scores = " + str(score), [8*WIDTH/10, HEIGHT/10], 20, "White")
    
    #update lives and scores
    if group_collide(rock_group, my_ship):
        lives -= 1 

    score += group_group_collide(rock_group, missile_group)     
    
    if lives <= 0: 
        started = False
        lives = 0
        soundtrack.rewind()
        rock_group = set([])

    # update ship and sprites
    my_ship.update()
    process_sprite_group(canvas, rock_group)
    process_sprite_group(canvas, missile_group)
    process_sprite_group(canvas, explosion_group)
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())
            
# timer handler that spawns a rock    
def rock_spawner():
    global rock_group, started  
    if not started: 
        rock_group = set([])
    
    if started and len(rock_group) <= 12: 
        ang_vel = (random.randrange(-10, 10, 1))/ 50.0
        pos = [random.randrange(asteroid_info.get_radius()+1, WIDTH - asteroid_info.get_radius()), 
                random.randrange(asteroid_info.get_radius()+1, HEIGHT - asteroid_info.get_radius())]
        vel = [random.random() * 1.3 - .3, random.random() * 1.3 - .3]
        if dist(pos, my_ship.pos) > my_ship.radius*2: 
            new_rock = Sprite(pos, vel, 0, ang_vel, asteroid_image, asteroid_info)
            rock_group.add(new_rock)

    
    
# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started, lives, score
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        score = 0
        lives = 3
        rock_spawner()
        soundtrack.play()
#    else:
#        soundtrack.pause()
#        started = False 

#define the key handlers
def keydown(key):
    if simplegui.KEY_MAP["left"] == key:
        my_ship.angle_vel -= ship_angle_vel_inc
    elif simplegui.KEY_MAP["right"] == key:
        my_ship.angle_vel += ship_angle_vel_inc
    elif simplegui.KEY_MAP["up"] == key:
        my_ship.thrust = True
        my_ship.thrust_sound(True)
    elif simplegui.KEY_MAP["space"] == key:
        my_ship.shoot()

def keyup(key):
    if simplegui.KEY_MAP["left"] == key:
        my_ship.angle_vel += ship_angle_vel_inc
    elif simplegui.KEY_MAP["right"] == key:
        my_ship.angle_vel -= ship_angle_vel_inc
    elif simplegui.KEY_MAP["up"] == key:
        my_ship.thrust = False
        my_ship.thrust_sound(False)
        
        
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)



# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(click)
label1 = frame.add_label("Control:", 100)
label2 = frame.add_label("Use SPACE bar to shoot, UP key to thrust, and the good old LEFT and RIGHT key.")
label3 = frame.add_label("Enjoy!")

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()