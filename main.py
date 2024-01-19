import os
import sqlite3
import sys
from random import randint, choice

import easygui
import pygame
from pygame import QUIT, KEYDOWN, KEYUP, K_LEFT, K_RIGHT, K_RETURN
from pygame.transform import scale
pygame.init()

sound1 = pygame.mixer.Sound('start_end.mp3')
sound2 = pygame.mixer.Sound('middle.mp3')
sound3 = pygame.mixer.Sound('lose (1).mp3')
sound4 = pygame.mixer.Sound('win.mp3')

pygame.display.init()
pygame.display.set_caption('Космолет')
screen = pygame.display.set_mode((800, 600))
rocket = "spr_2.png"
FPS = 20
levels = [(5, 2, 10), (10, 3, 15), (15, 4, 20)]  # (velocity, num, rocket speed)
coins_for_levels = [10, 20, 35]
enemy_types = ['pl2.png', 'pl3.png', 'pl4.png', 'pl5.png']
all_sprites = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
clock = pygame.time.Clock()

curr_level = 0
coins = 0
user_name = 'Noname'


def start_screen():
    fon = pygame.transform.scale(load_image('zast.png'), (600, 800))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    sound1.play(-1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.img_mask = pygame.mask.from_surface(self.frames[0])
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frame = sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size))
                self.frames.append(frame)

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % (3 * len(self.frames))
        self.image = self.frames[self.cur_frame // 3]

    def mask(self):
        return self.img_mask


class SpaceShip(AnimatedSprite):
    def __init__(self, sheet, columns, rows):
        super().__init__(sheet, columns, rows, 230, 590)
        self.step = 0

    def moveleft(self):
        self.step = -levels[curr_level][2]

    def moveright(self):
        self.step = levels[curr_level][2]

    def stopmove(self):
        self.step = 0

    def update(self):
        super().update()
        new_x = self.rect.x + self.step
        if new_x >= -20 and (new_x <= 620 - self.rect.width):
            self.rect.x = new_x


class Enemy(AnimatedSprite):
    global coins

    def __init__(self, sheet, columns, rows):
        super().__init__(sheet, columns, rows, randint(0, 400), 0)
        enemy_sprites.add(self)

    def update(self):
        global coins
        super().update()
        if self.rect.y < 800:
            self.rect.y += levels[curr_level][0]
        else:
            enemies.remove(self)
            self.remove(all_sprites)
            self.remove(enemy_sprites)
            coins += 1


def test_crush():
    mask1 = space_ship.mask()
    r1 = space_ship.rect
    for i in enemy_sprites:
        mask2 = i.mask()
        r2 = i.rect
        offset = (r2.x - r1.x, r2.y - r1.y)
        res = mask1.overlap_area(mask2, offset)
        if res > 0:
            return True
        else:
            return False


def terminate():
    pygame.quit()
    sys.exit()


def updateDB():
    con = sqlite3.connect("statistics.sqlite")
    cur = con.cursor()
    cur.execute("""INSERT INTO games(name, result) VALUES(?, ?)""", (user_name, coins))
    res = cur.execute("""SELECT name, result FROM games ORDER BY result DESC LIMIT 5""").fetchall()
    winners = [str(i[0]) + ' - ' + str(i[1]) for i in res]
    con.commit()
    con.close()
    return winners


def end_screen(win):
    f2 = pygame.font.Font(None, 50)
    winners = updateDB()
    if win:
        fon = pygame.transform.scale(load_image('end.jpg'), (600, 800))
        sound4.play(-1)
    else:
        fon = pygame.transform.scale(load_image('end_n.jpg'), (600, 800))
        sound3.play(-1)
    screen.blit(fon, (0, 0))
    text = f1.render(str(coins), 1, (191, 8, 68))
    screen.blit(text, (280, 225))
    h = 300
    for w in winners:
        text = f2.render(w, 1, (pygame.Color('black')))
        screen.blit(text, (65, h))
        h += 36
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == K_RETURN:
                    terminate()
                else:
                    terminate()
        pygame.display.flip()
        clock.tick(FPS)


big_sky = pygame.image.load("background.jpg")
sky = scale(big_sky, (600, 800))
space_ship = SpaceShip(load_image(rocket), 5, 1)
enemies = []


if __name__ == '__main__':
    pygame.init()
    size = width, height = 600, 800
    screen = pygame.display.set_mode(size)
    start_screen()
    user_name = easygui.enterbox("Имя игрока", "Введите свое имя")
    if user_name is None:
        user_name = 'Sky Walker'
    pygame.mixer.pause()
    running = True
    sound2.play(-1)
    while running:
        screen.blit(sky, (0, 0))
        all_sprites.draw(screen)
        f1 = pygame.font.Font(None, 35)
        text1 = f1.render('Очки:', 1, (pygame.Color('pink')))
        text2 = f1.render(str(coins), 1, (pygame.Color('pink')))
        screen.blit(text1, (420, 50))
        screen.blit(text2, (550, 50))
        text3 = f1.render('Уровень:', 1, (pygame.Color('pink')))
        text4 = f1.render(str(curr_level + 1), 1, (pygame.Color('pink')))
        screen.blit(text3, (420, 80))
        screen.blit(text4, (550, 80))
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_LEFT:
                    space_ship.moveleft()
                elif event.key == K_RIGHT:
                    space_ship.moveright()
            elif event.type == KEYUP:
                space_ship.stopmove()

        if test_crush():
            pygame.mixer.pause()
            end_screen(False)
        if coins == coins_for_levels[curr_level] and curr_level < 2:
            curr_level += 1
        if coins == 35:
            pygame.mixer.pause()
            end_screen(True)

        all_sprites.update()
        i = len(enemies)
        n = levels[curr_level][1]
        if i == 0 or i < n and enemies[-1].rect.y > (800 / n):
            enemies.append(Enemy(load_image(choice(enemy_types)), 1, 1))
        pygame.display.flip()
        clock.tick(FPS)

    terminate()
