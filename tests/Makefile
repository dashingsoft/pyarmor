ARCH := $(shell arch)
UNAME := $(shell uname)

ifeq ($(findstring Linux,$(UNAME)),Linux)

ifeq ($(ARCH),x86_64)
PLATFORM := linux_x86_64
else
PLATFORM := linux_i386
endif

else

ifeq ($(ARCH),amd64)
PLATFORM := win_amd64
else
PLATFORM := win32
endif

endif


ifndef PLATFORM
$(info Usage: PLATFORM=XXXX make)
$(info XXXX coule be win32, win_amd64, linux_i386 or linux_x86_64)
$(info )
$(error PLATFORM IS EMPTY)
endif

$(info )
$(info ****************** RUN TEST IN $(PLATFORM))
$(info )

ifeq ($(findstring linux,$(PLATFORM)),linux)
TARGET = _pytransform.so
PYROOT = /home/jondy/workspace/pytransform-legend/python/usr/local
PYTHON = LD_LIBRARY_PATH=$(PYROOT)/lib $(PYROOT)/bin/pythonXY
VERSIONS := 2.6 2.7 3.0 3.1 3.2 3.3 3.4
else
TARGET = _pytransform.dll
PYTHON = C:/PythonXY/python
VERSIONS := 25 26 27 30 31 32 33 34
endif

WORKPATH = __runtime__

VERSIONS := 27

.PHONY: test unit trial build


test: build
	for pyver in  $(VERSIONS) ; do \
            echo -e "\n******************** Testing Python$${pyver} ...\n" ; \
            $(subst XY,$${pyver},$(PYTHON)) test-functions.sh || exit 1; \
            echo -e "\n******************** Test Python$${pyver} End.\n" ; \
	done
	make clean


build:
	mkdir -p $(WORKPATH)
	cp ../src/platforms/$(PLATFORM)/$(TARGET) $(WORKPATH)


unit: build
	for pyver in  $(VERSIONS) ; do \
            echo -e "\n******************** Testing Python$${pyver} ...\n" ; \
            $(subst XY,$${pyver},$(PYTHON)) test-pyarmor.py || exit 1; \
            echo -e "\n******************** Test Python$${pyver} End.\n" ; \
	done
	make clean

trial: build
	for pyver in  $(VERSIONS) ; do \
            echo -e "\n******************** Testing Python$${pyver} ...\n" ; \
            $(subst XY,$${pyver},$(PYTHON)) test-trial-pyarmor.py || exit 1; \
            echo -e "\n******************** Test Python$${pyver} End.\n" ; \
	done
	make clean


clean:
	rm -rf *.pyc *.pyo __pycache__ _pytransform.log $(WORKPATH)
