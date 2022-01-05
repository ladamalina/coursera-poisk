#! /bin/bash

path=$1
cd ..
path_to_modules=`pwd`

PYTHONPATH=$PYTHONPATH:$path_to_modules python3 ./search_shell/shell.py $path
