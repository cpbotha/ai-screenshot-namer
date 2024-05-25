import base64
from pathlib import Path
import subprocess
import ollama
from openai import OpenAI

# before you can use a model:
# ollama pull llava-phi3

# vicuna language model, 13b q4_0 (8GB)
MODEL = "llava:13b-v1.6"

# llava+mistral punches above its weight
# https://ollama.com/library/llava:7b-v1.6-mistral-q4_K_M
# 7b q4_k_m, 4.5GB
# MODEL = "llava:7b-v1.6-mistral-q4_K_M"

# not too bad for such a small model
# MODEL = "llava-phi3"

PROMPT = """Suggest a lowercase filename of up to 64 characters (up to 10 words) for the included image (a screenshot) that is descriptive and useful for search.
Return ONLY the suggested filename. It should be lowercase and contain only letters, numbers, and underscores, with no extension. 
It should follow the form main-thing_sub-thing_sub-thing etc. Some good examples of filenames are:
"slide_sql_datagrid" OR "screenshot_python_datetime_conversion" OR "dashboard_sensor_graphs" OR "email_godaddy_domain_offer" OR "tweet_meme_ai_vs_ml"
"""

PROMPT_OCR_EXT = "In addition to the image itself, I include at the end of this message any text that appears in the image to help you come up with a good name."


# https://cookbook.openai.com/examples/multimodal/using_gpt4_vision_with_function_calling
# Function to encode the image as base64
def _encode_image(image_path: Path):
    # check if the image exists
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def _get_text_from_image(image_path: Path):
    # because check=True it will raise exception if called subprocess fails
    ret = subprocess.run(
        f"shortcuts run 'Extract text from image' --input-path '{image_path}' --output-type public.plain-text --output-path -",
        check=True,
        shell=True,
        capture_output=True,
        text=True,
    )
    return ret.stdout


def suggest_image_name(image_path: Path, ocr: bool = True, use_ollama=True):
    if ocr:
        ocr_text = _get_text_from_image(image_path)
        prompt = f"{PROMPT}\n{PROMPT_OCR_EXT}\nText from image:\n{ocr_text}"
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

        return res["message"]["content"]

    else:
        # this will use the key in env variable OPENAI_API_KEY
        client = OpenAI()
        base64_img = _encode_image(image_path)
        res = client.chat.completions.create(
            # https://platform.openai.com/docs/models/gpt-4o
            model="gpt-4o",
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
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_img}"
                            },
                        }
                    ],
                },
            ],
        )

        return res.choices[0].message.content
