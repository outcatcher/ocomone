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
import logging
import os

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class Resources:
    """Resource retrieval from dedicated resource directory.

    Example:
        ``resources = Resources(__file__)``

        ``resources["my_file.txt"]``

            will have return of:

        ``C:\\\\Path\\to\\python_file\\resources\\my_file.txt``
    """

    def __init__(self, content_root: str, resources_dir: str = "resources", create_resource_root=False):
        """Initialize resource retrieval, normally `content_root` should be `__file__`"""
        if os.path.isfile(content_root):
            content_root = os.path.dirname(content_root)
        self.resource_root = os.path.abspath(f"{content_root}/{resources_dir}")
        if create_resource_root and not os.path.exists(self.resource_root):
            LOGGER.warning("No resource root exists at %s, directory will be created", content_root)
            os.makedirs(self.resource_root, exist_ok=True)

    def __repr__(self):
        return f"{type(self).__name__} at {self.resource_root}"

    def __getitem__(self, resource_name):
        """Return path to resource by given name. If given path is absolute, return if without change"""
        if os.path.isabs(resource_name):
            return resource_name
        return os.path.abspath(f"{self.resource_root}/{resource_name}")
