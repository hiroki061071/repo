from __future__ import annotations
from core.errors import ValidationError

def validate_station_selected(station_name: str) -> None:
    if not station_name or not str(station_name).strip():
        raise ValidationError("地点が選択されていません。")

def validate_date_range(start_date, end_date) -> None:
    if start_date > end_date:
        raise ValidationError("開始日が終了日より後になっています。")
