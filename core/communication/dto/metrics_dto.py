from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class MetricsValue:
    value: float
    value_name: str


@dataclass
class MetricsDto:
    name: str
    timestamp: datetime
    step: int
    step_type: str
    phase: Literal["train", "val"]
    values: list[MetricsValue]

    def __post_init__(self):
        # Deserializa los dicts a MetricsValue automáticamente
        self.values = [
            MetricsValue(**v) if isinstance(v, dict) else v
            for v in self.values
        ]
