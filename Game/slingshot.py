import pygame
import math

from os.path import join
from my_utilities import *
from Game.birds import Bird
import numpy as np 
from values import *

class Slingshot():

    def __init__(self, screen, side):
        self.screen = screen
        self.side = side
        self.state = 'idle'  # States: 'idle', 'loaded', 'pulling'
        self.bird_loaded = None  
        self.pull_vector = pygame.Vector2(0, 0) 
        self.max_pull_distance = 400 
        SLINGSHOT_IMG_REST = pygame.image.load(join('Assets/Backgrounds', 'slingshotrest.webp')).convert_alpha()
        SLINGSHOT_IMG_PULL = pygame.image.load(join('Assets/Backgrounds', 'slingshotpull.webp')).convert_alpha()
        self.pull_sound = pygame.mixer.Sound(join('Assets/Music', 'Slingshotpull.mp3'))
        self.pull_sound.set_volume(0.3) 
        self.release_sound = pygame.mixer.Sound(join('Assets/Music', 'Slingshotrelease.mp3'))
        self.release_sound.set_volume(0.3)
        self.isplayed=False

        SLINGSHOT_CACHE = {
            'left_rest': pygame.transform.scale(SLINGSHOT_IMG_REST, slingshot_size),
            'left_pull': pygame.transform.scale(SLINGSHOT_IMG_PULL, slingshot_size),
            'right_rest': pygame.transform.flip(pygame.transform.scale(SLINGSHOT_IMG_REST, slingshot_size), True, False),
            'right_pull': pygame.transform.flip(pygame.transform.scale(SLINGSHOT_IMG_PULL, slingshot_size), True, False)
        }
        if side == 'left':
            self.image_rest = SLINGSHOT_CACHE['left_rest']
            self.image_pull = SLINGSHOT_CACHE['left_pull']
            self.load_pos = left_slingshot_loadpos
            self.base_pos = left_slingshot_pos
            self.anchor_front = (self.base_pos[0] - 18, self.base_pos[1] - 165)
            self.anchor_back = (self.base_pos[0] + 18, self.base_pos[1] - 165)

        elif side == 'right':
            self.image_rest = SLINGSHOT_CACHE['right_rest']
            self.image_pull = SLINGSHOT_CACHE['right_pull']
            self.load_pos = right_slingshot_loadpos
            self.base_pos = right_slingshot_pos
            self.anchor_front = (self.base_pos[0] + 18, self.base_pos[1] - 165)
            self.anchor_back = (self.base_pos[0] - 18, self.base_pos[1] - 165)

        self.rect_rest = self.image_rest.get_rect(midbottom=self.base_pos)
        self.rect_pull = self.image_pull.get_rect(midbottom=self.base_pos)
        self.current_rect = self.rect_rest
        self.current_image = self.image_rest


    def load_bird(self, bird):
        if self.state == 'idle':
            bird.rect.center = self.load_pos
            self.bird_loaded = bird 
            
    def start_pull(self):
        if self.state == 'loaded' and self.bird_loaded:
            self.state = 'pulling'

    def update_pull(self, mouse_pos):
        if self.state == 'pulling' and self.bird_loaded:
            if self.isplayed==False:
                self.pull_sound.play() # Play pull sound
                self.isplayed=True
            pull_origin = pygame.Vector2(self.load_pos)
            mouse_vector = pygame.Vector2(mouse_pos)
            self.pull_vector = mouse_vector - pull_origin
            distance = self.pull_vector.length()
            if distance==0: distance=1 
            self.pull_vector=(self.pull_vector/(distance**(0.1)))

            bird_draw_pos = pull_origin + self.pull_vector
            self.bird_loaded.set_pull_position(tuple(bird_draw_pos))
            
            if distance > self.max_pull_distance:
                self.pull_vector.scale_to_length(self.max_pull_distance)
                
        #//////////////////////////////////////////////////////////////////////////

    def release_bird(self):
        if self.state == 'pulling' and self.bird_loaded:
            launch_data = self.calculate_trajectory()
            self.pull_sound.stop() # Stop pull sound
            self.release_sound.play() # Play release sound

            if launch_data: 
                launched_bird_type = self.bird_loaded.bird_type
                self.bird_loaded.kill()
                self.bird_loaded = None 
                self.state = 'idle'
                self.pull_vector = pygame.Vector2(0, 0)
                # Return launch type and data (pos, angle, momentum)
                return launched_bird_type, launch_data
            else:
                return None, None
        return None, None

    def calculate_trajectory(self):
        if self.pull_vector.length_squared() < 1:
            return None
       
        launch_vector = -self.pull_vector
        angle = math.atan2(-launch_vector.y, launch_vector.x)
        elongation = self.pull_vector.length()
        momentum = elongation * spring_constant
        launch_pos = tuple(pygame.Vector2(self.load_pos) + self.pull_vector)
        return launch_pos, angle, momentum

    def draw(self, screen,wind):
        if self.state == 'pulling' :
             self.current_image = self.image_pull
             self.current_rect = self.rect_pull

             self.draw_slingshot_lines(screen)
             trajectory_points=self.calculate_trajectory_points(wind)
             pointradius=3
             for point in trajectory_points:
                draw_traj_pos = (int(point[0]),int(point[1]))
                pygame.draw.circle(screen,(255,0,0),draw_traj_pos,pointradius)
        else:
            self.current_image = self.image_rest
            self.current_rect = self.rect_rest
        
        screen.blit(self.current_image, self.current_rect)

    def draw_slingshot_lines(self, screen):
        if not self.bird_loaded: return

        line_color = (48, 23, 8) # Dark brown
        line_thickness = 11
        bird_center = pygame.Vector2(self.bird_loaded.rect.center)

        pygame.draw.line(screen, line_color, self.anchor_back, bird_center, line_thickness)
        pygame.draw.line(screen, line_color, self.anchor_front, bird_center, line_thickness)
        
    def calculate_trajectory_points(self,wind):
        points=[]
        launch_data=self.calculate_trajectory()
        if not launch_data: return points
        launch_pos,angle,momentum = launch_data
        initial_speed=momentum/bird_mass
        
        Vx=math.cos(angle)*initial_speed
        Vy=(-1)*math.sin(angle)*initial_speed
        
        time_gap=3
        no_steps=16
        current_pos=pygame.Vector2(launch_pos)
        
        for i in range(no_steps):
            Vx += wind*time_gap
            Vy += Gravity*time_gap
            
            current_pos.x += Vx*time_gap
            current_pos.y += Vy*time_gap
            
            if i%2 == 0:
                points.append(tuple(current_pos))
            
            if current_pos.y >= floor:
                break
        return points
        