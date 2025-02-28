import easyocr
import time

# Инициализация EasyOCR (один раз)
reader = easyocr.Reader(['ru', 'en'])  # Укажите язык текста

def recognize_text(img_path):
    # Засекаем начальное время
    start_time = time.time()

    # Распознавание текста с изображения
    result = reader.readtext(img_path, detail=0)  # detail=0 для простого вывода

    # Засекаем конечное время
    end_time = time.time()

    # Вычисляем время выполнения
    execution_time = end_time - start_time

    # Вывод результата и времени выполнения
    print(f"Распознанный текст: {result}")
    print(f"Время выполнения: {execution_time:.2f} секунд")

# Пример использования
img_path = 'C:/Mirea_Projects/DotaHelper_Startap/Capturing_Dota/Captured_screens/cropped_screenshot_1740395260.png'
recognize_text(img_path)
