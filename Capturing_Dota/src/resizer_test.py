""" Просто експерименты  """

import cv2

image_path = 'C:/Mirea_Projects/DotaHelper_Startap/Capturing_Dota/Captured_screens/combined_screenshot_1740135062.png'

image = cv2.imread(image_path)

resized_image = cv2.resize(image, (640, 320))

cv2.imshow('Resized Image', resized_image)

cv2.waitKey(0)

cv2.destroyAllWindows()
