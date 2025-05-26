import pygame
import numpy as np
import random
import math
from Game.blocks import *
from Game.projectile import *
from Game.birds import *
from Game.slingshot import *
from Screen_mode.game_setup import *
from Screen_mode.start_game import *
from my_utilities import *
from values import *

birds={'Red','Blue','Bomb','Chuck'}

zeroarr=np.zeros((6,4),dtype='object')
for x in range(4):
    for y in range(6):
        zeroarr[y,x]=((x,-y))
myarr=zeroarr.flatten()


    
def block_selector(block_types):
    return random.choice(block_types)

def block_position(i):
    pos_array=np.random.choice(myarr,i,replace=False)
    req_list=[]
    for arr in pos_array:
        arr=np.array(arr)
        req_list.append(np.array([(screen_width//60),0])+arr*block_size_val +np.array([0,floor]))
    return req_list

def fortress_setup(req_list):
    left_fortress=pygame.sprite.Group()
    right_fortress=pygame.sprite.Group()
    block_types = ['wood', 'stone', 'glass', 'woodhollow', 'stonehollow', 'glasshollow']
    for posn in req_list:
        blocktype=block_selector(block_types)
        block1=Block(blocktype,posn)
        block2=Block(blocktype,((screen_width-block_size_val)-posn[0],posn[1]))
        left_fortress.add(block1)
        right_fortress.add(block2)
    return left_fortress,right_fortress
    
def bird_init():
     left_birds=pygame.sprite.Group()
     right_birds=pygame.sprite.Group()
     for bird in birds:
         left_birds.add(Bird(bird,'left'))
         right_birds.add(Bird(bird,'right'))
        
     return left_birds,right_birds

def data(game_data,start_time):
    mytime=pygame.time.get_ticks()-start_time
    setting_values=[0,0]
    myfunction=0
    if game_data['Difficulty'] == 'Easy' : setting_values[0]=5
    elif game_data['Difficulty'] == 'Medium' : setting_values[0]=10
    elif game_data['Difficulty'] == 'Hard' : setting_values[0]=12
    
    if game_data['Wind Type'] == 'Constant' : myfunction = 1
    elif game_data['Wind Type'] == 'Variable' : myfunction = ((math.sin(math.pi * (mytime//1000))*10)//10)
    
    if game_data['Wind Direction'] =='Opposite to Player' :  myfunction = (-1)*myfunction
    elif game_data['Wind Direction'] =='In Direction of Player' : pass
     
    if game_data['Wind Speed'] =='Low' :setting_values[1]=0*(myfunction)
    elif game_data['Wind Speed'] =='Medium' : setting_values[1]=0.05*(myfunction)
    elif game_data['Wind Speed'] =='High' : setting_values[1]=0.1*(myfunction)
    
    return setting_values
    
def RunGame(screen,clock,game_data):
    backgroundsurface=background_load('game_background.jpeg')
    start_time=pygame.time.get_ticks()
    player1_score=0
    player2_score=0
    player1_name=game_data.get('Player1','Player 1')
    player2_name=game_data.get('Player2','Player 2')
    #player names ......
  
#initiate settings
#setup
    left_slingshot=Slingshot(screen,'left')
    right_slingshot=Slingshot(screen,'right')
    left_birds,right_birds=bird_init()
    
    setting_values = data(game_data,start_time)
    no_of_blocks=setting_values[0]
    wind=setting_values[1]
    
    #put blocks in their assigned position
    left_fortress,right_fortress=fortress_setup(block_position(no_of_blocks))
    projectiles=pygame.sprite.GroupSingle()
    
    #G....A....M....E
    turn='left'
    current_slingshot=left_slingshot
    current_birds_group=left_birds
    target_fortress=right_fortress
    active_projectile=None  #......................
    game_state='aim' #...........aim,projectile,turnover,gameover
    winner=None
    pygame.mixer.music.load('Assets/Music/Cave Ambience Sound Effect.mp3')
    pygame.mixer.music.set_volume(1)
    game_start=True
    while game_start:
        pygame.mixer.music.play(-1)
        #check it..............////////////////////
        setting_values = data(game_data,start_time)
        no_of_blocks=setting_values[0]
        wind=setting_values[1]
        mousepos=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_start = False     
                    
            if game_state=='aim':   #player has to aim and release
                                
                if event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and current_slingshot.state=='idle':
                    for bird in current_birds_group:
                        loaded_bird=bird.get_loaded(mousepos)
                        if loaded_bird:  #load it on slingshot
                            current_slingshot.load_bird(loaded_bird)
                            current_slingshot.state='loaded'
                            break
                        
                if pygame.mouse.get_pressed()[0]:          
                    if current_slingshot.state == 'loaded' and current_slingshot.bird_loaded:
                        if current_slingshot.bird_loaded.rect.collidepoint(mousepos):
                            current_slingshot.start_pull()
                            
                     # If currently pulling, update the slingshot pull
                    if current_slingshot.state == 'pulling':
                        current_slingshot.update_pull(mousepos)
                        
                    if not loaded_bird and current_slingshot.bird_loaded:
                         if current_slingshot.bird_loaded.rect.collidepoint(mousepos):
                              current_slingshot.start_pull()

                            
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if current_slingshot.state == 'pulling':
                        launched_bird_type, launch_data = current_slingshot.release_bird()
                        
                        if launched_bird_type and launch_data:
                            launch_pos, angle, momentum = launch_data
                            # Calculate wind
                            wind = setting_values[1]
                            # Create projectile
                            active_projectile = Projectile(launched_bird_type, launch_pos, angle, momentum, wind,turn)
                            active_projectile.projectileaudio.play()
                            projectiles.add(active_projectile)
                            game_state = "projectile"
                            #Bird Respawn
                            current_birds_group.add(Bird(launched_bird_type,turn)) # Replenish the used type
                                      
        left_birds.update()
        right_birds.update()
        left_fortress.update(left_fortress)
        right_fortress.update(right_fortress)
                
        if game_state=='projectile': #bird is launched and projectile is active
            projectiles.update() 
            for proj in projectiles:
                possiblecollided=pygame.sprite.spritecollide(proj,target_fortress,False,pygame.sprite.collide_rect)
                for block in possiblecollided:
                    if pygame.sprite.collide_mask(proj,block):
                        damage=proj.collide(block)
                        if turn=='left':
                            player1_score+=(damage*10)//10
                        elif turn=='right':
                            player2_score+=(damage*10)//10
                    #try to add sound effets here and dealy time for corpse
                    game_state='turnover'
                    active_projectile=None
        if game_state == 'projectile':
           if not projectiles.sprite:
               game_state='turnover'
               active_projectile=None
                    
        if game_state != 'gameover':
            if turn=='right':
                if not left_fortress and not right_fortress:
                        winner='Draw'
                elif not left_fortress:
                    winner=player2_name
                    game_state='gameover'
                elif not right_fortress:
                        winner=player2_name
                        game_state='gameover'
                        
        if pygame.time.get_ticks()-start_time>200000 and turn == 'left':
            if player1_score>player2_score: winner=player1_name
            elif player2_score>player1_score: winner=player2_name
            else: winner='Draw'
            game_state='gameover'
                     
        if game_state=='turnover':
            active_projectile=None
            if turn=='left':
                turn='right'
                current_slingshot=right_slingshot
                current_birds_group=right_birds
                target_fortress=left_fortress
            elif turn=='right':
                turn='left'
                current_slingshot=left_slingshot
                current_birds_group=left_birds
                target_fortress=right_fortress
            game_state='aim'
            
        #screen show
        
        screen.blit(backgroundsurface,(0,0))
        set_floor(floor,screen)
        
        left_fortress.draw(screen)
        right_fortress.draw(screen)
        left_slingshot.draw(screen,wind)
        right_slingshot.draw(screen,wind)
        left_birds.draw(screen)
        right_birds.draw(screen)
        projectiles.draw(screen)
           
        if turn=='left' and game_state != 'gameover': 
            player1_color='yellow'
            player2_color='white'
        elif turn=='right' and game_state != 'gameover':
            player1_color='white'
            player2_color='yellow'
            
        text_writer(screen,player1_name,(150,30),player1_color,name_font)
        text_writer(screen,'Score :',(100,60),'white',name_font)
        text_writer(screen,str(player1_score),(200,60),'white',name_font)
        text_writer(screen,player2_name,(screen_width-150,30),player2_color,name_font)
        text_writer(screen,'Score :',(screen_width-200,60),'white',name_font)
        text_writer(screen,str(player2_score),(screen_width-100,60),'white',name_font)
        timeleft=(pygame.time.get_ticks()-start_time)//1000
        text_writer(screen,'Time Left :',(screen_width//2-60,30),'white',name_font_small)
        text_writer(screen,str(200-timeleft),(screen_width//2 +40,30),'white',name_font_small)
        text_writer(screen,'Wind :',(screen_width//2 -30,60),'white',name_font_small)
        text_writer(screen,str(wind),(screen_width//2 +30,60),'white',name_font_small)
            
        if game_state=='gameover':
            if winner=='Draw':
                text_writer(screen,'Game Over',(screen_width//2,screen_height//2),'white',font_big)
                text_writer(screen,'It\'s a Draw!',(screen_width//2,screen_height//2 + 120),'white',name_font)
            else:
                text_writer(screen,'Game Over',(screen_width//2,screen_height//2),'white',font_big)
                text_writer(screen,f'{winner} Wins!',(screen_width//2,screen_height//2 +120),'white',font_big)
            playagainrect=text_writer(screen,'Play Again',(screen_width//2,screen_height//2 +200),'white',name_font)
            newgamerect=text_writer(screen,'New Game',(screen_width//2,screen_height//2 + 300),'white',name_font)
            if pygame.mouse.get_pressed()[0]:
                mouse_pos=pygame.mouse.get_pos()
                if playagainrect.collidepoint(mouse_pos):
                    game_start=True
                    RunGame(screen,clock,game_data)
                elif newgamerect.collidepoint(mouse_pos):
                    game_start=False
        
        pygame.display.flip()
        print(f"FPS: {clock.get_fps():.2f}")
        clock.tick(60)
            
    
    

    
        
    
    
    