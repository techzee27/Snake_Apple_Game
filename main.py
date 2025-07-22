import pygame
from pygame.locals import *
import time
import random
import os
import json

SIZE = 24

class Apple:
    def __init__(self, parent_screen):
        self.image = pygame.image.load("Snake_Apple_Game/resources/apple.jpg").convert()
        new_size = (25, 25)
        self.scaled_image = pygame.transform.scale(self.image, new_size)
        self.parent_screen = parent_screen
        self.x = SIZE*3
        self.y = SIZE*3

    def draw(self):
        self.parent_screen.blit(self.scaled_image,(self.x,self.y))
    
    def move(self):
        self.x = random.randint(0,25)*SIZE
        self.y = random.randint(0,18)*SIZE

class PowerUp:
    def __init__(self, parent_screen, power_type):
        self.parent_screen = parent_screen
        self.power_type = power_type  # 'double', 'shrink', 'speed'
        self.x = random.randint(0,37)*SIZE
        self.y = random.randint(0,30)*SIZE
        self.spawn_time = time.time()
        self.lifetime = 10  # Power-up disappears after 10 seconds
        
        # Create different colored squares for different power-ups
        self.image = pygame.Surface((25, 25))
        if power_type == 'double':
            self.image.fill((255, 215, 0))  # Gold
        elif power_type == 'shrink':
            self.image.fill((0, 255, 255))  # Cyan
        elif power_type == 'speed':
            self.image.fill((255, 0, 255))  # Magenta
    
    def draw(self):
        self.parent_screen.blit(self.image, (self.x, self.y))
    
    def is_expired(self):
        return time.time() - self.spawn_time > self.lifetime

class Obstacle:
    def __init__(self, parent_screen, x, y):
        self.parent_screen = parent_screen
        self.x = x
        self.y = y
        self.image = pygame.Surface((25, 25))
        self.image.fill((139, 69, 19))  # Brown color
    
    def draw(self):
        self.parent_screen.blit(self.image, (self.x, self.y))

class Snake:
    def __init__(self, parent_screen, length):
        self.length = length
        self.parent_screen = parent_screen
        block = pygame.image.load("Snake_Apple_Game/resources/red-square-png-14.png").convert()
        new_size = (25, 25)  # for example
        self.scaled_image = pygame.transform.scale(block, new_size)
        self.x = [SIZE]*length
        self.y = [SIZE]*length
        self.direction = 'down'

    def increase_length(self):
        self.length+=1
        self.x.append(-1)
        self.y.append(-1)

    def decrease_length(self):
        if self.length > 2:
            self.length -= 1
            self.x.pop()
            self.y.pop()

    def draw(self):
        for i in range(self.length):
            self.parent_screen.blit(self.scaled_image,(self.x[i],self.y[i]))
        pygame.display.flip()


        
    def move_left(self):
        self.direction = 'left'
    
    def move_right(self):
        self.direction = 'right'
    
    def move_up(self):
        self.direction = 'up'

    def move_down(self):
        self.direction = 'down'
    
    def walk(self):

        for i in range(self.length-1,0,-1):
            self.x[i] = self.x[i-1]
            self.y[i] = self.y[i-1]

        if self.direction == 'left':
            self.x[0] -= SIZE
        if self.direction == 'right':
            self.x[0] += SIZE
        if self.direction == 'up':
            self.y[0] -= SIZE
        if self.direction == 'down':
            self.y[0] += SIZE

        self.draw()

