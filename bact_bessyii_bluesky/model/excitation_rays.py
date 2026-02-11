from dataclasses import dataclass
from typing import Sequence


@dataclass
class Excitation:
    horizontal: float
    vertical: float


@dataclass
class ExcitationRay:
    ray: Sequence[Excitation]


@dataclass
class ExcitationCollection:
    col: Sequence[ExcitationRay]
