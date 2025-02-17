# Need:
# sudo apt install libstdc++-12-dev
# wget https://apt.llvm.org/llvm.sh
# chmod +x llvm.sh
# sudo ./llvm.sh all
# rm llvm.sh

EXTERNDIR       := $(CURDIR)/extern
EBUILDDIR       := $(EXTERNDIR)/ebuild
DPACKDIR        := $(EXTERNDIR)/dpack
STROLLDIR       := $(EXTERNDIR)/stroll
AFLDIR          := $(EXTERNDIR)/AFLplusplus
BUILDDIR        := $(CURDIR)/build
DESTDIR         := $(CURDIR)/out
VENV            := $(DESTDIR)
EXTRA_CFLAGS    := -I$(DESTDIR)/usr/local/include -I/usr/include \
		   -Wall -Wextra -Wformat=2 -Wconversion -Wundef -Wshadow \
		   -Wcast-qual -Wcast-align -Wmissing-declarations
EXTRA_LDFLAGS   := -L$(DESTDIR)/usr/local/lib -L/usr/lib/x86_64-linux-gnu/
LLVM_VERSION    := 18
CC              := $(DESTDIR)/usr/local/bin/afl-clang-lto
MAKE_ARGS       := EXTRA_CFLAGS:="$(EXTRA_CFLAGS)" \
		   EXTRA_LDFLAGS:="$(EXTRA_LDFLAGS)" \
		   DESTDIR:="$(DESTDIR)" \
		   PKG_CONFIG_PATH:="$(DESTDIR)/usr/local/lib/pkgconfig:/usr/lib/x86_64-linux-gnu/pkgconfig" \
		   CC:=$(CC) CXX=afl-clang-lto++ \
		   RANLIB=llvm-ranlib-$(LLVM_VERSION) \
		   AR=llvm-ar-$(LLVM_VERSION) \
		   AS=llvm-as-$(LLVM_VERSION) \
		   LD:=$(CC)
MAKEFLAGS       += --no-print-directory
PYTHON          := $(VENV)/bin/python3

GIT_EBUILD      := https://github.com/grgbr/ebuild.git
GIT_DPACK       := https://github.com/grgbr/dpack.git
GIT_STROLL      := https://github.com/grgbr/stroll.git
GIT_AFLPLUSPLUS := https://github.com/AFLplusplus/AFLplusplus.git

AFL_MAKE_ARGS   := BUILDDIR:=$(BUILDDIR)/afl DESTDIR:="$(DESTDIR)" \
		   PERFORMANCE=1 CODE_COVERAGE=1 CODE_COVERAGE=1 \
		   INTROSPECTION=1 LLVM_CONFIG=llvm-config-$(LLVM_VERSION)

-include .config.mk

export EBUILDDIR

all: test-lib

export PATH := $(VENV)/bin:$(DESTDIR)/usr/local/bin:$(PATH)
export LD_LIBRARY_PATH := $(DESTDIR)/usr/local/lib

#export AFL_LLVM_LAF_ALL=1
#export AFL_USE_ASAN=1
#export AFL_USE_MSAN=1
#export AFL_USE_CFISAN=1
#export AFL_USE_TSAN=1
#export AFL_USE_LSAN=1

define UP
$(strip $(subst a,A,$(subst b,B,$(subst c,C,$(subst d,D,$(subst e,E,\
$(subst f,F,$(subst g,G,$(subst h,H,$(subst i,I,$(subst j,J,$(subst k,K,\
$(subst l,L,$(subst m,M,$(subst n,N,$(subst o,O,$(subst p,P,$(subst q,Q,\
$(subst r,R,$(subst s,S,$(subst t,T,$(subst u,U,$(subst v,V,$(subst w,W,\
$(subst x,X,$(subst y,Y,$(subst z,Z,$(1))))))))))))))))))))))))))))
endef

