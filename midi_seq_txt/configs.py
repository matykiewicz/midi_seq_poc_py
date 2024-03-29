from attrs import define


@define
class InitConfig:
    sleep: float = 0.0001
    init_tempo: int = 60
    n_steps: int = 16
    n_parts: int = 16
    octaves: int = 5
    n_motions: int = 21
    tempo_step: int = 10
    tempo_min: int = 5
    tempo_max: int = 20
    n_keys: int = 8
    n_channels: int = 1
    n_buttons: int = 8
    midi_workers: int = 10
    init_time: float = 2.0
    n_quants: int = 4
    velocity_min: int = 0
    velocity_step: int = 20
    velocity_max: int = 6
    init_scale: str = "C"
