#!/bin/bash -e

topdir=$(realpath $(dirname $0)/..)
destdir=${topdir}/out
test_afl=${destdir}/bin/test_$1

echo Run $test_afl

export PATH=${topdir}/out/bin:${topdir}/out/usr/local/bin:$PATH
export LD_LIBRARY_PATH=${topdir}/out/lib:${topdir}/out/usr/local/lib:$LD_LIBRARY_PATH

case $1 in
	exchange) export LD_PRELOAD=${topdir}/build/libdesock/libdesock.so;;
esac
exec $test_afl
