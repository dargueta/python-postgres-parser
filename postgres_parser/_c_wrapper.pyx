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


def parse_json(query):
    """Parse SQL and return the AST as serialized JSON.

    This is a wrapper around ``pg_query_parse()``.

    Arguments:
        query (str): The SQL to parse.

    Returns:
        str: The AST of the parsed query/ies, as a JSON string.
    """
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


def parse(query):
    """A convenience method for :func:`parse_json` that returns a Python dict."""
    return json.loads(parse_json(query))


def parse_protobuf(query):
    """Parse SQL and return the AST as a Protobuf message.

    This is a wrapper around ``pg_query_parse_protobuf()``.

    Arguments:
        query (str): The SQL to parse.

    Returns:
        postgres_parser.pg_query_pb2.ParseResult: The AST.
    """
    raw_data = parse_to_protobuf_bytes(query)
    result = pg_query_pb2.ParseResult()
    result.ParseFromString(raw_data)
    return result


def parse_to_protobuf_bytes(query):
    """Parse SQL and return the AST as a *serialized* Protobuf message.

    Equivalent to ``parse_protobuf(...).SerializeToBytes()`` but is faster and uses less
    memory.

    Arguments:
        query (str): The SQL to parse.

    Returns:
        bytes:
            The serialized Protobuf message of the parsing result. If you want the
            Protobuf object and not its bytes, use :func:`parse_protobuf`.
    """
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


def fingerprint(query):
    """Parse SQL and return its signature.

    The returned integer can be used to identify similar queries. For more detailed
    information on what fingerprinting is and how it works, check out the documentation
    on libpg_query's
    `wiki <https://github.com/pganalyze/libpg_query/wiki/Fingerprinting>`_.

    Arguments:
        query (str): The SQL to parse.

    Returns:
        int: The fingerprint of the SQL passed in.
    """
    cdef c_definitions.PgQueryFingerprintResult fingerprint_result
    cdef char *query_c_string

    query_bytes = query.encode("utf-8")
    query_c_string = query_bytes

    with nogil:
        fingerprint_result = c_definitions.pg_query_fingerprint(query_c_string)

    if fingerprint_result.error is not NULL:
        exception = create_python_parse_exception(fingerprint_result.error)
        with nogil:
            c_definitions.pg_query_free_fingerprint_result(fingerprint_result)
        raise exception

    fingerprint = fingerprint_result.fingerprint
    with nogil:
        c_definitions.pg_query_free_fingerprint_result(fingerprint_result)
    return fingerprint
