"""Copyright 2019 Anton Kachurin

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import time
from contextlib import AbstractContextManager
from typing import Optional


class Timer(AbstractContextManager):
    """Context-measuring timer"""

    start_time: Optional[float]
    end_time: Optional[float]

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.monotonic()
        return self

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
