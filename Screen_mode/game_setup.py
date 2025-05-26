
import pygame
import sys
from my_utilities import *
from values import * 

COLOR_MAIN_BOX_BG = (40, 70, 100, 220) # Semi-transparent main box background
COLOR_SETTINGS_AREA_BG = (60, 90, 120, 200) # Slightly lighter for settings area
COLOR_INPUT_BG = (230, 240, 255)     # Light background for input fields
COLOR_INPUT_BORDER = (150, 160, 170)
COLOR_INPUT_BORDER_ACTIVE = (255, 255, 255) # White border when active
COLOR_BUTTON_BG = (70, 130, 180)      # Steel blue for buttons
COLOR_BUTTON_HOVER = (100, 160, 210)  # Lighter blue on hover
COLOR_BUTTON_SELECTED = (30, 80, 130) # Darker blue when selected
COLOR_BUTTON_BORDER = (180, 190, 200)
COLOR_TEXT_LIGHT = (240, 240, 240)    
COLOR_TEXT_DARK = (10, 10, 10)       
COLOR_TEXT_PLACEHOLDER = (160, 160, 160) 
COLOR_ERROR = (255, 80, 80)           # Red for error messages

PADDING = 15
INPUT_BOX_HEIGHT = 45
BUTTON_HEIGHT = 40
LABEL_WIDTH = 180 
MAX_PLAYER_NAME_LENGTH = 15 


