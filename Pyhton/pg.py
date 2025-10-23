import pygame
import sys
import random
import math

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 1000, 600
CODE_PANEL_WIDTH = 400
VISUAL_PANEL_WIDTH = WIDTH - CODE_PANEL_WIDTH

# Цвета
BG_COLOR = (26, 26, 26)
CODE_BG = (45, 45, 45)
TEXT_COLOR = (248, 248, 242)
ACCENT_COLOR = (0, 122, 204)


class GravityBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = 0
        self.color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255)
        )


class InteractiveCodingApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Стань программистом за 60 секунд!")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 16)
        self.title_font = pygame.font.SysFont("arial", 24, bold=True)

        self.current_scenario = None
        self.editing_field = None

        # Параметры сценариев
        self.gravity = 0.5
        self.friction = 0.99
        self.ball_size = 30
        self.balls = []

        self.input_boxes = {}

    def draw_scenario_selection(self):
        self.screen.fill(BG_COLOR)

        # Заголовок
        title = self.title_font.render("🎮 ВЫБЕРИ СВОЮ СИЛУ ПРОГРАММИСТА!", True, (255, 255, 255))
        subtitle = self.font.render("Измени всего одну строчку кода и увидишь магию!", True, (200, 200, 200))

        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        self.screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 150))

        # Карточки сценариев
        scenarios = [
            {"key": "gravity", "title": "⚡ ГРАВИТАЦИЯ", "desc": "Управляй физикой шариков!"},
            {"key": "colors", "title": "🎨 ЦВЕТНАЯ ИНФЕКЦИЯ", "desc": "Создай вирусный эффект!"},
            {"key": "particles", "title": "✨ ЧАСТИЦЫ", "desc": "Управляй тысячами частиц!"},
        ]

        for i, scenario in enumerate(scenarios):
            x = 150 + i * 300
            y = 250

            # Рамка карточки
            card_rect = pygame.Rect(x - 125, y - 75, 250, 150)
            pygame.draw.rect(self.screen, CODE_BG, card_rect, border_radius=15)
            pygame.draw.rect(self.screen, ACCENT_COLOR, card_rect, 3, border_radius=15)

            # Текст
            title_text = self.font.render(scenario["title"], True, (255, 255, 255))
            desc_text = self.font.render(scenario["desc"], True, (200, 200, 200))

            self.screen.blit(title_text, (x - title_text.get_width() // 2, y - 30))
            self.screen.blit(desc_text, (x - desc_text.get_width() // 2, y))

            # Сохраняем область для клика
            scenario["rect"] = card_rect

        return scenarios

    def draw_code_panel(self):
        # Фон панели кода
        code_panel = pygame.Rect(0, 0, CODE_PANEL_WIDTH, HEIGHT)
        pygame.draw.rect(self.screen, CODE_BG, code_panel)

        # Заголовок
        title = self.title_font.render("🧙 ТВОЙ ПЕРВЫЙ КОД:", True, TEXT_COLOR)
        self.screen.blit(title, (20, 20))

        if self.current_scenario == "gravity":
            # Отображение кода
            code_lines = [
                "function updatePhysics():",
                f"    gravity = {self.gravity}",
                f"    friction = {self.friction}",
                f"    ball_size = {self.ball_size}",
            ]

            for i, line in enumerate(code_lines):
                text = self.font.render(line, True, TEXT_COLOR)
                self.screen.blit(text, (30, 70 + i * 25))

            # Задания
            tasks = [
                "🎈 СДЕЛАЙ НЕВЕСОМОСТЬ! Кликни на числа",
                "⚡ Измени гравитацию на 0.1 или 2.0",
                "🌌 Измени трение на 0.999"
            ]

            tasks_title = self.font.render("🎯 ЗАДАНИЯ:", True, TEXT_COLOR)
            self.screen.blit(tasks_title, (20, 180))

            for i, task in enumerate(tasks):
                task_text = self.font.render(f"{i + 1}. {task}", True, (200, 200, 200))
                self.screen.blit(task_text, (30, 210 + i * 25))

            # Поля для редактирования
            self.input_boxes = {
                "gravity": pygame.Rect(150, 95, 60, 20),
                "friction": pygame.Rect(150, 120, 60, 20),
                "ball_size": pygame.Rect(150, 145, 60, 20),
            }

            for rect in self.input_boxes.values():
                pygame.draw.rect(self.screen, (60, 60, 60), rect)
                pygame.draw.rect(self.screen, ACCENT_COLOR, rect, 1)

        # Кнопки
        apply_btn = pygame.Rect(20, 300, 200, 40)
        back_btn = pygame.Rect(20, 350, 200, 40)

        pygame.draw.rect(self.screen, ACCENT_COLOR, apply_btn, border_radius=8)
        pygame.draw.rect(self.screen, (100, 100, 100), back_btn, border_radius=8)

        apply_text = self.font.render("🚀 ПРИМЕНИТЬ ИЗМЕНЕНИЯ", True, (255, 255, 255))
        back_text = self.font.render("← ВЫБРАТЬ ДРУГОЙ", True, (255, 255, 255))

        self.screen.blit(apply_text, (apply_btn.centerx - apply_text.get_width() // 2,
                                      apply_btn.centery - apply_text.get_height() // 2))
        self.screen.blit(back_text, (back_btn.centerx - back_text.get_width() // 2,
                                     back_btn.centery - back_text.get_height() // 2))

        return apply_btn, back_btn

    def draw_visual_panel(self):
        # Фон
        visual_panel = pygame.Rect(CODE_PANEL_WIDTH, 0, VISUAL_PANEL_WIDTH, HEIGHT)
        pygame.draw.rect(self.screen, BG_COLOR, visual_panel)

        if self.current_scenario == "gravity":
            # Пол
            pygame.draw.rect(self.screen, (51, 51, 51),
                             (CODE_PANEL_WIDTH, HEIGHT - 20, VISUAL_PANEL_WIDTH, 20))

            # Шарики
            for ball in self.balls:
                pygame.draw.circle(self.screen, ball.color,
                                   (int(ball.x + CODE_PANEL_WIDTH), int(ball.y)),
                                   self.ball_size)

                # Тень
                shadow_rect = (int(ball.x + CODE_PANEL_WIDTH - self.ball_size),
                               int(ball.y - self.ball_size),
                               self.ball_size * 2, self.ball_size * 2)
                pygame.draw.circle(self.screen, (0, 0, 0, 100),
                                   (int(ball.x + CODE_PANEL_WIDTH), int(ball.y)),
                                   self.ball_size)

    def update_gravity_physics(self):
        for ball in self.balls:
            # Гравитация
            ball.vy += self.gravity

            # Трение
            ball.vx *= self.friction
            ball.vy *= self.friction

            # Позиция
            ball.x += ball.vx
            ball.y += ball.vy

            # Границы
            if ball.x <= 0 or ball.x >= VISUAL_PANEL_WIDTH:
                ball.vx *= -0.8
                ball.x = max(0, min(VISUAL_PANEL_WIDTH, ball.x))

            if ball.y >= HEIGHT - 20 - self.ball_size:
                ball.vy *= -0.8
                ball.y = HEIGHT - 20 - self.ball_size

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if self.current_scenario is None:
                    # Выбор сценария
                    scenarios = self.draw_scenario_selection()
                    for scenario in scenarios:
                        if scenario["rect"].collidepoint(mouse_pos):
                            self.start_scenario(scenario["key"])

                else:
                    apply_btn, back_btn = self.draw_code_panel()

                    if apply_btn.collidepoint(mouse_pos):
                        self.apply_changes()
                    elif back_btn.collidepoint(mouse_pos):
                        self.current_scenario = None

                    # Проверка полей ввода
                    for field, rect in self.input_boxes.items():
                        if rect.collidepoint(mouse_pos):
                            self.editing_field = field
                            break

            elif event.type == pygame.KEYDOWN and self.editing_field:
                if event.key == pygame.K_RETURN:
                    self.editing_field = None
                elif event.key == pygame.K_BACKSPACE:
                    # Обработка backspace для числовых полей
                    current_value = str(getattr(self, self.editing_field))
                    if current_value:
                        new_value = current_value[:-1]
                        if new_value and new_value != '-':
                            setattr(self, self.editing_field, float(new_value) if '.' in new_value else int(new_value))
                elif event.unicode.isdigit() or event.unicode == '.' or (
                        event.unicode == '-' and not str(getattr(self, self.editing_field))):
                    # Добавление цифр, точки или минуса
                    current_value = str(getattr(self, self.editing_field))
                    new_value = current_value + event.unicode
                    try:
                        if '.' in new_value:
                            setattr(self, self.editing_field, float(new_value))
                        else:
                            setattr(self, self.editing_field, int(new_value))
                    except:
                        pass

    def start_scenario(self, scenario_key):
        self.current_scenario = scenario_key

        if scenario_key == "gravity":
            self.balls = []
            for i in range(8):
                self.balls.append(GravityBall(
                    random.randint(50, VISUAL_PANEL_WIDTH - 50),
                    random.randint(50, 200)
                ))

    def apply_changes(self):
        # Перезапускаем сценарий с новыми параметрами
        self.start_scenario(self.current_scenario)

    def run(self):
        while True:
            self.handle_events()

            if self.current_scenario is None:
                self.draw_scenario_selection()
            else:
                if self.current_scenario == "gravity":
                    self.update_gravity_physics()

                self.draw_code_panel()
                self.draw_visual_panel()

            pygame.display.flip()
            self.clock.tick(60)


# Запуск приложения
if __name__ == "__main__":
    app = InteractiveCodingApp()
    app.run()