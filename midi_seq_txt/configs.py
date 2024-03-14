from attrs import define


@define
class ExternalConfig:
    tempo_init: int


@define
class InternalConfig:
    sleep: float = 0.01
