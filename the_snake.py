from random import randrange
import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс объекта игры.

    Атрибуты:
        position: Координаты объекта на экране.
        body_color: Цвет игрового объекта.
    """

    def __init__(self, position=None, body_color=None):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объекты, переопределяется в классах-наследниках."""
        pass


class Apple(GameObject):
    """Класс, представляющий яблоко."""

    def __init__(self, snake_positions=None):
        if snake_positions is None:
            snake_positions = []
        position = self.randomize_position(snake_positions)
        super().__init__(position, APPLE_COLOR)

    def randomize_position(self, snake_positions):
        """
        Генерирует случайный кортеж (x, y) для яблока.
        Гарантирует, что яблоко не генерируется в змейке.

        Args:
            snake_positions: Список кортежей (x, y) с сегментами змейки.

        Returns:
            Кортеж с координатами яблока.
        """
        while True:
            possible_position = (
                randrange(0, SCREEN_WIDTH, GRID_SIZE),
                randrange(0, SCREEN_HEIGHT, GRID_SIZE))
            if possible_position not in snake_positions:
                self.position = possible_position
                return self.position

    def draw(self):
        """
        Переопределяет метод родительского класса.
        Отрисовывает объект яблоко на игровом поле.
        """
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, представляющий змейку в игре."""

    def __init__(self):
        position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        super().__init__(position, SNAKE_COLOR)
        self.positions = [position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    @property
    def length(self):
        """Возвращает текущую длину змейки."""
        return len(self.positions)

    def update_direction(self):
        """Обновляет направление движения змейк на следующее запрошенное."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self, apple_position):
        """
        Обновляет местоположение змейки на одну ячейку.
        Анализирует, съедено ли яблоко, увеличивает змейку при необходимости,
        запоминает координаты хвоста.

        Args:
            apple_position: Кортеж (x, y) с координатами яблока.
        """
        x, y = self.get_head_position()
        if self.direction == UP:
            new_x, new_y = x, y - GRID_SIZE
            self.positions.insert(0, (new_x, new_y % SCREEN_HEIGHT))
        elif self.direction == DOWN:
            new_x, new_y = x, y + GRID_SIZE
            self.positions.insert(0, (new_x, new_y % SCREEN_HEIGHT))
        elif self.direction == RIGHT:
            new_x, new_y = x + GRID_SIZE, y
            self.positions.insert(0, (new_x % SCREEN_WIDTH, new_y))
        elif self.direction == LEFT:
            new_x, new_y = x - GRID_SIZE, y
            self.positions.insert(0, (new_x % SCREEN_WIDTH, new_y))

        tail = self.positions.pop()
        if self.positions[0] == apple_position:
            self.positions.append(tail)
            self.last = None
        else:
            self.last = tail

    def draw(self):
        """Переопределяет метод родительского класса,
        отрисовывает или затирает сегмент.
        """
        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Возвращает координаты головы змейки (первый элемент списка)."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в исходное состояние (центр экрана, длина 1)."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш для изменения направления движения."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """
    Создает экземпляры классов и запускает игровой процесс в бесконечном цикле.
    Обрабатывает игровые события.
    """
    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move(apple.position)

        snake_head = snake.get_head_position()

        if snake_head == apple.position:
            apple.randomize_position(snake.positions)

        if snake_head in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)

        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
