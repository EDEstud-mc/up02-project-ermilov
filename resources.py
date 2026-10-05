from pathlib import Path
from PIL import Image, ImageTk

BASE_DIR = Path(__file__).resolve().parent
PATH_PICTURE = str(BASE_DIR / "resources" / "picture.png")
PATH_LOGO = str(BASE_DIR / "resources" / "logo.png")
PATH_ICON = str(BASE_DIR / "resources" / "icon.ico")


def _resolve_path(path):
    result = Path(path)
    return result if result.is_absolute() else BASE_DIR / result


def load_image(path, size=(100, 100)):
    try:
        with Image.open(_resolve_path(path)) as source:
            image = source.convert("RGBA")
        image = image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)
    except (OSError, ValueError) as error:
        print(f"Ошибка загрузки {path}: {error}")
        return None


def load_image_proportional(path, max_size=(100, 100)):
    try:
        with Image.open(_resolve_path(path)) as source:
            image = source.convert("RGBA")
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)
    except (OSError, ValueError) as error:
        print(f"Ошибка загрузки {path}: {error}")
        return None


def get_product_image(image_path, size=(100, 100)):
    """Отсутствующая или повреждённая обложка заменяется picture.png."""
    if image_path:
        path = _resolve_path(image_path)
        if path.is_file():
            photo = load_image(path, size)
            if photo is not None:
                return photo
    return load_image(PATH_PICTURE, size)
