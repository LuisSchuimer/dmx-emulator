from flask import (
    Flask, 
    render_template, 
    request,
    Response
)
from http import HTTPStatus
import json
from time import sleep

app = Flask(__name__)

lights = {}


import json

def _format_sse(data, event=None) -> str:
    """
    Formats data as a valid SSE message with properly serialized JSON.
    """
    if isinstance(data, dict):
        data = json.dumps(data)  # Serialize to proper JSON format
    elif not isinstance(data, str):
        raise ValueError("Data must be a dictionary or string")

    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg


@app.route("/")
def main():
    return render_template("index.html")

@app.route('/listen', methods=['GET'])
def listen():
    def stream():
        last_send = ""
        while True:
            serialized_data = json.dumps(lights)  # Serialize as proper JSON
            if serialized_data != last_send:
                last_send = serialized_data
                yield _format_sse(data=serialized_data)
            sleep(0.20)

    return Response(stream(), mimetype='text/event-stream')

@app.route("/add_light", methods=["POST"])
def add():
    lights[request.form.get("name")] = {
        "r": request.form.get("r", type=int),
        "g": request.form.get("g", type=int),
        "b": request.form.get("b", type=int),
        "br": request.form.get("br", type=float)
    }

    return "", HTTPStatus.OK

@app.route("/clear", methods=["POST"])
def clear(): lights.clear(); return "", HTTPStatus.OK

@app.route("/update_light", methods=["POST"])
def update_light():
    name = request.form.get("name", type=str)
    r = request.form.get("r", type=int)
    g = request.form.get("g", type=int)
    b = request.form.get("b", type=int)
    br = request.form.get("br", type=float)

    if r is not None:
        lights[name]["r"] = r
    if g is not None:
        lights[name]["g"] = g
    if b is not None:
        lights[name]["b"] = b
    if br is not None:
        lights[name]["br"] = br
    
    return "", HTTPStatus.OK


app.run(debug=True, host="0.0.0.0", port=1234)