import pytesseract
try:
	import Image
except:
	from PIL import Image

img = Image.open("test.jpg")
print pytesseract.image_to_string(img)
