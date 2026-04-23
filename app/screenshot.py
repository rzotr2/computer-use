import mss
from PIL import Image, ImageDraw, ImageFont
import io

def capture_screen_with_grid(grid_size=10):
    """
    Captures the primary monitor and draws a coordinate grid on it.
    grid_size: Number of divisions (e.g., 10 means 10x10 grid).
    """
    with mss.mss() as sct:
        # Get the primary monitor
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)

        # Convert to PIL Image
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

        draw = ImageDraw.Draw(img)
        width, height = img.size

        # Calculate step sizes
        step_x = width / grid_size
        step_y = height / grid_size

        # Try to load a font, fallback to default
        try:
            # On Mac, Arial might be available. On Linux/others, maybe not.
            # We'll use default if it fails.
            font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()

        # Draw vertical lines and labels
        for i in range(grid_size + 1):
            x = int(i * step_x)
            if x >= width: x = width - 1
            draw.line([(x, 0), (x, height)], fill="red", width=1)
            # Draw X coordinate label
            draw.text((x + 2, 5), str(i), fill="red", font=font)

        # Draw horizontal lines and labels
        for j in range(grid_size + 1):
            y = int(j * step_y)
            if y >= height: y = height - 1
            draw.line([(0, y), (width, y)], fill="red", width=1)
            # Draw Y coordinate label
            draw.text((5, y + 2), chr(65 + j) if j < 26 else str(j), fill="red", font=font)

        return img

def get_screenshot_bytes(img):
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()
