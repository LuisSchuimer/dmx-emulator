from dmx_emulator.emulator import (
    emulator_config,
    light_config,
    light,
    defaults,
    emulator,
    base,
    channel
)

config = emulator_config()
defaults = defaults()

config.add_light(light(config=defaults.rgb_light(channel_start=0, channel_end=3), name="Light1"))
config.add_light(light(config=defaults.rgb_light(channel_start=4, channel_end=7), name="Light2"))
config.add_light(light(config=light_config(
    channels=(8, 8),
    type="My Light",
    base_values=[
        base.COLOR("R", 255) 
    ],
    channel_config={
        0: channel.BRIGHTNESS()
    }
), 
name="A light"))


emulator = emulator(config, render_server=("127.0.0.1", 8001), development_mode=False)
emulator.start_render()

emulator.set_channel(0, 255)
emulator.set_channel(1, 150)
emulator.set_channel(4, 255)
emulator.set_channel(5, 150)

while True:
    for i in range(0, 256): emulator.set_channels([(1, i), (5, i), (2, i)])



