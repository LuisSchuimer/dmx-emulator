from flask import (
    Flask, 
    render_template, 
    request
)
from http import HTTPStatus

app = Flask(__name__)

lights = {}

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/update")
def update():
    return render_template(
        "components/lights.html",
        lights=lights
    )

@app.route("/add_light", methods=["POST"])
def add():
    lights[request.form.get("name")] = {
        "r": request.form.get("r", type=int),
        "g": request.form.get("g", type=int),
        "b": request.form.get("b", type=int),
        "br": request.form.get("br", type=int)
    }

    return "", HTTPStatus.OK

@app.route("/clear", methods=["POST"])
def clear(): lights.clear(); return "", HTTPStatus.OK

@app.route("/update_light", methods=["POST"])
def update_light():
    name = request.form.get("name", type=str)
    r = request.form.get("r", type=int); g = request.form.get("g", type=int); b = request.form.get("b", type=int)
    br = request.form.get("br", type=int)

    if r is not None:
        lights[name]["r"] = r
    if g is not None:
        lights[name]["g"] = g
    if b is not None:
        lights[name]["b"] = b
    if br is not None:
        lights[name]["br"] = br
    
    return "", HTTPStatus.OK


app.run(debug=True, host="0.0.0.0", port=8000)