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

from typing import Dict
from postgres_parser import pg_query_pb2

def parse_to_protobuf_bytes(query: str) -> str: ...
def parse_protobuf(query: str) -> pg_query_pb2.ParseResult: ...
def parse_json(query: str) -> str: ...
def parse(query: str) -> Dict[str, object]: ...
def fingerprint(query: str) -> int: ...
