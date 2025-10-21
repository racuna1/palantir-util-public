__author__ = "Ruben Acuna"
__copyright__ = "Copyright 2025"

import random
from typing import Any


def sample_distribution(str_dist: list[tuple[float, Any]]) -> str:
    p, strings = zip(*str_dist)
    choice = random.choices(strings, p, k=1)[0]
    return choice