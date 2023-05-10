#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import yaml
import os
import numpy as np
from stl import mesh

# 直方体の慣性テンソルより逆算
# https://moment-of-inertia.jp/moi/cuboid.html
def calc_cuboid_edge(mass, ixx, iyy, izz):
    a = np.sqrt(3.0/2.0/mass*(-ixx+iyy+izz))*2.0
    b = np.sqrt(3.0/2.0/mass*( ixx-iyy+izz))*2.0
    c = np.sqrt(3.0/2.0/mass*( ixx+iyy-izz))*2.0
    return np.sort([a, b, c]).tolist()


if __name__=='__main__':
    parser = argparse.ArgumentParser(
        prog='check configfile', # プログラム名
        # usage='', # プログラムの利用方法
        add_help=True, # -h/–help オプションの追加
        )
    parser.add_argument('--configfile', type=str, default="irsl_assembler_config.yaml")
    parser.add_argument('--density', type=float, default="1.29")
    parser.add_argument('--error_vol_th', type=float, default="0.02")
    parser.add_argument('--error_edge_th', type=float, default="0.02")
    parser.add_argument('--th_cogs', type=float, default="1")
    parser.add_argument('--dispall', action='store_true')
    parser.add_argument('--parts', nargs="*", type=str, default=[])

    args = parser.parse_args()
    config_filename = args.configfile
    density = args.density
    error_vol_th = args.error_vol_th
    error_edge_th = args.error_edge_th
    th_cogs = args.th_cogs

    # yamlファイルを読み込む
    with open(config_filename, 'r') as f:
        obj = yaml.safe_load(f)

    # 使用しているパーツのリストを作成
    parts_name_list = []
    for tab in obj["PanelSettings"]["tab_list"]:
        for parts_name in tab["parts"]:
            parts_name_list.append(parts_name)
    for parts_name in obj["PanelSettings"]["combo_list"]:
        parts_name_list.append(parts_name)

    for p in obj["PartsSettings"]:
        # mass-paramがないパーツは対象外とする
        if not 'mass-param' in p:
            continue

        # panelやtabに入っていないパーツは対象外とする
        if not p["type"] in parts_name_list:
            continue

        # deprecatedなパーツは対象外とする
        if "description" in p and p["description"].find("deprecated") != -1:
            continue

        # 都合 複数の要素から構成されているパーツはチェック対象外とする
        if len(p['visual']) > 1:
            continue

        # 引数で指定されたパーツではないときはチェック対象外とする
        if len(args.parts) >0 and not p['type'] in args.parts:
            continue

        # settingのmass-paramに従い慣性テンソルより想定される直方体の大きさを計算する
        setting_cog = p['mass-param']['center-of-mass']
        setting_inertia = p['mass-param']['inertia-tensor']
        setting_mass = p['mass-param']['mass']
        setting_cog = np.array(setting_cog)
        setting_inertia = np.array(setting_inertia).reshape(3,3)
        setting_w, setting_v = np.linalg.eig(setting_inertia)
        setting_edge = calc_cuboid_edge(setting_mass,  setting_w[0],  setting_w[1],  setting_w[2])
        setting_vol = np.prod(setting_edge)

        # stlファイルの場合
        if 'type' in p['visual'][0] and p['visual'][0]['type'] == 'mesh':
            #stlファイルを読み込み,scaleに合わせてcogとinertiaを変換する
            stl_filename = p['visual'][0]['url']
            scale = p['visual'][0]['scale'] * 1000
            stl_abs_filename = os.path.join(os.path.dirname(config_filename), stl_filename)
            stl_m = mesh.Mesh.from_file(stl_abs_filename)
            stl_mass, stl_cog, stl_iner = stl_m.get_mass_properties()

            stl_cog = np.array(stl_cog) * scale
            stl_iner = np.array(stl_iner) * density/1000 * (scale**5)

            # 慣性テンソルより想定される直方体の大きさを計算する
            stl_w, stl_v = np.linalg.eig(stl_iner)
            stl_edge = calc_cuboid_edge(setting_mass,  stl_w[0],  stl_w[1],  stl_w[2])
            stl_vol = np.prod(stl_edge)

            # 以下条件でメッセージを出力する
            # 体積の大きさの誤差率がsetting基準でしきい値より大きい場合
            # 辺長さの誤差率がsetting基準でしきい値より大きい場合
            # stlとsettingのcogの距離がしきい値より大きい場合
            error_vol = np.abs(setting_vol-stl_vol)/(setting_vol)
            error_edge = np.max(np.abs(np.array(setting_edge)-np.array(stl_edge))/np.array(setting_edge))
            length_cogs = np.linalg.norm(setting_cog-stl_cog)
            if  args.dispall or error_vol > error_vol_th or error_edge > error_edge_th or length_cogs > th_cogs:
                print("type name : ", p["type"])
                print("setting cog : ", setting_cog)
                print("stl cog : ", stl_cog)
                print("setting inertia : \n", setting_inertia)
                print("stl inertia : \n",stl_iner)
                print("setting cuboid size : ", setting_edge)
                print("stl cuboid size : ", stl_edge)
                print('-'*32)
        # box定義の場合
        elif 'box' in p['visual'][0]:
            #box体積を計算する
            box_vol = np.prod(p['visual'][0]['box'])
            # 以下条件でメッセージを出力する
            # 辺長さの誤差率がsetting基準でしきい値より大きい場合
            # stlとsettingのcogの距離がしきい値より大きい場合
            error_edge = np.max(np.abs(np.array(setting_edge)-np.sort(p['visual'][0]['box']))/np.array(setting_edge))
            length_cogs = np.linalg.norm(setting_cog-np.array(p['visual'][0]['translation']))
            if  args.dispall or error_edge > error_edge_th or length_cogs > th_cogs:
                tmp = (np.array(p['visual'][0]['box'])/2)**2
                box_inertia = setting_mass/3 * np.diag(np.sum(tmp)-tmp)
                print("type name : ", p["type"])
                print("setting cog : ", setting_cog)
                print("box cog : ", np.array(p['visual'][0]['translation']))
                print("setting inertia : \n", setting_inertia)
                print("box inertia : \n", box_inertia)
                # print("setting cuboid size : ", setting_edge)
                # print("box size : ",p['visual'][0]['box'])
                print('-'*32)


