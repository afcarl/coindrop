import math
import random
import os
import pygame
from pygame.locals import *
import pymunk as pm
from pymunk import Vec2d
from pygame.color import *

import munkserver
import utils
X,Y = 0,1
### Physics collision types
COLLTYPE_PIGGYBANK = 1
COLLTYPE_COIN = 2

WORLD_WIDTH = 600
WORLD_HEIGHT = 600
FLOOR_LEVEL = 100
TARGET_SIZE = 50

def flipy(y):
    global WORLD_HEIGHT
    return int(-y + WORLD_HEIGHT)

def flip_vec(vec):
    global WORLD_HEIGHT
    return (int(vec.x), int(-vec.y + WORLD_HEIGHT))

def euclidean_distance(v1, v2):
    return math.sqrt((v1.x - v2.x) ** 2 + (v1.y - v2.y) ** 2)

__SPACE__ = None
def get_space():
    return __SPACE__

__SCREEN__ = None
def get_screen():
    return __SCREEN__

__CLOCK__ = None
def get_clock():
    return __CLOCK__

__SIMULATION__ = None
def get_simulation():
    return __SIMULATION__


def load_image(fn, colorkey=None):
    try:
        path = os.path.join(utils.get_library_path(), 'images', fn)
        image = pygame.image.load(path)
    except pygame.error, message:
        print 'Cannot load image:', path
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

def get_slope(pt1, pt2):
    return float(pt2.y - pt1.y) / float(pt2.x - pt1.x)

def solve_line(pt1, pt2, x):
    slope = get_slope(pt1, pt2)
    b = pt2.y - (pt2.x * slope)
    return slope * x + b

def midpoint(pt1, pt2):
    minx = min(pt2.x, pt1.x)
    maxx = max(pt2.x, pt1.x)
    x = (maxx - minx) / 2.0 + minx
    y = solve_line(pt1, pt2, x)
    return Vec2d(x,y)

def normalize(normal, pt):
    nx = pt.x - normal.x
    ny = pt.y - normal.y
    return Vec2d(nx, ny)

def linear_modula(pt1, pt2, x):
    minx = min(pt2.x, pt1.x)
    maxx = max(pt2.x, pt1.x)
    return (x % (maxx - minx)) + minx

def end_points(pt1, pt2):
    mp = midpoint()
    pt1 = Vec2d(pt1.x - mp.x, pt1.y - mp.y)
    pt2 = Vec2d(pt2.x - mp.x, pt2.y - mp.y)
    return (pt1, pt2)

class MunkObject(object):
    def __init__(self, *args):
        self._make(*args)

    def get_screen(self):
        return get_screen()
    screen = property(get_screen)

    def get_space(self):
        return get_space()
    space = property(get_space)

    def _make(*args):
        pass

    def draw(self):
        pass

    """
    def __getattr__(self, attr):
        if hasattr(self, "object") and hasattr(self.object, attr):
            return getattr(self.object, attr)
        else:
            raise AttributeError, attr

    def __setattr__(self, attr, val):
        if hasattr(self, "object") and hasattr(self.object, attr):
            #print "setting internal attr %s to val %s" % (attr, val)
            setattr(self.object, attr, val)
        else:
            self.__dict__[attr] = val
    """

    def visible(self):
        return self.body.position.y > 0
    
class Body(MunkObject):
    def _make(self, mass, inertia, position):
        self.object = pm.Body(mass, inertia)
        self.position = position
        #self.space.add(self.object)

    def draw(self):
        v = self.position
        p = int(v.x), int(flipy(v.y))
        pygame.draw.circle(self.screen, THECOLORS["black"], p, 2, 2)
    
class Segment(MunkObject):
    def _make(self, body, pt1, pt2, thickness, static):
        self.object = pm.Segment(body, pt1, pt2, thickness)
        self.thickness = thickness
        self.space.add(self.object)

    def draw(self):
        pv1 = self.body.position + self.a.rotated(math.degrees(self.body.angle))
        pv2 = self.body.position + self.b.rotated(math.degrees(self.body.angle))
        p1 = pv1.x, flipy(pv1.y)
        p2 = pv2.x, flipy(pv2.y)
        pygame.draw.line(self.screen, THECOLORS["darkblue"], p1, p2, self.thickness)

