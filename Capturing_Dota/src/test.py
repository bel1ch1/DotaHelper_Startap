import easyocr

# Инициализация EasyOCR с использованием GPU
reader = easyocr.Reader(['en'], gpu=True)  # gpu=True по умолчанию


import time
start = time.time()
# Распознавание текста
results = reader.readtext("C:/Mirea_Projects/DotaHelper_Startap/Capturing_Dota/src/test.png")
end = time.time()
for (bbox, text, prob) in results:
    print(f"Text: {text}, Confidence: {prob}")

print(end - start)
