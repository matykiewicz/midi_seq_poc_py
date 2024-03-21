from attrs import define


@define
class InitConfig:
    sleep: float = 0.01
    steps: int = 16
    parts: int = 16
    octaves: int = 2
    tempo_step: int = 10
    tempo_min: int = 5
    tempo_max: int = 20
    n_keys: int = 8
    n_channels: int = 1
