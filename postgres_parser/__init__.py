# Copyright 2021 Diego Argueta
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ._c_wrapper import fingerprint
from ._c_wrapper import parse
from ._c_wrapper import parse_protobuf
from ._c_wrapper import parse_json
from ._c_wrapper import parse_to_protobuf_bytes
from ._version import __version__
from ._version import __version_info__
from ._version import PG_MAJORVERSION
from ._version import PG_VERSION
from ._version import PG_VERSION_NUM
from .errors import Error
from .errors import ParseError


__all__ = [
    "fingerprint",
    "parse",
    "parse_json",
    "parse_protobuf",
    "parse_to_protobuf_bytes",
    "Error",
    "ParseError",
]
