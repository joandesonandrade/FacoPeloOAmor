from pytesseract import image_to_string as ocr
from PIL import Image as img

class rec:
    def __init__(self,imagem):
        self.image = img.open(imagem)

    def extrairTexto(self):
        texto = ocr(self.image, lang='por').replace(' ','').replace('|','').replace('[','').replace(']','').replace(')','').replace('(','').replace('}','').replace('{','')
        return (texto,self.image)