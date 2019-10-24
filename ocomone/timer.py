import time
from typing import Optional


class Timer:
    """Context-measuring timer"""

    start_time: Optional[float]
    end_time: Optional[float]

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.monotonic()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.monotonic()

    @property
    def elapsed_ms(self):
        e_time = self.end_time or time.monotonic()
        return round((e_time - self.start_time) * 1000)

    @property
    def elapsed(self):
        e_time = self.end_time or time.monotonic()
        return round(e_time - self.start_time)
