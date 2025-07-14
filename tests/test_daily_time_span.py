# tests/test_daily_time_span.py
# Dies ist ein einfacher Test für die Zeitlogik.

from datetime import time
import pytest
from src.daily_time_span import DailyTimeSpan

def test_check_time_normal_span():
    """Testet einen normalen Zeitbereich innerhalb eines Tages."""
    span = DailyTimeSpan(H1=8, M1=0, H2=22, M2=0)
    
    # Zeiten, die innerhalb liegen sollten
    assert span.check_time(time(12, 30)) is True
    assert span.check_time(time(8, 0)) is True
    
    # Zeiten, die außerhalb liegen sollten
    assert span.check_time(time(7, 59)) is False
    assert span.check_time(time(22, 1)) is False

def test_check_time_midnight_span():
    """Testet einen Zeitbereich, der über Mitternacht geht."""
    span = DailyTimeSpan(H1=22, M1=0, H2=6, M2=0)
    
    # Zeiten, die innerhalb liegen sollten
    assert span.check_time(time(23, 30)) is True  # Abends
    assert span.check_time(time(0, 15)) is True   # Nach Mitternacht
    assert span.check_time(time(5, 59)) is True   # Morgens
    
    # Zeiten, die außerhalb liegen sollten
    assert span.check_time(time(21, 59)) is False
    assert span.check_time(time(6, 1)) is False
