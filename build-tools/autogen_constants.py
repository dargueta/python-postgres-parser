import argparse
import datetime
import json
import os
import re
import sys
import textwrap
from typing import Iterable
from typing import Optional

import camel_converter
import jinja2


HERE = os.path.dirname(__file__)
REPO_ROOT = os.path.join(HERE, "..")
LIBPG_QUERY_ROOT = os.path.join(REPO_ROOT, "extern", "libpg_query")
SRCDATA_ROOT = os.path.join(LIBPG_QUERY_ROOT, "srcdata")


RECOGNIZED_C_TYPES = {
    "ctypes.c_int": "int",
    "ctypes.POINTER(ctypes.c_char)": "str",
}


def ctypes_to_python(ctypes_type: str) -> str:
    if ctypes_type in RECOGNIZED_C_TYPES:
        return RECOGNIZED_C_TYPES[ctypes_type]
    raise NotImplementedError("Unrecognized ctypes annotation: %r" % ctypes_type)


def get_jinja_environment() -> jinja2.Environment:
    return jinja2.Environment(
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        undefined=jinja2.StrictUndefined,
    )


def comment_to_docstring(comment: Optional[str], indentation_level: int = 0) -> str:
    if not comment:
        return ""

    comment = comment.strip()

    if comment.startswith(("//", "/*")):
        comment = comment[2:]
    if comment.endswith("*/"):
        comment = comment[:-2]

    comment = comment.strip()
    lines = [
        re.sub(r"^\s*\*?\s*(?P<text>.*)\s*$", r"\g<text>", line)
        for line in comment.splitlines()
    ]

    if not lines:
        text = ""
    elif len(lines) == 1:
        text = lines[0]
    else:
        text = (
            lines[0]
            + "\n"
            + textwrap.indent("\n".join(lines[1:]), " " * (4 * indentation_level))
            + "\n"
        )

    if text.endswith('"'):
        return text + "."
    return text


def find_common_prefix(items: Iterable[str]) -> str:
    prefix = os.path.commonprefix(
        [i for i in items if not isinstance(i, jinja2.StrictUndefined)]
    )
    if prefix.endswith("_"):
        return prefix
    return ""


def remove_prefix(what: str, prefix: str) -> str:
    if not prefix:
        return what
    if what.startswith(prefix):
        return what[len(prefix) :]
    return what


def to_snake(string: str) -> str:
    if string.upper() != string:
        # camel_converter cannot handle uppercase strings properly.
        converted = camel_converter.to_snake(string)
    else:
        converted = string

    # Fix some edge cases/bugginess in camel_converter
    converted = re.sub(r"_{2,}", r"_", converted)
    converted = re.sub(r"([S])_([Q])_([L])_", r"\1\2\3_", converted, flags=re.I)
    converted = re.sub(r"([C])_([T])_([E])_", r"\1\2\3_", converted, flags=re.I)
    return converted


def render_file(
    source_data_file: str, source_data_name: str, template_file: str
) -> str:
    with open(source_data_file, "r") as fd:
        defs = json.load(fd)

    with open(template_file, "r") as fd:
        template_text = fd.read()

    env = get_jinja_environment()
    template = env.from_string(template_text)
    return template.render(
        source_file=source_data_file,
        comment_to_docstring=comment_to_docstring,
        to_snake=to_snake,
        to_upper_snake=(lambda s: to_snake(s).upper()),
        remove_prefix=remove_prefix,
        dirname=os.path.dirname,
        basename=os.path.basename,
        ctypes_to_python=ctypes_to_python,
        current_year=datetime.date.today().year,
        find_common_prefix=find_common_prefix,
        **{source_data_name: defs}
    )


def generate_enums() -> str:
    return render_file(
        os.path.join(SRCDATA_ROOT, "enum_defs.json"),
        "all_enums",
        os.path.join(HERE, "enums.py.j2"),
    )


def generate_structs() -> str:
    return render_file(
        os.path.join(SRCDATA_ROOT, "struct_defs.json"),
        "all_structs",
        os.path.join(HERE, "struct_definitions.pxd.j2"),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("generator_name")
    parser.add_argument("output_file")
    args = parser.parse_args()

    try:
        generator = globals()["generate_" + args.generator_name]
    except KeyError:
        print("Undefined generator: %r" % args.generator_name)
        sys.exit(1)

    text = generator()

    with open(args.output_file, "w") as fd:
        fd.write(text)
    sys.exit(0)


if __name__ == "__main__":
    main()
