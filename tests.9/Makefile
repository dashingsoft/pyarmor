#
# Run tests in different platforms and different Python
#
# 1. Basic usage, test all pythons in this platform
#
#    make test
#    make test-nogil
#
# 2. Test one python version
#
#    make test-3.13
#
# 3. Test free-threaded version
#
#    make test-3.14 NOGIL=y
#
HOSTS := darwin.x86_64 darwin.arm64 linux.x86_64 linux.aarch64 windows.x86_64

UNAME ?= $(shell uname)
ARCH ?= $(shell arch)
PYVERS ?= 3.9 3.10 3.11 3.12 3.13 3.14 3.15

PYVER ?= $(word 1,${PYVERS})
ifneq ($(findstring ${PYVER},${PYVERS}),${PYVER})
    $(error "${PYVER}" not in supported Python versions "${PYVERS}")
endif

ifeq ($(findstring Linux,$(UNAME)),Linux)
    ifeq ($(ARCH),x86_64)
        HOST ?= linux.x86_64
    else ifeq ($(ARCH),aarch64)
        HOST ?= linux.aarch64
    else
        HOST ?= linux.x86
    endif
else ifeq ($(findstring Darwin,$(UNAME)),Darwin)
    ifeq ($(ARCH),arm64)
        HOST ?= darwin.arm64
    else
	HOST ?= darwin.x86_64
    endif
else
    ifeq ($(ARCH),x86_64)
	HOST ?=windows.x86_64
    else
	HOST ?=windows.x86
    endif
endif

ifeq ($(findstring windows,${HOST}),windows)
    PYTHON := venv/bin/python$(subst .,,${PYVER})
else
    PYTHON := venv/bin/python${PYVER}
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

ifndef testpkg
$(error no test package found)
endif

ifndef corepkg
$(error no core package found)
endif

ifndef minipkg
$(error no mini package found)
endif

$(info got test package: $(basename ${testpkg}))
$(info got core package: $(basename ${corepkg}))
$(info got mini package: $(basename ${minipkg}))

PIPOPTIONS := --force-reinstall --disable-pip-version-check

.PHONY: all test test-nogil test-* install clean

all: test test-nogil

test:
	for ver in ${PYVERS} ; do \
		make test-$$ver ; \
	done

test-nogil:
	for ver in ${PYVERS} ; do \
		make test-$$ver NOGIL=y ; \
	done

install:
	${PYTHON} -m pip install ${PIPOPTIONS} ${corepkg} ${testpkg} ${minipkg}

test-%:
	PYVER=$(subst test-,,$@) make install run-test

run-test:
	${PYTHON} ${workpath}/accept_test.py

clean:
	rm -rf ${workpath} __pycache__ testv9.tar.gz