class GameState:
    MENU = "menu"
    INSTRUCTIONS = "instructions"
    DIFFICULTY = "difficulty"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake Game")
        
        self.surface = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        
        # Game state management
        self.state = GameState.MENU
        self.menu_selection = 0
        self.difficulty_selection = 1  # Default to Medium
        self.pause_selection = 0
        self.game_over_selection = 0
        
        # Difficulty settings
        self.difficulties = {
            0: {"name": "Easy", "speed": 0.15, "obstacles": False},
            1: {"name": "Medium", "speed": 0.1, "obstacles": False},
            2: {"name": "Hard", "speed": 0.05, "obstacles": True}
        }
        
        # Game objects
        self.snake = None
        self.apple = None
        self.obstacles = []
        self.power_ups = []
        self.power_up_timer = 0
        self.speed_boost = 1.0
        self.speed_boost_timer = 0
        
        # Score and high score
        self.score_multiplier = 1
        self.multiplier_timer = 0
        self.high_score = self.load_high_score()
        
        # Initialize audio
        try:
            pygame.mixer.init()
            self.play_background_music()
        except:
            print("Audio initialization failed - continuing without sound")
    
    def load_high_score(self):
        try:
            if os.path.exists("highscore.txt"):
                with open("highscore.txt", "r") as f:
                    return int(f.read().strip())
        except:
            pass
        return 0
    
    def save_high_score(self, score):
        if score > self.high_score:
            self.high_score = score
    
    def play_background_music(self):
        pygame.mixer.music.load("Snake_Apple_Game/resources/bg.mp3")  # Path to your background music
        pygame.mixer.music.play(-1)  # Play indefinitely

    
    def play_sound(self, sound_file):
        try:
            sound = pygame.mixer.Sound(sound_file)
            pygame.mixer.Sound.play(sound)
        except:
            pass
    
    def render_background(self):
        try:
            bg = pygame.image.load("Snake_Apple_Game/resources/bg_image.jpg").convert()
            new_size = (800, 600)
            self.surface.blit(pygame.transform.scale(bg, new_size), (0, 0))
        except:
            self.surface.fill((36, 138, 43))
    
    def is_collision(self, x1, y1, x2, y2):
        if x1 >= x2 and x1 < x2+SIZE:
            if y1 >= y2 and y1 < y2+SIZE:
                return True
        return False
    
    def init_game(self):
        """Initialize a new game"""
        self.snake = Snake(self.surface, 2)
        self.apple = Apple(self.surface)
        self.obstacles = []
        self.power_ups = []
        self.power_up_timer = time.time()
        self.speed_boost = 1.0
        self.speed_boost_timer = 0
        self.score_multiplier = 1
        self.multiplier_timer = 0
        pygame.display.flip()
        
        # Create obstacles for hard difficulty
        if self.difficulties[self.difficulty_selection]["obstacles"]:
            for _ in range(5):
                x = random.randint(5, 35) * SIZE
                y = random.randint(5, 25) * SIZE
                # Make sure obstacle doesn't spawn on snake or apple
                while (x == self.snake.x[0] and y == self.snake.y[0]) or (x == self.apple.x and y == self.apple.y):
                    x = random.randint(5, 35) * SIZE
                    y = random.randint(5, 25) * SIZE
                self.obstacles.append(Obstacle(self.surface, x, y))
    
    def spawn_power_up(self):
        """Randomly spawn power-ups"""
        if time.time() - self.power_up_timer > 15:  # Spawn every 15 seconds
            if random.random() < 0.7:  # 70% chance to spawn
                power_type = random.choice(['double', 'shrink', 'speed'])
                power_up = PowerUp(self.surface, power_type)
                # Make sure power-up doesn't spawn on snake, apple, or obstacles
                valid_position = False
                attempts = 0
                while not valid_position and attempts < 50:
                    power_up.x = random.randint(0, 37) * SIZE
                    power_up.y = random.randint(0, 30) * SIZE
                    valid_position = True
                    
                    # Check collision with snake
                    for i in range(self.snake.length):
                        if self.is_collision(power_up.x, power_up.y, self.snake.x[i], self.snake.y[i]):
                            valid_position = False
                            break
                    
                    # Check collision with apple
                    if self.is_collision(power_up.x, power_up.y, self.apple.x, self.apple.y):
                        valid_position = False
                    
                    # Check collision with obstacles
                    for obstacle in self.obstacles:
                        if self.is_collision(power_up.x, power_up.y, obstacle.x, obstacle.y):
                            valid_position = False
                            break
                    
                    attempts += 1
                
                if valid_position:
                    self.power_ups.append(power_up)
            
            self.power_up_timer = time.time()
    
    def update_power_ups(self):
        """Update power-up effects and remove expired ones"""
        # Remove expired power-ups
        self.power_ups = [pu for pu in self.power_ups if not pu.is_expired()]
        
        # Update speed boost timer
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1
            if self.speed_boost_timer <= 0:
                self.speed_boost = 1.0
        
        # Update score multiplier timer
        if self.multiplier_timer > 0:
            self.multiplier_timer -= 1
            if self.multiplier_timer <= 0:
                self.score_multiplier = 1
    
    def play(self):
        """Main game loop"""
        self.render_background()
        self.snake.walk()
        self.apple.draw()
        pygame.display.flip()
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw()
        
        # Spawn and draw power-ups
        self.spawn_power_up()
        for power_up in self.power_ups:
            power_up.draw()
        
        self.update_power_ups()
        self.display_score()
        self.display_power_up_status()
        pygame.display.flip()

        # Snake colliding with apple
        if self.is_collision(self.snake.x[0], self.snake.y[0], self.apple.x, self.apple.y):
            self.play_sound("Snake_Apple_Game/resources/ding-sound-effect_2.mp3")
            self.snake.increase_length()
            self.apple.move()
        
        # Snake colliding with power-ups
        for power_up in self.power_ups[:]:  # Use slice to avoid modification during iteration
            if self.is_collision(self.snake.x[0], self.snake.y[0], power_up.x, power_up.y):
                self.play_sound("Snake_Apple_Game/resources/ding-sound-effect_2.mp3")
                
                if power_up.power_type == 'double':
                    self.score_multiplier = 2
                    self.multiplier_timer = 300  # 5 seconds at 60 FPS
                elif power_up.power_type == 'shrink':
                    self.snake.decrease_length()
                elif power_up.power_type == 'speed':
                    self.speed_boost = 0.5  # Half speed (slower)
                    self.speed_boost_timer = 300  # 5 seconds
                
                self.power_ups.remove(power_up)
        
        # Snake colliding with itself
        for i in range(3, self.snake.length):
            if self.is_collision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                self.play_sound("Snake_Apple_Game/resources/Crash.mp3")
                self.game_over()
                return
        
        # Snake colliding with obstacles
        for obstacle in self.obstacles:
            if self.is_collision(self.snake.x[0], self.snake.y[0], obstacle.x, obstacle.y):
                self.play_sound("Snake_Apple_Game/resources/Crash.mp3")
                self.game_over()
                return
        
        # Snake colliding with wall
        if (self.snake.x[0] < 0 or self.snake.x[0] >= 800 or 
            self.snake.y[0] < 0 or self.snake.y[0] >= 600):
            self.play_sound("Snake_Apple_Game/resources/Crash.mp3")
            self.game_over()
            return
    
    def game_over(self):
        """Handle game over"""
        current_score = (self.snake.length - 2) * self.score_multiplier
        if current_score > self.high_score:
            self.high_score = current_score
            self.save_high_score(self.high_score)
            pygame.display.flip()
        
        self.state = GameState.GAME_OVER
        self.game_over_selection = 0
        pygame.mixer.music.pause()
    
    def display_score(self):
        font = pygame.font.SysFont('arial', 30)
        current_score = (self.snake.length - 2) * self.score_multiplier
        score_text = font.render(f"Score: {current_score}", True, (255, 255, 255))
        self.surface.blit(score_text, (600, 10))
        
        high_score_text = font.render(f"High: {self.high_score}", True, (255, 255, 255))
        self.surface.blit(high_score_text, (600, 45))
    
    def display_power_up_status(self):
        """Display active power-up status"""
        font = pygame.font.SysFont('arial', 20)
        y_offset = 80
        
        if self.score_multiplier > 1:
            text = font.render(f"Double Points! ({self.multiplier_timer//60 + 1}s)", True, (255, 215, 0))
            self.surface.blit(text, (10, y_offset))
            y_offset += 25
        
        if self.speed_boost < 1.0:
            text = font.render(f"Speed Boost! ({self.speed_boost_timer//60 + 1}s)", True, (255, 0, 255))
            self.surface.blit(text, (10, y_offset))
    
    def show_menu(self):
        """Display main menu"""
        self.render_background()
        
        # Title
        font_title = pygame.font.SysFont('arial', 48)
        title = font_title.render("SNAKE GAME", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 100))
        self.surface.blit(title, title_rect)
        
        # High Score
        font_score = pygame.font.SysFont('arial', 24)
        high_score_text = font_score.render(f"High Score: {self.high_score}", True, (255, 215, 0))
        high_score_rect = high_score_text.get_rect(center=(400, 150))
        self.surface.blit(high_score_text, high_score_rect)
        
        # Menu options
        font_menu = pygame.font.SysFont('arial', 32)
        menu_options = ["Start Game", "Instructions", "Select Difficulty", "Exit Game"]
        
        for i, option in enumerate(menu_options):
            color = (255, 255, 0) if i == self.menu_selection else (255, 255, 255)
            text = font_menu.render(f"{i+1}. {option}", True, color)
            text_rect = text.get_rect(center=(400, 220 + i * 50))
            self.surface.blit(text, text_rect)
        
        pygame.display.flip()
    
    def show_instructions(self):
        """Display instructions screen"""
        self.render_background()
        
        font_title = pygame.font.SysFont('arial', 36)
        title = font_title.render("HOW TO PLAY", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 80))
        self.surface.blit(title, title_rect)
        
        font_text = pygame.font.SysFont('arial', 24)
        instructions = [
            "Use ARROW KEYS to move the snake",
            "Eat apples to grow and increase your score",
            "Avoid hitting walls, obstacles, or yourself",
            "Press P to pause during gameplay",
            "Press ESC to quit",
            "",
            "POWER-UPS:",
            "Gold Square - Double points for 5 seconds",
            "Cyan Square - Shrink snake by one segment",
            "Magenta Square - Slow down for 5 seconds",
            "",
            "Press BACKSPACE to return to main menu"
        ]
        
        for i, line in enumerate(instructions):
            if line.startswith("POWER-UPS:"):
                color = (255, 215, 0)
            elif "Gold" in line:
                color = (255, 215, 0)
            elif "Cyan" in line:
                color = (0, 255, 255)
            elif "Magenta" in line:
                color = (255, 0, 255)
            else:
                color = (255, 255, 255)
            
            text = font_text.render(line, True, color)
            text_rect = text.get_rect(center=(400, 140 + i * 30))
            self.surface.blit(text, text_rect)
        
        pygame.display.flip()
    
    def show_difficulty_selection(self):
        """Display difficulty selection screen"""
        self.render_background()
        
        font_title = pygame.font.SysFont('arial', 36)
        title = font_title.render("SELECT DIFFICULTY", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 150))
        self.surface.blit(title, title_rect)
        
        font_menu = pygame.font.SysFont('arial', 28)
        difficulties = ["Easy - Slow speed", "Medium - Normal speed", "Hard - Fast speed + Obstacles"]
        
        for i, diff in enumerate(difficulties):
            color = (255, 255, 0) if i == self.difficulty_selection else (255, 255, 255)
            text = font_menu.render(f"{i+1}. {diff}", True, color)
            text_rect = text.get_rect(center=(400, 220 + i * 50))
            self.surface.blit(text, text_rect)
        
        font_text = pygame.font.SysFont('arial', 20)
        instruction = font_text.render("Use UP/DOWN arrows and press ENTER to select", True, (255, 255, 255))
        instruction_rect = instruction.get_rect(center=(400, 400))
        self.surface.blit(instruction, instruction_rect)
        
        back_text = font_text.render("Press BACKSPACE to return to main menu", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=(400, 430))
        self.surface.blit(back_text, back_rect)
        
        pygame.display.flip()
    
    def show_pause_menu(self):
        """Display pause menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.surface.blit(overlay, (0, 0))
        
        font_title = pygame.font.SysFont('arial', 48)
        title = font_title.render("PAUSED", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 200))
        self.surface.blit(title, title_rect)
        
        font_menu = pygame.font.SysFont('arial', 32)
        pause_options = ["Resume Game", "Quit to Main Menu"]
        
        for i, option in enumerate(pause_options):
            color = (255, 255, 0) if i == self.pause_selection else (255, 255, 255)
            text = font_menu.render(f"{i+1}. {option}", True, color)
            text_rect = text.get_rect(center=(400, 280 + i * 50))
            self.surface.blit(text, text_rect)
        
        pygame.display.flip()
    
    def show_game_over_screen(self):
        """Display game over screen"""
        self.render_background()
        
        font_title = pygame.font.SysFont('arial', 48)
        title = font_title.render("GAME OVER", True, (255, 0, 0))
        title_rect = title.get_rect(center=(400, 150))
        self.surface.blit(title, title_rect)
        
        font_score = pygame.font.SysFont('arial', 32)
        current_score = (self.snake.length - 2) * self.score_multiplier
        score_text = font_score.render(f"Your Score: {current_score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(400, 220))
        self.surface.blit(score_text, score_rect)
        
        high_score_text = font_score.render(f"High Score: {self.high_score}", True, (255, 215, 0))
        high_score_rect = high_score_text.get_rect(center=(400, 260))
        self.surface.blit(high_score_text, high_score_rect)
        
        if current_score == self.high_score and current_score > 0:
            new_record = font_score.render("NEW HIGH SCORE!", True, (255, 215, 0))
            new_record_rect = new_record.get_rect(center=(400, 300))
            self.surface.blit(new_record, new_record_rect)
        
        font_menu = pygame.font.SysFont('arial', 28)
        game_over_options = ["Play Again", "Return to Main Menu"]
        
        for i, option in enumerate(game_over_options):
            color = (255, 255, 0) if i == self.game_over_selection else (255, 255, 255)
            text = font_menu.render(f"{i+1}. {option}", True, color)
            text_rect = text.get_rect(center=(400, 380 + i * 40))
            self.surface.blit(text, text_rect)
        
        pygame.display.flip()
    
    def handle_menu_input(self, event):
        """Handle input for main menu"""
        if event.type == KEYDOWN:
            if event.key == K_UP:
                self.menu_selection = (self.menu_selection - 1) % 4
            elif event.key == K_DOWN:
                self.menu_selection = (self.menu_selection + 1) % 4
            elif event.key in [K_RETURN, K_KP_ENTER]:
                if self.menu_selection == 0:  # Start Game
                    self.init_game()
                    self.state = GameState.PLAYING
                    pygame.mixer.music.unpause()
                elif self.menu_selection == 1:  # Instructions
                    self.state = GameState.INSTRUCTIONS
                elif self.menu_selection == 2:  # Difficulty
                    self.state = GameState.DIFFICULTY
                elif self.menu_selection == 3:  # Exit
                    return False
            elif event.key in [K_1, K_2, K_3, K_4]:
                # Number key shortcuts
                key_to_selection = {K_1: 0, K_2: 1, K_3: 2, K_4: 3}
                self.menu_selection = key_to_selection[event.key]
        return True
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                
                elif self.state == GameState.MENU:
                    running = self.handle_menu_input(event)
                
                elif self.state == GameState.INSTRUCTIONS:
                    if event.type == KEYDOWN and event.key == K_BACKSPACE:
                        self.state = GameState.MENU
                
                elif self.state == GameState.DIFFICULTY:
                    if event.type == KEYDOWN:
                        if event.key == K_UP:
                            self.difficulty_selection = (self.difficulty_selection - 1) % 3
                        elif event.key == K_DOWN:
                            self.difficulty_selection = (self.difficulty_selection + 1) % 3
                        elif event.key in [K_RETURN, K_KP_ENTER]:
                            self.state = GameState.MENU
                        elif event.key == K_BACKSPACE:
                            self.state = GameState.MENU
                        elif event.key in [K_1, K_2, K_3]:
                            key_to_selection = {K_1: 0, K_2: 1, K_3: 2}
                            self.difficulty_selection = key_to_selection[event.key]
                
                elif self.state == GameState.PLAYING:
                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            self.state = GameState.MENU
                            pygame.mixer.music.pause()
                        elif event.key == K_p:
                            self.state = GameState.PAUSED
                            self.pause_selection = 0
                            pygame.mixer.music.pause()
                        elif event.key == K_UP:
                            self.snake.move_up()
                        elif event.key == K_DOWN:
                            self.snake.move_down()
                        elif event.key == K_LEFT:
                            self.snake.move_left()
                        elif event.key == K_RIGHT:
                            self.snake.move_right()
                
                elif self.state == GameState.PAUSED:
                    if event.type == KEYDOWN:
                        if event.key == K_UP:
                            self.pause_selection = (self.pause_selection - 1) % 2
                        elif event.key == K_DOWN:
                            self.pause_selection = (self.pause_selection + 1) % 2
                        elif event.key in [K_RETURN, K_KP_ENTER]:
                            if self.pause_selection == 0:  # Resume
                                self.state = GameState.PLAYING
                                pygame.mixer.music.unpause()
                            else:  # Quit to menu
                                self.state = GameState.MENU
                        elif event.key == K_p:  # Quick resume with P
                            self.state = GameState.PLAYING
                            pygame.mixer.music.unpause()
                
                elif self.state == GameState.GAME_OVER:
                    if event.type == KEYDOWN:
                        if event.key == K_UP:
                            self.game_over_selection = (self.game_over_selection - 1) % 2
                        elif event.key == K_DOWN:
                            self.game_over_selection = (self.game_over_selection + 1) % 2
                        elif event.key in [K_RETURN, K_KP_ENTER]:
                            if self.game_over_selection == 0:  # Play Again
                                self.init_game()
                                self.state = GameState.PLAYING
                                pygame.mixer.music.unpause()
                            else:  # Return to menu
                                self.state = GameState.MENU
                                pygame.mixer.music.unpause()
                        elif event.key in [K_1, K_2]:
                            key_to_selection = {K_1: 0, K_2: 1}
                            self.game_over_selection = key_to_selection[event.key]
            
            # Render based on current state
            if self.state == GameState.MENU:
                self.show_menu()
            elif self.state == GameState.INSTRUCTIONS:
                self.show_instructions()
            elif self.state == GameState.DIFFICULTY:
                self.show_difficulty_selection()
            elif self.state == GameState.PLAYING:
                self.play()
                # Control game speed based on difficulty
                sleep_time = self.difficulties[self.difficulty_selection]["speed"] * self.speed_boost
                self.clock.tick(int(1 / (self.difficulties[self.difficulty_selection]["speed"] * self.speed_boost)))
            elif self.state == GameState.PAUSED:
                self.show_pause_menu()
            elif self.state == GameState.GAME_OVER:
                self.show_game_over_screen()
            
            self.clock.tick(60)  # 60 FPS for smooth menus
        
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()