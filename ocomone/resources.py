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

import os


class Resources:
    """Resource retrieval from dedicated resource directory.

    Example:
        ``resources = Resources(__file__)``

        ``resources["my_file.txt"]``

            will have return of:

        ``C:\\\\Path\\to\\python_file\\resources\\my_file.txt``
    """

    def __init__(self, content_root: str, resources_dir: str = "resources"):
        """Initialize resource retrieval, normally `content_root` should be `__file__`"""
        self.resource_root = os.path.abspath(f"{os.path.dirname(content_root)}/{resources_dir}")

    def __getitem__(self, resource_name):
        """Return path to resource by given name. If given path is absolute, return if without change"""
        if os.path.isabs(resource_name):
            return resource_name
        return os.path.abspath(f"{self.resource_root}/{resource_name}")
