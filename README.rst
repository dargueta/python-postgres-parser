Parse SQL Using the PostgreSQL Parser
=====================================

This is (currently) a thin Python wrapper around `libpg_query <https://github.com/pganalyze/libpg_query>`_,
which lets you parse SQL using the PostgreSQL database's actual parser. For the
time being this only provides direct equivalents to the C functions, but I
intend to add more features such as visitor classes in the future.


Supported Functions
-------------------

All supported functions are exported directly into the package's namespace. They
generally have the same name as the corresponding C function minus the ``pg_query_``
prefix. The one exception is that the functions that return JSON have ``_json``
tacked onto the end, and the form that does *not* have that suffix returns
deserialized JSON. Thus, ``pg_query_parse`` is exported as ``parse_json`` *and*
``parse``, with ``parse`` returning a Python dict and ``parse_json`` returning a
JSON string. Other functions are not renamed.

=========================== ========== =====================================================================
Function                    Supported? Notes
--------------------------- ---------- ---------------------------------------------------------------------
pg_query_deparse_protobuf
pg_query_fingerprint        ✔
pg_query_normalize
pg_query_parse              ✔          Exposed as ``parse_json`` (JSON string) and ``parse`` (dict)
pg_query_parse_plpgsql
pg_query_parse_protobuf     ✔
pg_query_scan
pg_query_split_with_parser
pg_query_split_with_scanner
=========================== ========== =====================================================================


Development
-----------

Aside from a supported version of Python, you'll need:

* Some implementation of ``make``
* A C compiler recognized by `Cython <https://cython.org/>`_
* A `Protobuf <https://developers.google.com/protocol-buffers>`_ compiler

You can install the necessary Python dependencies from ``dev-requirements.txt``.


License
-------

I'm releasing this under the terms of the Apache 2.0 License. See LICENSE.txt for
the legal details.
