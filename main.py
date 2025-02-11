from SaveLoadManager import SaveLoadSystem
from pgone import *
import pgzrun
from pygame import quit
from gui import *
import random
import os
import sys
from pygame.math import Vector2
import pygame
from attacks import attack
##############################################
#Defining variables
WIDTH = 1000
HEIGHT = 700
world = SpriteActor(Sprite("map.png",702,702,0,1,1,(255,255,255)), (WIDTH//2, HEIGHT//2))
player_idle = Sprite("hero_of_ashes.png",28,26,0,4)
player_walk = Sprite("hero_of_ashes.png",28,26,1,4)
player = SpriteActor(player_idle, (WIDTH//2, HEIGHT//2))
gamestate = "Menu"
menu_state = "Start Menu"
buttons = []
saveloadmanager = SaveLoadSystem(".savedata", "save_data")
player_active_attacks = []
player_active_attacks_actors = []
enemies_health, enemies_pos, number_of_enemies_to_spawn_next, enemies_color, enemmies_sprite_filenames, player_abilities, player_attacks = saveloadmanager.load_game_data(["enemies_health", "enemies_pos", "number_of_enemies_to_spawn_next","enemies_color", "enemies_sprite_filenames", "player_abilities", "player_attacks"], [[], [], 1, [], [], [], []])
enemies = []
if enemies_health != []:
    for index, enemy in enumerate(enemies_health):
        enemies.append(SpriteActor(Sprite("slimes/slime_idle2.png", 22, 17, enemies_color[index], 7), enemies_pos[index]))
#####################################################
#Setting up scaling for the screen and player speed
world.scale = 3
player.scale = 1
player.speed = 3*player.scale
#Load saved data, but assign defaults... basically half of the stuff that SaveLoadSystem does
##########################################################
#Gamestate functions
def game_in_progress():
    global number_of_enemies_to_spawn_next, gamestate, enemies_health, menu_state, player_active_attacks, player_active_attacks_actors
    #Handle Player movement, world will auto-scroll
    if keyboard.d:
        player.flip_h = True
        if world.right <= WIDTH or player.x <= WIDTH//2:
            player.x += player.speed
        else:
            world.x -= player.speed
            for enemy in enemies:
                enemy.x -= player.speed
            for attack in player_active_attacks_actors:
                attack.x -= player.speed
        if player.right > world.right:
            player.x -= player.speed
    if keyboard.s:
        if world.bottom <= HEIGHT or player.y <= HEIGHT//2:
            player.y += player.speed
        else:
            world.y -= player.speed
            for enemy in enemies:
                enemy.y -= player.speed
            for attack in player_active_attacks_actors:
                attack.y -= player.speed
        if player.bottom > world.bottom:
            player.y -= player.speed
    if keyboard.a:
        player.flip_h = False
        if world.left >= 0 or player.x >= WIDTH/2:
            player.x -= player.speed
        else:
            world.x += player.speed
            for enemy in enemies:
                enemy.x += player.speed
            for attack in player_active_attacks_actors:
                attack.x += player.speed
        if player.left < world.left:
            player.x += player.speed
    if keyboard.w:
        if world.top >= 0 or player.y >= HEIGHT//2:
            player.y -= player.speed
        else:
            world.y += player.speed
            for enemy in enemies:
                enemy.y += player.speed
            for attack in player_active_attacks_actors:
                attack.y += player.speed
        if player.top < world.top:
            player.y += player.speed
    if keyboard.d or keyboard.s or keyboard.a or keyboard.w:
        player.sprite = player_walk
    else:
        player.sprite = player_idle         
    #Handle Enemies
    if enemies == []:
        gamestate = "Menu"
        menu_state = "Level up init"
        for i in range(0, number_of_enemies_to_spawn_next):
            row_number = random.randint(0, 6)
            enemies_health.append(number_of_enemies_to_spawn_next)
            new_sprite = Sprite("slimes/slime_idle2.png",22,17,row_number,7)
            new_x = random.randint(int(world.left), int(world.right))
            new_y = random.randint(int(world.top), int(world.bottom))
            new_slime = SpriteActor(new_sprite,(new_x,new_y))
            enemies.append(new_slime)
        number_of_enemies_to_spawn_next += 1
    for index, enemy in enumerate(enemies):
        #Enemy movement
        if enemy.sprite.filename == "slimes/slime_idle2.png":
            if enemy.x < player.x:
                enemy.flip_h = False
            else:
                enemy.flip_h = True
            player_pos = Vector2(player.x, player.y)
            enemy_pos = Vector2(enemy.x, enemy.y)
            movement_vector = player_pos - enemy_pos
            if movement_vector.length() != 0:
                movement_vector = movement_vector.normalize()
            enemy.x += movement_vector.x
            enemy.y += movement_vector.y
            if enemy.collidelist(enemies) != -1 and enemy.collidelist(enemies) != index:
                enemy.x -= movement_vector.x * 0.5
                enemy.y -= movement_vector.y * 0.5

            if enemies_health[index] <= 0:
                enemy.sprite = Sprite("slimes/slime_die.png", 33, 15, enemy.sprite.row_number, 13)
        elif enemy.sprite.filename == "slimes/slime_die.png":
            if enemy.sprite.i == enemy.sprite.frame_count - 1:
                enemies.pop(index)
                enemies_health.pop(index)
        elif enemy.sprite.filename == "slimes/slime_hit.png":
            player_pos = Vector2(player.x, player.y)
            enemy_pos = Vector2(enemy.x, enemy.y)
            movement_vector = player_pos - enemy_pos
            if movement_vector.length() != 0:
                movement_vector = movement_vector.normalize()
            enemy.x -= movement_vector.x
            enemy.y -= movement_vector.y
            if enemy.sprite.i == enemy.sprite.frame_count - 1:
                enemy.sprite = Sprite("slimes/slime_idle2.png",22,17,enemy.sprite.row_number,7,2)
    #Handle use of player attacks and abilities
    for index, attack in enumerate(player_attacks):
        if attack.cooldown_remaining <= 0:
            if player_abilities[index] == "Fireball":
                player_active_attacks_actors.append(Actor("fireball.png",player.pos))
                player_active_attacks.append(attack)
            elif player_abilities[index] == "Lightning":
                player_active_attacks_actors.append(Actor("lightning.png", player.pos))
                player_active_attacks.append(attack)
                #Start lightning
            attack.cooldown_remaining = 60 * attack.cooldown  
        else:
            attack.cooldown_remaining -= 1
    #Handle logic of player attacks. IE damage, movement, etc.
    for index, attack in enumerate(player_active_attacks):
        if player_active_attacks_actors[index].image == "fireball.png":
            #Fireball logic
            if player_active_attacks_actors[index].collidelist(enemies) != -1:
                for enemy_index, enemy in enumerate(enemies):
                    if enemy.sprite.filename != "slimes/sllime_hit.png":
                        damage = attack.attack(player_active_attacks_actors[index].pos, enemy.pos)
                        if damage > 0:
                            if enemy.sprite.filename == "slimes/slime_idle2.png":
                                sounds.hurt.play()
                                enemies_health[enemy_index] -= damage
                                enemy.sprite = Sprite("slimes/slime_hit.png", 22, 17, enemy.sprite.row_number, 3, 10/attack.stuntime)
                player_active_attacks_actors.pop(index)
                player_active_attacks.pop(index)
            else:
                if len(enemies) != 0:
                    fireball_pos = Vector2(player_active_attacks_actors[index].x, player_active_attacks_actors[index].y)
                    shortest_distance = 10000
                    closest_enemy_index = -1
                    for i, enemy in enumerate(enemies):
                        if enemy.distance_to(player_active_attacks_actors[index].pos) < shortest_distance:
                            shortest_distance = enemy.distance_to(player_active_attacks_actors[index].pos)
                            closest_enemy_index = i
                    enemy_pos = Vector2(enemies[closest_enemy_index].x, enemies[closest_enemy_index].y)
                    movement_vector = enemy_pos - fireball_pos
                    if movement_vector.length != 0:
                        movement_vector = movement_vector.normalize()
                    player_active_attacks_actors[index].x += movement_vector.x * 5
                    player_active_attacks_actors[index].y += movement_vector.y * 5

        elif player_active_attacks_actors[index].image == "lightning.png":
            #Lightning
            shortest_distance = 300
            closest_enemy_index = -1
            for i, enemy in enumerate(enemies):
                if enemy.distance_to(player_active_attacks_actors[index].pos) <= shortest_distance:
                    shortest_distance = enemy.distance_to(player_active_attacks_actors[index].pos)
                    closest_enemy_index = i
            if closest_enemy_index != -1:
                player_active_attacks_actors[index].midbottom = enemies[closest_enemy_index].pos
                damage = attack.attack(enemies[closest_enemy_index].pos, enemies[closest_enemy_index].pos)
                if damage > 0:
                    if enemies[closest_enemy_index].sprite.filename == "slimes/slime_idle2.png":
                        sounds.hurt.play()
                        enemies_health[closest_enemy_index] -= damage
                        enemies[closest_enemy_index].sprite = Sprite("slimes/slime_hit.png", 22, 17, enemies[closest_enemy_index].sprite.row_number, 3, 10/attack.stuntime)
                    else:
                        player_active_attacks.pop(index)
                        player_active_attacks_actors.pop(index)
            else:
                player_active_attacks.pop(index)
                player_active_attacks_actors.pop(index)
def menu():
    global gamestate, buttons, menu_state
    if menu_state == "Start Menu":
        if buttons != [button("start_button.png", (WIDTH//2, HEIGHT//2), 81, 54, 0, 1, 1)]:
            buttons = [button("start_button.png", (WIDTH//2,HEIGHT//2), 81, 54, 0, 1, 1)]
    elif menu_state == "Pause":
        if buttons != []:
            buttons = [button("main_menu.png",(WIDTH//2,HEIGHT//4),93,54,0,1,1),
                       button("unpause.png",(WIDTH//2,2*HEIGHT//4),47*3,18*3,0,1,1),
                       button("quit.png",(WIDTH//2,3*HEIGHT//4),24*3,18*3,0,1,1)]
    elif menu_state == "Level up":
        pass #Levelup code here
    elif menu_state == "Level up init":
        buttons = []
        #Select three random cards from images/sprites/buttons/level_up_cards and define buttons
        files = os.listdir("images/sprites/buttons/level_up_cards")
        for i in range(3):
            card = random.choice(files)
            card_button = button("level_up_cards/" + card, ((i+1) * WIDTH//4, HEIGHT//2), 100, 140, 0, 4, 10)
            #This hopefully makes it easy to add animated cards
            card_button.SpriteActor.sprite.frame_width = card_button.SpriteActor.width // 100
            buttons.append(card_button)
        menu_state = "Level up"

#############################################################

def draw():
    screen.clear()
    screen.fill("beige")
    #What is drawn is dependent on the gamestate
    if gamestate == "Game in progress":
        world.draw()
        player.draw()
        for enemy in enemies:
            enemy.draw()
        for attack in player_active_attacks_actors:
            attack.draw()
        screen.draw.text(f"Level  {number_of_enemies_to_spawn_next - 1}\nEnemies  remaining:  {len(enemies)}", centerx = WIDTH//2, top = 10, owidth = 1.5, ocolor = (1, 1, 1))
    if gamestate == "Menu":
        for button in buttons:
            button.SpriteActor.draw()

def update():
    global gamestate, menu_state
    #Check if the window is focused. If it isn't, pause the game.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            menu_state = "Pause"
            menu()
            on_mouse_down((WIDTH//2, 3*HEIGHT//4))
        if event.type == pygame.ACTIVEEVENT and gamestate != "Menu":
            if event.gain != 1:
                on_key_down(keys.ESCAPE)
    #Execute different code depending on the gamestate; menu() can have different menu_states that also change it.
    if gamestate == "Menu":
        menu()
    elif gamestate == "Game in progress":
        game_in_progress()
    #Checks if buttons are being hovered over
    mouse_pos = pygame.mouse.get_pos()
    mouse_hovering_over_buttons(mouse_pos)


def on_mouse_down(pos):
    #General logic for clicking buttons
    global menu_state, gamestate, buttons, enemies, enemies_health, number_of_enemies_to_spawn_next, player_abilities, player_attacks
    if gamestate == "Menu":
        for button in buttons:
            if button.mouse_collision_bool(pos):
                if button.get_filename() == "start_button.png":
                    menu_state = "None"
                    gamestate = "Game in progress"
                elif button.get_filename() == "main_menu.png":
                    enemies = []
                    enemies_health = []
                    number_of_enemies_to_spawn_next = 1
                    player.pos = (WIDTH//2, HEIGHT//2)
                    world.pos = (WIDTH//2, HEIGHT//2)
                    menu_state = "Start Menu"
                elif button.get_filename() == "unpause.png":
                    menu_state = "None"
                    gamestate = "Game in progress"
                elif button.get_filename() == "quit.png":
                    #Save vars here using saveloadmanager
                    enemies_pos = []
                    enemies_color = []
                    enemies_sprite_filenames = []
                    for enemy in enemies:
                        enemies_pos.append(enemy.pos)
                        enemies_color.append(enemy.sprite.row_number)
                        enemies_sprite_filenames.append(enemy.sprite.filename)
                    saveloadmanager.save_game_data([enemies_health,enemies_pos,number_of_enemies_to_spawn_next,enemies_color,enemies_sprite_filenames, player_abilities, player_attacks],["enemies_health", "enemies_pos", "number_of_enemies_to_spawn_next","enemies_color", "enemies_sprite_filenames", "player_abilities", "player_attacks"])
                    quit()
                    sys.exit()
                elif "level_up_cards" in button.get_filename():
                    #Code to add each ability to a list goes here
                    if button.get_filename() == "level_up_cards/fireball_card.png":# and "Fireball" not in player_abilities:
                        player_abilities.append("Fireball")
                        player_attacks.append(attack(2, 5, 10, 1))
                    elif button.get_filename() == "level_up_cards/chain_lightning_card.png":# and "Lightning" not in player_abilities:
                        player_abilities.append("Lightning")
                        player_attacks.append(attack(1, 1, 0, 1/5))
                    menu_state = "None"
                    gamestate = "Game in progress"

def mouse_hovering_over_buttons(pos):
    #Rotates buttons when they are hovered over
    global buttons
    for button in buttons:
        if button.mouse_collision_bool(pos):
            button.SpriteActor.angle = 5
            button.SpriteActor.scale = 1.1
        else:
            button.SpriteActor.angle = 0
            button.SpriteActor.scale = 1

def on_key_down(key):
    #Basic pause/play mechanic
    global gamestate, menu_state
    if key == keys.ESCAPE and gamestate != "Menu":
        gamestate = "Menu"
        menu_state = "Pause"
    elif key == keys.ESCAPE and gamestate == "Menu" and menu_state == "Pause":
        gamestate = "Game in progress"
        menu_state = "None"
try:
    pgzrun.go()
except pygame.error:
    print("\n\n\n\n\n\n\n\nThe game was quit")