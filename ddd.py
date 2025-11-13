from os import remove
from random import randint

import pygame
import random
import sys

from pygame.event import clear
from pygame.examples.cursors import image
from pygame.examples.music_drop_fade import starting_pos

# launching Pygame
pygame.init()

# window size
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Undertale Battle System")

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

cool_phase = False
zone_attack_interval = 2000
lastb_timer = 0
zn = None
secondlvl = False
# game zone
game_zone = pygame.Rect(200, 150, 400, 300)  # Прямоугольник, где игрок может двигаться
battle_activation_zone = pygame.Rect(350, 275, 50, 50)  # Зона активации боя внутри игровой зоны
battle_zone = pygame.Rect(250, 150, 400, 300)  # Зона проведения боя

# dialogue zone
dialog_zone = pygame.Rect(500, 400, 100, 50)

# player
player = pygame.Rect(250, 250, 20, 20)  # Игрок
spawn_point = (250, 250)  # Точка спавна игрока
player_color = BLACK
player_speed = 5

# projectiles
projectiles = []
projectile_speed = 3
spawn_timer = 0
SPAWN_INTERVAL = 30  # Интервал спавна снарядов (в кадрах)

# enemy
enemy = {"x": 400, "y": 100, "radius": 30, "color": YELLOW}
enemy_attack_timer = 0
ENEMY_ATTACK_INTERVAL = 120  # Интервал между атаками врага (в кадрах)

# cooldown for player attacks
player_attack_timer = 0
PLAYER_ATTACK_DELAY = 60  # 60 кадров = 1 секунда при 60 FPS
#this finction dont working beacouse I dont finish it yet so I just respawn player
def second_lavel():
    exit_battle()
    respawn_player()
    draw_map()


def generate_projectile():
    projectile_x = random.randint(battle_zone.left + 10, battle_zone.right - 10)
    return pygame.Rect(projectile_x, battle_zone.top, 10, 10)

# game timers
clock = pygame.time.Clock()

# game stats
player_health = 10
enemy_health = 20
menu_active = False
selected_option = 0
in_battle = False
in_dialog = False
current_dialog_index = 0

dialog_text = [
    "Hello, traveler!",
    "Welcome to this strange place.",
    "Beware of the dangers ahead.",
    "Good luck on your journey!"
]

# action menu
menu_options = ["Attack", "Defend", "Heal", "Spare"]


def draw_map():
    screen.fill(WHITE)

    # drawing game zone draw
    pygame.draw.rect(screen, CYAN, game_zone)

    # drawing battle activation zone
    pygame.draw.rect(screen, GREEN, battle_activation_zone)

    # drawing dialogue zone
    pygame.draw.rect(screen, YELLOW, dialog_zone)

    # drawing player
    pygame.draw.rect(screen, player_color, player)

    pygame.display.flip()


def draw_battle():
    screen.fill(BLACK)

    # hp bar
    health_text = pygame.font.Font(None, 36).render(f"Health: {player_health}", True, WHITE)
    enemy_health_text = pygame.font.Font(None, 36).render(f"Enemy Health: {enemy_health}", True, WHITE)

    screen.blit(health_text, (10, 10))
    screen.blit(enemy_health_text, (WIDTH - 200, 10))

    # fight zone
    pygame.draw.rect(screen, WHITE, battle_zone, 2)

    # player(in battle)
    pygame.draw.rect(screen, RED, player)

    # enemy(circle)
    pygame.draw.circle(screen, enemy["color"], (enemy["x"], enemy["y"]), enemy["radius"])

    # drawing projectiles
    for projectile in projectiles:
        pygame.draw.rect(screen, WHITE, projectile)

    # showing the menu if it active
    if menu_active:
        draw_menu()

    if enemy_health <= 10:
        last_breth()

        print("second phase")

        if cool_phase == True:
            global zn
            global lastb_timer
            if pygame.time.get_ticks()- lastb_timer > zone_attack_interval:
                zn = zone_attack()
                print("eto zona bratan")
                screen.blit(zn[0],(zn[1],zn[2]))


                lastb_timer = pygame.time.get_ticks()
            else:
                screen.blit(zn[0], (zn[1], zn[2]))

    pygame.display.flip()


def draw_menu():
    font = pygame.font.Font(None, 36)
    menu_x, menu_y = 50, 450
    for i, option in enumerate(menu_options):
        color = RED if i == selected_option else WHITE
        option_text = font.render(option, True, color)
        screen.blit(option_text, (menu_x, menu_y + i * 40))


def draw_dialog():
    font = pygame.font.Font(None, 36)
    dialog_box = pygame.Rect(50, 500, 700, 80)
    pygame.draw.rect(screen, BLACK, dialog_box)
    pygame.draw.rect(screen, WHITE, dialog_box, 3)

    # dialogue text showing
    dialog_text_surface = font.render(dialog_text[current_dialog_index], True, WHITE)
    screen.blit(dialog_text_surface, (dialog_box.x + 10, dialog_box.y + 20))
    pygame.display.flip()


def last_breth():
    pygame.draw.line(screen,color=RED,start_pos=(380,90),end_pos=(420,110),width=(5))

    global cool_phase
    cool_phase = True

