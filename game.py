#!/usr/bin/env python3
"""
Mikan Snake - a pygame snake game for Hack Club Snek
全てのグラフィックはコードで描画 (AI画像アセット不使用)

Features:
  1. Classic snake gameplay (grow, score, speed-up)
  2. Pause (P key)
  3. Particle effects on eating
  4. High score persistence (JSON)
  5. Sound effects (generated with numpy, no audio files)
"""

import json
import math
import os
import random
import sys

import pygame

# ---- 初期化 ----
pygame.init()
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1)
    HAS_AUDIO = True
except Exception:
    HAS_AUDIO = False

CELL = 24
COLS, ROWS = 30, 22
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL + 60
FPS = 60
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'highscore.json')

BG = (13, 17, 23)
GRID = (22, 27, 34)
FG = (230, 237, 243)
ORANGE = (240, 136, 62)
ORANGE_DARK = (200, 100, 40)
GREEN = (63, 185, 80)
RED = (248, 81, 73)
MUTED = (139, 148, 158)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Mikan Snake')
clock = pygame.time.Clock()
font = pygame.font.SysFont('dejavusans', 22, bold=True)
small = pygame.font.SysFont('dejavusans', 16)


def make_beep(freq, dur, vol=0.3):
    """numpyでビープ音を生成 (音声ファイル不使用)"""
    if not HAS_AUDIO:
        return None
    try:
        import numpy as np
        sr = 22050
        t = np.linspace(0, dur, int(sr * dur), False)
        wave = np.sin(freq * t * 2 * math.pi) * np.exp(-t * 8) * vol
        snd = np.asarray(wave * 32767, dtype=np.int16)
        return pygame.sndarray.make_sound(snd)
    except Exception:
        return None


SND_EAT = make_beep(880, 0.12)
SND_DIE = make_beep(220, 0.4)


def load_highscore():
    try:
        with open(SAVE_FILE) as f:
            return json.load(f).get('highscore', 0)
    except Exception:
        return 0


def save_highscore(v):
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump({'highscore': v}, f)
    except Exception:
        pass


class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        ang = random.uniform(0, math.tau)
        spd = random.uniform(1, 4)
        self.vx, self.vy = math.cos(ang) * spd, math.sin(ang) * spd
        self.life = random.uniform(20, 40)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.94
        self.vy *= 0.94
        self.life -= 1

    def draw(self, surf):
        a = max(0, self.life / self.max_life)
        r = max(1, int(4 * a))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), r)


class Snake:
    def __init__(self):
        cx, cy = COLS // 2, ROWS // 2
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.dir = (1, 0)
        self.grow = 0
        self.score = 0
        self.speed = 8.0
        self.move_timer = 0.0

    def set_dir(self, d):
        if (d[0] * -1, d[1] * -1) != self.dir:
            self.dir = d

    def step(self, food, particles):
        head = (self.body[0][0] + self.dir[0], self.body[0][1] + self.dir[1])
        # 壁 (ラップアラウンド)
        head = (head[0] % COLS, head[1] % ROWS)
        if head in self.body[:-1]:
            return False  # 死亡
        self.body.insert(0, head)
        if head == food.pos:
            self.score += 10
            self.grow += 2
            self.speed = min(20.0, self.speed + 0.4)
            for _ in range(18):
                particles.append(Particle(food.px, food.py, ORANGE))
            if SND_EAT:
                SND_EAT.play()
            food.respawn(self.body)
        else:
            if self.grow > 0:
                self.grow -= 1
            else:
                self.body.pop()
        return True

    def draw(self, surf):
        for i, (x, y) in enumerate(self.body):
            r = pygame.Rect(x * CELL, y * CELL + 60, CELL, CELL)
            if i == 0:
                pygame.draw.rect(surf, ORANGE, r.inflate(-2, -2), border_radius=8)
                # 目
                ex = x * CELL + CELL // 2 + self.dir[0] * 4
                ey = y * CELL + 60 + CELL // 2 + self.dir[1] * 4
                pygame.draw.circle(surf, FG, (ex - 3, ey - 2), 2)
                pygame.draw.circle(surf, FG, (ex + 3, ey - 2), 2)
            else:
                fade = max(0.45, 1.0 - i * 0.02)
                col = tuple(int(c * fade) for c in ORANGE_DARK)
                pygame.draw.rect(surf, col, r.inflate(-4, -4), border_radius=6)


