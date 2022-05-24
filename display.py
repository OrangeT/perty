from displayhatmini import DisplayHATMini
from pilmoji import Pilmoji
from pilmoji.source import AppleEmojiSource

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("""This example requires PIL/Pillow, try:

sudo apt install python3-pil

""")

width = DisplayHATMini.WIDTH
height = DisplayHATMini.HEIGHT
buffer = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(buffer)
font_size = 200
unicode_font = ImageFont.truetype("DejaVuSans.ttf", 220)

displayhatmini = DisplayHATMini(buffer)
displayhatmini.set_led(0.05, 0.05, 0.05)

def text(draw, text, position, size, color):
    with Pilmoji(buffer, source=AppleEmojiSource) as pilmoji:
        pilmoji.text((45, 10), text, (0, 0, 0), unicode_font)

def generate_gradient(
	colour1: str, colour2: str, width: int, height: int) -> Image:
	"""Generate a vertical gradient."""
	base = Image.new('RGB', (width, height), colour1)
	top = Image.new('RGB', (width, height), colour2)
	mask = Image.new('L', (width, height))
	mask_data = []
	for y in range(height):
	    mask_data.extend([int(255 * (y / height))] * width)
	mask.putdata(mask_data)
	base.paste(top, (0, 0), mask)
	return base

def display_emoji(emoji):

        global buffer

        grad = generate_gradient('#00FFFF', '#FFFFFF', DisplayHATMini.WIDTH, DisplayHATMini.HEIGHT)
        buffer.paste(grad, (0, 0))
        text(draw, emoji, (50, 50), 100, (255, 255, 255))
        rotated = buffer.transpose(method=Image.Transpose.ROTATE_180)
        buffer.paste(rotated, (0, 0))
        displayhatmini.display()