class Circle(MunkObject):
    def _make(self, body, radius):
        self.object = pm.Circle(body, radius, (0,0))
        self.space.add(self.object)

    def draw(self):
        r = self.radius
        v = self.body.position
        rot = self.body.rotation_vector
        p = int(v.x), int(flipy(v.y))
        p2 = Vec2d(rot.x, -rot.y) * r * 0.9
        pygame.draw.circle(self.screen, THECOLORS[self.Color], p, int(r), 2)
        pygame.draw.line(self.screen, THECOLORS["red"], p, p+p2)

def min_mod(_min, mod, val):
    return max(_min, val % mod)

class Pinwheel(MunkObject):
    WidthMax = 12 
    WidthMin = 6
    LengthMin = 20
    LengthMax = 200

    def _make(self, ctr_pt, length, width, mass, inertia):
        length = min_mod(self.LengthMin, self.LengthMax, length)
        width = min_mod(self.WidthMin, self.WidthMax, width)
        hl = length / 2
        hw = width / 2
        self.body = pm.Body(mass, inertia)
        self.body.position = ctr_pt
        pt1 = (-hw, -hl)
        pt2 = (hw, -hl)
        l1 = pm.Segment(self.body, pt1, pt2, 1)
        pt3 = (hw, -hw)
        l2 = pm.Segment(self.body, pt2, pt3, 1)
        pt4 = (hl, -hw)
        l3 = pm.Segment(self.body, pt3, pt4, 1)
        pt5 = (hl, hw)
        l4 = pm.Segment(self.body, pt4, pt5, 1)
        pt6 = (hw, hw)
        l5 = pm.Segment(self.body, pt5, pt6, 1)
        pt7 = (hw, hl)
        l6 = pm.Segment(self.body, pt6, pt7, 1)
        pt8 = (-hw, hl)
        l7 = pm.Segment(self.body, pt7, pt8, 1)
        pt9 = (-hw, hw)
        l8 = pm.Segment(self.body, pt8, pt9, 1)
        pt10 = (-hl, hw)
        l9 = pm.Segment(self.body, pt9, pt10, 1)
        pt11 = (-hl, -hw)
        l10 = pm.Segment(self.body, pt10, pt11, 1)
        pt12 = (-hw, -hw)
        l11 = pm.Segment(self.body, pt11, pt12, 1)
        l12 = pm.Segment(self.body, pt12, pt1, 1)
        self.object = [l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11, l12]
        self.space.add(self.object, self.body)
        # pivot
        self.ctr_pt = ctr_pt
        self.pivot_body = pm.Body(pm.inf, pm.inf)
        #self.pivot_body.position = ctr_pt
        #self.pivot = pm.PivotJoint(self.body, self.pivot_body, ctr_pt)
        self.pivot = pm.PivotJoint(self.body, self.pivot_body, ctr_pt)
        self.space.add(self.pivot)

    def draw(self):
        for line in self.object:
            pv1 = self.body.position + line.a.rotated(math.degrees(self.body.angle))
            pv2 = line.body.position + line.b.rotated(math.degrees(self.body.angle))
            p1 = flip_vec(pv1)
            p2 = flip_vec(pv2)
            pygame.draw.lines(self.screen, THECOLORS["darkblue"], 0, [p1,p2])
        p1 = flip_vec(self.ctr_pt)
        pygame.draw.circle(self.screen, THECOLORS["black"], p1, 5)

class Bridge(MunkObject):
    Width = 2
    LengthMin = 10
    LengthMax = 200

    def _make(self, ctr_pt, length, rot):
        hl = min_mod(self.LengthMin, self.LengthMax, length) / 2
        hw = self.Width / 2
        self.body = pm.Body(pm.inf, pm.inf)
        self.body.position = ctr_pt
        self.body.angle = rot
        pt1 = (-hl, -hw)
        pt2 = (hl, -hw)
        pt3 = (hl, hw)
        pt4 = (-hl, hw)
        l1 = pm.Segment(self.body, pt1, pt2, 5.0)
        l2 = pm.Segment(self.body, pt2, pt3, 5.0)
        l3 = pm.Segment(self.body, pt3, pt4, 5.0)
        l4 = pm.Segment(self.body, pt4, pt1, 5.0)
        self.object = [l1, l2, l3, l4]
        self.space.add_static(self.object)

    def draw(self):
        for line in self.object:
            pv1 = self.body.position + line.a.rotated(math.degrees(self.body.angle))
            pv2 = line.body.position + line.b.rotated(math.degrees(self.body.angle))
            p1 = flip_vec(pv1)
            p2 = flip_vec(pv2)
            pygame.draw.lines(self.screen, THECOLORS["darkred"], 0, [p1,p2])

