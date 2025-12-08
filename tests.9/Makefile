#
# Run tests in different platforms and different Python
#
# 1. Basic usage, test all pythons in this platform
#
#    make test
#    make nogil-test
#
# 2. Test one python version
#
#    make test-3.13
#
# 3. Test free-threaded version
#
#    make nogil-test-3.13
#
# Prerequisites:
#
# - Python has been installed in the path "venv"
# - Pyarmor has been registerred (Pro features)
#
HOSTS := darwin.x86_64 darwin.arm64 linux.x86_64 linux.aarch64 windows.x86_64

UNAME ?= $(shell uname)
ARCH ?= $(shell arch)
PYVERS ?= 3.9 3.10 3.11 3.12 3.13 3.14
PYVERS_T ?= 3.13 3.14

PYVER ?= $(word 1,${PYVERS})
ifneq ($(findstring ${PYVER},${PYVERS}),${PYVER})
    $(error "${PYVER}" not in supported Python versions "${PYVERS}")
endif

ifeq ($(findstring Linux,$(UNAME)),Linux)
    ifeq ($(ARCH),x86_64)
        HOST ?= linux.x86_64
        PYTHON := /usr/local/bin/python${PYVER}
    else ifeq ($(ARCH),aarch64)
        HOST ?= linux.aarch64
        PYTHON := /usr/bin/python${PYVER}
    else
        HOST ?= linux.x86
        PYTHON := /usr/local/bin/python${PYVER}
    endif

    PYTHON_T := ${PYTHON}t

else ifeq ($(findstring Darwin,$(UNAME)),Darwin)
    ifeq ($(ARCH),arm64)
        HOST ?= darwin.arm64
        PYTHON := venv/${PYVER}/bin/python${PYVER}
        PYTHON_T := venv/${PYVER}t/bin/python${PYVER}
    else
	HOST ?= darwin.x86_64
        PYTHON := venv/${PYVER}/bin/python${PYVER}
        PYTHON_T := venv/${PYVER}t/bin/python${PYVER}
    endif

else
    ifeq ($(ARCH),x86_64)
	HOST ?=windows.x86_64
        PYTHON := venv/${PYVER}/Scripts/python.exe
        PYTHON_T := venv/${PYVER}t/Scripts/python.exe
    else
	HOST ?=windows.x86
        PYTHON := venv/${PYVER}/Scripts/python.exe
        PYTHON_T := venv/${PYVER}t/Scripts/python.exe
    endif
endif

PIPINST = install --force-reinstall --disable-pip-version-check
ifeq (${HOST},linux.aarch64)
    PIP := ${PYTHON} pip.pyz ${PIPINST}
    PIP_T := ${PYTHON_T} pip.pyz ${PIPINST}
else
    PIP := ${PYTHON} -m pip ${PIPINST}
    PIP_T := ${PYTHON_T} -m pip ${PIPINST}
endif

$(info python is ${PYTHON})

PLATFORM = $(strip $(subst linux.x86,manylinux1_i686,\
	$(subst linux.x86_64,manylinux1_x86_64,\
	$(subst linux.aarch64,manylinux2014_aarch64,\
	$(subst linux.armv7,manylinux2014_armv7l,\
	$(subst windows.x86,win32,\
	$(subst windows.x86_64,win_amd64,\
	$(subst darwin.arm64,macosx_11_0_arm64,\
	$(subst darwin.x86_64,macosx_10_14_x86_64,\
	${HOST})))))))))

PYTAG=cp$(subst .,,${PYVER})

workpath := __runner__
pkgpath := ${workpath}/pkgdist
testpkg := $(wildcard ${pkgpath}/pyarmor_cli-*-none-any.whl)
corepkg := $(wildcard ${pkgpath}/pyarmor_cli_core-*-${PYTAG}-*-${PLATFORM}.whl)
minipkg := $(wildcard ${pkgpath}/pyarmor_mini-*-${PYTAG}-${PYTAG}-${PLATFORM}.whl)
minipkg_t := $(wildcard ${pkgpath}/pyarmor_mini-*-${PYTAG}-${PYTAG}t-${PLATFORM}.whl)

ifndef testpkg
$(error no test package found)
endif

ifndef corepkg
$(error no core package found)
endif

ifndef minipkg
$(error no mini package found)
endif

$(info got test package: $(notdir ${testpkg}))
$(info got core package: $(notdir ${corepkg}))
$(info got mini package: $(notdir ${minipkg}))

.PHONY: all test nogil-test test-* notil-test-* install clean

all: test nogil-test

test:
	for ver in ${PYVERS} ; do \
		make test-$$ver ; \
	done

nogil-test:
	for ver in ${PYVERS_T} ; do \
		make nogil-test-$$ver ; \
	done

install:
	${PIP} ${corepkg} ${testpkg} ${minipkg}

test-%:
	PYVER=$(subst test-,,$@) make install run-test

nogil-install:
	${PIP_T} ${minipkg_t}

nogil-test-%:
	PYVER=$(subst nogil-test-,,$@) make install nogil-install run-nogil-test

run-test:
	${PYTHON} ${workpath}/accept_test.py

run-nogil-test:
	PYTHON_NOGIL=${PYTHON_T} ${PYTHON} ${workpath}/accept_test_nogil.py

clean:
	rm -rf ${workpath} __pycache__ testv9.tar.gz
