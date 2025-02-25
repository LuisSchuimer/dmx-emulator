from typing import (
    Tuple,
    Literal
)
from dmx_emulator.logger import log
from uuid import uuid4
import socket
from dmx_emulator.exceptions import *

class Channel:
    class COLOR:
        def __init__(self, color: Literal["R", "G", "B"]):
            self.name = color
            self.max_value = 255
            self.min_value = 0
            self.value = self.min_value

    class BRIGHTNESS:
        def __init__(self):
            self.name = "BR"
            self.max_value = 255
            self.min_value = 0
            self.value = self.min_value

class Base:
    class COLOR:
        def __init__(self, color: Literal["R", "G", "B"], value: int):
            self.type = color
            self.value = value
    
    class BRIGHTNESS:
        def __init__(self, value: int):
            self.type = "BR"
            self.value = value

class Light_Config:
    def __init__(
            self, 
            channels: Tuple[int, int],
            type: str,
            channel_config: dict[int, Channel],
            base_values: list[Base] = []
        ) -> None:
        self.channels = channels
        self.type = type
        self.base_values = base_values
        self.channel_config = channel_config


class Defaults:
    def _check_if_valid(self, channel_start: int, channel_end: int):
        if channel_start > 512 or channel_end > 512: raise ChannelTooBig()
        if channel_start < 0 or channel_end <0: raise ChannelTooSmall()

    def rgb_light(self, channel_start: int, channel_end):
        self._check_if_valid(channel_start=channel_start, channel_end=channel_end)
        return Light_Config(
            channels=(channel_start, channel_end),
            type="RGB Light",
            base_values=[],
            channel_config={
                0: Channel.COLOR("R"),
                1: Channel.COLOR("G"),
                2: Channel.COLOR("B"),
                3: Channel.BRIGHTNESS()
            }
        )

    def white_light(self, channel_start: int):
        self._check_if_valid(channel_start=channel_start, channel_end=channel_start)
        return Light_Config(
            channels=(channel_start, channel_start),
            type= "White Light",
            base_values=[
                Base.COLOR(color="R", value=255),
                Base.COLOR(color="G", value=255),
                Base.COLOR(color="B", value=255)
            ],
            channel_config= {
                0: Channel.BRIGHTNESS()
            } 
        )
    
class Light:
    def __init__(self, config: Light_Config, name: str = "DMX Light"):
        self.name = name
        self.id = str(uuid4())
        self.config = config

class Emulator_Config:
    def __init__(self):
        self.lights: list = []
    
    def add_light(self, light: Light):
        self.lights.append(light)


class Emulator:
    def __init__(self, config, render_server: Tuple[str, int], development_mode: bool = False):
        self.config = config
        self.development_mode = development_mode
        self.render_server = render_server
        self.connection = None  # Persistent socket connection
        self.sleep_time = 0.005
        self.started = False

    def _establish_connection(self):
        if not self.connection:
            try:
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection.connect(self.render_server)
            except socket.error as e:
                log.error(f"Failed to establish connection to the push-server {self.render_server}")
                self.connection = None

    def _close_connection(self):
        if self.connection:
            try:
                self.connection.close()
            except socket.error as e:
                pass #! Implement exception 
            finally:
                self.connection = None

    def _send_data(self, data):
        if not self.connection:
            self._establish_connection()
        if self.connection:
            try:
                self.connection.sendall(bytes(f"{str(data)}\n", "utf-8"))
            except socket.error as e:
                #! Implement Exception
                self._close_connection()

    def _get_channel_values(self, light):
        values = {"r": 0, "g": 0, "b": 0, "br": 0}
        for channel in light.config.channel_config.values():
            match channel.name:
                case "R": values["r"] = int(channel.value)
                case "G": values["g"] = int(channel.value)
                case "B": values["b"] = int(channel.value)
                case "BR": values["br"] = float(channel.value / 255)

        for base_value in light.config.base_values:
            match base_value.type:
                case "R": values["r"] = int(base_value.value)
                case "G": values["g"] = int(base_value.value)
                case "B": values["b"] = int(base_value.value)
                case "BR": values["br"] = float(base_value.value / 255)
        return values

    def set_channel(self, CHANNEL: int, VALUE: int):
        if VALUE > 255:
            raise ValueTooBig(value=VALUE)
        for light in self.config.lights:
            for channel in range(light.config.channels[0], light.config.channels[1] + 1):
                if channel == CHANNEL:
                    light.config.channel_config[channel - light.config.channels[0]].value = VALUE
                    if self.started:
                        values = self._get_channel_values(light)
                        data = {
                            "name": str(light.name),
                            "id": str(light.id),
                            "r": int(values["r"]),
                            "g": int(values["g"]),
                            "b": int(values["b"]),
                            "br": float(values["br"]),
                        }
                        self._send_data(data)

    def set_channels(self, CHANGES: list[tuple]):
        for change in CHANGES:
            if change[1] > 255:
                raise ValueTooBig(value=change[1])
            for light in self.config.lights:
                for channel in range(light.config.channels[0], light.config.channels[1] + 1):
                    if channel == change[0]:
                        light.config.channel_config[channel - light.config.channels[0]].value = change[1]
                        if self.started:
                            values = self._get_channel_values(light)
                            data = {
                                "name": str(light.name),
                                "id": str(light.id),
                                "r": int(values["r"]),
                                "g": int(values["g"]),
                                "b": int(values["b"]),
                                "br": float(values["br"]),
                            }
                            self._send_data(data)

    def start_render(self):
        self.started = True
        self._establish_connection()
        clear_data = {"clear": 1}
        self._send_data(clear_data)

        for light in self.config.lights:
            values = self._get_channel_values(light)
            data = {
                "name": str(light.name),
                "id": str(light.id),
                "r": int(values["r"]),
                "g": int(values["g"]),
                "b": int(values["b"]),
                "br": float(values["br"]),
            }
            self._send_data(data)

    def stop_render(self):
        self._close_connection()
        self.started = False