def get_game_data(screen):
    
    current_selection = {key: None for key in setting_keys}
    input_text = {"Player1": "", "Player2": ""}
    active_box = None 

    box_width = int(screen_width * 0.9)
    box_height = int(screen_height * 0.9)
    box_rect = pygame.Rect(0, 0, box_width, box_height)
    box_rect.center = (screen_width // 2, screen_height // 2)

   
    input_boxes = {} 
    option_buttons = {} 
    start_button_rect = None

    # Cursor blinking logic
    cursor_visible = True
    cursor_timer = 0
    cursor_interval = 500  # milliseconds

    clock = pygame.time.Clock()
    run = True
    error_message = None
    error_timer = 0

    def draw_setup_screen(mouse_pos):
        nonlocal start_button_rect # Allow modification of the outer scope variable

        background_img = background_load('setup_background.jpg')
        screen.blit(background_img, (0, 0))
        
        main_box_surface = pygame.Surface(box_rect.size, pygame.SRCALPHA)
        main_box_surface.fill(COLOR_MAIN_BOX_BG)
        screen.blit(main_box_surface, box_rect.topleft)
        pygame.draw.rect(screen, COLOR_TEXT_LIGHT, box_rect, 2, border_radius=20)

        current_y = box_rect.top + PADDING * 2
        content_width = box_rect.width - PADDING * 4 # Usable width inside the box
        content_start_x = box_rect.left + PADDING * 2

        title_rect = text_writer(screen, 'Game Setup', (box_rect.centerx, current_y + 20), COLOR_TEXT_LIGHT, font_big)
        current_y = title_rect.bottom + PADDING * 2

        name_label_rect = text_writer(screen, 'Enter Player Names', (box_rect.centerx, current_y), COLOR_TEXT_LIGHT, name_font)
        current_y = name_label_rect.bottom + PADDING

        input_width = int(content_width * 0.6)
        input_start_x = box_rect.centerx - (input_width // 2)

        for i, player in enumerate(["Player1", "Player2"]):
            input_box_rect = pygame.Rect(input_start_x, current_y, input_width, INPUT_BOX_HEIGHT)
            input_boxes[player] = input_box_rect 

            is_active = active_box == player
            border_color = COLOR_INPUT_BORDER_ACTIVE if is_active else COLOR_INPUT_BORDER
            bg_color = COLOR_INPUT_BG

            pygame.draw.rect(screen, bg_color, input_box_rect, border_radius=10)
            pygame.draw.rect(screen, border_color, input_box_rect, width=2, border_radius=10)

            display_text = input_text[player]
            if display_text:
                text_surface = name_font.render(display_text, True, COLOR_TEXT_DARK)
                screen.blit(text_surface, (input_box_rect.x + PADDING // 2, input_box_rect.y + (INPUT_BOX_HEIGHT - text_surface.get_height()) // 2))
            elif not is_active: 
                placeholder = name_font.render(f"Enter {player} Name", True, COLOR_TEXT_PLACEHOLDER)
                screen.blit(placeholder, (input_box_rect.x + PADDING // 2, input_box_rect.y + (INPUT_BOX_HEIGHT - placeholder.get_height()) // 2))

            # Blinking Cursor
            if is_active and cursor_visible:
                text_width = name_font.render(display_text, True, COLOR_TEXT_DARK).get_width()
                cursor_x = input_box_rect.x + PADDING // 2 + text_width + 2
                cursor_y1 = input_box_rect.y + PADDING // 2
                cursor_y2 = input_box_rect.bottom - PADDING // 2
                pygame.draw.line(screen, COLOR_TEXT_DARK, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)

            current_y += INPUT_BOX_HEIGHT + PADDING 

        current_y += PADDING

        #  Settings Section
        settings_area_rect = pygame.Rect(content_start_x, current_y, content_width, box_rect.bottom - current_y - PADDING * 5)
        settings_area_surface = pygame.Surface(settings_area_rect.size, pygame.SRCALPHA)
        settings_area_surface.fill(COLOR_SETTINGS_AREA_BG)
        screen.blit(settings_area_surface, settings_area_rect.topleft)
        pygame.draw.rect(screen, COLOR_TEXT_LIGHT, settings_area_rect, 1, border_radius=15) 

        settings_y = settings_area_rect.top + PADDING

        option_buttons.clear() 

        for key in setting_keys:
           
            label_pos = (settings_area_rect.left + PADDING, settings_y + (BUTTON_HEIGHT - name_font_small.get_height()) // 2)
            label_surface = name_font_small.render(f"{key}:", True, COLOR_TEXT_LIGHT)
            screen.blit(label_surface, label_pos)

            button_start_x = settings_area_rect.left + PADDING + LABEL_WIDTH
            current_x = button_start_x
            for option in settings[key]:
                option_surface = name_font.render(option, True, COLOR_TEXT_LIGHT)
                text_width, text_height = option_surface.get_size()
                button_width = text_width + PADDING * 2

                if current_x + button_width > settings_area_rect.right - PADDING:
                     current_x = button_start_x
                     settings_y += BUTTON_HEIGHT + PADDING

                button_rect = pygame.Rect(current_x, settings_y, button_width, BUTTON_HEIGHT)
                option_buttons[(key, option)] = button_rect 

                is_selected = current_selection[key] == option
                is_hovered = button_rect.collidepoint(mouse_pos)

                color = COLOR_BUTTON_BG
                if is_selected:
                    color = COLOR_BUTTON_SELECTED
                elif is_hovered:
                    color = COLOR_BUTTON_HOVER

                pygame.draw.rect(screen, color, button_rect, border_radius=15)
                pygame.draw.rect(screen, COLOR_BUTTON_BORDER, button_rect, width=1, border_radius=15) # Subtle border

                # Center text in button
                text_rect = option_surface.get_rect(center=button_rect.center)
                screen.blit(option_surface, text_rect)

                current_x += button_rect.width + PADDING

            settings_y += BUTTON_HEIGHT + PADDING * 2 

       
        start_button_y = box_rect.bottom - PADDING  - BUTTON_HEIGHT // 2
        start_button_rect = draw_start_button(screen, clock, (box_rect.centerx, start_button_y), mouse_pos)

        # Error Message Display
        if error_message and pygame.time.get_ticks() < error_timer:
            text_writer(screen, error_message, (box_rect.centerx, start_button_rect.top - PADDING * 2), COLOR_ERROR, name_font_small)


    #Draw the START Button
    def draw_start_button(screen, clock, center_pos, mouse_pos):
        """Draws the START button and handles its hover effect."""
        button_text = "START GAME"
        start_surface = font.render(button_text, True, COLOR_TEXT_LIGHT)
        
        button_rect = start_surface.get_rect(center=center_pos).inflate(PADDING * 2, PADDING)

        is_hovered = button_rect.collidepoint(mouse_pos)
        color = COLOR_BUTTON_HOVER if is_hovered else COLOR_BUTTON_BG

        pygame.draw.rect(screen, color, button_rect, border_radius=20)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, button_rect, width=2, border_radius=20) # Border

        screen.blit(start_surface, start_surface.get_rect(center=button_rect.center))
        return button_rect 
    while run:
        mouse_pos = pygame.mouse.get_pos()

        current_time = pygame.time.get_ticks()
        if current_time - cursor_timer >= cursor_interval:
            cursor_visible = not cursor_visible
            cursor_timer = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                clicked_on_input = False
                for player, rect in input_boxes.items():
                    if rect.collidepoint(mouse_pos):
                        active_box = player
                        clicked_on_input = True
                        break
                if not clicked_on_input:
                    active_box = None 
                for (setting, option), rect in option_buttons.items():
                    if rect.collidepoint(mouse_pos):
                        current_selection[setting] = option
                        break 

                if start_button_rect and start_button_rect.collidepoint(mouse_pos):
                    
                    all_settings_selected = all(current_selection.values())
                    if not all_settings_selected:
                        error_message = "Please select an option for all settings!"
                        error_timer = pygame.time.get_ticks() + 2000 #2sec
                    else:
                        result = {
                            "Player1": input_text["Player1"].strip() or "Player 1", # Default names
                            "Player2": input_text["Player2"].strip() or "Player 2"
                        }
                        result.update(current_selection)
                        return result 
                    
            if event.type == pygame.KEYDOWN:
                if active_box: 
                    if event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                        if active_box == "Player1":
                            active_box = "Player2"
                        else:
                            active_box = None
                    elif event.key == pygame.K_BACKSPACE:
                        input_text[active_box] = input_text[active_box][:-1]
                    elif len(input_text[active_box]) < MAX_PLAYER_NAME_LENGTH:
                        if event.unicode.isprintable():
                             input_text[active_box] += event.unicode
                elif event.key == pygame.K_ESCAPE: 
                     pygame.quit()
                     sys.exit()


        # Drawing
        draw_setup_screen(mouse_pos)
        pygame.display.flip()
        clock.tick(60) 

