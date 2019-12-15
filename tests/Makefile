ARCH := $(shell arch)
UNAME := $(shell uname)
BASH := bash

ifeq ($(findstring Linux,$(UNAME)),Linux)

ifeq ($(ARCH),x86_64)
PLATFORM := linux_x86_64
else
PLATFORM := linux_i386
endif

else

ifeq ($(findstring Darwin,$(UNAME)),Darwin)
PLATFORM := macosx_x86_64
BASH := /usr/local/bin/bash
else

ifeq ($(ARCH),x86_64)
PLATFORM := win_amd64
else
PLATFORM := win32
endif

endif

endif


ifndef PLATFORM
$(info Usage: PLATFORM=XXXX make)
$(info XXXX coule be win32, win_amd64, linux_i386, linux_x86_64 or macosx_x86_64)
$(info )
$(error PLATFORM IS EMPTY)
endif

$(info )
$(info ****************** RUN TEST IN $(PLATFORM))
$(info )

ifeq ($(findstring linux,$(PLATFORM)),linux)

TARGET = _pytransform.so
PYROOT = /home/jondy/workspace/pytransform-legend/python/usr/local
CMDPREFIX = LD_LIBRARY_PATH=$(PYROOT)/lib
PYCMD = $(PYROOT)/bin/pythonXY
PYLIB = $(PYROOT)/lib/pythonXY
ifeq ($(ARCH),x86_64)
    VERSIONS := 2.6 2.7 3.0 3.1 3.2 3.3 3.4 3.5 3.6 3.7 3.8
else
    VERSIONS := 2.6 2.7 3.0 3.1 3.2 3.3 3.4 3.5 3.6 3.7
endif

else

ifeq ($(findstring macosx,$(PLATFORM)),macosx)
TARGET = _pytransform.dylib
CMDPREFIX =
PYCMD = pythonXY
PYLIB = /usr/lib/pythonXY
VERSIONS := 2.7 3
else
TARGET = _pytransform.dll
CMDPREFIX =
PYCMD = C:/PythonXY/python
PYLIB = C:/PythonXY/Lib
ifeq ($(ARCH),x86_64)
    VERSIONS := 26 27 30 31 32 33 34 35 36 37 38
else
    VERSIONS := 26 27 30 31 32 33 34
endif
endif

endif

WORKPATH = __runtime__

.PHONY: test unit trial build


test:
	for pyver in  $(VERSIONS) ; do \
            echo "" && echo "******************** Testing Python$${pyver} ..." && echo "" ; \
            $(CMDPREFIX) PYTHON=$(subst XY,$${pyver},$(PYCMD)) $(BASH) integration-test.sh || exit 1; \
            echo "" && echo "******************** Test Python$${pyver} End." && echo "" ; \
	done
	make clean

stest:
	for pyver in  $(VERSIONS) ; do \
            echo "" && echo "******************** Testing Python$${pyver} ..." && echo "" ; \
            $(CMDPREFIX) PYTHON=$(subst XY,$${pyver},$(PYCMD)) $(BASH) system-test.sh || exit 1; \
            echo "" && echo "******************** Test Python$${pyver} End." && echo "" ; \
	done
	make clean

ftest:
	for pyver in  $(VERSIONS) ; do \
            echo "" && echo "******************** Testing Python$${pyver} ..." && echo "" ; \
            $(CMDPREFIX) PYTHON=$(subst XY,$${pyver},$(PYCMD)) $(BASH) function-test.sh || exit 1; \
            echo "" && echo "******************** Test Python$${pyver} End." && echo "" ; \
	done
	make clean

atest:
	for pyver in  $(VERSIONS) ; do \
            echo "" && echo "******************** Testing Python$${pyver} ..." && echo "" ; \
            $(CMDPREFIX) PYTHON=$(subst XY,$${pyver},$(PYCMD)) $(BASH) accept-test.sh || exit 1; \
            echo "" && echo "******************** Test Python$${pyver} End." && echo "" ; \
	done
	make clean

ptest:
	for pyver in  $(VERSIONS) ; do \
            echo "" && echo "******************** Testing Python$${pyver} ..." && echo "" ; \
            TESTLIB=$(subst XY,$${pyver},$(PYLIB))/test $(CMDPREFIX) PYTHON=$(subst XY,$${pyver},$(PYCMD)) $(BASH) python-test.sh || exit 1; \
            echo "" && echo "******************** Test Python$${pyver} End." && echo "" ; \
	done
	make clean

build:
	rm -rf $(WORKPATH)
	mkdir -p $(WORKPATH)
	cp ../src/platforms/$(PLATFORM)/$(TARGET) $(WORKPATH)


unit:
	for pyver in  $(VERSIONS) ; do \
            make build ; \
            echo "" && echo "******************** Testing Python$${pyver} ..." && echo "" ; \
            $(CMDPREFIX) $(subst XY,$${pyver},$(PYCMD)) test-pyarmor.py || exit 1; \
            echo "" && echo "******************** Test Python$${pyver} End." && echo "" ; \
            make clean; \
	done


trial:
	for pyver in  $(VERSIONS) ; do \
            make build ; \
            echo "" && echo "******************** Testing Python$${pyver} ..." && echo "" ; \
            $(CMDPREFIX) $(subst XY,$${pyver},$(PYCMD)) test-trial-pyarmor.py || exit 1; \
            echo "" && echo "******************** Test Python$${pyver} End." && echo "" ; \
            make clean; \
	done

clean:
	rm -rf *.pyc *.pyo __pycache__ _pytransform.log $(WORKPATH)
