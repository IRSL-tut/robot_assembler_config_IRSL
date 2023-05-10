#

Setting files for robot_assembler_plugin ( https://github.com/IRSL-tut/robot_assembler_plugin )


# mass-paramの計算方法
特に指定のないものについては物体密度はFusion360のプラスチックの密度と同じ1.29(g/cm^3)で計算を行う．
## Dynamixel
公式のページを参考にする．  
XL430-W250は[このページ](https://emanual.robotis.com/docs/en/dxl/x/xl430-w250/)の一番下
## STLファイル(Fusion360を用いる場合)
1. 作成したボディの物理マテリアルを「プラスチック」に変更する．変更方法は[ここ](http://fusion360.blog.jp/model/modify/physical-material)を参考にする
1. [ボディのプロパティ](https://www.autodesk.co.jp/support/technical/article/caas/sfdcarticles/sfdcarticles/JPN/How-to-Find-Mass-Properties-in-Fusion-360.html)からCoGや重心回りの慣性テンソルを取得する.

## STLファイル([numpy-stl](https://github.com/WoLpH/numpy-stl/)を用いる場合)
以下のpythonコードにて取得する．
```
from stl import mesh
density = 1.29 
stl_abs_filename = 'object.stl'
stl_m = mesh.Mesh.from_file(stl_abs_filename)
stl_mass, stl_cog, stl_iner = stl_m.get_mass_properties()
print("CoG : ", stl_cog)
print("Inertia : \n", stl_iner * (density/10**3))

```
## BOX定義の場合
[ここ](https://moment-of-inertia.jp/moi/cuboid.html)を参考に慣性計算する．

# configチェックツール
tool/check_config.pyで簡易的にmass-paramのチェックを行うことができる．
```
python3 tools/check_config.py 
```