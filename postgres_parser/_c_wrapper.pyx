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

# cython: language_level=3
# cython: embedsignature=True

# YOLO optimizations -- if we get crashes then remove these to debug.
# cython: boundscheck=False
# cython: wraparound=False

import json

from postgres_parser cimport c_definitions
from postgres_parser import errors
from postgres_parser import pg_query_pb2

from cpython.bytes cimport PyBytes_FromStringAndSize


cdef object create_python_parse_exception(c_definitions.PgQueryError *err):
    cdef str message = err.message.decode("utf-8")
    cdef str funcname = None
    cdef str filename = None
    cdef str context = None

    if err.funcname is not NULL:
        funcname = err.funcname.decode("utf-8")
    if err.filename is not NULL:
        filename = err.filename.decode("utf-8")
    if err.context is not NULL:
        context = err.context.decode("utf-8")

    return errors.ParseError(
        message=message,
        funcname=funcname,
        filename=filename,
        lineno=err.lineno,
        cursorpos=err.cursorpos,
        context=context,
    )


def parse_to_protobuf_bytes(query):
    # type: (str) -> bytes
    cdef c_definitions.PgQueryProtobufParseResult parse_result
    cdef char *query_c_string

    query_bytes = query.encode("utf-8")
    query_c_string = query_bytes

    with nogil:
        parse_result = c_definitions.pg_query_parse_protobuf(query_c_string)

    if parse_result.error is not NULL:
        exception = create_python_parse_exception(parse_result.error)
        with nogil:
            c_definitions.pg_query_free_protobuf_parse_result(parse_result)
        raise exception

    try:
        return_bytes = PyBytes_FromStringAndSize(
            parse_result.parse_tree.data,
            parse_result.parse_tree.len,
        )
    finally:
        # Can't do nogil here because of the `finally`
        c_definitions.pg_query_free_protobuf_parse_result(parse_result)
    return return_bytes


def parse_to_protobuf(query):
    # type: (str) -> pg_query_pb2.ParseResult
    raw_data = parse_to_protobuf_bytes(query)
    result = pg_query_pb2.ParseResult()
    result.ParseFromString(raw_data)
    return result


def parse_to_json(query):
    # type: (str) -> str
    cdef c_definitions.PgQueryParseResult parse_result
    cdef char *query_c_string

    query_bytes = query.encode("utf-8")
    query_c_string = query_bytes

    with nogil:
        parse_result = c_definitions.pg_query_parse(query_c_string)

    if parse_result.error is not NULL:
        exception = create_python_parse_exception(parse_result.error)
        with nogil:
            c_definitions.pg_query_free_parse_result(parse_result)
        raise exception

    try:
        return parse_result.parse_tree.decode("utf-8")
    finally:
        # Same issue here, can't use nogil
        c_definitions.pg_query_free_parse_result(parse_result)


def parse_to_dict(query):
    # type: (str) -> Dict[str, object]
    return json.loads(parse_to_json(query))
