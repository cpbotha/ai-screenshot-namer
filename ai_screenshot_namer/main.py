"""Main module of ai-screenshot-renamer, copright 2024 Charl P. Botha <cpbotha@vxlabs.com>."""

import base64
import io
import os
import re
import subprocess
from pathlib import Path
from typing import cast

import click
import dateparser
import ollama
from openai import OpenAI
from PIL import Image

# default model is llava-phi3, small and fast, not too bad
# you can configure the local model like this:
# export AISN_MODEL=llama3.2-vision

# before you can use a model (replace llava-phi3 with what you chose):
# ollama pull llava-phi3

# vicuna language model, 13b q4_0 (8GB)
# MODEL = "llava:13b-v1.6"

# llava+mistral punches above its weight
# https://ollama.com/library/llava:7b-v1.6-mistral-q4_K_M
# 7b q4_k_m, 4.5GB
# MODEL = "llava:7b-v1.6-mistral-q4_K_M"

# on this Apple M1 Max, this 8GB model takes about 35s per image
# quality is high though!
# MODEL = "llama3.2-vision"

# llava-phi3 is not too bad for such a small model
# 2 to 5 seconds per image on Apple M1 Max
MODEL = os.getenv("AISN_MODEL", "llava-phi3")

FILENAME_MAX_CHARACTERS = 64

PROMPT = f"""
Suggest a lowercase filename of up to {FILENAME_MAX_CHARACTERS} characters (up to 10 words) for the included image (a
screenshot) that is descriptive and useful for search.

Do not return any explanation, ONLY the suggested filename. 

The filename should be lowercase and contain only letters, numbers, and underscores, with no extension. It should follow
the form main-thing_sub-thing_sub-thing etc.

Some good examples of filenames are: "slide_sql_datagrid" OR "screenshot_python_datetime_conversion" OR
"dashboard_sensor_graphs" OR "email_godaddy_domain_offer" OR "tweet_meme_ai_vs_ml"
"""

PROMPT_OCR_EXT = "In addition to the image itself, I include at the end of this message any text that appears in the image to help you come up with a good name."


def _calc_max_image_size(size: tuple[int, int]) -> tuple[int, int]:
    """Calculate the maximum image size that can be sent to OpenAI."""
    # long side should be less than 2000, short side should be less than 768
    # https://platform.openai.com/docs/guides/vision#managing-images
    long_idx, short_idx = (0, 1) if size[0] > size[1] else (1, 0)
    new_size = list(size)
    if new_size[long_idx] > 2000:
        new_size[short_idx] = int(2000 / size[long_idx] * size[short_idx])
        new_size[long_idx] = 2000
    if new_size[short_idx] > 768:
        new_size[long_idx] = int(768 / size[short_idx] * size[long_idx])
        new_size[short_idx] = 768
    return cast(tuple[int, int], tuple(new_size))


# https://cookbook.openai.com/examples/multimodal/using_gpt4_vision_with_function_calling
# Function to encode the image as base64
def _encode_image(image_path: Path):
    # check if the image exists
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # read image_path, convert to webp via io, then encode as base64
    pillow_image = Image.open(image_path)
    new_size = _calc_max_image_size(pillow_image.size)
    if new_size != pillow_image.size:
        pillow_image.resize(new_size)
        click.echo(f"Resize image for API submission from {pillow_image.size} to {new_size}")

    bio = io.BytesIO()
    pillow_image.save(bio, "WEBP")
    size_kb_in = image_path.stat().st_size / 1024
    size_kb_out = bio.tell() / 1024
    click.echo(f"API submission image size: {size_kb_in:.1f} KB → {size_kb_out:.1f} KB")
    return base64.b64encode(bio.getvalue()).decode("utf-8")


