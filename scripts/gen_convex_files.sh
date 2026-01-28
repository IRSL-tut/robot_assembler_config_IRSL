#!/bin/bash

#pip install --user --break-system-packages trimesh coacd

OPTIONS="-nm -d -dt 32 -pr 128 -t 0.09"

if [ -e meshes_convex ]; then
    rm -rf meshes_convex
fi
cp -r meshes meshes_convex

for ff in $(find meshes -name '*.stl'); do
    fnew=$(echo $ff | sed -e 's@meshes/@meshes_convex/@');
    fobj="${fnew%.*}.obj"
    coacd ${OPTIONS} -i ${ff} -o ${fobj}
    if [ -e ${fobj} ]; then
        rm -rf ${fnew}
    fi
done

# <COACD>
#   -t THRESHOLD, --threshold THRESHOLD
#                         termination criteria in [0.01, 1] (0.01: most fine-grained; 1: most coarse)
#   -pm PREPROCESS_MODE, --preprocess-mode PREPROCESS_MODE
#                         No remeshing before running CoACD. Only suitable for manifold input.
#   -r RESOLUTION, --resolution RESOLUTION
#                         surface samping resolution for Hausdorff distance computation
#   -nm, --no-merge       If merge is enabled, try to reduce total number of parts by merging.
#   -d, --decimate        If decimate is enabled, reduce total number of vertices per convex hull to max_ch_vertex.
#   -dt MAX_CH_VERTEX, --max-ch-vertex MAX_CH_VERTEX
#                         max # vertices per convex hull, works only when decimate is enabled
#   -ex, --extrude        If extrude is enabled, extrude the neighboring convex hulls along the overlap face (other faces are unchanged).
#   -em EXTRUDE_MARGIN, --extrude-margin EXTRUDE_MARGIN
#                         extrude margin, works only when extrude is enabled
#   -c MAX_CONVEX_HULL, --max-convex-hull MAX_CONVEX_HULL
#                         max # convex hulls in the result, -1 for no limit, works only when merge is enabled
#   -mi MCTS_ITERATION, --mcts-iteration MCTS_ITERATION
#                         Number of MCTS iterations.
#   -md MCTS_MAX_DEPTH, --mcts-max-depth MCTS_MAX_DEPTH
#                         Maximum depth for MCTS search.
#   -mn MCTS_NODE, --mcts-node MCTS_NODE
#                         Number of cut candidates for MCTS.
#   -pr PREP_RESOLUTION, --prep-resolution PREP_RESOLUTION
#                         Preprocessing resolution.
#   --pca                 Use PCA to align input mesh. Suitable for non-axis-aligned mesh.
#   -am APX_MODE, --apx-mode APX_MODE
#                         Approximation shape mode (ch/box).
#   --seed SEED           Random seed.
# 
# [CoACD] [info] threshold               0.05
# [CoACD] [info] max # convex hull       -1
# [CoACD] [info] preprocess mode         auto
# [CoACD] [info] preprocess resolution   50
# [CoACD] [info] pca                     false
# [CoACD] [info] mcts max depth          3
# [CoACD] [info] mcts nodes              20
# [CoACD] [info] mcts iterations         150
# [CoACD] [info] merge                   true
# [CoACD] [info] decimate                false
# [CoACD] [info] max_ch_vertex           256
# [CoACD] [info] extrude                 false
# [CoACD] [info] extrude margin          0.01
# [CoACD] [info] approximate mode        ch
# [CoACD] [info] seed                    0
