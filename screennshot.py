import pyautogui

# Capturar pantalla.
screenshot = pyautogui.screenshot(region=(50, 50, 400, 300))

# Mostrar imagen.
screenshot.show()
