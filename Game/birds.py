import pygame
import random
from my_utilities import *
from values import *


class Bird(pygame.sprite.Sprite):
    images={}
    sounds={}
    def __init__(self,bird_type,side):
        super().__init__()
        y=random.randint(-100,100)
        self.bird_type=bird_type
        if bird_type not in Bird.images:
            Bird.images[bird_type] = {
                'default': bird_load(f'{bird_type}'), 
                'angry': bird_load(f'{bird_type}_angry'),
                'happy': bird_load(f'{bird_type}_happy'),
                'air': bird_load(f'{bird_type}_air'),
                'mouse': bird_load(f'{bird_type}_mouse'),
                'blink': bird_load(f'{bird_type}_blink'),
            }
        self.bird_images = Bird.images[bird_type]
        if self.bird_type=='Red': 
            x=-75
            self.blink_constant=-1000
        elif self.bird_type=='Blue': 
            x=-25
            self.blink_constant=0
        elif self.bird_type=='Chuck':
            x=25
            self.blink_constant=1000
        elif self.bird_type=='Bomb': 
            x=75
            self.blink_constant=1500
        self.image = self.bird_images['default'] 
        self.side=side
        if side=='left' : 
            self.pos=(left_slingshot_pos[0]+x,y)
        elif side == 'right' : 
            self.image=pygame.transform.flip(self.image, True, False)
            self.pos=(right_slingshot_pos[0]+x,y)
        self.rect=self.image.get_rect(center=self.pos)
        self.mask=pygame.mask.from_surface(self.image)
        self.state='air'
        self.birdVy=0
        self.birdVx=0
        if bird_type not in Bird.sounds:
            Bird.sounds[bird_type] = {
                'mouse': pygame.mixer.Sound(join('Assets/Music', f'{bird_type} load sound .mp3')),
            }
        self.birdloadsound = Bird.sounds[self.bird_type]['mouse']
        self.birdloadsound.set_volume(0.3)
        self.hasplayed=False
    def animation(self):
        current_image=self.image
        if self.state=='loaded':
             self.image = self.bird_images['default']
        elif  self.state=='pull':
            self.image = self.bird_images['angry']
        elif  self.state=='happy':
            self.image = self.bird_images['happy']
        elif self.state=='air':
            self.image = self.bird_images['air']
        elif self.state=='mouse':
           self.image = self.bird_images['mouse']
        elif self.state=='idle':  
            time_now=pygame.time.get_ticks()
            if (time_now+self.blink_constant)%5000 < 200: 
                self.image = self.bird_images['blink']
            else:
                self.image = self.bird_images['default']
        if self.image is not current_image: # Check if the surface object changed  #chatgpt
             old_center = self.rect.center
             if self.side == 'right':
                    self.image = pygame.transform.flip(self.image, True, False)
             self.rect = self.image.get_rect(center=old_center)
             self.mask = pygame.mask.from_surface(self.image)
            
            #used help of AI to optimise image loading
    def get_loaded(self,mousepos):
        if self.rect.collidepoint(mousepos):
            self.state='loaded'
            return self

    def gravity(self):
        if self.state != 'loaded' and self.state != 'pull':
            self.birdVy+=Gravity
            self.rect.centery+= self.birdVy
            if floor-self.rect.bottom < 50:
                self.state='happy'
            if self.rect.bottom>= floor :
                if self.birdVy > 10 :
                    self.birdVy = -(0.2)*self.birdVy
                else : 
                    self.birdVy=0
                    self.state='idle'
    
    def wall_boundary(self):
        if self.rect.left <=0:
            self.birdVx=-1*collision_factor_with_wall*self.birdVx
        elif self.rect.right >= screen_width:
            self.birdVx=-1*collision_factor_with_wall*self.birdVx
            
    def state_change(self):
        mouse_pos=pygame.mouse.get_pos()
        if self.state == 'idle':
                if self.rect.collidepoint(mouse_pos):
                    self.state = 'mouse'
                    if self.hasplayed==False:
                        self.birdloadsound.play()
                        self.hasplayed=True
        elif self.state == 'mouse' and not self.rect.collidepoint(mouse_pos):
            self.state = 'idle'
            self.hasplayed=False# Revert if mouse moves off
        
    
    def set_pull_position(self, pos):
        # Called by slingshot when dragging
        self.state = 'pull'
        self.rect.center = pos
                 
    def update(self):
        self.animation()
        self.gravity()
        self.wall_boundary()
        self.state_change()