def handle_projectiles():
    global player_health

    for projectile in projectiles[:]:  #checking list copy
        projectile.y += projectile_speed

        # cheking collision with player
        if projectile.colliderect(player):
            projectiles.remove(projectile)
            player_health -= 1

        # removing projectiles if it out of screen
        elif projectile.top > HEIGHT:
            projectiles.remove(projectile)




def handle_menu_action():
    global player_health, enemy_health, player_attack_timer

    if menu_options[selected_option] == "Attack":
        if player_attack_timer == 0:  # cheking cooldown for attack
            print("Player attacks!")
            enemy_health -= 5
            player_attack_timer = PLAYER_ATTACK_DELAY  # set delay



            if enemy_health <= 0:
                print("Enemy defeated!")
                exit_battle()
                global secondlvl
                secondlvl = True

        else:
            print("Attack is on cooldown!")

    elif menu_options[selected_option] == "Defend":
        print("Player defends!")
        # the defense ogic is not ready
    elif menu_options[selected_option] == "Heal":
        print("Player heals!")
        player_health = min(player_health + 3, 10)  # healing player
    elif menu_options[selected_option] == "Spare":
        print("Player spares the enemy!")
        exit_battle()


def enemy_attack():
    global player_health
    attack_x = random.randint(battle_zone.left + 10, battle_zone.right - 10)
    attack_y = random.randint(battle_zone.top + 10, battle_zone.bottom - 10)

    if player.colliderect(pygame.Rect(attack_x - 10, attack_y - 10, 20, 20)):
        player_health -= 2

    if player_health <= 0:
        print("Player died!")
        exit_battle()
        draw_map()
        player_health = 10

        # respawn_player()


def exit_battle():
    global in_battle, projectiles, enemy_health, player_attack_timer
    in_battle = False
    projectiles.clear()
    enemy_health = 20  # reset the enemy hp before the next fight
    player_attack_timer = 0  # restart player cooldown for attack
    print("Returning to map...")



def respawn_player():
    global in_battle, projectiles, player_health
    in_battle = False
    projectiles.clear()
    player_health = 10  # make player hp full
    player.x, player.y = spawn_point  # moving player to spawn point
    print("Player respawned at spawn point.")

def zone_attack():
    sizex = randint(50,100)
    sizey = randint(50,100)
    posx = randint(250,600)
    posy = randint(150,300)
    zone = pygame.Surface((sizex,sizey),pygame.SRCALPHA)
    zone.fill((255,0,0,100))
    zonerect = pygame.Rect(posx ,posy, sizex, sizey)
    return[zone, posx, posy,zonerect]



# main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if in_dialog:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                current_dialog_index += 1
                if current_dialog_index >= len(dialog_text):
                    in_dialog = False
                    current_dialog_index = 0
        elif event.type == pygame.KEYDOWN:
            if menu_active:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    handle_menu_action()
                    menu_active = False
            else:
                if event.key == pygame.K_SPACE:
                    menu_active = True

    keys = pygame.key.get_pressed()

    if not in_battle and not in_dialog:
        # player controls
        if keys[pygame.K_UP]:
            if player.top > 0:
                player.y -= player_speed
        if keys[pygame.K_DOWN]:
            if player.bottom < HEIGHT:
                player.y += player_speed
        if keys[pygame.K_LEFT]:
            if player.left > 0:
                player.x -= player_speed
        if keys[pygame.K_RIGHT]:
            if player.right < WIDTH:
                player.x += player_speed

        # cheking enter to the fight zone
        if player.colliderect(battle_activation_zone):
            in_battle = True
            print("Battle started!")

        # cheking enter to the dialogue zone
        if player.colliderect(dialog_zone):
            in_dialog = True
            print("Dialog started!")

        draw_map()

    elif in_battle:

        # fight logic

        spawn_timer += 1
        if spawn_timer >= SPAWN_INTERVAL:
            spawn_timer = 0
            projectiles.append(generate_projectile())



        enemy_attack_timer += 1
        if enemy_attack_timer >= ENEMY_ATTACK_INTERVAL:
            enemy_attack_timer = 0
            enemy_attack()



        if player_attack_timer > 0:
            player_attack_timer -= 1  # Уменьшаем таймер атаки игрока

        handle_projectiles()

        if cool_phase ==  True:
            if zn[3].colliderect(player):
                zn[1] = 900
                zn[2] = 900
                zn[3].x = 900
                zn[3].y = 900
                player_health -= 3

        # player controling in fight
        if keys[pygame.K_UP] and player.top > battle_zone.top:
            player.y -= player_speed
        if keys[pygame.K_DOWN] and player.bottom < battle_zone.bottom:
            player.y += player_speed
        if keys[pygame.K_LEFT] and player.left > battle_zone.left:
            player.x -= player_speed
        if keys[pygame.K_RIGHT] and player.right < battle_zone.right:
            player.x += player_speed

        draw_battle()



    elif in_dialog:
        draw_dialog()
    elif secondlvl == True:
        second_lavel()
        print("ll")

    clock.tick(60)

pygame.quit()
sys.exit()
