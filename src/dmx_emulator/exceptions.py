class RenderServerUnreachable(Exception):
    def __init__(self, render_server: str): super().__init__(f"Render-Server ({render_server}) is offline or unreachable")

class ChannelTooBig(Exception):
    def __init__(self): super().__init__("Defined channel cannot be bigger than 512")

class ChannelTooSmall(Exception):
    def __init__(self): super().__init__("Defined channel cannot be smaller than 0")

class ValueTooBig(Exception):
    def __init__(self, value: int, max_value: int = 255): super().__init__(f"Send value cannot be bigger than {max_value} (is {value})")
    
class ValueTooSmall(Exception):
    def __init__(self, value: int, min_value: int = 0): super().__init__(f"Send value cannot be smaller than {min_value} (is {value})")