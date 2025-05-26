import pygame
import sys
from os.path import join
from values import *
pygame.font.init()

font=pygame.font.Font("Assets/angrybirds-regular.ttf",50)
font_big=pygame.font.Font("Assets/angrybirds-regular.ttf",80)
name_font=pygame.font.SysFont("comicsans",35)
name_font_small=pygame.font.SysFont("comicsans",24)


def background_load(name):
    req_image=pygame.image.load(join("Assets/Backgrounds",name)).convert()
    req_image=pygame.transform.smoothscale(req_image,(screen_width,screen_height))
    return req_image

def block_load(name):
    req_image=pygame.image.load(join("Assets/Blocks",name)).convert_alpha()
    req_image=pygame.transform.smoothscale(req_image,block_size)
    return req_image

def text_writer(screen,text,text_pos,color,my_font=font):
    text_surface=my_font.render(text,True,color)
    text_rect=text_surface.get_rect(center=text_pos)
    screen.blit(text_surface,text_rect)
    return text_rect

def bird_load(name):
    req_image=pygame.image.load(f"Assets/Birds/{name}.webp").convert_alpha()
    req_image=pygame.transform.smoothscale(req_image,bird_size)
    return req_image

def set_floor(floor,screen):
    floor_img=pygame.image.load("Assets/Backgrounds/floor.jpeg").convert()#......//////////////
    floor_img=pygame.transform.smoothscale(floor_img,(screen_width,screen_height-floor))
    floor_rect=floor_img.get_rect(topleft=(0,floor))
    screen.blit(floor_img,floor_rect)

    
        
   
        
           
        
    