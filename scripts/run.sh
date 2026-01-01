#!/bin/bash -e

topdir=$(realpath $(dirname $0)/..)
builddir=${topdir}/build
test_afl=${builddir}/test_$1

export PATH=${topdir}/out/bin:${topdir}/out/usr/local/bin:$PATH
export LD_LIBRARY_PATH=${topdir}/out/lib:${topdir}/out/usr/local/lib:$LD_LIBRARY_PATH

echo Run $test_afl
exec $test_afl
