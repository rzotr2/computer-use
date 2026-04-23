import mss
from PIL import Image, ImageDraw, ImageFont
import io

def capture_screen_with_grid(grid_size=100, major_step=10):
    """
    Captures the primary monitor and draws a high-precision coordinate grid.
    grid_size: Number of total divisions (e.g., 100x100).
    major_step: Interval for drawing major lines and labels.
    """
    with mss.mss() as sct:
        # Get the primary monitor
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)

        # Convert to PIL Image
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

        draw = ImageDraw.Draw(img)
        width, height = img.size

        # Calculate step sizes for the 100x100 grid
        step_x = width / grid_size
        step_y = height / grid_size

        try:
            font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()

        # Draw vertical lines
        for i in range(grid_size + 1):
            x = int(i * step_x)
            if x >= width: x = width - 1

            if i % major_step == 0:
                # Major line
                draw.line([(x, 0), (x, height)], fill=(255, 0, 0), width=2)
                # Label at top and bottom
                draw.text((x + 2, 5), str(i), fill="red", font=font)
                draw.text((x + 2, height - 20), str(i), fill="red", font=font)
            else:
                # Minor line - thinner
                draw.line([(x, 0), (x, height)], fill=(200, 0, 0), width=1)

        # Draw horizontal lines
        for j in range(grid_size + 1):
            y = int(j * step_y)
            if y >= height: y = height - 1

            if j % major_step == 0:
                # Major line
                draw.line([(0, y), (width, y)], fill=(255, 0, 0), width=2)
                # Label at left and right
                draw.text((5, y + 2), str(j), fill="red", font=font)
                draw.text((width - 25, y + 2), str(j), fill="red", font=font)
            else:
                # Minor line
                draw.line([(0, y), (width, y)], fill=(200, 0, 0), width=1)

        return img

def get_screenshot_bytes(img):
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()
