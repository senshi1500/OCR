import cv2
import pytesseract
import pyperclip

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
custom_config = r'--oem 3 --psm 6'
# Cargar imagen
img = cv2.imread("sample.jpg")
# Convierte la imagen a escala de grises
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# Aplicar umbral para convertir a imagen binaria
threshold_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
# Pasa la imagen por pytesseract
text = pytesseract.image_to_string(threshold_img)
# Imprimir el texto extraído
print(text)

pyperclip.copy(text)

