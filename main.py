from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import requests
import json

load_dotenv()
import os

app = Flask(__name__)


def generate_image(description):

    try:
        response = requests.post(
            url="https://fal.run/fal-ai/fast-sdxl",
            headers={
                "Authorization": f'Key {os.getenv("FAL_ID_SECRET")}',
                "Content-Type": "application/json",
            },
            data=json.dumps({"prompt": description, "num_images": 3}),
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
        images = generate_image(data["beschrijving"])["images"]
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
