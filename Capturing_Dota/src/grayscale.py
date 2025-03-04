from PIL import Image

# Загрузите изображение
image = Image.open('C:/Mirea_Projects/DotaHelper_Startap/Capturing_Dota/Captured_screens/combined_screenshot_1741013786.png')
gray_image = image.convert('L')
# Сохраните грейское изображение
gray_image.save('gray_image.jpg')

# Отобразите изображение
gray_image.show()
