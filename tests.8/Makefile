HOSTS := darwin.x86_64 darwin.arm64 linux.x86_64 linux.x86 windows.x86_64

UNAME = $(shell uname)
ARCH := $(shell arch)

ifeq ($(findstring Linux,$(UNAME)),Linux)
    ifeq ($(ARCH),x86_64)
        HOST ?= linux.x86_64
    else
        HOST ?= linux.x86
    endif
else ifeq ($(findstring Darwin,$(UNAME)),Darwin)
    ifeq ($(ARCH),i386)
        HOST ?= darwin.x86_64
	PYTHONBIN := /usr/local/bin
    else
        HOST ?= darwin.arm64
    endif
else ifeq ($(ARCH),x86_64)
	HOST ?=windows.x86_64
endif

ifneq ($(findstring $(HOST),${HOSTS}),$(HOST))
    $(error  "${HOST}" not in supported platforms "${HOSTS}")
endif

PYTHONS ?= $(wildcard ${PYTHONBIN}/python3.? ${PYTHONBIN}/python3.1?)
PYVERS ?= $(subst ${PYTHONBIN}/python,,${PYTHONS})

PYVER ?= $(word 1,${PYVERS})
ifneq ($(findstring ${PYVER},${PYVERS}),${PYVER})
    $(error "${PYVER}" not in supported Python versions "${PYVERS}")
endif

PYTHON ?= ${PYTHONBIN}/python${PYVER}
$(info test python is ${PYTHON})
ifneq ($(findstring ${PYVER},$(shell ${PYTHON} --version)),${PYVER})
    $(error invalid ${PYTHON})
endif

homepath = __home__
localpath = .pyarmor
pkgpath = __dist__
platform = $(strip $(subst linux.x86,manylinux1_i686,\
	$(subst linux.x86_64,manylinux1_x86_64,\
	$(subst linux.aarch64,manylinux2014_aarch64,\
	$(subst linux.armv7,manylinux2014_armv7l,\
	$(subst windows.x86,win32,\
	$(subst windows.x86_64,win_amd64,\
	$(subst darwin.arm64,macosx_10_14_arm64,\
	$(subst darwin.x86_64,macosx_10_14_x86_64,\
	${HOST})))))))))

pkgfile=$(shell cd ${pkgpath}; ls -t pyarmor-*.tar.gz)
testver=$(subst pyarmor-,,$(subst .tar.gz,,${pkgfile}))
corever=$(subst pyarmor.cli.core-,,$(subst -cp38-none-macosx_10_14_x86_64.whl,,$(shell cd ${pkgpath}; ls -t pyarmor.cli.core-*-cp38-none-macosx_10_14_x86_64.whl)))

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
	rm -rf ./pyarmor
	tar xzf ${pkgpath}/pyarmor-${testver}.tar.gz
	mv pyarmor-${testver}/src pyarmor
	rm -rf pyarmor-${testver}/src
	unzip ${pkgpath}/pyarmor.cli.core-${corever}-cp$(subst .,,$(subst install-,,$@))-none-${platform}.whl
	rm -rf pyarmor.cli.core-${corever}.dist-info

atest:
	${PYTHON} accept_test.py

ptest:
	${PYTHON} test_pyfeatures.py

clean:
	rm -rf ${homepath} ${localpath} ./pyarmor ./pyarmor-*
