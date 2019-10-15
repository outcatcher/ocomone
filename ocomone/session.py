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
from requests import Session


class BaseUrlSession(Session):
    """Requests :class:`Session` with base url"""

    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url

    def request(self, method, url: str, *args, **kwargs):  # pylint: disable=arguments-differ
        """Send request with given base URL, see `Session.request` documentation for further details"""
        if "://" not in url:  # not an absolute URL with protocol defined
            if url.startswith("/"):
                url = url[1:]
            url = f"{self.base_url}/{url}"
        return super().request(method, url, *args, **kwargs)
