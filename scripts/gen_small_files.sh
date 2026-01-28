#!/bin/bash

## move to upper directory
DIR="$(dirname "$0")/.."
cd ${DIR}

if [ -e meshes_small ]; then
    rm -rf meshes_small
fi

cp -r meshes meshes_small

for ff in $(find meshes -name '*.stl'); do
    fnew=$(echo $ff | sed -e 's@meshes/@meshes_small/@');
    meshlabserver -i $ff -o $fnew -s scripts/mesh_reduction.mlx;
done