def _get_text_from_image(image_path: Path):
    # because check=True it will raise exception if called subprocess fails
    try:
        ret = subprocess.run(
            f"shortcuts run 'Extract text from image' --input-path '{str(image_path)}' --output-type public.plain-text --output-path -",
            check=True,
            shell=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        click.echo(f"Error extracting text from image (expected if not macOS): {repr(e)}")
        return None
    else:
        return ret.stdout


# macos gives me e.g. Screenshot 2024-05-24 at 23.53.04.png
# this will extract the date, which is all I need for my naming scheme in addition to the AI suggestion
def _extract_date_from_filename(filename):
    # Define a regex pattern to capture potential date segments
    date_pattern = re.compile(r"\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4}|\d{4}\d{2}\d{2}|\d{2}\d{2}\d{4}")

    # Search for the date pattern in the filename
    match = date_pattern.search(filename)

    if match:
        date_str = match.group()
        # Parse the date string to a datetime object
        date_obj = dateparser.parse(date_str)
        return date_obj
    else:
        return None


def suggest_image_name(image_path: Path, ocr: bool = True, use_ollama=True):
    """Suggest a filename for the image at image_path using AI (VLM) and optionally OCR text from the image."""
    if ocr:
        ocr_text = _get_text_from_image(image_path)
        if ocr_text:
            prompt = f"{PROMPT}\n{PROMPT_OCR_EXT}\nText from image:\n{ocr_text}"
        else:
            click.echo("No text extracted from image.")
            prompt = PROMPT
    else:
        prompt = PROMPT

    if use_ollama:
        res = ollama.chat(
            model=MODEL,
            # "Describe this image:"
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_path],
                }
            ],
        )

        draft = res["message"]["content"]

    else:
        # if you don't set OPENAI_MODEL or OPENAI_API_URL it will default to the OpenAI defaults
        model = os.getenv("AISN_OPENAI_MODEL", "gpt-4o-mini")
        api_base_url = os.getenv("AISN_OPENAI_BASE_URL", None)
        # this will use the key in env variable OPENAI_API_KEY
        client = OpenAI(api_key=os.getenv("AISN_OPENAI_API_KEY", None), base_url=api_base_url)
        base64_img = _encode_image(image_path)
        res = client.chat.completions.create(
            # https://platform.openai.com/docs/models/gpt-4o
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": [
                        # {"type": "text", "text": "Message can also go here"},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/webp;base64,{base64_img}"},
                        }
                    ],
                },
            ],
        )

        draft = res.choices[0].message.content

    # filter out anything but alpha, numbers, underscores
    # and replace whitespace with underscores
    # llava-phi often adds " characters
    if draft is not None:
        draft = re.sub(r"[^\w\s]", "", draft).replace(" ", "_")

    return draft


def sanitize_filename(filename: str, max_length: int) -> str:
    """Sanitize filename and truncate to max_length."""
    filename = filename.strip()
    filename = filename.replace("\n", "_").replace("\r", "_")
    return filename[:max_length]


@click.command()
# so we can pass in multiple files, via shell path globbing e.g.
# https://click.palletsprojects.com/en/8.1.x/arguments/#option-like-arguments
@click.argument("screenshots", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--use-openai",
    is_flag=True,
    help="Use OpenAI instead of the default Ollama (local)",
    default=False,
)
@click.option(
    "--do-rename",
    is_flag=True,
    help="Actually rename the files (usually we just print the suggestions)",
    default=False,
)
def cli(screenshots: list[Path], use_openai: bool = True, do_rename: bool = False):
    """Rename SCREENSHOTS based on AI (VLM) image description and extracted text."""
    if not screenshots:
        click.echo("Please specify at least one screenshot filename.", err=True)
        return

    really_use_openai = use_openai or os.getenv("AISN_OPENAI_MODEL")
    click.echo(f"Using {'OpenAI' if really_use_openai else 'Ollama: ' + MODEL}")
    for screenshot in screenshots:
        screenshot = Path(screenshot)
        date = _extract_date_from_filename(screenshot.stem)
        # output date as e.g. 20240525
        date_str = "" if date is None else f"{date.strftime("%Y-%m-%d")}-"
        # construct new Path with stem = date_str + suggested name
        if suggestion := suggest_image_name(screenshot, use_ollama=not really_use_openai):
            new_name = f"{date_str}{sanitize_filename(suggestion, FILENAME_MAX_CHARACTERS - len(date_str))}"
            new_path = screenshot.with_name(new_name + screenshot.suffix)
            click.echo(f"{screenshot} → {new_path}")
            if do_rename:
                screenshot.rename(new_path)


if __name__ == "__main__":
    cli()
