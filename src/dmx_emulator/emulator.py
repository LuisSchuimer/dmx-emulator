import requests
from typing import Tuple
from time import sleep
from dmx_emulator.exceptions import *

class channel:
    class COLOR:
        def __init__(self, color: str):
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

class base:
    class COLOR:
        def __init__(self, color: str, value):
            self.type = color
            self.value = value
    
    class BRIGHTNESS:
        def __init__(self, value):
            self.type = "BR"
            self.value = value

class light_config:
    def __init__(
            self, 
            channels: Tuple[int, int],
            type: str,
            channel_config: dict[int, channel],
            base_values: list[base] = []
        ) -> None:
        self.channels = channels
        self.type = type
        self.base_values = base_values
        self.channel_config = channel_config


class defaults:
    def _check_if_valid(self, channel_start: int, channel_end: int):
        if channel_start > 512 or channel_end > 512: raise ChannelTooBig()
        if channel_start < 0 or channel_end <0: raise ChannelTooSmall()

    def rgb_light(self, channel_start: int, channel_end):
        self._check_if_valid(channel_start=channel_start, channel_end=channel_end)
        return light_config(
            channels=(channel_start, channel_end),
            type="RGB Light",
            base_values=[],
            channel_config={
                0: channel.COLOR("R"),
                1: channel.COLOR("G"),
                2: channel.COLOR("B"),
                3: channel.BRIGHTNESS()
            }
        )

    def white_light(self, channel_start: int):
        self._check_if_valid(channel_start=channel_start, channel_end=channel_start)
        return light_config(
            channels=(channel_start, channel_start),
            type= "White Light",
            base_values=[
                base.COLOR(color="R", value=255),
                base.COLOR(color="G", value=255),
                base.COLOR(color="B", value=255)
            ],
            channel_config= {
                0: channel.BRIGHTNESS()
            } 
        )
    
class light:
    def __init__(self, config: light_config, name: str = "DMX Light"):
        self.name = name
        self.config = config

class emulator_config:
    def __init__(self):
        self.lights: list = []
    
    def add_light(self, light: light):
        self.lights.append(light)

class emulator:
    def __init__(self, config: emulator_config, render_server: str = None, development_mode: bool = False):
        self.config = config
        self.development_mode = development_mode
        self.render_server = render_server
        self.sleep_time = 0.005
        self.started = False

    def _get_channel_values(self, light: light) -> dict:
        values: dict = {"r": 0, "g": 0, "b": 0, "br": 0}
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


    def set_channel(self, CHANNEL: int, VALUE: int) -> None:
        if VALUE > 255: raise ValueTooBig(value=VALUE)
        for light in self.config.lights:
            for channel in range(light.config.channels[0], light.config.channels[1]+1): 
                if channel == CHANNEL: 
                    light.config.channel_config[channel - light.config.channels[0]].value = VALUE
                    if self.started and self.render_server:
                        values = self._get_channel_values(light=light)
                        try:
                            requests.post(
                                f"{self.render_server}/update_light",
                                    data={
                                        "name": str(light.name),
                                        "r": int(values["r"]),
                                        "g": int(values["g"]),
                                        "b": int(values["b"]),
                                        "br": float(values["br"])
                                    }
                                )
                            sleep(self.sleep_time)
                        except Exception as exception: 
                            if not self.development_mode and exception == requests.exceptions.ConnectionError: raise RenderServerUnreachable(self.render_server)
                            else: raise exception
    
    
    def set_channels(self, CHANGES: list[tuple]) :
        for change in CHANGES:
            if change[1] > 255: raise ValueTooBig(value=change[1])
            for light in self.config.lights:
                for channel in range(light.config.channels[0], light.config.channels[1]+1):
                    if channel == change[0]: 
                        light.config.channel_config[channel - light.config.channels[0]].value = change[1]
                        if self.started and self.render_server:
                            values = self._get_channel_values(light=light)
                            try:
                                requests.post(f"{self.render_server}/update_light",
                                    data={
                                        "name": str(light.name),
                                        "r": int(values["r"]),
                                        "g": int(values["g"]),
                                        "b": int(values["b"]),
                                        "br": float(values["br"])
                                    }
                                )
                                sleep(self.sleep_time)
                            except Exception as exception: 
                                if not self.development_mode and exception == requests.exceptions.ConnectionError: raise RenderServerUnreachable(self.render_server)
                                else: raise exception

    
    def start_render(self):
        self.started = True
        try: requests.post(f"{self.render_server}/clear") 
        except Exception as exception: 
            if not self.development_mode and exception == requests.exceptions.ConnectionError: raise RenderServerUnreachable(self.render_server)
            else: raise exception

        for light in self.config.lights:
            if self.render_server:
                values = self._get_channel_values(light=light)
                try:
                    requests.post(
                        f"{self.render_server}/add_light",
                        data={
                            "name": str(light.name), 
                            "r": int(values["r"]), 
                            "g": int(values["g"]), 
                            "b": int(values["b"]), 
                            "br": float(values["br"])
                        }
                    )
                    sleep(self.sleep_time)
                except Exception as exception: 
                    if not self.development_mode and exception == requests.exceptions.ConnectionError: raise RenderServerUnreachable(self.render_server)
                    else: raise exception
                
