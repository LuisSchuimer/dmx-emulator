import requests
from time import sleep

class channel:
    class COLOR:
        def __init__(self, color: str):
            self.name = color
            self.max_value = 255
            self.min_value = 0
            self.value = 0

    class BRIGHTNESS:
        def __init__(self):
            self.name = "BR"
            self.max_value = 255
            self.min_value = 0
            self.value = 0

class defaults:
    def rgb_light(self, channel_start: int, channel_end: int):
        if channel_start > 512 or channel_end > 512: raise Exception("Defined channel cannot be bigger than 512")
        if channel_start < 0 or channel_end < 0: raise Exception("Defined channel cannot be smaller than 0")
        if (channel_end - channel_start) < 2: raise Exception("RGB Light needs 4 Channels or more")

        return {
            "channels": (channel_start, channel_end),
            "is_rgb": True,
            "channel_config": {
                0: channel.COLOR("R"),
                1: channel.COLOR("G"),
                2: channel.COLOR("B"),
                3: channel.BRIGHTNESS()
            } 
        }

class light:
    def __init__(self, config: dict, name: str = "DMX Light"):
        self.name = name
        self.config = config

class config:
    def __init__(self):
        self.lights: list = []
    
    def add_light(self, light: light):
        self.lights.append(light)

class emulator:
    def __init__(self, config: config, render_server: str = None):
        self.config = config
        self.render_server = render_server
        self.sleep_time = 0.001
        self.started = False
    
    def set_channel(self, CHANNEL: int, VALUE: int):
        if VALUE > 255: raise Exception(f"Send value cannot be bigger than 255 (is {VALUE})")
        for light in self.config.lights:
            for channel in range(light.config["channels"][0], light.config["channels"][1]+1): 
                if channel == CHANNEL: 
                    light.config["channel_config"][channel - light.config["channels"][0]].value = VALUE
                    if self.started:
                        requests.post(
                            f"{self.render_server}/update_light",
                            data={
                                "name": light.name,
                                "r": light.config["channel_config"][0].value,
                                "g": light.config["channel_config"][1].value,
                                "b": light.config["channel_config"][2].value,
                                "br": light.config["channel_config"][3].value / 255
                            }
                        )
                        sleep(self.sleep_time)
    
    
    def set_channels(self, CHANGES: list[tuple]):
        for change in CHANGES:
            if change[1] > 255: raise Exception(f"Send value cannot be bigger than 255 (is {change[1]})")
            for light in self.config.lights:
                for channel in range(light.config["channels"][0], light.config["channels"][1]+1):
                    if channel == change[0]: 
                        light.config["channel_config"][channel - light.config["channels"][0]].value = change[1]
                        if self.started:
                            requests.post(
                                f"{self.render_server}/update_light",
                                data={
                                    "name": light.name,
                                    "r": light.config["channel_config"][0].value,
                                    "g": light.config["channel_config"][1].value,
                                    "b": light.config["channel_config"][2].value,
                                    "br": light.config["channel_config"][3].value / 255
                                }
                            )
                            sleep(self.sleep_time)

    
    def start_render(self):
        self.started = True
        requests.post(f"{self.render_server}/clear")
        for light in self.config.lights:
            requests.post(
                f"{self.render_server}/add",
                data={
                    "name": light.name,
                    "r": light.config["channel_config"][0].value,
                    "g": light.config["channel_config"][1].value,
                    "b": light.config["channel_config"][2].value,
                    "br": light.config["channel_config"][3].value / 255
                }
            )
            sleep(self.sleep_time)
