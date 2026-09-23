from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont


def demo_image(*, title: str, colors: tuple[str, str], size: tuple[int, int]) -> ContentFile:
    image = Image.new("RGB", size, colors[0])
    draw = ImageDraw.Draw(image)
    width, height = size
    draw.rectangle((width // 2, 0, width, height), fill=colors[1])
    draw.ellipse(
        (width * 0.12, height * 0.12, width * 0.88, height * 0.88),
        outline="white",
        width=max(3, width // 80),
    )
    initials = "".join(word[0] for word in title.split()[:2]).upper()
    font = ImageFont.load_default(size=max(14, min(size) // 4))
    box = draw.textbbox((0, 0), initials, font=font)
    draw.text(
        ((width - (box[2] - box[0])) / 2, (height - (box[3] - box[1])) / 2),
        initials,
        fill="white",
        font=font,
    )
    output = BytesIO()
    image.save(output, format="WEBP", quality=88)
    return ContentFile(output.getvalue())
