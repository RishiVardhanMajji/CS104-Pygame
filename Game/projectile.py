import pygame
import math
from os.path import isfile, join
from my_utilities import *
from values import * 

class Projectile(pygame.sprite.Sprite):
    images = {}
    sounds = {}

    def __init__(self, bird_type, pos, angle, momentum, air, side):
        super().__init__()
        self.side = side # 'left' or 'right'
        self.air = air # Wind effect
        self.bird_type = bird_type
        self.no_of_bounces = 0 # Number of bounces before becoming a corpse

        
        if bird_type not in Projectile.images:
            Projectile.images[bird_type] = {
                'air': bird_load(f'{bird_type}_projectile'),
                'corpse': bird_load(f'{bird_type}_corpse')
             }
        self.image_air = Projectile.images[self.bird_type]['air']
        self.image_corpse = Projectile.images[self.bird_type]['corpse']

        if bird_type not in Projectile.sounds:
            Projectile.sounds[bird_type] = {
                'air': pygame.mixer.Sound(join('Assets/Music', f'{bird_type} projectile sound .mp3')),
                'corpse': pygame.mixer.Sound(join('Assets/Music', f'{bird_type} corpse sound .mp3')),
            }
        self.projectileaudio = Projectile.sounds[bird_type]['air']
        self.projectileaudio.set_volume(0.3)
        self.projectileaudio.play() 
        self.corpseaudio = Projectile.sounds[bird_type]['corpse']
        self.corpseaudio.set_volume(0.3)
        # ---------------------------------
        self.image = self.image_air
        if self.side == 'right':
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

        initial_speed = momentum / bird_mass
        self.Vx = math.cos(angle) * initial_speed
        self.Vy = -math.sin(angle) * initial_speed 

        self.start_time = pygame.time.get_ticks()
        self.has_collided = False 
        self.collision_time = 0 

    def update(self):
        """Updates projectile position, handles gravity, air resistance, boundaries, and corpse state."""
        if self.has_collided:
            self.Vy += Gravity
            self.Vx *= 0.98   
            # Stop movement if slow
            if abs(self.Vx) < 0.1: self.Vx = 0
            # Update position
            self.rect.x += int(self.Vx)
            self.rect.y += int(self.Vy)
            
            # Corpse floor collision 
            if self.rect.bottom >= floor:
                self.rect.bottom = floor
                self.Vy = -self.Vy * 0.1
                self.Vx *= 0.8       # High friction on ground
                if abs(self.Vy) < 0.5: self.Vy = 0 # Stop bouncing if slow

            # Remove corpse after timeout or when stopped
            time_since_collision = pygame.time.get_ticks() - self.collision_time
            is_stopped_on_floor = abs(self.Vx) < 0.1 and abs(self.Vy) < 0.5 and self.rect.bottom >= floor
            if time_since_collision > 4000 or (is_stopped_on_floor and time_since_collision > 2000):
                 self.kill()

        else:
            self.Vx += self.air # Apply wind
            self.Vy += Gravity  # Apply gravity

            # Update position
            self.rect.x += int(self.Vx)
            self.rect.y += int(self.Vy)

            # Boundary check(walls and floor)
            bounce_occurred = False
            if self.rect.bottom >= floor:
                self.rect.bottom = floor 
                self.Vy = -self.Vy * collision_factor_with_wall # Bounce
                self.Vx *= 0.9 # Friction
                bounce_occurred = True
            if self.rect.top <= 0: # Bounce
                self.rect.top = 0
                self.Vy = -self.Vy * collision_factor_with_wall
                bounce_occurred = True
            if self.rect.left <= 0:
                self.rect.left = 0
                self.Vx = -self.Vx * collision_factor_with_wall
                bounce_occurred = True
            elif self.rect.right >= screen_width:
                self.rect.right = screen_width
                self.Vx = -self.Vx * collision_factor_with_wall
                bounce_occurred = True

            if bounce_occurred: self.no_of_bounces += 1
            if self.no_of_bounces >= 3: 
                self.has_collided = True
                self.corpseaudio.play() 
                self.image = self.image_corpse
                if self.side == 'right':
                    self.image = pygame.transform.flip(self.image, True, False)
                old_center = self.rect.center
                self.rect = self.image.get_rect(center=old_center)
                self.mask = pygame.mask.from_surface(self.image)

            if pygame.time.get_ticks() - self.start_time > 6000: # 6 seconds
                self.kill()
                
    def damage_dealt(self, bird_type, block_type):
        current_momentum = math.hypot(self.Vx, self.Vy) * bird_mass
        damage = 0
        effectiveness = 1.0 #

        if bird_type=='Red': effectiveness = 0.75
        elif bird_type=='Blue': effectiveness = 0.9 if 'glass' in block_type else 0.6
        elif bird_type=='Chuck': effectiveness = 0.9 if 'wood' in block_type else 0.6
        elif bird_type=='Bomb': effectiveness = 0.9 if 'stone' in block_type else 0.6
        
        damage = current_momentum * effectiveness * 5

        return damage

    def collide(self, block): 
        if not self.has_collided and pygame.sprite.collide_mask(self, block):

            #Apply Damage
            damage = self.damage_dealt(self.bird_type, block.block_type)
            block.damage(damage)

            restitution = 0.5 
            m1 = bird_mass
            m2 = block.mass 
            v1x, v1y = self.Vx, self.Vy
            v2x = block.Vxblock
            v2y = block.Vyblock
            
            new_v1x = ((m1 - m2 * restitution) * v1x + (m2 * (1 + restitution)) * v2x) / (m1 + m2)
            new_v2x = ((m1 * (1 + restitution)) * v1x + (m2 - m1 * restitution) * v2x) / (m1 + m2)
            new_v1y = ((m1 - m2 * restitution) * v1y + (m2 * (1 + restitution)) * v2y) / (m1 + m2)
            new_v2y = ((m1 * (1 + restitution)) * v1y + (m2 - m1 * restitution) * v2y) / (m1 + m2)

            self.Vx = new_v1x
            self.Vy = new_v1y
            block.Vxblock = new_v2x
            block.Vyblock = new_v2y

            # Positional Correction (Separation) [[ USED AI ]]
            dx = block.rect.centerx - self.rect.centerx
            dy = block.rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)
            if distance == 0: distance = 0.1; dx = 0.1

            touching_distance = self.rect.width / 2 + block.rect.width / 2
            overlap = touching_distance - distance

            if overlap > 0: # Only apply if actually overlapping
                nx = dx / distance
                ny = dy / distance
                correction_factor = 0.6 # Gentler correction factor
                correction_amount = overlap * correction_factor
                separation_x = nx * correction_amount * 0.5
                separation_y = ny * correction_amount * 0.5

                self.rect.x -= int(separation_x)
                self.rect.y -= int(separation_y)
                block.rect.x += int(separation_x)
                block.rect.y += int(separation_y)

            self.has_collided = True
            self.corpseaudio.play()
            self.image = self.image_corpse
            if self.side == 'right': # Flip corpse if launched from right
                 self.image = pygame.transform.flip(self.image, True, False)
            old_center = self.rect.center
            self.rect = self.image.get_rect(center=old_center)
            self.mask = pygame.mask.from_surface(self.image)
            self.collision_time = pygame.time.get_ticks()

            return damage
        return 0