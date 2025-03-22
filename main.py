"""
Простая игра "Змейка" на Pygame
Управление: стрелки клавиатуры, ESC - выход
"""

import random
from typing import List, Tuple

import pygame

# Константы игры
BLOCK_SIZE = 20  # Размер одного блока (змейки и еды)
SCREEN_WIDTH = 800  # Ширина игрового окна
SCREEN_HEIGHT = 600  # Высота игрового окна
COLORS = {  # Цветовая схема
    "background": (0, 0, 0),
    "snake": (0, 255, 0),
    "food": (255, 0, 0),
    "text": (255, 255, 255)
}


class Direction:
    """Класс для хранения возможных направлений движения змейки"""
    UP = (0, -BLOCK_SIZE)
    DOWN = (0, BLOCK_SIZE)
    LEFT = (-BLOCK_SIZE, 0)
    RIGHT = (BLOCK_SIZE, 0)


class Snake:
    """Класс, представляющий змейку и её поведение"""

    def __init__(self):
        # Инициализация змейки с тремя сегментами по центру экрана
        self.body: List[Tuple[int, int]] = [
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            (SCREEN_WIDTH // 2 - BLOCK_SIZE, SCREEN_HEIGHT // 2),
            (SCREEN_WIDTH // 2 - 2 * BLOCK_SIZE, SCREEN_HEIGHT // 2)
        ]
        self.direction = Direction.RIGHT  # Начальное направление
        self.grow = False  # Флаг роста при поедании еды

    def move(self) -> None:
        """Перемещает змейку в текущем направлении"""
        # Добавляем новую голову в направлении движения
        new_head = (self.body[0][0] + self.direction[0],
                    self.body[0][1] + self.direction[1])
        self.body.insert(0, new_head)

        # Удаляем последний сегмент, если не нужно расти
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def change_direction(self, new_direction: Tuple[int, int]) -> None:
        """Меняет направление движения с проверкой на противоположное"""
        current_x, current_y = self.direction
        new_x, new_y = new_direction

        # Проверка, что новое направление не противоположно текущему
        # Сумма координат противоположных направлений даст (0, 0)
        match (current_x + new_x, current_y + new_y):
            case (0, 0):
                return  # Игнорируем противоположное направление
            case _:
                self.direction = new_direction

    def check_collision(self) -> bool:
        """Проверяет столкновения с границами экрана и собственным телом"""
        head = self.body[0]
        return any((
            head in self.body[1:],  # Столкновение с телом
            head[0] < 0,  # Левая граница
            head[0] >= SCREEN_WIDTH,  # Правая граница
            head[1] < 0,  # Верхняя граница
            head[1] >= SCREEN_HEIGHT  # Нижняя граница
        ))

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает змейку на указанной поверхности"""
        for segment in self.body:
            pygame.draw.rect(
                surface,
                COLORS["snake"],
                (*segment, BLOCK_SIZE, BLOCK_SIZE)
            )


class Food:
    """Класс для работы с едой: генерация и отрисовка"""

    def __init__(self, snake_body: List[Tuple[int, int]]):
        self.position = self.generate_valid_position(snake_body)

    def generate_valid_position(self, snake_body: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Генерирует позицию еды, не совпадающую с телом змейки"""
        while True:
            # Генерация позиции кратной размеру блока
            x = random.randint(0, (SCREEN_WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (SCREEN_HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            if (x, y) not in snake_body:
                return (x, y)

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает еду на указанной поверхности"""
        pygame.draw.rect(
            surface,
            COLORS["food"],
            (*self.position, BLOCK_SIZE, BLOCK_SIZE)
        )


class Game:
    """Основной класс игры, управляющий логикой и отрисовкой"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()  # Для контроля FPS
        self.font = pygame.font.Font(None, 36)  # Шрифт для текста
        self.reset()

    def reset(self) -> None:
        """Сбрасывает состояние игры к начальному"""
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.score = 0
        self.running = True  # Флаг работы игрового цикла

    def handle_input(self) -> None:
        """Обрабатывает пользовательский ввод"""
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False

                case pygame.KEYDOWN:
                    # Обработка нажатий клавиш с использованием match/case
                    match event.key:
                        case pygame.K_UP:
                            self.snake.change_direction(Direction.UP)
                        case pygame.K_DOWN:
                            self.snake.change_direction(Direction.DOWN)
                        case pygame.K_LEFT:
                            self.snake.change_direction(Direction.LEFT)
                        case pygame.K_RIGHT:
                            self.snake.change_direction(Direction.RIGHT)
                        case pygame.K_ESCAPE:
                            self.running = False

    def update(self) -> None:
        """Обновляет игровое состояние"""
        self.snake.move()

        # Проверка съедания еды
        if self.snake.body[0] == self.food.position:
            self.snake.grow = True
            self.score += 1
            self.food = Food(self.snake.body)  # Генерация новой еды

        # Проверка столкновений
        if self.snake.check_collision():
            self.running = False

    def draw(self) -> None:
        """Отрисовывает все игровые объекты"""
        self.screen.fill(COLORS["background"])
        self.snake.draw(self.screen)
        self.food.draw(self.screen)

        # Отрисовка счета
        score_text = self.font.render(f"Score: {self.score}", True, COLORS["text"])
        self.screen.blit(score_text, (10, 10))

        pygame.display.flip()  # Обновление экрана

    def show_game_over(self) -> None:
        """Показывает экран завершения игры"""
        text = self.font.render(f"Game Over! Score: {self.score}", True, COLORS["text"])
        text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(3000)  # Задержка перед закрытием

    def run(self) -> None:
        """Запускает основной игровой цикл"""
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(5)  # Ограничение по FPS

        self.show_game_over()
        pygame.quit()


if __name__ == "__main__":
    # Создание экземпляра игры и запуск
    Game().run()
