#!/bin/bash -e

topdir=$(realpath $(dirname $0)/..)
builddir=${topdir}/build
test_afl=${builddir}/test_$1
input=${builddir}/input
output=${builddir}/afl

export PATH=${topdir}/out/bin:${topdir}/out/usr/local/bin:$PATH
export LD_LIBRARY_PATH=${topdir}/out/lib:${topdir}/out/usr/local/lib:$LD_LIBRARY_PATH

rm -rf ${builddir}/default
rm -rf $output
rm -rf $input

mkdir -p $input

echo Make $input/sample file
if ! out=$($test_afl $input/sample 2>&1); then
        echo -e "\n${out}"
        exit 1
fi

#echo Test $input/sample file
#if ! out=$(cat $input/sample | valgrind --leak-check=full --error-exitcode=1 $test_afl 2>&1); then
#        echo -e "\n${out}"
#        exit 1
#fi

echo Check with AFL $input/sample file
if ! out=$(AFL_DEBUG=1 afl-fuzz -V 1 -i $input -o ${builddir} $test_afl 2>&1); then
        echo -e "\n${out}"
        exit 1
fi

if [ $(ls ${builddir}/default/crashes/ | wc -l) -ne 0 ]; then
        echo ~~~~~~~~~~~~~~~~~~
        echo ~   Crash found  ~
        echo ~~~~~~~~~~~~~~~~~~
        exit 1
fi
tmux new-session -d -s real

## Create the windows on which each node or .launch file is going to run
tmux send-keys -t real 'tmux rename-window whatsup ' ENTER
tmux send-keys -t real 'tmux new-window -n main '    ENTER
tmux send-keys -t real 'tmux new-window -n fast '    ENTER
tmux send-keys -t real 'tmux new-window -n exploit ' ENTER
tmux send-keys -t real 'tmux new-window -n explore ' ENTER
tmux send-keys -t real 'tmux new-window -n seek '    ENTER
tmux send-keys -t real 'tmux new-window -n rare '    ENTER
tmux send-keys -t real 'tmux new-window -n mmopt '   ENTER
tmux send-keys -t real 'tmux new-window -n coe '     ENTER
tmux send-keys -t real 'tmux new-window -n lin '     ENTER
tmux send-keys -t real 'tmux new-window -n quad '    ENTER
tmux send-keys -t real 'tmux new-window -n lfast1 '  ENTER
tmux send-keys -t real 'tmux new-window -n lfast2 '  ENTER
tmux send-keys -t real 'tmux new-window -n lfast3 '  ENTER
tmux send-keys -t real 'tmux new-window -n lfast4 '  ENTER
tmux send-keys -t real 'tmux new-window -n lfast5 '  ENTER


## Send the command to each window from window 0
tmux send-keys -t real "tmux send-keys -t main    'PATH=$PATH AFL_IMPORT_FIRST=1 afl-fuzz -D -Z -i $input -o $output            -M main    $test_afl' ENTER" ENTER
tmux send-keys -t real "tmux send-keys -t fast    'PATH=$PATH AFL_IMPORT_FIRST=1 afl-fuzz       -i $input -o $output -p fast    -S fast    $test_afl' ENTER" ENTER
tmux send-keys -t real "tmux send-keys -t lfast1  'PATH=$PATH AFL_IMPORT_FIRST=1 afl-fuzz -L 0  -i $input -o $output -p fast    -S lfast1  $test_afl' ENTER" ENTER
tmux send-keys -t real "tmux send-keys -t lfast2  'PATH=$PATH AFL_IMPORT_FIRST=1 afl-fuzz -L 0  -i $input -o $output -p fast    -S lfast2  $test_afl' ENTER" ENTER
tmux send-keys -t real "tmux send-keys -t lfast3  'PATH=$PATH AFL_IMPORT_FIRST=1 afl-fuzz -L 0  -i $input -o $output -p fast    -S lfast3  $test_afl' ENTER" ENTER
tmux send-keys -t real "tmux send-keys -t lfast4  'PATH=$PATH AFL_IMPORT_FIRST=1 afl-fuzz -L 0  -i $input -o $output -p fast    -S lfast4  $test_afl' ENTER" ENTER
tmux send-keys -t real "tmux send-keys -t lfast5  'PATH=$PATH AFL_IMPORT_FIRST=1 afl-fuzz -L 0  -i $input -o $output -p fast    -S lfast5  $test_afl' ENTER" ENTER
tmux send-keys -t real "tmux send-keys -t exploit 'PATH=$PATH AFL_IMPORT_FIRST=1 afl-fuzz       -i $input -o $output -p exploit -S exploit $test_afl' ENTER" ENTER
tmux send-keys -t real "tmux send-keys -t explore 'PATH=$PATH AFL_IMPORT_FIRST=1 afl-fuzz       -i $input -o $output -p explore -S explore $test_afl' ENTER" ENTER
tmux send-keys -t real "tmux send-keys -t seek    'PATH=$PATH AFL_IMPORT_FIRST=1 afl-fuzz       -i $input -o $output -p seek    -S seek    $test_afl' ENTER" ENTER
tmux send-keys -t real "tmux send-keys -t rare    'PATH=$PATH AFL_IMPORT_FIRST=1 afl-fuzz       -i $input -o $output -p rare    -S rare    $test_afl' ENTER" ENTER
tmux send-keys -t real "tmux send-keys -t mmopt   'PATH=$PATH AFL_IMPORT_FIRST=1 afl-fuzz       -i $input -o $output -p mmopt   -S mmopt   $test_afl' ENTER" ENTER
tmux send-keys -t real "tmux send-keys -t coe     'PATH=$PATH AFL_IMPORT_FIRST=1 afl-fuzz       -i $input -o $output -p coe     -S coe     $test_afl' ENTER" ENTER
tmux send-keys -t real "tmux send-keys -t lin     'PATH=$PATH AFL_IMPORT_FIRST=1 afl-fuzz       -i $input -o $output -p lin     -S lin     $test_afl' ENTER" ENTER
tmux send-keys -t real "tmux send-keys -t quad    'PATH=$PATH AFL_IMPORT_FIRST=1 afl-fuzz       -i $input -o $output -p quad    -S quad    $test_afl' ENTER" ENTER

tmux send-keys -t real "tmux send-keys -t whatsup  'while true; do PATH=$PATH afl-whatsup -s $output/; sleep 10; clear; done' ENTER" ENTER
tmux send-keys -t real "tmux select-window -t whatsup " ENTER

## Attach to session
tmux attach -t real
