"""
星际防卫 - 太空射击游戏
控制飞船左右移动，射击外星敌人，避免被击中或与敌人相撞。
"""
import pygame
import random
import sys
from typing import List, Optional

# 初始化 Pygame
pygame.init()
pygame.mixer.init()

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# 游戏对象速度
PLAYER_SPEED = 6
BULLET_SPEED = 8
ENEMY_BASE_SPEED = 2
ENEMY_SHOOT_COOLDOWN = 60  # 帧数间隔

# 初始设定
PLAYER_LIVES = 3
INVINCIBLE_FRAMES = 60  # 无敌帧数


class Player(pygame.sprite.Sprite):
    """玩家飞船类"""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill(GREEN)
        pygame.draw.polygon(self.image, WHITE, [(20, 0), (0, 30), (40, 30)])
        self.rect = self.image.get_rect()
        self.rect.midbottom = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
        self.speed_x = 0
        self.lives = PLAYER_LIVES
        self.invincible_timer = 0
        self.last_shot = 0
        self.shoot_delay = 15  # 射击冷却帧数

    def update(self):
        # 移动
        self.rect.x += self.speed_x
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # 无敌帧倒计时
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            # 闪烁效果
            if self.invincible_timer // 5 % 2:
                self.image.set_alpha(128)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)

    def shoot(self):
        """产生子弹"""
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top, direction=-1)
            return bullet
        return None

    def hit(self):
        """被击中处理"""
        if self.invincible_timer <= 0 and self.lives > 0:
            self.lives -= 1
            self.invincible_timer = INVINCIBLE_FRAMES
            return True
        return False


class Bullet(pygame.sprite.Sprite):
    """子弹类（玩家和敌人通用）"""
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = BULLET_SPEED * direction  # direction: -1向上, 1向下

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    """敌人类"""
    def __init__(self, x, y, speed_x=1):
        super().__init__()
        self.image = pygame.Surface((35, 30))
        self.image.fill(RED)
        pygame.draw.polygon(self.image, BLACK, [(17, 5), (5, 25), (29, 25)])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = speed_x
        self.speed_y = ENEMY_BASE_SPEED
        self.shoot_timer = random.randint(0, ENEMY_SHOOT_COOLDOWN * 2)

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        # 边界反弹并下沉（经典入侵模式）
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.speed_x = -self.speed_x
            self.rect.y += 15  # 下沉
            # 防止无限下沉超出边界
            if self.rect.bottom > SCREEN_HEIGHT:
                self.kill()

    def try_shoot(self):
        """按概率射击"""
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot_timer = random.randint(ENEMY_SHOOT_COOLDOWN, ENEMY_SHOOT_COOLDOWN * 2)
            bullet = Bullet(self.rect.centerx, self.rect.bottom, direction=1)
            return bullet
        return None


class Star(pygame.sprite.Sprite):
    """背景星星，动态闪烁"""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((2, 2))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH)
        self.rect.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.5, 2)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.bottom = 0
            self.rect.x = random.randint(0, SCREEN_WIDTH)


def show_text(screen, text, size, x, y, color=WHITE):
    """辅助函数：显示文字"""
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)


