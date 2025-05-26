import pygame
from values import *
from my_utilities import *

stone_mass = 6
hollowstone_mass = 4
wood_mass = 4
hollowwood_mass = 3
glass_mass = 2
hollowglass_mass = 1

BLOCK_ATTRIBUTES = {
    'wood':        {'health': 240, 'mass': 3.0, 'img': 'wood.webp', 'damaged_img': 'wooddamaged.webp'},
    'woodhollow':  {'health': 180, 'mass': 1.0, 'img': 'woodhollow.webp', 'damaged_img': 'woodhollowdamaged.png'},
    'stone':       {'health': 300, 'mass': 6.0, 'img': 'stone.webp', 'damaged_img': 'stonedamaged.webp'},
    'stonehollow': {'health': 240, 'mass': 4.0, 'img': 'stonehollow.webp', 'damaged_img': 'stonehollowdamaged.webp'},
    'glass':       {'health': 210, 'mass': 0.8, 'img': 'glass.webp', 'damaged_img': 'glassdamaged.webp'},
    'glasshollow': {'health': 150, 'mass': 0.5, 'img': 'glasshollow.webp', 'damaged_img': 'glasshollowdamaged.webp'}
}

class Block(pygame.sprite.Sprite):
    images = {}
    sounds = {}

    def __init__(self, block_type, pos, Vxblock=0, Vyblock=0):
        super().__init__()
        self.block_type = block_type
        self.is_damaged = False
        properties = BLOCK_ATTRIBUTES.get(block_type)

        # Image loading
        if self.block_type not in Block.images:
            img_name = properties['img']
            dmg_img_name = properties.get('damaged_img', properties['img'])
            Block.images[self.block_type] = {
                'normal': block_load(img_name),
                'damaged': block_load(dmg_img_name)
            }
        
        self.image_normal = Block.images[self.block_type]['normal']
        self.image_damaged = Block.images[self.block_type]['damaged']

        # Sound loading
        if self.block_type not in Block.sounds:
            Block.sounds[self.block_type] = {
                'hit': pygame.mixer.Sound(join('Assets/Music', f'{block_type}hit.mp3')),
                'semi break': pygame.mixer.Sound(join('Assets/Music', f'{block_type}semibreak.mp3')),
                'break': pygame.mixer.Sound(join('Assets/Music', f'{block_type}break.mp3')),
            }
        self.blockhitsound = Block.sounds[self.block_type]['hit']
        self.blockhitsound.set_volume(0.3)
        self.blocksemi_breaksound = Block.sounds[self.block_type]['semi break']
        self.blocksemi_breaksound.set_volume(0.3)
        self.blockbreaksound = Block.sounds[self.block_type]['break']
        self.blockbreaksound.set_volume(0.3)

        self.first_time = True
        self.image = self.image_normal
        self.rect = self.image.get_rect(bottomleft=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.max_health = properties['health']
        self.health = self.max_health
        self.mass = properties['mass']
        self.Vxblock = Vxblock
        self.Vyblock = Vyblock
        self.state = 'init'

        self.restitution = 0.2 

    def update(self, group):
        # --- Apply Friction ---
        if self.Vxblock > 0:
            self.Vxblock -= 0.05
            if self.Vxblock < 0: self.Vxblock = 0
        elif self.Vxblock < 0:
            self.Vxblock += 0.05
            if self.Vxblock > 0: self.Vxblock = 0
            
        self.Vyblock += Gravity

        if self.Vyblock > 12:
            self.Vyblock = 12
        # --- Move horizontally ---
        self.rect.x += self.Vxblock
        self.handle_horizontal_collisions(group)
        # --- Move vertically ---
        self.rect.y += self.Vyblock
        self.handle_vertical_collisions(group)
        # --- Floor boundary ---
        self.boundary()

    def handle_horizontal_collisions(self, group):
        collided_blocks = pygame.sprite.spritecollide(self, group, False)
        for block in collided_blocks:
            if block == self:
                continue
            if self.Vxblock > 0:
                self.rect.right = block.rect.left
                self.Vxblock = -self.Vxblock * self.restitution
            elif self.Vxblock < 0:
                self.rect.left = block.rect.right
                self.Vxblock = -self.Vxblock * self.restitution

            if abs(self.Vxblock) < 0.5:
                self.Vxblock = 0

    def handle_vertical_collisions(self, group):
        collided_blocks = pygame.sprite.spritecollide(self, group, False)
        for block in collided_blocks:
            if block == self:
                continue
            if self.Vyblock > 0:  # Falling down
                self.rect.bottom = block.rect.top
                self.Vyblock = -self.Vyblock * self.restitution
                if abs(self.Vyblock) < 0.5:
                    self.Vyblock = 0
                    self.state = 'rest'
            elif self.Vyblock < 0:  # Moving up
                self.rect.top = block.rect.bottom
                self.Vyblock = -self.Vyblock * self.restitution

    def boundary(self):
        if self.rect.bottom >= floor:
            self.rect.bottom = floor
            if self.Vyblock > 0:
                self.Vyblock = -self.Vyblock * self.restitution
                if abs(self.Vyblock) < 0.5:
                    self.Vyblock = 0
                    self.state = 'rest'

        if self.rect.right >= screen_width:
            self.rect.right = screen_width
            if self.Vxblock > 0:
                self.Vxblock = -self.Vxblock * self.restitution

        if self.rect.left <= 0:
            self.rect.left = 0
            if self.Vxblock < 0:
                self.Vxblock = -self.Vxblock * self.restitution

    def damage(self, damage=0):
        self.health -= damage
        if damage > 0:
            self.blockhitsound.play()

        image_updated = False
        if self.health <= self.max_health / 2 and not self.is_damaged:
            self.image = self.image_damaged
            if self.first_time:
                self.blockhitsound.stop()
                self.blocksemi_breaksound.play()
                self.first_time = False
            self.is_damaged = True
            image_updated = True

        if image_updated:
            self.mask = pygame.mask.from_surface(self.image)

        if self.health <= 0:
            self.blockhitsound.stop()
            self.blockbreaksound.play()
            self.kill()
