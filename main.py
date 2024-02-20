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
            data=json.dumps({"prompt": description}),
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
        image_url = generate_image(data["beschrijving"])["images"][0]["url"]
        return '<img src="' + image_url + '"/>'

    print()
    return render_template("form.html")


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
