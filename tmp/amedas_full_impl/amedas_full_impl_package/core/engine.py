from __future__ import annotations
import pandas as pd
from core.constants import SUN_THRESHOLD
from core.models import Event

def extract_events(df: pd.DataFrame) -> list[Event]:
    if df.empty:
        return []

    work = df.sort_values("date").reset_index(drop=True).copy()
    events: list[Event] = []
    start = None
    prev = None
    count = 0

    for _, row in work.iterrows():
        sunshine = row["sunshine_hours"]
        current_date = row["date"]

        if pd.isna(sunshine):
            if start is not None:
                events.append(Event(start=start, end=prev, days=count, hours=count * 24))
                start = None
                prev = None
                count = 0
            continue

        if sunshine < SUN_THRESHOLD:
            if start is None:
                start = current_date
                prev = current_date
                count = 1
            else:
                if (current_date - prev).days == 1:
                    count += 1
                    prev = current_date
                else:
                    events.append(Event(start=start, end=prev, days=count, hours=count * 24))
                    start = current_date
                    prev = current_date
                    count = 1
        else:
            if start is not None:
                events.append(Event(start=start, end=prev, days=count, hours=count * 24))
                start = None
                prev = None
                count = 0

    if start is not None:
        events.append(Event(start=start, end=prev, days=count, hours=count * 24))
    return events