def show_game_over(screen, score, final=False):
    """显示游戏结束画面"""
    screen.fill(BLACK)
    show_text(screen, "GAME OVER", 72, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50, RED)
    show_text(screen, f"Final Score: {score}", 48, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20, WHITE)
    show_text(screen, "Press R to Restart or Q to Quit", 32, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100, YELLOW)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                    return True   # 重新开始
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
    return False


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("星际防卫 - 太空射击")
    clock = pygame.time.Clock()

    # 游戏变量
    running = True
    score = 0
    level = 1
    enemies_killed = 0

    # 精灵组
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    stars = pygame.sprite.Group()

    # 创建背景星星
    for _ in range(100):
        star = Star()
        stars.add(star)
        all_sprites.add(star)

    player = Player()
    all_sprites.add(player)

    # 创建敌人波次
    def create_enemy_wave():
        nonlocal level
        rows = 3 + level // 3
        cols = 8
        enemy_spacing_x = 50
        enemy_spacing_y = 50
        start_x = (SCREEN_WIDTH - (cols - 1) * enemy_spacing_x) // 2
        start_y = 60
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * enemy_spacing_x
                y = start_y + row * enemy_spacing_y
                speed_x = 1 * (1 + level * 0.1)
                enemy = Enemy(x, y, speed_x)
                all_sprites.add(enemy)
                enemies.add(enemy)

    create_enemy_wave()

    # 音效（简单beep模拟，无音频文件）
    def play_beep(frequency=1000, duration=100):
        """简易蜂鸣音效（可选）"""
        # pygame.mixer不依赖外部文件时可用此方法，但需初始化mixer
        # 实际使用中若无声音没关系，跳过亦可
        pass

    # 主循环
    while running:
        clock.tick(FPS)

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.speed_x = -PLAYER_SPEED
                if event.key == pygame.K_RIGHT:
                    player.speed_x = PLAYER_SPEED
                if event.key == pygame.K_SPACE:
                    bullet = player.shoot()
                    if bullet:
                        bullets.add(bullet)
                        all_sprites.add(bullet)
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    player.speed_x = 0

        # 更新所有精灵
        all_sprites.update()
        bullets.update()
        enemy_bullets.update()

        # 玩家射击冷却自动管理（已在player.shoot内使用时间）
        # 敌人射击
        for enemy in enemies:
            bullet = enemy.try_shoot()
            if bullet:
                enemy_bullets.add(bullet)
                all_sprites.add(bullet)

        # 碰撞检测：玩家子弹 vs 敌人
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            score += 10
            enemies_killed += 1
            # 每击败5个敌人升一级，增加速度
            if enemies_killed % 5 == 0:
                level += 1
                # 提高敌人整体速度
                for e in enemies:
                    e.speed_y = ENEMY_BASE_SPEED * (1 + level * 0.05)
                    e.speed_x = 1 * (1 + level * 0.1)
                    if e.speed_x > 0:
                        e.speed_x = abs(e.speed_x)
                    else:
                        e.speed_x = -abs(e.speed_x)

        # 玩家与敌人的碰撞
        player_collisions = pygame.sprite.spritecollide(player, enemies, True)
        for _ in player_collisions:
            if player.hit():
                # 同时移除敌人（碰撞敌人直接消灭）
                if player.lives <= 0:
                    if show_game_over(screen, score):
                        # 重置游戏
                        return main()
                    else:
                        running = False
                # 闪烁无敌期间不再受伤害
            else:
                # 无敌时也移除碰撞的敌人防止无限擦伤？
                # 此处为了公平，无敌期间碰撞到敌人，敌人也会消失但玩家不扣血
                pass

        # 玩家与敌方子弹碰撞
        bullet_hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        for _ in bullet_hits:
            if player.hit():
                if player.lives <= 0:
                    if show_game_over(screen, score):
                        return main()
                    else:
                        running = False

        # 检查是否有敌人超出底部边界（游戏结束）
        for enemy in enemies:
            if enemy.rect.bottom >= SCREEN_HEIGHT - 30:
                # 敌人到达底部，游戏失败
                if show_game_over(screen, score):
                    return main()
                else:
                    running = False

        # 若所有敌人被消灭，生成新一波
        if len(enemies) == 0:
            level += 1
            create_enemy_wave()
            # 提高敌人基础速度
            for e in enemies:
                e.speed_y = ENEMY_BASE_SPEED * (1 + level * 0.05)

        # 绘制
        screen.fill(BLACK)
        all_sprites.draw(screen)
        # 显示UI
        show_text(screen, f"Score: {score}", 32, 70, 20, WHITE)
        show_text(screen, f"Lives: {player.lives}", 32, 120, 55, GREEN)
        show_text(screen, f"Level: {level}", 32, SCREEN_WIDTH - 80, 20, YELLOW)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()