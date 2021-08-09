import os
import sys
import pprint


def header_hook(header: str, data: str) -> None:
    header.include_path = os.path.relpath(
        header.rel_fname,
        os.path.join("extern", "libpg_query"),
    )
    header.dirname = os.path.dirname(header.include_path)
    header.basename = os.path.basename(header.rel_fname)