class Lever(MunkObject):
    WidthMax = 12 
    WidthMin = 6
    LengthMin = 10
    LengthMax = 200

    def _make(self, center_pt, length, mass, inertia):
        hl = min_mod(self.LengthMin, self.LengthMax, length) / 2
        hw = 2
        pt1 = (-hl, -hw)
        pt2 = (hl, -hw)
        pt3 = (hl, hw)
        pt4 = (-hl, hw)
        self.body = pm.Body(mass, inertia)
        self.body.position = center_pt
        l1 = pm.Segment(self.body, pt1, pt2, 5.0)
        l2 = pm.Segment(self.body, pt2, pt3, 5.0)
        l3 = pm.Segment(self.body, pt3, pt4, 5.0)
        l4 = pm.Segment(self.body, pt4, pt1, 5.0)
        self.object = [l1, l2, l3, l4]
        self.space.add(self.object, self.body)
        # pivot
        self.pivot_body = pm.Body(pm.inf, pm.inf)
        self.pivot_body.position = center_pt
        self.pivot = pm.PivotJoint(self.body, self.pivot_body, center_pt)
        self.space.add(self.object, self.body, self.pivot)

    def draw(self):
        for line in self.object:
            pv1 = self.body.position + line.a.rotated(math.degrees(self.body.angle))
            pv2 = line.body.position + line.b.rotated(math.degrees(self.body.angle))
            p1 = flip_vec(pv1)
            p2 = flip_vec(pv2)
            pygame.draw.lines(self.screen, THECOLORS["green"], 0, [p1,p2])
        p1 = flip_vec(self.body.position)
        pygame.draw.circle(self.screen, THECOLORS["blue"], p1, 5)

class CoinSprite(pygame.sprite.Sprite):
    def __init__(self, coin):
        pygame.sprite.Sprite.__init__(self)
        size = map(int, (coin.Diameter * 1.5, coin.Diameter * 1.5))
        self.image = load_image(coin.SpriteImageFile, -1)
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.original_image = self.image
        self.current_rotate = 0

    def move(self, pos):
        x = pos.x - self.rect.center[0]
        y = pos.y - self.rect.center[1]
        self.rect.move_ip(x, y)

    def rotate(self, r):
        rotate = pygame.transform.rotate
        r = int(math.degrees(r))
        if r != self.current_rotate:
            self.current_rotate = r
            self.image = rotate(self.original_image, float(math.degrees(r)))

class Coin(MunkObject):
    POS = (100, 600)
    SpriteImageFile = "penny.png"

    def _make(self):
        self.collected = False
        self._alive = True
        inertia = pm.moment_for_circle(self.Mass, 0, 10, (0,0))
        self.body = pm.Body(self.Mass * 1.5, inertia)
        self.body.position = self.POS
        #self.body.position = (self.Collection, WORLD_HEIGHT)
        self.object = pm.Circle(self.body, self.Diameter * 1.5 / 2, (0,0))
        self.object.coin = self
        self.object.friction = 0.5
        self.object.collision_type = COLLTYPE_COIN
        self.space.add(self.body, self.object)
        if self.screen:
            self.sprite = CoinSprite(self)
            self.sprites = pygame.sprite.RenderPlain((self.sprite,))

    def get_alive(self):
        return self._alive and (self.body.position.y > FLOOR_LEVEL) 

    def set_alive(self, flag):
        self._alive = bool(flag)
    alive = property(get_alive, set_alive)

    def draw(self):
        p2 = self.body.position
        p1 = Vec2d(self.Collection, FLOOR_LEVEL)
        distance = int(euclidean_distance(p1, p2))
        midpt = midpoint(p1, p2) + Vec2d(15,15)
        p1 = flip_vec(p1)
        p2 = flip_vec(p2)
        pygame.draw.line(self.screen, THECOLORS[self.Color], p1, p2, 1)
        font = pygame.font.Font(pygame.font.match_font("freemonobold"), 25)
        line = str(distance)
        text = font.render(line, 0, THECOLORS[self.Color])
        self.screen.blit(text, flip_vec(midpt))
        # sprite
        r = self.object.radius
        v = self.body.position
        rot = self.body.angle
        p = Vec2d(int(v.x), int(flipy(v.y)))
        self.sprite.move(p)
        self.sprite.rotate(rot)
        self.sprites.update()
        self.sprites.draw(self.screen)

    def remove(self):
        self.space.remove(self.body, self.object)

