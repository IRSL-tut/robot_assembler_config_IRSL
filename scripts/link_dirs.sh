#!/bin/bash

DIR="$(dirname "$0")/.."

cd ${DIR}

rm -rf meshes_vis meshes_col

if [ "$1" == "raw" ]; then
    ln -sf meshes_raw    meshes_vis
else
    ln -sf meshes_small  meshes_vis
fi

ln -sf meshes_convex meshes_col
