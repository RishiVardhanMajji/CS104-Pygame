

screen_width=1280
screen_height=720
floor=574
block_size_val=60#pxl sixe of blocks
slingshot_brown=(60,31,16)
slingshot_size=(80,200)
spring_custom=100
left_slingshot_pos=((screen_width//4),floor)
left_slingshot_loadpos=((screen_width//4)+10,floor-164)
right_slingshot_pos=(screen_width-left_slingshot_pos[0],floor)
right_slingshot_loadpos=(screen_width-left_slingshot_pos[0]-10,floor-164)
Gravity=0.2
spring_constant=0.2  #to be verified
collision_factor_with_wall=0.8
collision_factor_with_block=0.1
bird_mass=2
block_size=(60,60)
bird_size=(50,50) 
friction=0.01
settings = {
    "Difficulty": ["Easy", "Medium", "Hard"],
    "Wind Speed": ["Low", "Medium", "High"],
    "Wind Direction": ["Opposite to Player", "In Direction of Player"],
    "Wind Type": ["Constant", "Variable"]
}
setting_keys = list(settings.keys())