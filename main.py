from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get form data
        form_data = request.form
        # Convert form data to JSON
        data = {}
        for key, value in form_data.items():
            data[key] = value
        # Return JSON response
        print(data)
        return jsonify(data)
    # Render form template for GET requests
    return render_template("form.html")


if __name__ == "__main__":
    app.run(debug=True)