test-%: tests/test-%.yaml | $(BUILDDIR)/troer-%
	@echo ====== Test $*
	@troer $< -Itests -o $(BUILDDIR)/troer-$*
	@$(CC) $(EXTRA_CFLAGS) $(EXTRA_LDFLAGS) \
		-o $(BUILDDIR)/troer-$*/test \
		$(BUILDDIR)/troer-$*/*.c tests/$*.c \
		-I$(BUILDDIR)/troer-$* \
		$(call UP,-DCONFIG_TEST_$*_ASSERT=1) \
		$(DESTDIR)/usr/local/lib/libdpack.a \
		$(DESTDIR)/usr/local/lib/libstroll.a

install: venv dpack stroll

clobber:
	@rm -rf $(EXTERNDIR)
	@rm -rf $(BUILDDIR)
	@rm -rf $(DESTDIR)

$(EXTERNDIR):
	@mkdir -p $@

$(BUILDDIR)/% $(DESTDIR)/%:
	@mkdir -p $@

#################### DOWNLOAD

$(EXTERNDIR)/%: | $(EXTERNDIR)
	@echo ===== Git clone $*
	@git clone $($(call UP,GIT_$*)) $@

#################### AFL++

$(CC): | $(AFLDIR)
	@echo ===== build afl++
	@$(MAKE) -C $(AFLDIR) $(AFL_MAKE_ARGS) distrib
	@$(MAKE) -C $(AFLDIR) $(AFL_MAKE_ARGS) install

#################### STROLL

guiconfig-stroll: | $(STROLLDIR) $(EBUILDDIR) $(AFLDIR) $(CC)
	@$(MAKE) -C $(STROLLDIR) $(MAKE_ARGS) BUILDDIR:=$(BUILDDIR)/stroll menuconfig

$(BUILDDIR)/stroll/.config: $(BUILDDIR)/stroll | $(STROLLDIR) $(EBUILDDIR) $(AFLDIR) $(CC)
	@cp defconfig/stroll.defconfig $@
	@$(MAKE) -C $(STROLLDIR) $(MAKE_ARGS) BUILDDIR:=$(BUILDDIR)/stroll olddefconfig

$(DESTDIR)/usr/local/lib/libstroll.a: $(BUILDDIR)/stroll/.config
	@echo ===== build stroll
	$(MAKE) -C $(STROLLDIR) $(MAKE_ARGS) BUILDDIR:=$(BUILDDIR)/stroll build
	$(MAKE) -C $(STROLLDIR) $(MAKE_ARGS) BUILDDIR:=$(BUILDDIR)/stroll install

stroll: $(DESTDIR)/usr/local/lib/libstroll.a

#################### DPACK

guiconfig-dpack: | $(DPACKDIR) $(EBUILDDIR) $(AFLDIR) $(CC)
	@$(MAKE) -C $(DPACKDIR) $(MAKE_ARGS) BUILDDIR:=$(BUILDDIR)/dpack menuconfig

$(BUILDDIR)/dpack/.config: $(BUILDDIR)/dpack | $(DPACKDIR) $(EBUILDDIR) $(AFLDIR) $(CC)
	@cp defconfig/dpack.defconfig $@
	@$(MAKE) -C $(DPACKDIR) $(MAKE_ARGS) BUILDDIR:=$(BUILDDIR)/dpack olddefconfig

$(DESTDIR)/usr/local/lib/libdpack.a: $(BUILDDIR)/dpack/.config stroll
	@echo ===== build dpack
	@$(MAKE) -C $(DPACKDIR) $(MAKE_ARGS) BUILDDIR:=$(BUILDDIR)/dpack build
	@$(MAKE) -C $(DPACKDIR) $(MAKE_ARGS) BUILDDIR:=$(BUILDDIR)/dpack install

dpack: $(DESTDIR)/usr/local/lib/libdpack.a

#################### VENV

$(VENV)/bin/python3:
	@python3 -m venv $(VENV)
	@$(PYTHON) -m pip install -e .

venv: $(VENV)/bin/python3

.PHONY: test install clobber
