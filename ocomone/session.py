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
