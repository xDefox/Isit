import flet as ft
import math
import random
import time


def main(page: ft.Page):
    # Настройка страницы
    page.title = "🎮 Стань программистом за 60 секунд!"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = "#1a1a1a"

    # Переменные для сценария гравитации
    gravity = 0.5
    friction = 0.99
    ball_size = 30
    balls = []

    # Создаем шарики
    for i in range(8):
        balls.append({
            'x': random.randint(50, 300),
            'y': random.randint(50, 150),
            'vx': random.uniform(-3, 3),
            'vy': 0,
            'color': f"hsl({random.randint(0, 360)}, 70%, 60%)"
        })

    # Элементы интерфейса
    gravity_field = ft.TextField(
        value=str(gravity),
        width=80,
        text_size=14,
        height=40,
        content_padding=10
    )

    friction_field = ft.TextField(
        value=str(friction),
        width=80,
        text_size=14,
        height=40,
        content_padding=10
    )

    ball_size_field = ft.TextField(
        value=str(ball_size),
        width=80,
        text_size=14,
        height=40,
        content_padding=10
    )

    # Canvas для анимации
    canvas = ft.Container(
        width=600,
        height=400,
        bgcolor="#1a1a1a",
        border=ft.border.all(2, "#333"),
        content=ft.Stack([])
    )

    def update_animation(e=None):
        # Обновляем физику
        for ball in balls:
            # Гравитация
            ball['vy'] += gravity

            # Трение
            ball['vx'] *= friction
            ball['vy'] *= friction

            # Позиция
            ball['x'] += ball['vx']
            ball['y'] += ball['vy']

            # Границы
            if ball['x'] <= 0 or ball['x'] >= 600:
                ball['vx'] *= -0.8
                ball['x'] = max(0, min(600, ball['x']))

            if ball['y'] >= 400 - ball_size:
                ball['vy'] *= -0.8
                ball['y'] = 400 - ball_size

        # Отрисовываем
        shapes = [
            ft.Container(width=600, height=400, bgcolor="#1a1a1a"),
            ft.Container(width=600, height=10, top=390, bgcolor="#333")
        ]

        for ball in balls:
            shapes.append(
                ft.Container(
                    width=ball_size,
                    height=ball_size,
                    left=ball['x'] - ball_size / 2,
                    top=ball['y'] - ball_size / 2,
                    bgcolor=ball['color'],
                    border_radius=ball_size / 2,
                    shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.BLACK54)
                )
            )

        canvas.content = ft.Stack(shapes)
        canvas.update()

    def apply_changes(e):
        nonlocal gravity, friction, ball_size

        try:
            gravity = float(gravity_field.value)
            friction = float(friction_field.value)
            ball_size = int(ball_size_field.value)

            # Показываем сообщение об успехе
            page.show_snack_bar(ft.SnackBar(content=ft.Text("✅ Изменения применены!")))
            update_animation()

        except ValueError:
            page.show_snack_bar(ft.SnackBar(content=ft.Text("❌ Введите корректные числа!")))

    # Панель кода
    code_panel = ft.Container(
        width=400,
        height=400,
        padding=20,
        bgcolor="#2d2d2d",
        content=ft.Column([
            ft.Text("🧙 ТВОЙ ПЕРВЫЙ КОД:", size=20, weight="bold", color="white"),

            ft.Container(
                bgcolor="#1a1a1a",
                padding=15,
                border_radius=8,
                content=ft.Column([
                    ft.Text("function updatePhysics():", style="labelMedium", color="white", font_family="monospace"),
                    ft.Row([
                        ft.Text("    gravity = ", style="labelMedium", color="white", font_family="monospace"),
                        gravity_field,
                    ]),
                    ft.Row([
                        ft.Text("    friction = ", style="labelMedium", color="white", font_family="monospace"),
                        friction_field,
                    ]),
                    ft.Row([
                        ft.Text("    ball_size = ", style="labelMedium", color="white", font_family="monospace"),
                        ball_size_field,
                    ]),
                ])
            ),

            ft.Text("🎯 ЗАДАНИЯ:", size=16, weight="bold", color="white"),
            ft.Container(
                bgcolor="#1a1a1a",
                padding=15,
                border_radius=8,
                content=ft.Column([
                    ft.Text("1. 🎈 СДЕЛАЙ НЕВЕСОМОСТЬ! Измени 0.5 на 0.1", color="white"),
                    ft.Text("2. ⚡ СДЕЛАЙ СУПЕР-ГРАВИТАЦИЮ! Введи 2.0", color="white"),
                    ft.Text("3. 🌌 СДЕЛАЙ ВАКУУМ! Измени 0.99 на 0.999", color="white"),
                ])
            ),

            ft.Row([
                ft.ElevatedButton(
                    "🚀 ПРИМЕНИТЬ ИЗМЕНЕНИЯ!",
                    on_click=apply_changes,
                    style=ft.ButtonStyle(bgcolor=ft.colors.BLUE, color=ft.colors.WHITE)
                ),
            ])
        ], scroll=ft.ScrollMode.ADAPTIVE)
    )

    # Главный layout
    main_row = ft.Row([
        code_panel,
        canvas
    ])

    page.add(main_row)

    # Запускаем анимацию
    def animation_loop():
        while True:
            update_animation()
            time.sleep(0.016)  # ~60 FPS

    import threading
    threading.Thread(target=animation_loop, daemon=True).start()


if __name__ == "__main__":
    ft.app(target=main)