import pygame
import traceback
import sys
import random
import math
import numpy as np
import os
from os import listdir
from my_utilities import *
from values import *
from os.path import join
from Screen_mode.start_game import *
from Screen_mode.game_setup import *
from Game.Game import RunGame

#////////////////////////////////////////////////////////////////////////////////
#pygame setup
pygame.init()
pygame.mixer.init()

screen=pygame.display.set_mode((1280,720),pygame.RESIZABLE)
pygame.display.set_caption("Angry Birds")
pygame.display.set_icon(pygame.image.load("Assets/Logos/main_logo.jpg").convert_alpha())
font=pygame.font.Font("Assets/angrybirds-regular.ttf",50)

clock = pygame.time.Clock()
def main(screen):
    start_game(screen,clock)    
    pygame.quit()
    sys.exit()
           
if __name__=="__main__":
    main(screen)
    
