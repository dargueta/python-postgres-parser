LIBPGQUERY_TAG=$(CURRENT_POSTGRES_VERSION)-$(CURRENT_LIBPGQUERY_VERSION)
LIBPGQUERY_DIR=extern/libpg_query
SRC_ROOT=postgres_parser
PYTHON_SOURCES=$(wildcard $(SRC_ROOT)/*.py)
CYTHON_SOURCES=$(SRC_ROOT)/_c_wrapper.pyx
AUTOGENERATED_PXD_FILES=$(SRC_ROOT)/c_definitions.pxd  $(SRC_ROOT)/struct_definitions.pxd
AUTOGENERATED_PYX_FILES=
AUTOGENERATED_C_FILES=$(patsubst %.pyx,%.c,$(AUTOGENERATED_PYX_FILES) $(CYTHON_SOURCES))
AUTOGENERATED_PYTHON_FILES=$(SRC_ROOT)/enums.py $(SRC_ROOT)/_version.py
AUTOGENERATED_PROTOBUF_FILES=$(SRC_ROOT)/pg_query_pb2.py
AUTOGENERATED_FILES= $(AUTOGENERATED_PXD_FILES) $(AUTOGENERATED_PYX_FILES) $(AUTOGENERATED_PYTHON_FILES) $(AUTOGENERATED_PROTOBUF_FILES)
H2W_ARGS=--hooks build-tools/h2w_hooks.py
LIBPGQUERY_HEADER_FILES=$(LIBPGQUERY_DIR)/pg_query.h
CURRENT_VERSION=0.1.0


.PHONY: distfiles
distfiles: $(AUTOGENERATED_FILES) $(CYTHON_SOURCES) $(AUTOGENERATED_C_FILES)


.PHONY: install
install: distfiles
	pip3 install --force --user --verbose --use-feature=in-tree-build .


$(SRC_ROOT)/struct_definitions.pxd: build-tools/struct_definitions.pxd.j2 $(LIBPGQUERY_DIR)/srcdata/struct_defs.json
	python3 build-tools/autogen_constants.py structs $@


# WARNING: Do *not* change the order of the prerequisites
$(SRC_ROOT)/c_definitions.pxd: build-tools/c_definitions.pxd.j2 $(LIBPGQUERY_DIR)/pg_query.h
	h2w -o $@ $(H2W_ARGS) -- $^


$(SRC_ROOT)/enums.py: build-tools/enums.py.j2 $(LIBPGQUERY_DIR)/srcdata/enum_defs.json
	python3 build-tools/autogen_constants.py enums $@


# WARNING: Do *not* change the order of the prerequisites
$(SRC_ROOT)/%.pyx: build-tools/%.pyx.j2 $(LIBPGQUERY_HEADER_FILES)
	h2w -o $@ $(H2W_ARGS) -- $^


$(SRC_ROOT)/%.py: build-tools/%.py.j2 $(LIBPGQUERY_HEADER_FILES)
	h2w -o $@ $(H2W_ARGS) -- $^


$(SRC_ROOT)/%_pb2.py: $(LIBPGQUERY_DIR)/protobuf/%.proto
	protoc --proto_path=$(<D) --python_out=$(@D) $?


$(SRC_ROOT)/%.c: $(SRC_ROOT)/%.pyx | $(AUTOGENERATED_PXD_FILES) $(AUTOGENERATED_PY_FILES)
	cython -3 -Werror -Wextra -I $(LIBPGQUERY_DIR) $^


%.proto: ;
%.h: ;
%.j2: ;


.PHONY: setup
setup:
	pip3 install -U -r dev-requirements.txt


.PHONY: clean
clean:
	find . -name '__pycache__' -exec $(RM) -r '{}' \+
	find $(SRC_ROOT) \( -name '*.html' -o -name '*.c' -o -name '*.so' -o -name '*.pyd' \) -delete
	$(RM) -r .tox .mypy_cache .pytest_cache *.egg-info sdist dist build
	$(RM) $(AUTOGENERATED_FILES) $(TARGET_LIBRARY_FILENAME)
	$(MAKE) -C $(LIBPGQUERY_DIR) clean


.PHONY: publish
publish: distfiles
	python3 setup.py sdist bdist_wheel
	twine upload dist/*
