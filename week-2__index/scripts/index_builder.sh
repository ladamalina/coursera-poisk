#! /bin/bash

path=$1

cd ..
path_to_modules=`pwd`

PYTHONPATH=$PYTHONPATH:$path_to_modules python3 ./index/builder.py $path
