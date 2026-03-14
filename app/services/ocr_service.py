import pytesseract
import cv2
import numpy as np
from PIL import Image
import os

def extract_text_from_image(file_path: str) -> str:
    try:
        # If running on windows, may need to set tesseract_cmd
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        image = cv2.imread(file_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Simple preprocessing
        blur = cv2.GaussianBlur(gray, (3,3), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        
        # Invert to have black text on white bg for tesseract
        inverted = 255 - thresh
        
        custom_config = r'--oem 3 --psm 6'
        extracted_text = pytesseract.image_to_string(inverted, config=custom_config)
        return extracted_text.strip()
    except Exception as e:
        return f"Error extracting text: {str(e)}"
