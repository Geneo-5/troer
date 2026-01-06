# Need:
# sudo apt install libstdc++-12-dev
# wget https://apt.llvm.org/llvm.sh
# chmod +x llvm.sh
# sudo ./llvm.sh all
# rm llvm.sh

EXTERNDIR       := $(CURDIR)/extern
EBUILDDIR       := $(EXTERNDIR)/ebuild
DEPENDSDIR      := $(EXTERNDIR)/depends
AFLDIR          := $(EXTERNDIR)/AFLplusplus
BUILDDIR        := $(CURDIR)/build
DESTDIR         := $(CURDIR)/out
VENV            := $(DESTDIR)
EXTRA_CFLAGS    := -I$(DESTDIR)/usr/local/include -I/usr/include \
		   -Wall -Wextra -Wformat=2 -Wconversion -Wundef -Wshadow \
		   -Wcast-qual -Wcast-align -Wmissing-declarations -Xanalyzer \
		   -ggdb -g -D_GNU_SOURCE
EXTRA_LDFLAGS   := -L$(DESTDIR)/usr/local/lib -L/usr/lib/x86_64-linux-gnu/ -rdynamic
LLVM_VERSION    := 19
CC              := $(DESTDIR)/usr/local/bin/afl-clang-lto
MAKE_ARGS        = EXTRA_CFLAGS:="$(EXTRA_CFLAGS)" \
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
GIT_UTILS       := https://github.com/grgbr/utils.git
GIT_UTILS       := https://github.com/grgbr/utils.git
GIT_GALV        := https://github.com/grgbr/galv.git -b svc
GIT_ELOG        := https://github.com/grgbr/elog.git
GIT_HED         := https://github.com/geneo-5/hed.git
GIT_AFLPLUSPLUS := https://github.com/AFLplusplus/AFLplusplus.git

AFL_MAKE_ARGS   := BUILDDIR:=$(BUILDDIR)/afl DESTDIR:="$(DESTDIR)" \
		   PERFORMANCE=1 CODE_COVERAGE=1 CODE_COVERAGE=1 \
		   INTROSPECTION=1 LLVM_CONFIG=llvm-config-$(LLVM_VERSION)

-include .config.mk
-include $(EBUILDDIR)/helpers.mk

export EBUILDDIR

all: test-lib test-exchange test-storage

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

src := Makefile $(shell find src/ tests/ -type f)

$(BUILDDIR)/test_%: EXTRA_CFLAGS+=$(call UP,-DCONFIG_TEST_$*_ASSERT)
$(BUILDDIR)/test_%: tests/test-%.yaml $(src) | $(BUILDDIR)/test-% \
	$(BUILDDIR)/troer-% \
	$(BUILDDIR)/troer-%-base \
	$(BUILDDIR)/troer-%-builtin
	@echo ====== Test $*
	@troer --include tests $< $(BUILDDIR)/troer-$*-base
	@troer --json --makefile builtin --include tests $< $(BUILDDIR)/troer-$*-builtin
	@troer --json --makefile both    --include tests $< $(BUILDDIR)/troer-$*
	@$(MAKE) -C $(BUILDDIR)/troer-$* $(MAKE_ARGS) BUILDDIR:=$(BUILDDIR)/test-$* defconfig
	@$(MAKE) -C $(BUILDDIR)/troer-$* $(MAKE_ARGS) BUILDDIR:=$(BUILDDIR)/test-$* build
	@$(MAKE) -C $(BUILDDIR)/troer-$* $(MAKE_ARGS) BUILDDIR:=$(BUILDDIR)/test-$* install
	@$(MAKE) -C $(BUILDDIR)/troer-$* $(MAKE_ARGS) BUILDDIR:=$(BUILDDIR)/test-$* tags
	@$(MAKE) -C $(BUILDDIR)/troer-$* $(MAKE_ARGS) BUILDDIR:=$(BUILDDIR)/test-$* dist
	@$(CC)  $(EXTRA_CFLAGS) \
		$(call pkgconfig, --cflags libdpack) \
		$(call pkgconfig, --cflags libstroll) \
		$(call pkgconfig, --cflags libhed) \
		$(call pkgconfig, --cflags libgalv) \
		$(call pkgconfig, --cflags libutils) \
		$(call pkgconfig, --cflags libelog) \
		$(call pkgconfig, --cflags libtest_$*) \
		$(call pkgconfig, --cflags json-c) \
		$(call pkgconfig, --cflags pcre2-8) \
		$(EXTRA_LDFLAGS) -l:libdpack.a -l:libstroll.a -l:libjson-c.a \
		-l:libutils.a -l:libgalv.a -l:libhed.a -letux_timer_heap \
		-lelog -l:liblmdb.a -l:libtest-$*.a \
		-o $(BUILDDIR)/test_$* \
		tests/$*.c

