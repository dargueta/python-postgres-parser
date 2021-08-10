import os
import subprocess

import setuptools
from setuptools.command import build_ext


HERE = os.path.dirname(os.path.abspath(__file__))
LIBPG_QUERY_ROOT = os.path.join("extern", "libpg_query")


C_SOURCE_FILES = [
    os.path.join("postgres_parser", f)
    for f in os.listdir("postgres_parser")
    if f.endswith(".c")
]


class BuildOverride(build_ext.build_ext):
    """An overridden command class to force libpg_query to build before us."""

    def run(self) -> object:
        # We'll use version 2 of the JSON output format.
        # Fortunately we can pass the directive using CFLAGS like this because
        # libpg_parse's Makefile uses the `override` directive to set its own flags in
        # addition to whatever was passed in. If it didn't do that, we would overwrite
        # everything, and this could go badly for us.
        subprocess.run(
            ["make", "-C", LIBPG_QUERY_ROOT, "CFLAGS='-DJSON_OUTPUT_V2=1'", "build"],
            check=True,
        )
        # Let setuptools do whatever it was going to do.
        return super().run()


EXTENSIONS = [
    setuptools.Extension(
        "postgres_parser._c_wrapper",
        sources=C_SOURCE_FILES,
        libraries=["pg_query"],  # The C library we need to link to
        library_dirs=[LIBPG_QUERY_ROOT],  # Where to find that library
        include_dirs=[LIBPG_QUERY_ROOT],  # Path to the header we need
    )
]


setuptools.setup(
    ext_modules=EXTENSIONS,
    cmdclass={"build_ext": BuildOverride},
    # This shouldn't be necessary -- it's declared in setup.cfg!
    packages=["postgres_parser"],
)
