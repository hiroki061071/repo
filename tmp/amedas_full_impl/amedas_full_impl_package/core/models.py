from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

@dataclass
class Event:
    start: pd.Timestamp
    end: pd.Timestamp
    days: int
    hours: int
