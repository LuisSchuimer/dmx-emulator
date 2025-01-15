from flask import Flask, render_template, Response
import asyncio
import json
import socket
from waitress import serve
from dmx_emulator.logger import log
import datetime

app = Flask(__name__)
lights = {"timestamp": ""}

async def push_server(host: str, port: int):
    async def handle_connection(client_socket: socket.socket):
        global lights
        """
        Handles a continuous connection with the client, receiving and processing messages.
        """
        try:
            while True:
                try:
                    data = str(client_socket.recv(1000).decode("utf-8")).replace("'", "\"").strip()
                    for op in data.split("\n"):
                        try: res = json.loads(op)
                        except: continue

                        # Process the received message
                        if res.get("clear") is None:
                            id = res["id"]
                            if lights.get(id) is not None:
                                lights[id]["name"] = str(res["name"]) 
                                lights[id]["r"] = int(res["r"])
                                lights[id]["g"] = int(res["g"])
                                lights[id]["b"] = int(res["b"])
                                lights[id]["br"] = float(res["br"])
                            else:
                                lights[id] = {
                                    "name": str(res["name"]),
                                    "r": int(res["r"]),
                                    "g": int(res["g"]),
                                    "b": int(res["b"]),
                                    "br": float(res["br"])
                                }
                        else:
                            if res["clear"]:
                                lights.clear()
                except Exception as e:
                    log.error(e)
        finally:
            # Ensure the connection is closed properly
            client_socket.close()

    # Set up the push server socket
    push_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    push_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    push_server.bind((host, port))
    push_server.listen(1)
    print(f"Push-server running ({host}:{port})")

    while True:
        # Accept a single connection
        client_socket, _ = push_server.accept()

        # Handle the connection in a blocking way
        await handle_connection(client_socket)


# SSE formatting helper
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
            lights["timestamp"] = ""
            serialized_data = json.dumps(lights)  # Serialize as proper JSON
            if serialized_data != last_send:
                last_send = serialized_data
                lights["timestamp"] = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f"))
                yield _format_sse(data=json.dumps(lights))

    return Response(stream(), mimetype='text/event-stream')

# Flask server runner using waitress
def run_flask(host: str, port: int):
    print(f"Web-Server serving on (https://{host}:{port})")
    serve(app, host=host, port=port)

# Main event loop
if __name__ == "__main__":
    push_server_host = ("127.0.0.1", 8001)
    web_server_host = ("127.0.0.1", 1234)
    # Explicitly create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)  # Set the event loop explicitly

    # Run push_server in the asyncio event loop
    loop.create_task(push_server(host=push_server_host[0], port=push_server_host[1]))

    # Run Flask with Waitress in a separate thread
    from threading import Thread
    flask_thread = Thread(target=run_flask, daemon=True, args=(web_server_host[0], web_server_host[1],))
    flask_thread.start()

    # Start the asyncio event loop
    loop.run_forever()