class PiggyBucket(MunkObject):
    def _make(self, coin):
        self.coin = coin
        self.body = pm.Body(pm.inf, pm.inf)
        self.body.position = (self.coin.Collection, FLOOR_LEVEL)
        coords = self.get_rel_coords()
        left_line = pm.Segment(self.body, coords[0][0], coords[0][1], 5.0)
        right_line = pm.Segment(self.body, coords[1][0], coords[1][1], 5.0)
        bottom_line = pm.Segment(self.body, coords[2][0], coords[2][1], 5.0)
        bottom_line.friction = .99
        self.space.add_static(left_line, right_line, bottom_line)
        self.target = pm.Body(pm.inf, pm.inf)
        self.target.position = (self.coin.Collection, FLOOR_LEVEL - 5)
        radius =  int(TARGET_SIZE / 3.0)
        self.object = pm.Circle(self.target, radius, (0,0))
        self.object.collision_type = COLLTYPE_PIGGYBANK
        self.object.bucket = self
        self.space.add(self.object)
        
    def get_rel_coords(self, flip=False):
        half_len = TARGET_SIZE / 2.0
        coords = []
        # left
        p1 = Vec2d(-half_len, -half_len)
        p2 = Vec2d(-half_len, half_len)
        coords.append((p1, p2))
        # right
        p1 = Vec2d(half_len, -half_len)
        p2 = Vec2d(half_len, half_len)
        coords.append((p1, p2))
        # bottom
        p1 = Vec2d(-half_len, -half_len)
        p2 = Vec2d(half_len, -half_len)
        coords.append((p1, p2))
        return coords

    def get_box_coords(self, flip=False):
        center = Vec2d(self.coin.Collection, FLOOR_LEVEL)
        half_len = TARGET_SIZE / 2.0
        coords = []
        p1 = int(center.x + half_len), int(center.y + half_len)
        p2 = int(center.x + half_len), int(center.y - half_len)
        if flip:
            p1 = flip_vec(p1)
            p2 = flip_vec(p2)
        coords.append((p1, p2))
        p1 = int(center.x - half_len), int(center.y + half_len)
        p2 = int(center.x - half_len), int(center.y - half_len)
        if flip:
            p1 = flip_vec(p1)
            p2 = flip_vec(p2)
        coords.append((p1, p2))
        p1 = int(center.x - half_len), int(center.y + half_len)
        p2 = int(center.x + half_len), int(center.y + half_len)
        if flip:
            p1 = flip_vec(p1)
            p2 = flip_vec(p2)
        coords.append((p1, p2))
        return coords

    def draw(self):
        r = TARGET_SIZE / 2.0
        v = self.body.position
        #rot = self.body.rotation_vector
        half_width = r
        half_height = r
        v = Vec2d(v.x, flipy(v.y))
        p1 = int(v.x + half_width), int(v.y + half_height)
        p2 = int(v.x + half_width), int(v.y - half_height)
        pygame.draw.line(self.screen, THECOLORS["red"], p1, p2, 5)
        p1 = int(v.x - half_width), int(v.y + half_height)
        p2 = int(v.x - half_width), int(v.y - half_height)
        pygame.draw.line(self.screen, THECOLORS["red"], p1, p2, 5)
        p1 = int(v.x - half_width), int(v.y + half_height)
        p2 = int(v.x + half_width), int(v.y + half_height)
        pygame.draw.line(self.screen, THECOLORS["red"], p1, p2, 5)
        r = TARGET_SIZE / 3.0
        v = flip_vec(self.target.position)
        #pygame.draw.circle(self.screen, THECOLORS["blue"], v, int(r), 2)
        line = self.coin.__name__
        font = pygame.font.Font(pygame.font.match_font("freemonobold"), 20)
        text = font.render(line, 0, THECOLORS["black"])
        self.screen.blit(text, (self.body.position.x - 20, WORLD_HEIGHT - 70))

    def visible(self):
        return (self.ball.body.position.y + self.ball.radius) > 0

