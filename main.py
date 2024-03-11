from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import requests
import json
from datetime import datetime
from deep_translator import GoogleTranslator

load_dotenv()
import os

app = Flask(__name__)

# Configuration
ENDPOINTS = [
    {"name": "fooocus", "url": "https://fal.run/fal-ai/fooocus"},
    {"name": "fast-sdxl", "url": "https://fal.run/fal-ai/fast-sdxl"},
]

PRE_PROMPT = "wide angle shot, daylight, warm-toned, 35mm, --ar 4:3, --s 250, natural lighting, realistic faces, realistic bodies, sharp focus, sport shooting, dynamic range, wide shot, "


def get_season(date_str):
    date = datetime.strptime(date_str, "%b %d, %Y")
    if date.month in [12, 1, 2]:
        return "winter"
    elif date.month in [6, 7, 8]:
        return "summer"
    elif date.month in [9, 10, 11]:
        return "autumn"
    elif date.month in [3, 4, 5]:
        return "spring"


def generate_base_prompt(form_data):
    return f"{PRE_PROMPT}, Evenement voor '{form_data['naam-evenement']}', evenementbeschrijving '{form_data['beschrijving']}' personen van leeftijdscategorie '{form_data['geschikt-voor']}', personen van diverse etnische afkomst, weersomstandigheden zijn volgens het seizoen {get_season(form_data['begindatum'])},"


def translate_prompt(prompt):
    return GoogleTranslator(source="nl", target="en").translate(prompt)


def generate_image_url(description, endpoint):
    endpoint_url = next(ep["url"] for ep in ENDPOINTS if ep["name"] == endpoint)
    response = requests.post(
        url=endpoint_url,
        headers={
            "Authorization": f'Key {os.getenv("FAL_ID_SECRET")}',
            "Content-Type": "application/json",
        },
        data=json.dumps(
            {
                "prompt": description,
                "negative_prompt": "cartoon, painting, illustration, bad anatomy, disfigured, extra limbs, mutated, deformed, long neck (worst quality, low quality, normal quality:2)",
                "num_inference_steps": 50,
                "num_images": 1,
                "image_format": "jpeg",
            }
        ),
    )
    return response.json()["images"][0]["url"]


def generate_image_tags(image_urls):
    image_tags = []
    for index, image in enumerate(image_urls):
        image_tags.append(
            f'<div id="{image["endpoint"]}§{index}" style="display: flex; flex-direction: column; width: 30%"><img src="{image["url"]}" /><p>{image["endpoint"]}</p><button type="submit" hx-post="/{image["endpoint"]}§{index}" hx-target="#{image["endpoint"]}§{index}"><svg  xmlns="http://www.w3.org/2000/svg"  width="24"  height="24"  viewBox="0 0 24 24"  fill="none"  stroke="#0ea5e9"  stroke-width="2"  stroke-linecap="round"  stroke-linejoin="round"  class="icon icon-tabler icons-tabler-outline icon-tabler-reload"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M19.933 13.041a8 8 0 1 1 -9.925 -8.788c3.899 -1 7.935 1.007 9.425 4.747" /><path d="M20 4v5h-5" /></svg></button></div>'
        )
    return "".join(image_tags)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        form_data = request.form.to_dict()
        base_prompt = generate_base_prompt(form_data)
        prompt = translate_prompt(base_prompt)
        image_urls = [
            {"url": generate_image_url(prompt, "fooocus"), "endpoint": "fooocus"},
            {"url": generate_image_url(prompt, "fooocus"), "endpoint": "fooocus"},
            {"url": generate_image_url(prompt, "fast-sdxl"), "endpoint": "fast-sdxl"},
        ]
        return (
            '<div style="display: flex; width: 100%; justify-content: space-between">'
            + generate_image_tags(image_urls)
            + "</div>"
        )
    return render_template("form.html")


@app.route("/<id>", methods=["POST"])
def generate(id):
    form_data = request.form.to_dict()
    endpoint, index = id.split("§")
    base_prompt = generate_base_prompt(form_data)
    prompt = translate_prompt(base_prompt)
    image_url = generate_image_url(prompt, endpoint)
    return f'<div id="{endpoint}§{index}" style="display: flex; flex-direction: column; width: 100%"><img src="{image_url}" /><p>{endpoint}</p><button type="submit" hx-post="/{endpoint}§{index}" hx-target="#{endpoint}§{index}"><svg  xmlns="http://www.w3.org/2000/svg"  width="24"  height="24"  viewBox="0 0 24 24"  fill="none"  stroke="#0ea5e9"  stroke-width="2"  stroke-linecap="round"  stroke-linejoin="round"  class="icon icon-tabler icons-tabler-outline icon-tabler-reload"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M19.933 13.041a8 8 0 1 1 -9.925 -8.788c3.899 -1 7.935 1.007 9.425 4.747" /><path d="M20 4v5h-5" /></svg></button></div>'


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
