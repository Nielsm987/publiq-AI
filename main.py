from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import requests
import json
from datetime import datetime
from deep_translator import GoogleTranslator


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


endpoints = [
    {
        "name": "fooocus",
        "url": "https://fal.run/fal-ai/fooocus",
    },
    {
        "name": "fast-sdxl",
        "url": "https://fal.run/fal-ai/fast-sdxl",
    },
]


def generate_image(description, endpoint):
    try:
        # get the endpoint url from endpoints based on the endpoint name
        endpoint_url = list(filter(lambda x: x["name"] == endpoint, endpoints))[0][
            "url"
        ]
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

        pre_prompt = "wide angle shot, daylight, warm-toned, 35mm, --ar 4:3, --s 250, natural lighting, realistic faces, realistic bodies, sharp focus, sport shooting, dynamic range, wide shot, "
        input_prompt = f"Evenement voor '{data['naam-evenement']}', evenementbeschrijving '{data['beschrijving']}' personen van leeftijdscategorie '{data['geschikt-voor']}', personen van diverse etnische afkomst, weersomstandigheden zijn volgens het seizoen {'winter' if get_season(data['begindatum']) == 'winter' else 'zomer' if get_season(data['begindatum']) == 'summer' else 'herfst' if get_season(data['begindatum']) == 'autumn' else 'lente'},"
        base_prompt = f"{pre_prompt}, {input_prompt}"
        prompt = GoogleTranslator(source="nl", target="en").translate(base_prompt)

        print(prompt)

        image_urls = []
        image_tags = []

        image_urls.append(
            {
                "url": generate_image(prompt, "fooocus")["images"][0]["url"],
                "endpoint": "fooocus",
            }
        )
        image_urls.append(
            {
                "url": generate_image(prompt, "fooocus")["images"][0]["url"],
                "endpoint": "fooocus",
            }
        )
        image_urls.append(
            {
                "url": generate_image(prompt, "fast-sdxl")["images"][0]["url"],
                "endpoint": "fast-sdxl",
            }
        )

        # Generate images from different endpoints

        for index, image in enumerate(image_urls):
            image_tags.append(
                f'<div id="{image["endpoint"]}§{index}" style="display: flex; flex-direction: column; width: 30%"><img src="{image["url"]}" /><p>{image["endpoint"]}</p><button type="submit" hx-post="/{image["endpoint"]}§{index}" hx-target="#{image["endpoint"]}§{index}"><svg  xmlns="http://www.w3.org/2000/svg"  width="24"  height="24"  viewBox="0 0 24 24"  fill="none"  stroke="#0ea5e9"  stroke-width="2"  stroke-linecap="round"  stroke-linejoin="round"  class="icon icon-tabler icons-tabler-outline icon-tabler-reload"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M19.933 13.041a8 8 0 1 1 -9.925 -8.788c3.899 -1 7.935 1.007 9.425 4.747" /><path d="M20 4v5h-5" /></svg></button></div>'
            )

        joined_image_tags = "".join(image_tags)

        return (
            '<div style="display: flex; width: 100%; justify-content: space-between">'
            + joined_image_tags
            + "</div>"
        )

    return render_template("form.html")


@app.route("/<id>", methods=["POST"])
def generate(id):
    form_data = request.form
    endpoint = id.split("§")[0]
    index = id.split("§")[1]

    data = {}
    for key, value in form_data.items():
        data[key] = value

    pre_prompt = "wide angle shot, daylight, warm-toned, 35mm, --ar 4:3, --s 250, natural lighting, realistic faces, realistic bodies, sharp focus, sport shooting, dynamic range, wide shot, "
    input_prompt = f"Evenement voor '{data['naam-evenement']}', evenementbeschrijving '{data['beschrijving']}' personen van leeftijdscategorie '{data['geschikt-voor']}', personen van diverse etnische afkomst, weersomstandigheden zijn volgens het seizoen {'winter' if get_season(data['begindatum']) == 'winter' else 'zomer' if get_season(data['begindatum']) == 'summer' else 'herfst' if get_season(data['begindatum']) == 'autumn' else 'lente'},"
    base_prompt = f"{pre_prompt}, {input_prompt}"
    prompt = GoogleTranslator(source="nl", target="en").translate(base_prompt)

    print(endpoint)
    image = {
        "url": generate_image(prompt, endpoint)["images"][0]["url"],
        "endpoint": endpoint,
    }

    return f'<div id="{image["endpoint"]}§{index}" style="display: flex; flex-direction: column; width: 100%"><img src="{image["url"]}" /><p>{image["endpoint"]}</p><button type="submit" hx-post="/{image["endpoint"]}§{index}" hx-target="#{image["endpoint"]}§{index}"><svg  xmlns="http://www.w3.org/2000/svg"  width="24"  height="24"  viewBox="0 0 24 24"  fill="none"  stroke="#0ea5e9"  stroke-width="2"  stroke-linecap="round"  stroke-linejoin="round"  class="icon icon-tabler icons-tabler-outline icon-tabler-reload"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M19.933 13.041a8 8 0 1 1 -9.925 -8.788c3.899 -1 7.935 1.007 9.425 4.747" /><path d="M20 4v5h-5" /></svg></button></div>'


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
