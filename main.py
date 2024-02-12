from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        form_data = request.form
        data = {}
        for key, value in form_data.items():
            data[key] = value
        print(data)
        return jsonify(data)
    return render_template("form.html")


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
