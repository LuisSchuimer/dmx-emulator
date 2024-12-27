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
            self.color = color,
            self.value = value

class light_config:
    def __init__(
            self, 
            channels: Tuple[int, int],
            type: str,
            base_values: list,
            channel_config: dict
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
        self._check_if_valid(channel_start=channel_start)
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
    def __init__(self, config: emulator_config, render_server: str = None):
        self.config = config
        self.render_server = render_server
        self.sleep_time = 0.001
        self.started = False
    
    def set_channel(self, CHANNEL: int, VALUE: int):
        if VALUE > 255: raise ValueTooBig(value=VALUE)
        for light in self.config.lights:
            for channel in range(light.config.channels[0], light.config.channels[1]+1): 
                if channel == CHANNEL: 
                    light.config.channel_config[channel - light.config.channels[0]].value = VALUE
                    if self.started and self.render_server:
                        try:
                            requests.post(
                                f"{self.render_server}/update_light",
                                data={
                                        "name": str(light.name),
                                        "r": int(light.config.channel_config[0].value),
                                        "g": int(light.config.channel_config[1].value),
                                        "b": int(light.config.channel_config[2].value),
                                        "br": float(light.config.channel_config[3].value / 255)
                                    }
                                )
                            sleep(self.sleep_time)
                        except requests.exceptions.ConnectionError: raise RenderServerUnreachable(self.render_server)
    
    
    def set_channels(self, CHANGES: list[tuple]):
        for change in CHANGES:
            if change[1] > 255: raise ValueTooBig(value=change[1])
            for light in self.config.lights:
                for channel in range(light.config.channels[0], light.config.channels[1]+1):
                    if channel == change[0]: 
                        light.config.channel_config[channel - light.config.channels[0]].value = change[1]
                        if self.started and self.render_server:
                            try:
                                requests.post(
                                    f"{self.render_server}/update_light",
                                    data={
                                        "name": str(light.name),
                                        "r": int(light.config.channel_config[0].value),
                                        "g": int(light.config.channel_config[1].value),
                                        "b": int(light.config.channel_config[2].value),
                                        "br": float(light.config.channel_config[3].value / 255)
                                    }
                                )
                                sleep(self.sleep_time)
                            except requests.exceptions.ConnectionError: raise RenderServerUnreachable(self.render_server)

    
    def start_render(self):
        self.started = True
        try: requests.post(f"{self.render_server}/clear") 
        except requests.exceptions.ConnectionError: raise RenderServerUnreachable(self.render_server)
        for light in self.config.lights:
            if self.render_server:
                try:
                    requests.post(
                        f"{self.render_server}/add_light",
                        data={
                            "name": str(light.name),
                            "r": int(light.config.channel_config[0].value),
                            "g": int(light.config.channel_config[1].value),
                            "b": int(light.config.channel_config[2].value),
                            "br": float(light.config.channel_config[3].value / 255)
                        }
                    )
                    sleep(self.sleep_time)
                except requests.exceptions.ConnectionError: raise RenderServerUnreachable(self.render_server)
