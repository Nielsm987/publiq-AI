from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import requests
import json
from datetime import datetime

load_dotenv()
import os

app = Flask(__name__)


def is_winter(date_str):
    date = datetime.strptime(date_str, "%b %d, %Y")
    return date.month in [12, 1, 2]


def is_summer(date_str):
    date = datetime.strptime(date_str, "%b %d, %Y")
    return date.month in [6, 7, 8]


def is_autumn(date_str):
    date = datetime.strptime(date_str, "%b %d, %Y")
    return date.month in [9, 10, 11]


def is_spring(date_str):
    date = datetime.strptime(date_str, "%b %d, %Y")
    return date.month in [3, 4, 5]


def generate_image(description):

    try:
        response = requests.post(
            url="https://fal.run/fal-ai/fast-sdxl",
            headers={
                "Authorization": f'Key {os.getenv("FAL_ID_SECRET")}',
                "Content-Type": "application/json",
            },
            data=json.dumps(
                {
                    "prompt": description,
                    "negative_prompt": "cartoon, painting, illustration, (worst quality, low quality, normal quality:2)",
                    "num_inference_steps": 50,
                    "num_images": 3,
                    "image_format": "jpeg",
                }
            ),
        )
        print(response.json())
        return response.json()
    except requests.exceptions.RequestException:
        print("HTTP Request failed")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        form_data = request.form
        data = {}
        for key, value in form_data.items():
            data[key] = value

        prompt = f"Genereer een fotorealistische afbeelding met respect voor lichaamsverhoudingen voor een evenement met als titel '{data['naam-evenement']}'"
        prompt += (
            f" het evenement kan als volgt beschreven worden '{data['beschrijving']}'"
        )
        prompt += f" op de afbeeldingen moeten personen van de leeftijdscategorie '{data['geschikt-voor']}' te zien zijn met een gemengde etnische afkomst"
        prompt += f" op de afbeeldingen moet je zien dat het {'winter' if is_winter(data['begindatum']) else 'zomer' if is_summer(data['begindatum']) else 'herfst' if is_autumn(data['begindatum']) else 'lente'} is"

        print(prompt)

        # Generate images based on the constructed prompt
        images = generate_image(prompt)["images"]
        image_tags = []
        for image in images:
            image_url = image["url"]
            image_tags.append('<img style="width: 30%" src="' + image_url + '" />')
        joined_image_tags = "".join(image_tags)

        print(joined_image_tags)
        return (
            '<div style="display: flex; width: 100%; justify-content: space-between">'
            + joined_image_tags
            + "</div>"
        )

    return render_template("form.html")


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