class Penny(Coin):
    Color = "darkred"
    SpriteImageFile = "penny.png"
    Diameter = 19.05
    Mass = 2.5
    Collection = 250
    value = 1
    RealValue = 1

class Nickel(Coin):
    Color = "darkgreen"
    SpriteImageFile = "nickel.png"
    Diameter = 21.21
    Mass = 5.00
    Collection = 350
    RealValue = 5
    value = 1

class Dime(Coin):
    Color = "darkblue"
    SpriteImageFile = "dime.png"
    Diameter = 17.91
    Mass = 2.268
    Collection = 450
    RealValue = 10
    value = 1

class Quarter(Coin):
    Color = "red"
    SpriteImageFile = "quarter.png"
    Diameter = 24.26
    Mass = 5.670
    Collection = 550
    RealValue = 25
    value = 1

Coins = [Penny, Nickel, Dime, Quarter]

class PiggyBank(MunkObject):
    BonusValue = 100

    def get_results(self):
        res = {
            'coin_graph': self.coin_graph,
            'value': self.value,
            'real_value': self.real_value,
        }
        return res

    def _make(self):
        self.value = 0
        self.real_value = 0
        self.buckets = []
        self.coin_graph = dict((coin.__name__, []) for coin in Coins)
        self.bonus = set()
        for coin in Coins:
            self.buckets.append(PiggyBucket(coin))
        self.space.add_collisionpair_func(COLLTYPE_COIN, COLLTYPE_PIGGYBANK, self.collision, "")

    def draw(self):
        for bucket in self.buckets:
            bucket.draw()
        # Display some text
        #font = pygame.font.Font(None, 25)
        font = pygame.font.Font(pygame.font.match_font("freemonobold"), 25)
        line = "Score: %s     Bank: %s" % (self.value, self.get_dollars())
        text = font.render(line, 0, THECOLORS["black"])
        self.screen.blit(text, (WORLD_WIDTH - 250, WORLD_HEIGHT - 20))

    def get_dollars(self):
        value = self.real_value / 100.0
        return "$%.02f" % value

    def get_bucket(self, coin):
        for bucket in self.buckets:
            if bucket.coin == coin.__class__:
                return bucket

    def collision(self, shapeA, shapeB, contacts, normal_coef, data):
        if shapeA.collision_type != COLLTYPE_COIN:
            return False
        coin = shapeA.coin
        if shapeB.collision_type != COLLTYPE_PIGGYBANK:
            return False
        bucket = shapeB.bucket
        if bucket.coin != coin.__class__:
            # coin is sitting in wrong bucket, kill it
            coin.alive = False
            return False
        coin.alive = False
        if not coin.collected:
            sim = get_simulation()
            self.coin_graph[coin.__class__.__name__].append(sim.frame_count)
            coin.collected = True
            #self.value += coin.value
            #if coin.__class__ not in self.bonus:
                #self.bonus.add(coin.__class__)
                #self.value += self.BonusValue
            self.real_value += coin.RealValue
        return False

