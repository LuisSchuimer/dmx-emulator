from dmx_emulator.emulator import (
    Emulator_Config,
    Light_Config,
    Light,
    Defaults,
    Emulator,
    Base,
    Channel
)

config = Emulator_Config()
defaults = Defaults()

config.add_light(Light(config=defaults.rgb_light(channel_start=0, channel_end=3), name="Light1"))
for n in range(2): config.add_light(Light(config=defaults.rgb_light(channel_start=4, channel_end=7), name=f"Light"))

config.add_light(Light(config=Light_Config(
    channels=(8, 8),
    type="My Light",
    base_values=[
        Base.COLOR("R", 255) 
    ],
    channel_config={
        0: Channel.BRIGHTNESS()
    }
), 
name="Light"))


emulator = Emulator(config, render_server=("127.0.0.1", 8001), development_mode=False)
emulator.start_render()

emulator.set_channel(0, 255)
emulator.set_channel(1, 150)
emulator.set_channel(4, 255)
emulator.set_channel(5, 150)

emulator.set_channel(3, 255)
emulator.set_channel(7, 255)

while True:
    for i in range(0, 256): emulator.set_channels([(1, i), (5, i), (2, i), (8, i)])



