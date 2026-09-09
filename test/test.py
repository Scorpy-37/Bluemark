import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 400
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self, color, x, y):
        self.color = color
        self.positions = [(x, y)]
        self.direction = RIGHT
        self.length = 1
        self.score = 0

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        head = self.get_head_position()
        x, y = self.direction
        new_head = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)

        if new_head in self.positions[1:]:
            return False  # Game over

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()
        return True

    def reset(self):
        self.positions = [((GRID_WIDTH // 2), (GRID_HEIGHT // 2))]
        self.direction = RIGHT
        self.length = 1

    def render(self, surface):
        for p in self.positions:
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

    def render(self, surface):
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('2-Player Snake Game')
    clock = pygame.time.Clock()

    # Initialize game objects
    snake1 = Snake(GREEN, GRID_WIDTH // 4, GRID_HEIGHT // 2)
    snake2 = Snake(BLUE, (3 * GRID_WIDTH) // 4, GRID_HEIGHT // 2)
    foods = [Food() for _ in range(3)]
    scores = [0, 0]

    font = pygame.font.SysFont('Arial', 25)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Player 1 controls (WASD)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and snake1.direction != DOWN:
            snake1.direction = UP
        elif keys[pygame.K_s] and snake1.direction != UP:
            snake1.direction = DOWN
        elif keys[pygame.K_a] and snake1.direction != RIGHT:
            snake1.direction = LEFT
        elif keys[pygame.K_d] and snake1.direction != LEFT:
            snake1.direction = RIGHT

        # Player 2 controls (Arrow keys)
        if keys[pygame.K_UP] and snake2.direction != DOWN:
            snake2.direction = UP
        elif keys[pygame.K_DOWN] and snake2.direction != UP:
            snake2.direction = DOWN
        elif keys[pygame.K_LEFT] and snake2.direction != RIGHT:
            snake2.direction = LEFT
        elif keys[pygame.K_RIGHT] and snake2.direction != LEFT:
            snake2.direction = RIGHT

        # Update snakes
        game_over1 = not snake1.update()
        game_over2 = not snake2.update()

        # Check for collisions with food
        for food in foods[:]:
            if snake1.get_head_position() == food.position:
                snake1.length += 1
                snake1.score += 1
                foods.remove(food)
                foods.append(Food())
            elif snake2.get_head_position() == food.position:
                snake2.length += 1
                snake2.score += 1
                foods.remove(food)
                foods.append(Food())

        # Check for collisions between snakes
        if not game_over1 and not game_over2:
            if snake1.positions[0] in snake2.positions or snake2.positions[0] in snake1.positions:
                game_over1 = True
                game_over2 = True

        # Reset game if either player loses
        if game_over1 or game_over2:
            for _ in range(3):
                foods.append(Food())
            if game_over1 and not game_over2:
                scores[0] += 1
                snake1.reset()
            elif game_over2 and not game_over1:
                scores[1] += 1
                snake2.reset()

        # Drawing
        screen.fill(BLACK)
        snake1.render(screen)
        snake2.render(screen)

        for food in foods:
            food.render(screen)

        # Display scores
        score_text = font.render(f'Player 1: {snake1.score} | Player 2: {snake2.score}', True, WHITE)
        game_over_text = font.render('Game Over! Press R to restart', True, RED) if (game_over1 or game_over2) else None

        screen.blit(score_text, (10, 10))
        if game_over_text:
            screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()