class Food:
    def __init__(self, snake_body):
        self.respawn(snake_body)

    def respawn(self, snake_body):
        while True:
            self.pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
            if self.pos not in snake_body:
                break
        self.px = self.pos[0] * CELL + CELL // 2
        self.py = self.pos[1] * CELL + 60 + CELL // 2
        self.pulse = 0.0

    def draw(self, surf):
        self.pulse += 0.08
        r = CELL // 2 - 3 + math.sin(self.pulse) * 2
        pygame.draw.circle(surf, RED, (self.px, self.py), int(r))
        pygame.draw.circle(surf, (255, 180, 180), (self.px - 3, self.py - 3), 2)


def draw_hud(surf, score, high, paused):
    bar = pygame.Rect(0, 0, WIDTH, 60)
    pygame.draw.rect(surf, GRID, bar)
    s = font.render(f'SCORE {score}', True, FG)
    h = small.render(f'BEST {high}', True, MUTED)
    surf.blit(s, (16, 16))
    surf.blit(h, (16, 40))
    if paused:
        p = font.render('PAUSED (P to resume)', True, ORANGE)
        surf.blit(p, (WIDTH // 2 - p.get_width() // 2, 18))


def main():
    snake = Snake()
    food = Food(snake.body)
    particles = []
    high = load_highscore()
    paused = False
    dead = False
    new_record = False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if dead and e.key in (pygame.K_SPACE, pygame.K_RETURN):
                    snake = Snake()
                    food = Food(snake.body)
                    particles = []
                    dead = False
                    new_record = False
                elif e.key == pygame.K_p and not dead:
                    paused = not paused
                elif e.key in (pygame.K_UP, pygame.K_w):
                    snake.set_dir((0, -1))
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    snake.set_dir((0, 1))
                elif e.key in (pygame.K_LEFT, pygame.K_a):
                    snake.set_dir((-1, 0))
                elif e.key in (pygame.K_RIGHT, pygame.K_d):
                    snake.set_dir((1, 0))

        if not dead and not paused:
            snake.move_timer += dt
            interval = 1.0 / snake.speed
            while snake.move_timer >= interval:
                snake.move_timer -= interval
                alive = snake.step(food, particles)
                if not alive:
                    dead = True
                    if SND_DIE:
                        SND_DIE.play()
                    if snake.score > high:
                        high = snake.score
                        save_highscore(high)
                        new_record = True
                    break

        for pt in particles[:]:
            pt.update()
            if pt.life <= 0:
                particles.remove(pt)

        screen.fill(BG)
        for gx in range(0, WIDTH, CELL):
            pygame.draw.line(screen, GRID, (gx, 60), (gx, HEIGHT))
        for gy in range(60, HEIGHT, CELL):
            pygame.draw.line(screen, GRID, (0, gy), (WIDTH, gy))

        food.draw(screen)
        snake.draw(screen)
        for pt in particles:
            pt.draw(screen)
        draw_hud(screen, snake.score, high, paused)

        if dead:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            screen.blit(overlay, (0, 0))
            t1 = font.render('GAME OVER', True, RED)
            t2 = font.render(f'Score: {snake.score}', True, FG)
            t3 = small.render('Press SPACE to play again', True, MUTED)
            if new_record:
                t4 = font.render('NEW RECORD!', True, ORANGE)
                screen.blit(t4, (WIDTH // 2 - t4.get_width() // 2, HEIGHT // 2 - 70))
            screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 - 30))
            screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2 + 10))
            screen.blit(t3, (WIDTH // 2 - t3.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
