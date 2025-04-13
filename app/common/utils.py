from __future__ import annotations

from http.client import HTTPResponse
from io import BytesIO
from pathlib import Path
from typing import cast
from urllib.request import Request
from urllib.request import urlopen

from PIL import Image
from PIL import ImageSequence

from app.common import settings

DATA_PATH = Path.cwd() / "assets"
GLOBO_FILE_PATH = DATA_PATH / "globo.png"


def download_file(url: str) -> bytes:
    """
    Downloads a file from a URL and returns its content as bytes.
    :param url: The URL of the file to download.
    :return: The content of the file as bytes.
    """
    # TODO: If the url is from tenor it may not download as a gif, so we need to handle that case
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw_response = urlopen(req)
    response = cast(HTTPResponse, raw_response)
    return response.read()


def merge_globo_with_image_vertically(image_bytes: bytes) -> bytes:
    globo_img: Image.Image = Image.open(GLOBO_FILE_PATH)
    img: Image.Image = Image.open(BytesIO(image_bytes))

    if img.format == "GIF" and getattr(img, "is_animated", False):
        frames = []
        for frame in ImageSequence.Iterator(img):
            frame = frame.convert("RGBA")
            resized_globo = globo_img.resize(
                (frame.width, int(globo_img.height * frame.width / globo_img.width)),
                resample=Image.Resampling.BICUBIC,
            )

            merged = Image.new(
                "RGBA",
                (frame.width, resized_globo.height + frame.height),
            )
            merged.paste(resized_globo, (0, 0), resized_globo)
            merged.paste(frame, (0, resized_globo.height), frame)

            frames.append(merged)

        output = BytesIO()
        frames[0].save(
            output,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            loop=0,
            duration=img.info.get("duration", 100),
            disposal=2,
            transparency=img.info.get("transparency"),
        )
        output.seek(0)
        return output.read()

    else:
        img = img.convert("RGBA")
        if globo_img.width != img.width:
            resized_globo = globo_img.resize(
                (img.width, int(globo_img.height * img.width / globo_img.width)),
                resample=Image.Resampling.BICUBIC,
            )
        else:
            resized_globo = globo_img

        dst = Image.new(
            "RGBA",
            (resized_globo.width, resized_globo.height + img.height),
        )
        dst.paste(resized_globo, (0, 0))
        dst.paste(img, (0, resized_globo.height))

        output = BytesIO()
        dst.save(output, format="PNG")
        output.seek(0)
        return output.read()
