import pygame
from my_utilities import *
from Screen_mode.game_setup import *
from Game.Game import RunGame
def start_game(screen,clock):
    screen.blit(background_load('intro_background.png'),(0,0))
    start_rect=pygame.draw.rect(screen,(173,216,230),(560,538,160,60),border_radius=20)
    text_writer(screen,'START',(640,570),'white')
    pygame.display.update()
    started=True
    while started:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                started=False
                pygame.quit()
                sys.exit()
        if(pygame.mouse.get_pressed())[0] and start_rect.collidepoint(pygame.mouse.get_pos()):
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    started=False
                    pygame.quit()
                    sys.exit()
                screen.blit(background_load('setup_background.jpg'),(0,0))
                game_data=get_game_data(screen)
                pygame.display.update()
                if game_data:
                    RunGame(screen,clock,game_data)  
                    started=False     
    #check the closing of this loop