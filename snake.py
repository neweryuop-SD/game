"""
贪吃蛇·终极版 - 修复作弊模式食物跟随问题
- 鼠标左键：重置游戏
- 鼠标右键：切换作弊模式（无敌 + 食物仅在吃掉后重生在蛇头前方2格）
- 回车键：暂停/继续
- ESC键：退出
- 方向键：移动
"""

import pygame
import random
import sys
from pygame.locals import *

# ========== 窗口设置 ==========
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE   # 40
GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE # 30

# ========== 配色方案 ==========
COLOR_BG_DARK = (6, 87, 88)       # #065758
COLOR_BG_LIGHT = (0, 153, 159)    # #00999F
COLOR_SNAKE_BODY = (129, 210, 227) # #81D2E3
COLOR_SNAKE_HEAD = (188, 237, 216) # #BCEDD8
COLOR_FOOD = (254, 238, 48)       # #FEEE30
COLOR_FOOD_GLOW = (255, 245, 150)
COLOR_OBSTACLE = (0, 153, 159)    # #00999F
COLOR_UI_TEXT = (188, 237, 216)   # #BCEDD8
COLOR_CHEAT = (254, 238, 48)      # #FEEE30
COLOR_GRID = (6, 87, 88, 80)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("贪吃蛇·终极版")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.SysFont('arial', 36, bold=True)
        self.font_small = pygame.font.SysFont('arial', 24)
        self.font_tiny = pygame.font.SysFont('arial', 18)

        self.highscore = self.load_highscore()
        self.cheat_mode = False

        # 游戏状态变量
        self.snake = []
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.score = 0
        self.game_over = False
        self.base_speed = 10
        self.current_speed = 10
        self.double_score = False
        self.double_score_timer = 0
        self.speed_boost = False
        self.speed_boost_timer = 0
        self.obstacles = []
        self.food = None
        self.special_food = None
        self.special_food_timer = 0
        self.next_obstacle_score = 5
        self.paused = False

        self.reset_game()

    def load_highscore(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0

    def save_highscore(self):
        with open("highscore.txt", "w") as f:
            f.write(str(self.highscore))

    def reset_game(self):
        mid_x = GRID_WIDTH // 2
        mid_y = GRID_HEIGHT // 2
        self.snake = [(mid_x - 2, mid_y), (mid_x - 1, mid_y), (mid_x, mid_y)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.score = 0
        self.game_over = False
        self.paused = False
        self.double_score = False
        self.double_score_timer = 0
        self.speed_boost = False
        self.speed_boost_timer = 0
        self.obstacles = []
        self.special_food = None
        self.special_food_timer = 0
        self.next_obstacle_score = 5
        self.base_speed = 10
        self.update_speed()

        if self.cheat_mode:
            # 作弊模式：食物放在蛇头前方2格
            self.food = self.get_forward_food_position()
        else:
            self.food = self.random_food()

    def get_forward_food_position(self):
        """返回蛇头前方2格的位置（作弊模式专用）"""
        if not self.snake:
            return (GRID_WIDTH//2, GRID_HEIGHT//2)
        head = self.snake[-1]
        dir_x, dir_y = self.direction
        fx = head[0] + dir_x * 2
        fy = head[1] + dir_y * 2
        fx = max(0, min(fx, GRID_WIDTH - 1))
        fy = max(0, min(fy, GRID_HEIGHT - 1))
        return (fx, fy)

    def random_food(self, avoid_positions=None):
        if avoid_positions is None:
            avoid_positions = []
        avoid_set = set(self.snake) | set(self.obstacles) | set(avoid_positions)
        if self.special_food:
            avoid_set.add(self.special_food)
        if len(avoid_set) >= GRID_WIDTH * GRID_HEIGHT:
            return None
        while True:
            pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
            if pos not in avoid_set:
                return pos

    def generate_obstacle(self):
        if self.cheat_mode:
            return
        pos = self.random_food()
        if pos:
            self.obstacles.append(pos)

    def generate_special_food(self):
        if self.cheat_mode:
            self.special_food = None
            return
        if self.special_food is None and random.random() < 0.1:
            pos = self.random_food()
            if pos:
                self.special_food = pos
                self.special_food_timer = 150

    def update_speed(self):
        base = self.base_speed + len(self.snake) // 5
        if base > 25:
            base = 25
        if self.speed_boost:
            base = min(35, base + 5)
        self.current_speed = base

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.save_highscore()
                pygame.quit()
                sys.exit()

            # 鼠标左键 -> 重置
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.reset_game()
                continue

            # 鼠标右键 -> 切换作弊模式
            if event.type == MOUSEBUTTONDOWN and event.button == 3:
                self.cheat_mode = not self.cheat_mode
                if self.cheat_mode:
                    # 进入作弊模式：清空障碍物和特殊食物，食物重新定位到蛇头前方
                    self.obstacles = []
                    self.special_food = None
                    self.food = self.get_forward_food_position()
                else:
                    # 退出作弊模式：重新生成普通随机食物
                    self.food = self.random_food()
                self.double_score = False
                self.speed_boost = False
                print(f"Cheat mode: {self.cheat_mode}")
                continue

            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if not self.game_over:
                        self.paused = not self.paused
                    continue
                if event.key == K_ESCAPE:
                    self.save_highscore()
                    pygame.quit()
                    sys.exit()

                if not self.game_over and not self.paused:
                    if event.key == K_UP and self.direction != DOWN:
                        self.next_direction = UP
                    elif event.key == K_DOWN and self.direction != UP:
                        self.next_direction = DOWN
                    elif event.key == K_LEFT and self.direction != RIGHT:
                        self.next_direction = LEFT
                    elif event.key == K_RIGHT and self.direction != LEFT:
                        self.next_direction = RIGHT

    def update_game(self):
        if self.game_over or self.paused:
            return

        self.direction = self.next_direction
        head = self.snake[-1]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        if self.cheat_mode:
            # 穿墙
            new_head = (new_head[0] % GRID_WIDTH, new_head[1] % GRID_HEIGHT)
            # 自身碰撞和障碍物碰撞在作弊模式下忽略（不死亡）
            # 注意：自身碰撞仍然会导致游戏逻辑错乱，但为了“不会死亡”，我们可以让蛇继续移动。
            # 不过自身重叠会奇怪，但为了作弊，可以允许。
        else:
            # 正常碰撞检测
            if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
                new_head in self.snake or
                new_head in self.obstacles):
                self.game_over = True
                if self.score > self.highscore:
                    self.highscore = self.score
                    self.save_highscore()
                return

        # 移动蛇
        self.snake.append(new_head)

        # 判断是否吃到食物
        ate_normal = (new_head == self.food)
        ate_special = (self.special_food and new_head == self.special_food)
        if self.cheat_mode:
            ate_special = False

        if ate_normal:
            self.score += 1
            if self.double_score:
                self.score += 1

            if self.cheat_mode:
                # 作弊模式：食物重新生成到新蛇头前方2格
                self.food = self.get_forward_food_position()
            else:
                # 普通模式：随机生成新食物
                self.food = self.random_food()
                if self.score >= self.next_obstacle_score:
                    self.generate_obstacle()
                    self.next_obstacle_score += 5
            self.update_speed()
        elif ate_special:
            self.score += 2
            self.double_score = True
            self.speed_boost = True
            self.double_score_timer = 150
            self.speed_boost_timer = 150
            self.special_food = None
            self.update_speed()
            if not self.cheat_mode:
                self.food = self.random_food()
        else:
            # 没吃到东西，移除尾部
            self.snake.pop(0)
            # 注意：作弊模式下，食物位置**不变**，等待被吃掉，绝不每帧刷新！

        # 特殊食物生成（仅非作弊模式）
        if not self.cheat_mode:
            if self.special_food is not None:
                self.special_food_timer -= 1
                if self.special_food_timer <= 0:
                    self.special_food = None
            self.generate_special_food()
        else:
            self.special_food = None

        # 双倍分/加速计时
        if self.double_score:
            self.double_score_timer -= 1
            if self.double_score_timer <= 0:
                self.double_score = False
        if self.speed_boost:
            self.speed_boost_timer -= 1
            if self.speed_boost_timer <= 0:
                self.speed_boost = False
                self.update_speed()

    # ========== 绘制函数（配色美化，与前相同） ==========
    def draw_background(self):
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            r = int(COLOR_BG_DARK[0] * (1 - ratio) + COLOR_BG_LIGHT[0] * ratio)
            g = int(COLOR_BG_DARK[1] * (1 - ratio) + COLOR_BG_LIGHT[1] * ratio)
            b = int(COLOR_BG_DARK[2] * (1 - ratio) + COLOR_BG_LIGHT[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))

    def draw_grid(self):
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, (*COLOR_GRID[:3], 60), (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, (*COLOR_GRID[:3], 60), (0, y), (WINDOW_WIDTH, y))

    def draw_rounded_rect(self, surface, color, rect, radius=5):
        pygame.draw.rect(surface, color, rect, border_radius=radius)

    def draw_snake(self):
        for i, seg in enumerate(self.snake):
            rect = pygame.Rect(seg[0]*CELL_SIZE, seg[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = COLOR_SNAKE_BODY if i < len(self.snake)-1 else COLOR_SNAKE_HEAD
            shadow_rect = rect.move(2, 2)
            self.draw_rounded_rect(self.screen, BLACK, shadow_rect, radius=6)
            self.draw_rounded_rect(self.screen, color, rect, radius=6)
            if i == len(self.snake)-1:
                eye_size = 3
                eye_offset = 5
                if self.direction == RIGHT:
                    pos1 = (rect.right - eye_offset, rect.top + eye_offset)
                    pos2 = (rect.right - eye_offset, rect.bottom - eye_offset)
                elif self.direction == LEFT:
                    pos1 = (rect.left + eye_offset - eye_size, rect.top + eye_offset)
                    pos2 = (rect.left + eye_offset - eye_size, rect.bottom - eye_offset)
                elif self.direction == UP:
                    pos1 = (rect.left + eye_offset, rect.top + eye_offset)
                    pos2 = (rect.right - eye_offset - eye_size, rect.top + eye_offset)
                else:
                    pos1 = (rect.left + eye_offset, rect.bottom - eye_offset - eye_size)
                    pos2 = (rect.right - eye_offset - eye_size, rect.bottom - eye_offset - eye_size)
                pygame.draw.circle(self.screen, WHITE, pos1, eye_size)
                pygame.draw.circle(self.screen, WHITE, pos2, eye_size)

    def draw_food(self):
        if self.food is None:
            return
        center = (self.food[0]*CELL_SIZE + CELL_SIZE//2, self.food[1]*CELL_SIZE + CELL_SIZE//2)
        pygame.draw.circle(self.screen, COLOR_FOOD, center, CELL_SIZE//2 - 2)
        pygame.draw.circle(self.screen, COLOR_FOOD_GLOW, center, CELL_SIZE//3)
        glow = pygame.Surface((CELL_SIZE+10, CELL_SIZE+10), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*COLOR_FOOD, 80), (CELL_SIZE//2+5, CELL_SIZE//2+5), CELL_SIZE//2+3)
        self.screen.blit(glow, (self.food[0]*CELL_SIZE-5, self.food[1]*CELL_SIZE-5))

    def draw_special_food(self):
        if self.special_food and not self.cheat_mode:
            rect = pygame.Rect(self.special_food[0]*CELL_SIZE, self.special_food[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            self.draw_rounded_rect(self.screen, (254, 238, 48), rect, radius=8)
            flash = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            flash.fill((255, 255, 150, 100))
            self.screen.blit(flash, rect)

    def draw_obstacles(self):
        if self.cheat_mode:
            return
        for obs in self.obstacles:
            rect = pygame.Rect(obs[0]*CELL_SIZE, obs[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            self.draw_rounded_rect(self.screen, COLOR_OBSTACLE, rect, radius=4)
            pygame.draw.line(self.screen, BLACK, rect.topleft, rect.bottomright, 2)
            pygame.draw.line(self.screen, BLACK, rect.topright, rect.bottomleft, 2)

    def draw_ui(self):
        score_text = self.font_large.render(f"Score: {self.score}", True, COLOR_UI_TEXT)
        score_shadow = self.font_large.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_shadow, (12, 12))
        self.screen.blit(score_text, (10, 10))

        high_text = self.font_small.render(f"Best: {self.highscore}", True, COLOR_FOOD)
        self.screen.blit(high_text, (10, 55))

        if self.cheat_mode:
            cheat_surf = self.font_small.render("CHEAT MODE ON", True, COLOR_CHEAT)
            self.screen.blit(cheat_surf, (WINDOW_WIDTH - 180, 10))

        y_off = 90
        if self.double_score:
            db_text = self.font_tiny.render("DOUBLE SCORE!", True, COLOR_FOOD)
            self.screen.blit(db_text, (10, y_off))
            y_off += 25
        if self.speed_boost:
            sp_text = self.font_tiny.render("SPEED UP!", True, (0, 255, 200))
            self.screen.blit(sp_text, (10, y_off))

        tip1 = self.font_tiny.render("L-click: Reset   R-click: Cheat   Enter: Pause   Esc: Quit", True, COLOR_UI_TEXT)
        self.screen.blit(tip1, (WINDOW_WIDTH - 460, 10))
        tip2 = self.font_tiny.render("Arrow keys: Move", True, COLOR_UI_TEXT)
        self.screen.blit(tip2, (WINDOW_WIDTH - 220, 35))

        if self.paused and not self.game_over:
            pause_surf = self.font_large.render("PAUSED", True, COLOR_FOOD)
            rect = pause_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(pause_surf, rect)

        if self.game_over:
            go_surf = self.font_large.render("GAME OVER", True, COLOR_FOOD)
            go_rect = go_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 40))
            self.screen.blit(go_surf, go_rect)
            restart_surf = self.font_small.render("Left click to restart", True, COLOR_UI_TEXT)
            restart_rect = restart_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
            self.screen.blit(restart_surf, restart_rect)

    def run(self):
        while True:
            self.handle_events()
            self.update_game()
            self.draw_background()
            self.draw_grid()
            self.draw_obstacles()
            self.draw_food()
            self.draw_special_food()
            self.draw_snake()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(self.current_speed)

if __name__ == "__main__":
    game = SnakeGame()
    game.run()