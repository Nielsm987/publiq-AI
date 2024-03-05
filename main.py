from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import requests
import json
from datetime import datetime

load_dotenv()
import os

app = Flask(__name__)


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


def generate_image(description, endpoint_url):
    try:
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

        prompt = f"Genereer een fotorealistische afbeelding met respect voor lichaamsverhoudingen voor een evenement met als titel '{data['naam-evenement']}' het evenement kan als volgt beschreven worden '{data['beschrijving']}' op de afbeeldingen moeten personen van de leeftijdscategorie '{data['geschikt-voor']}' te zien zijn met een gemengde etnische afkomst op de afbeeldingen moet je zien dat het {'winter' if get_season(data['begindatum']) == 'winter' else 'zomer' if get_season(data['begindatum']) == 'summer' else 'herfst' if get_season(data['begindatum']) == 'autumn' else 'lente'} is"

        print(prompt)

        # Define your endpoint URLs
        endpoint_urls = [
            "https://fal.run/fal-ai/fooocus",
            "https://fal.run/fal-ai/fast-sdxl",
            "https://fal.run/fal-ai/fooocus",
        ]

        image_tags = []
        image_model = []

        # Generate images from different endpoints
        for endpoint_url in endpoint_urls:
            # get the endpoint name  and append it to the image_model list
            image_model.append(
                '<p style="width: 30%">' + endpoint_url.split("/")[-1] + "</p>"
            )
            images = generate_image(prompt, endpoint_url)["images"]
            for image in images:
                image_url = image["url"]
                image_tags.append('<img style="width: 30%" src="' + image_url + '" />')

        joined_image_tags = "".join(image_tags)
        joined_image_model = "".join(image_model)

        print(joined_image_tags)
        return (
            '<div style="display: flex; width: 100%; justify-content: space-between">'
            + joined_image_tags
            + "</div>"
            + '<div style="display: flex; width: 100%; justify-content: space-between">'
            + joined_image_model
            + "</div>"
        )

    return render_template("form.html")


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
