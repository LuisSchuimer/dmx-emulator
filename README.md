# DMX Emulator Documentation

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Running the Scripts](#running-the-scripts)
    - [Running the Renderer Server (Web Server & Push Server)](#running-the-renderer-server-web-server--push-server)
    - [Running the DMX Emulator](#running-the-dmx-emulator)
    - [Running the Test Script](#running-the-test-script)
4. [File Structure](#file-structure)
5. [Usage](#usage)
    - [Emulator](#emulator)
    - [Renderer](#renderer)
    - [Testing](#testing)
6. [Dependencies](#dependencies)
7. [Conclusion](#conclusion)

---

## Overview
The DMX Emulator package simulates and controls DMX lights using a server-client architecture. The main components include:
- **Emulator**: Simulates the lights and sends data to the renderer.
- **Renderer**: A Flask web server that visualizes the light data in real time.
- **Communication**: The server and renderer communicate through socket connections.

The renderer is accessible through a web interface where you can visualize and interact with the lights.

---

## Installation

To set up the DMX Emulator package, use **`rye`** for managing dependencies and running the scripts.

1. **Install `rye`**:
   - If `rye` isn't already installed, use the following command:

     ```bash
     pip install rye
     ```

2. **Set up dependencies**:
   - In your project directory, run the following command to install all required dependencies:

     ```bash
     rye sync
     ```

---

## Running the Scripts

### Running the Renderer Server (Web Server & Push Server)
To start the renderer (which sets up the web server and the push server), use the following command:

```bash
rye run python -m dmx_emulator.renderer
```

This will start:
- The **Flask web server** on `localhost:1234`
- The **Push server** on `localhost:8001`

Open your web browser and navigate to `http://localhost:1234` to access the light control interface.

### Running the DMX Emulator
The DMX Emulator is imported as a package and doesn't need to be run directly. Instead, you will use it in your project (e.g., via `test.py` or other integration scripts).

### Running the Test Script
To test the interaction between the emulator and the renderer, run the provided `test.py` script:

```bash
python test.py
```

This will simulate light updates and send them to the renderer in real-time.

---

## File Structure

- **`emulator.py`**: Core functionality for controlling DMX lights, managing light and channel configurations, and socket communication with the renderer.
- **`renderer.py`**: Implements the Flask web server that handles client connections and visualizes the light data.
- **`test.py`**: A script for testing the functionality of the emulator by simulating light updates.

---

## Usage

### Emulator
The `Emulator` class allows you to create and control a set of lights using a configuration object.

#### Key Classes and Functions

- **Channel**: Represents a channel for controlling a light's attribute (e.g., color or brightness).
  - `Channel.COLOR`: Represents a color channel (Red, Green, Blue).
  - `Channel.BRIGHTNESS`: Represents a brightness channel.

- **Light_Config**: Defines the configuration for a light, including its channel mappings and base values (e.g., default brightness levels).

- **Emulator_Config**: Manages the configuration for multiple lights.

- **Emulator**: The main class for interacting with the lights, sending data to the renderer, and managing socket connections.
  - `add_light(light: Light)`: Adds a new light to the emulator.
  - `start_render()`: Starts the rendering process and establishes a socket connection to the renderer.
  - `stop_render()`: Stops the rendering process and closes the connection.
  - `set_channel(channel: int, value: int)`: Sets the value of a specific channel.
  - `set_channels(changes: list[tuple])`: Sets multiple channels at once.

#### Example Usage

```python
from dmx_emulator.emulator import Emulator_Config, Light_Config, Light, Defaults, Emulator, Base, Channel

# Setup Emulator Configuration
config = Emulator_Config()
defaults = Defaults()

config.add_light(Light(config=defaults.rgb_light(channel_start=0, channel_end=3), name="Light1"))
config.add_light(Light(config=defaults.rgb_light(channel_start=4, channel_end=7), name="Light2"))

# Create custom light
config.add_light(Light(config=Light_Config(
    channels=(8, 8),
    type="My Light",
    base_values=[Base.COLOR("R", 255)],
    channel_config={0: Channel.BRIGHTNESS()}
), name="A light"))

# Initialize Emulator
emulator = Emulator(config, render_server=("127.0.0.1", 8001), development_mode=False)
emulator.start_render()

# Set channels
emulator.set_channel(0, 255)
emulator.set_channel(1, 150)
emulator.set_channel(4, 255)

# Continuously update light channels
while True:
    for i in range(0, 256):
        emulator.set_channels([(1, i), (5, i), (2, i), (8, i)])
```

### Renderer
The `renderer.py` script creates a Flask web server that serves a real-time light control interface.

#### Key Components

- **Flask Web Server**:
  - `main()`: Renders the main HTML page.
  - `listen()`: Streams the light data to clients via Server-Sent Events (SSE).

- **Socket Communication**:
  - `push_server()`: A continuous socket connection that listens for incoming light data from the emulator.

#### Running the Renderer
The web server runs on `localhost:1234`, and the push server listens on `localhost:8001`. When the emulator sends light data, it is displayed and updated in the web interface.

```python
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.create_task(push_server(host="localhost", port=8001))

    from threading import Thread
    flask_thread = Thread(target=run_flask, daemon=True, args=("localhost", 1234,))
    flask_thread.start()

    loop.run_forever()
```

### Testing
The `test.py` file demonstrates how to interact with the emulator by creating lights and sending data to the renderer.

---

## Dependencies

- **`flask`**: Web framework used to serve the light control interface.
- **`waitress`**: WSGI server used to run the Flask application.
- **`rye`**: Dependency manager for handling the installation of packages.

---

## Conclusion

This package provides a robust way to emulate and control DMX lights via a server-client architecture. The integration of Flask for visualization and WebSockets for real-time updates offers an intuitive way to control and monitor lighting setups.
