from dmx_emulator.emulator import (
    config,
    light,
    defaults,
    emulator
)
import time

config = config()
defaults = defaults()

config.add_light(light(config=defaults.rgb_light(channel_start=0, channel_end=3), name="Light1"))
config.add_light(light(config=defaults.rgb_light(channel_start=4, channel_end=7), name="Light2"))
config.add_light(light(config=defaults.rgb_light(channel_start=4, channel_end=7), name="Light"))


emulator = emulator(config, render_server="http://127.0.0.1:8000")

emulator.start_render()

emulator.set_channel(3, 255)
emulator.set_channel(6, 255)

for i in range(0, 256): emulator.set_channels([(1, i), (5, i), (2, i)])


