# measurement_config.py
from dataclasses import dataclass, field
from array import array
from datetime import datetime

from typing import List

@dataclass()
class MeasurementConfig:
    prefix: str
    currents: List[int]
    catalog_name: str
    machine_name: str
    measurement_name: str
    uids: List[str]
    timestamp: str = field(default_factory=lambda: str(datetime.now()))
