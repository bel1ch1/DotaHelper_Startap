import easyocr
import time

# Инициализация OCR
reader = easyocr.Reader(['en'], gpu=True)

# Распознавание текста (таймера и всего остального)
def recognize_text(image_path):
    result = reader.readtext(image_path)
    texts = []  # Список для хранения всех найденных текстов
    for detection in result:
        text = detection[1]  # detection[1] содержит распознанный текст
        texts.append(text)
    return texts

# Пример использования
image_path = 'C:/Mirea_Projects/DotaHelper_Startap/Data_Recognition/src/text_recognition/{C8202A7E-C5BB-44E5-B81F-58FE481BADEF}.png' # Укажите правильный путь к изображению

# Измерение времени выполнения
start = time.time()
recognized_texts = recognize_text(image_path)
end = time.time()

# Вывод результатов
print(f"Время выполнения: {end - start} секунд")
print("Распознанные тексты:")
for text in recognized_texts:
    print(text)
