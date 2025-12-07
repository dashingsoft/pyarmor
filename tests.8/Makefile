HOSTS := darwin.x86_64 darwin.arm64 linux.x86_64 linux.aarch64 linux.x86 windows.x86_64 windows.x86

UNAME = $(shell uname)
ARCH := $(shell arch)

ALL_PYVERS := 3.7 3.8 3.9 3.10 3.11 3.12 3.13 3.14 3.15

ifeq ($(findstring Linux,$(UNAME)),Linux)
    ifeq ($(ARCH),x86_64)
        HOST ?= linux.x86_64
	PYVERS := ${ALL_PYVERS}
	PYTHONBIN := /usr/local/bin/pythonXY
    else ifeq ($(ARCH),aarch64)
        HOST ?= linux.aarch64
	PYVERS := 3.10
	PYTHONBIN := /usr/local/bin/pythonXY
    else
        HOST ?= linux.x86
	PYVERS := ${ALL_PYVERS}
	PYTHONBIN := /usr/local/bin/pythonXY
    endif
else ifeq ($(findstring Darwin,$(UNAME)),Darwin)
    ifeq ($(ARCH),arm64)
        HOST ?= darwin.arm64
	PYVERS := 3.9 3.10
	PYTHONBIN := /usr/local/bin/pythonXY
    else
	HOST ?= darwin.x86_64
	PYVERS := ${ALL_PYVERS}
	PYTHONBIN := /usr/local/bin/pythonXY
    endif
else
    ifeq (${HOST},windows.x86)
	PYVERS := 3.7 3.8
	PYTHONBIN := C:/PythonXY-32/python
    else ifeq ($(ARCH),x86_64)
	HOST ?=windows.x86_64
	PYVERS := 3.7 3.8
	PYTHONBIN := C:/PythonXY/python
    else
	HOST ?=windows.x86
	PYVERS := 3.7 3.8
	PYTHONBIN := C:/PythonXY-32/python
    endif
endif

ifneq ($(findstring $(HOST),${HOSTS}),$(HOST))
    $(error  "${HOST}" not in supported platforms "${HOSTS}")
endif

PYVER ?= $(word 1,${PYVERS})
ifneq ($(findstring ${PYVER},${PYVERS}),${PYVER})
    $(error "${PYVER}" not in supported Python versions "${PYVERS}")
endif

ifeq (${HOST},windows.x86_64)
    PYTHON ?= $(subst XY,$(subst .,,${PYVER}),${PYTHONBIN})
else ifeq (${HOST},windows.x86)
    PYTHON ?= $(subst XY,$(subst .,,${PYVER}),${PYTHONBIN})
else
    PYTHON ?= $(subst XY,${PYVER},${PYTHONBIN})
endif

$(info python is ${PYTHON})
ifneq ($(findstring ${PYVER},$(shell ${PYTHON} --version)),${PYVER})
    $(error invalid ${PYTHON})
endif

platform = $(strip $(subst linux.x86,manylinux1_i686,\
	$(subst linux.x86_64,manylinux1_x86_64,\
	$(subst linux.aarch64,manylinux2014_aarch64,\
	$(subst linux.armv7,manylinux2014_armv7l,\
	$(subst windows.x86,win32,\
	$(subst windows.x86_64,win_amd64,\
	$(subst darwin.arm64,macosx_11_0_arm64,\
	$(subst darwin.x86_64,macosx_10_14_x86_64,\
	${HOST})))))))))

pkgpath := ../dist
whlpath := ../../pytransform/publish/core/dist
pkgpath := $(shell (test -d ${pkgpath} && echo ${pkgpath}) || echo ./pkgdist)
whlpath := $(shell (test -d ${whlpath} && echo ${whlpath}) || echo ./pkgdist)

pkgfile := $(word 1,$(shell cd ${pkgpath}; ls -t pyarmor-*.tar.gz))
testver := $(subst pyarmor-,,$(subst .tar.gz,,${pkgfile}))
coreprefix := pyarmor_cli_core-
coresuffix := -cp38-none-macosx_10_14_x86_64.whl
corever=$(subst ${coreprefix},,$(subst ${coresuffix},,$(shell cd ${whlpath}; ls -t ${coreprefix}*${coresuffix})))

$(info got test package file: ${pkgfile})
$(info pyarmor version: ${testver})
$(info core version: ${corever})


.PHONY: all clean atest ptest test-* install-%

all:
	for ver in ${PYVERS} ; do \
		make test-$$ver ; \
	done

test-%:
	PYVER=$(subst test-,,$@) make install-$(subst test-,,$@) atest ptest

install-%:
	@rm -rf ./pyarmor ./pyarmor_cli_core_themida*
	@tar xzf ${pkgpath}/pyarmor-${testver}.tar.gz
	@mv pyarmor-${testver}/pyarmor .
	@rm -rf pyarmor-${testver}
	@unzip ${whlpath}/pyarmor_cli_core-${corever}-cp$(subst .,,$(subst install-,,$@))-none-${platform}.whl > /dev/null
	@(themida=../pyarmor_cli_core_themida-${corever}-cp$(subst .,,$(subst install-,,$@))-none-any.whl && test -f $$themida && unzip $$themida > /dev/null || echo no themida $$themida)
	@rm -rf pyarmor_cli_core-${corever}.dist-info

atest:
	${PYTHON} accept_test.py

ptest:
	${PYTHON} test_pyfeatures.py

clean:
	rm -rf ${homepath} ${localpath} ./pyarmor ./pyarmor-* ./pyarmor.*.log

# Unused
install-mini:
	-@test -d ${pkgpath}/mini.extensions/${HOST} && mkdir -p pyarmor/mini/ && cp ${pkgpath}/mini.extensions/${HOST}/libs/cp${PYVER}/pyarmor_mini.* ./pyarmor/mini/
