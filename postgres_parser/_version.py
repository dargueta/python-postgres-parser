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

from typing import NamedTuple
from typing import Optional

import pkg_resources as _pkgr

from ._exported_constants import PG_VERSION_NUM as PG_VERSION_NUM


class VersionInfo(NamedTuple):
    """Detailed information about the current version of the software."""

    major: int
    minor: int
    patch: int
    suffix: Optional[str]

    def __str__(self) -> str:
        return "%d.%d.%d%s" % (self.major, self.minor, self.patch, self.suffix or "")


def __to_version_info(v: str) -> VersionInfo:
    parts = _pkgr.parse_version(v)
    base = parts.base_version  # type: ignore[attr-defined]
    major, minor, *_possibly_patch = base.split(".")
    if _possibly_patch:
        patch = _possibly_patch[0]
    else:
        patch = "0"
    return VersionInfo(
        int(major),
        int(minor),
        int(patch),
        (parts.public[len(base) :].lstrip(".") or None),  # type: ignore[attr-defined]
    )


# Do not modify directly; use ``bumpversion`` command instead.
__version__ = "0.1.0"


# Don't touch these at all
__version_info__ = __to_version_info(__version__)

PG_VERSION = VersionInfo(
    major=PG_VERSION_NUM // 10000,
    minor=(PG_VERSION_NUM // 100) % 100,
    patch=PG_VERSION_NUM % 100,
    suffix=None,
)

PG_MAJORVERSION = PG_VERSION.major
