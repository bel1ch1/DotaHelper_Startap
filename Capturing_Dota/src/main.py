"""  Программа для захвата частей экрана доты  """

import pygetwindow as gw
import numpy as np
import mss
import mss.tools
import os
import time


# Название окна
dota_title = "Dota 2"
def main():
    # Поиск окна Доты
    window = gw.getWindowsWithTitle(dota_title)
    if window:
        game_window = window[0]
        print(game_window.title)

        # Координаты углов окна
        left, top, width, height = game_window.left, game_window.top, game_window.width, game_window.height
        print(f"Left: {left}, Top: {top}, Width: {width}, Height: {height}")

        # Проверка активного окна
        is_active = game_window.isActive
        print(is_active)

    else: print('Not Found')

    with mss.mss() as sct:
            monitor = {
                "left": left,
                "top": top,
                "width": width,
                "height": height
            }
            screenshot = sct.grab(monitor)
            output_filename = "screenshot.png"
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=output_filename)
            print(f"Скриншот сохранен в файл: {output_filename}")
            if os.path.exists(output_filename):
                print("Скриншот успешно сохранен!")
            else:
                print("Ошибка: файл не был создан.")

if __name__ == '__main__':
    time.sleep(5)
    main()