class Simulation:
    CoinPeriod = 60

    def __init__(self, visualize=False, watch=False):
        global __SIMULATION__
        __SIMULATION__ = self
        self.watch = watch
        self.visualize = watch or visualize
        self.max_coins = 400
        if not self.watch:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
        self.reset()

    def reset(self):
        self.init_space()
        if self.visualize:
            self.setup_pygame()
        self.init_world()

    def screenshot(self, fn):
        self.draw()
        surface = pygame.display.get_surface()
        img = pygame.image.save(surface, fn)

    def setup_pygame(self):
        self.init_screen()
        self.init_clock()

    def load(self, obj):
        self.objects.append(obj)

    def run(self, func=None):
        self.running = True
        while self.running:
            self.loop()
            if func:
                func(self)
        for coin in self.coins:
            coin.alive = False
        self.remove_dead_coins()
        return self.piggybank.get_results()

    def init_space(self):
        global __SPACE__
        pm.init_pymunk()
        self.space = pm.Space()
        self.space.gravity = Vec2d(0.0, -900.0)
        __SPACE__ = self.space
    
    def init_screen(self):
        global __SCREEN__
        global WORLD_WIDTH, WORLD_HEIGHT
        pygame.init()
        self.screen = pygame.display.set_mode((WORLD_WIDTH, WORLD_HEIGHT))
        __SCREEN__ = self.screen

    def init_clock(self):
        global __CLOCK__
        self.clock = pygame.time.Clock()
        __CLOCK__ = self.clock
    
    def init_world(self):
        self.frame_count = 0
        self.piggybank = PiggyBank()
        self.coins = []
        self.coin_cnt = 0
        self.next_coin = self.CoinPeriod
        self.objects = []
        
    def loop(self):
        self.coindrop()
        self.physics()
        if self.watch:
            self.clock.tick(50)
            self.draw()
            pygame.display.flip()
            pygame.display.set_caption("fps: " + str(self.clock.get_fps()))
        self.remove_dead_coins()
        self.frame_count += 1

    def remove_dead_coins(self):
        for coin in self.coins[:]:
            if not coin.alive:
                coin.remove()
                self.coins.remove(coin)
                if not coin.collected:
                    bucket = self.piggybank.get_bucket(coin)
                    distance = int(euclidean_distance(coin.body.position, bucket.body.position))
                    self.piggybank.value += distance

    def movie(self, frames=10):
        fcnt = 0
        scnt = 0
        self.running = True
        while self.running:
            if (fcnt % frames) == 0:
                fcnt = 0
                fn = "%s.png" % scnt
                self.draw()
                pygame.display.flip()
                self.screenshot(fn)
                print fn
                scnt += 1
            fcnt += 1
            self.coindrop()
            self.physics()
        
    def coindrop(self):
        if (self.frame_count % self.CoinPeriod) == 0:
            self.next_coin = self.CoinPeriod
            self.coin_cnt += 1
            if self.coin_cnt == self.max_coins + 1:
                self.running = False
                return
            coin = random.choice(Coins)
            coin = coin()
            self.coins.append(coin)

    def physics(self):
        dt = 1.0/50.0
        self.space.step(dt)
            
    def draw(self):
        ### Draw stuff
        self.screen.fill(THECOLORS["lightgray"])

        self.piggybank.draw()
        for obj in self.objects:           
            obj.draw()

        for coin in self.coins:           
            coin.draw()
        self.coins = filter(lambda coin: coin.visible(), self.coins)

def run():
    def rand_coord():
        x = random.randint(0, 600)
        y = random.randint(0, 600)
        return Vec2d(x, y)
    def rand_bridge():
        ctr = rand_coord()
        length = random.randint(0, 0xffff)
        rot = random.randint(0, 0xffff)
        return Bridge(ctr, length, rot)
    def rand_lever():
        ctr = rand_coord()
        length = random.randint(0, 0xffff)
        mass = random.randint(0, 0xffff)
        inertia = random.randint(0, 0xffff)
        return Lever(ctr, length, mass, inertia)
    def rand_pinwheel():
        pt1 = rand_coord()
        length = random.randint(0, 0xffff)
        width = random.randint(0, 0xffff)
        mass = random.randint(0, 0xffff)
        inertia = random.randint(0, 0xffff)
        return Pinwheel(pt1, length, width, mass, inertia)
    sim = Simulation(True)
    for x in range(20):
        #sim.load(rand_pinwheel())
        obj = random.choice((rand_bridge, rand_pinwheel, rand_lever))
        sim.load(obj())
    #sim = Simulation(False)
    for x in range(3):
        pass
        #l = rand_lever()
        #sim.load(l)
    sim.run()

if __name__ == '__main__':
    run()
