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

import dataclasses
from typing import Optional


__all__ = [
    "Error",
    "ParseError",
]


class Error(Exception):
    """The base class for all errors thrown by this library."""

    # XXX It is too vague to throw this directly; any PR doing so will be rudely denied.


@dataclasses.dataclass
class ParseError(Error):
    """An error occurred while parsing a query."""

    message: str
    """The original error message from Postgres."""

    funcname: str
    """The C function inside the parser that caused the exception."""

    filename: str
    """The name of the C source file the exception happened in."""

    lineno: int
    """The line number at which the error occurred, or 0 if not available."""

    cursorpos: int
    """The zero-based index into the query string.

    .. todo:: This may be wrong if the query contains multi-byte characters.
    """

    context: Optional[str]
    """More context on what caused the error (may be null)."""

    def __post_init__(self) -> None:
        parts = []
        if self.filename:
            parts.append("in %(filename)s@%(lineno)d (absolute offset %(cursorpos)d)")
        else:
            parts.append("at absolute offset %(cursorpos)d")
        if self.funcname:
            parts.append("in %(funcname)s()")

        parts.extend(("--", "%(message)s"))
        super().__init__(" ".join(parts) % vars(self))
