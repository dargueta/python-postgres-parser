import os
import subprocess

import setuptools
from setuptools.command import build_ext
from Cython.Build import cythonize


HERE = os.path.dirname(os.path.abspath(__file__))
LIBPG_QUERY_ROOT = os.path.join(HERE, "extern", "libpg_query")


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
        sources=[os.path.join(HERE, "postgres_parser", "*.pyx")],
        libraries=["pg_query"],  # The C library we need to link to
        library_dirs=[LIBPG_QUERY_ROOT],  # Where to find that library
        include_dirs=[LIBPG_QUERY_ROOT],  # Path to the header we need
    ),
]


def build(setup_kwargs):
    setuptools.setup(
        ext_modules=cythonize(EXTENSIONS),
        cmdclass={"build_ext": BuildOverride},
        script_args=["build_ext"],
        **setup_kwargs,
    )
    return setup_kwargs


if __name__ == "__main__":
    build({})
