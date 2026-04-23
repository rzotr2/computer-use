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
            # Try to load a larger font if possible
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        except:
            font = ImageFont.load_default()

        # Draw vertical lines
        for i in range(grid_size + 1):
            x = int(i * step_x)
            if x >= width: x = width - 1

            if i % major_step == 0:
                # Major line
                draw.line([(x, 0), (x, height)], fill=(255, 0, 0, 150), width=2)
                # Label at top and bottom
                label = str(i)
                # Draw label with background for better visibility
                draw.rectangle([x + 2, 5, x + 30, 30], fill=(255, 255, 255, 180))
                draw.text((x + 4, 5), label, fill="red", font=font)

                draw.rectangle([x + 2, height - 35, x + 30, height - 5], fill=(255, 255, 255, 180))
                draw.text((x + 4, height - 35), label, fill="red", font=font)
            else:
                # Minor line - thinner
                draw.line([(x, 0), (x, height)], fill=(200, 0, 0, 80), width=1)

        # Draw horizontal lines
        for j in range(grid_size + 1):
            y = int(j * step_y)
            if y >= height: y = height - 1

            if j % major_step == 0:
                # Major line
                draw.line([(0, y), (width, y)], fill=(255, 0, 0, 150), width=2)
                # Label at left and right
                label = str(j)
                draw.rectangle([5, y + 2, 35, y + 25], fill=(255, 255, 255, 180))
                draw.text((7, y + 2), label, fill="red", font=font)

                draw.rectangle([width - 40, y + 2, width - 5, y + 25], fill=(255, 255, 255, 180))
                draw.text((width - 38, y + 2), label, fill="red", font=font)
            else:
                # Minor line
                draw.line([(0, y), (width, y)], fill=(200, 0, 0, 80), width=1)

        return img

def get_screenshot_bytes(img):
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()