test-%: $(BUILDDIR)/test_%
	@:

run-%: $(BUILDDIR)/test_%
	@$(CURDIR)/scripts/run.sh $*

install: venv dpack stroll utils galv hed elog

clean:
	@rm -rf $(BUILDDIR)/troer-*
	@rm -rf $(BUILDDIR)/test-*
	@rm -f  $(BUILDDIR)/test_*
	@rm -f  $(DESTDIR)/usr/local/lib/libtest-*.a
	@rm -f  $(DESTDIR)/usr/local/lib/libtest-*.so
	@rm -f  $(DESTDIR)/usr/local/lib/pkgconfig/libtest-*.pc
	@rm -rf $(DESTDIR)/usr/local/include/test-*

clobber:
	@rm -rf $(EXTERNDIR)
	@rm -rf $(BUILDDIR)
	@rm -rf $(DESTDIR)
	@git restore $(EXTERNDIR)

$(EXTERNDIR) $(DEPENDSDIR):
	@mkdir -p $@

$(BUILDDIR)/% $(DESTDIR)/%:
	@mkdir -p $@

#################### DOWNLOAD

$(EXTERNDIR)/%: | $(EXTERNDIR)
	@[ -n "$($(call UP,GIT_$*))" ] && echo ===== Git clone $*
	@[ -n "$($(call UP,GIT_$*))" ] && git clone $($(call UP,GIT_$*)) $@

#################### AFL++

$(CC): | $(AFLDIR)
	@echo ===== build afl++
	@$(MAKE) -C $(AFLDIR) $(AFL_MAKE_ARGS) source-only
	@$(MAKE) -C $(AFLDIR) $(AFL_MAKE_ARGS) install

define extern_cmd
guiconfig-$(strip $(1)): | $$(EXTERNDIR)/$(strip $(1)) $$(EBUILDDIR) $$(AFLDIR) $$(CC)
	@$$(MAKE) -C $$(EXTERNDIR)/$(strip $(1)) $$(MAKE_ARGS) BUILDDIR:=$$(BUILDDIR)/$(strip $(1)) menuconfig

$$(BUILDDIR)/$(strip $(1))/.config: $$(BUILDDIR)/$(strip $(1)) | $$(EXTERNDIR)/$(strip $(1)) $$(EBUILDDIR) $$(AFLDIR) $$(CC)
	@cp defconfig/$(strip $(1)).defconfig $$@
	@$$(MAKE) -C $$(EXTERNDIR)/$(strip $(1)) $$(MAKE_ARGS) BUILDDIR:=$$(BUILDDIR)/$(strip $(1)) olddefconfig

$$(DESTDIR)/usr/local/lib/lib$(strip $(1)).a: $$(BUILDDIR)/$(strip $(1))/.config $(2)
	@echo ===== build $(strip $(1))
	@$$(MAKE) -C $$(EXTERNDIR)/$(strip $(1)) $$(MAKE_ARGS) BUILDDIR:=$$(BUILDDIR)/$(strip $(1)) build
	@$$(MAKE) -C $$(EXTERNDIR)/$(strip $(1)) $$(MAKE_ARGS) BUILDDIR:=$$(BUILDDIR)/$(strip $(1)) install

$(strip $(1)): $$(DESTDIR)/usr/local/lib/lib$(strip $(1)).a
endef

define extern_rules
$(eval $(call extern_cmd, $(1), $(2)))
endef

$(call extern_rules, stroll)
$(call extern_rules, utils, stroll)
$(call extern_rules, dpack, stroll)
$(call extern_rules, elog, utils)
$(call extern_rules, galv, elog)
$(call extern_rules, hed, galv dpack)

#################### VENV

$(PYTHON):
	@echo ===== Make python venv
	@$(PYTHON3) -m venv $(VENV)

$(VENV)/bin/troer: CHEETAH_C_EXTENSIONS_REQUIRED=1
$(VENV)/bin/troer: $(VENV)/bin/python3
	@echo ===== Install editable troer
	@$(PYTHON) -m pip install --force-reinstall --find-links "$(DEPENDSDIR)" -e .

venv: $(VENV)/bin/troer

.PHONY: pip-download
pip-download: | $(DEPENDSDIR)
	@echo ===== Download troer depends
	@cd $(DEPENDSDIR); $(PYTHON) -m pip download $(CURDIR)
	@cd $(DEPENDSDIR); $(PYTHON) -m pip download -r $(CURDIR)/install-depends.txt

.PHONY: all install clobber clean
