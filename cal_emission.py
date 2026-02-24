# 分路段计算污染物排放量
# 2023/04/20 by chenxinyi

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import geopandas as gpd
from shapely import geometry
import warnings
import time


# FUNCTION: 计算特定小时下路段的NOx排放量
def cal_segment_NOx(segment, vehicle_travel, nodes_info_node, bayonets_info_node, bayonets_info_time, target_hour):
    """

    :param segment: 路段信息 DataFrame['o', 'd', 'length', 'od']
    :param vehicle_travel: 车辆出行信息及对应的排放因子 DataFrame
    :param nodes_info_node: 轨迹经过的每一路网节点
    :param bayonets_info_node: 轨迹经过的每一交通卡口
    :param bayonets_info_time: 轨迹经过的每一交通卡口对应时刻
    :param target_hour: 指定小时时刻
    :return: 路段小时NOx排放量(g)、路段车流量(veh/h)
    """

    # 路段平均车速
    segment['velocity'] = 0

    # 路段流量及车型比例数据
    segment['flow'] = 0
    segment['hm-0-flow'] = 0
    segment['hm-1-flow'] = 0
    segment['hm-2-flow'] = 0
    segment['hm-3-flow'] = 0
    segment['hm-4-flow'] = 0
    segment['hm-5-flow'] = 0
    segment['hm-6-flow'] = 0
    segment['light-0-flow'] = 0
    segment['light-1-flow'] = 0
    segment['light-2-flow'] = 0
    segment['light-3-flow'] = 0
    segment['light-4-flow'] = 0
    segment['light-5-flow'] = 0
    segment['light-6-flow'] = 0

    # 路段NOx排放数据
    segment['NOx'] = 0
    segment['hm-0-NOx'] = 0
    segment['hm-1-NOx'] = 0
    segment['hm-2-NOx'] = 0
    segment['hm-3-NOx'] = 0
    segment['hm-4-NOx'] = 0
    segment['hm-5-NOx'] = 0
    segment['hm-6-NOx'] = 0
    segment['light-0-NOx'] = 0
    segment['light-1-NOx'] = 0
    segment['light-2-NOx'] = 0
    segment['light-3-NOx'] = 0
    segment['light-4-NOx'] = 0
    segment['light-5-NOx'] = 0
    segment['light-6-NOx'] = 0

    # 单轨迹
    iter = len(vehicle_travel)
    # start = time.perf_counter()
    for i in range(iter):
        if vehicle_travel.loc[i, 'completion'] == 'get':
            CLLX = vehicle_travel.loc[i, 'CLLX']
            PFBZ = vehicle_travel.loc[i, 'PFBZ']
            speed = vehicle_travel.loc[i, 'velocity']
            EF = vehicle_travel.loc[i, 'EF']
            path = nodes_info_node[i]
            bigseg_node = bayonets_info_node[i]
            bigseg_time = bayonets_info_time[i]

            # 单轨迹、单路段
            loc = 0
            for j in range(len(path) - 1):
                # 判断时间是否在单位尺度内
                refer_time = bigseg_time[loc]
                # print(refer_time)
                if refer_time.hour == target_hour:
                    seg_o = path[j]
                    seg_d = path[j + 1]
                    seg_od = seg_o + ':' + seg_d
                    # 查找对应的路段索引
                    index = segment[segment['od'] == seg_od].index.tolist()

                    if index:
                        index = index[0]

                        # 计算路段的平均车速之和
                        segment.loc[index, 'velocity'] = segment.loc[index, 'velocity'] + speed

                        # 计算路段污染物的总排放量/车流量
                        seg_NOx = segment.loc[index, 'length'] * EF
                        segment.loc[index, 'NOx'] = segment.loc[index, 'NOx'] + seg_NOx
                        segment.loc[index, 'flow'] = segment.loc[index, 'flow'] + 1
                        # print(j, segment.loc[index, 'od'], segment.loc[index, 'NOx(g)'])

                        # 计算分车型、排放标准的污染物排放量/车流量
                        # 国0
                        if PFBZ == '国0' and CLLX in ['H1', 'H2']:
                            segment.loc[index, 'hm-0-NOx'] = segment.loc[index, 'hm-0-NOx'] + seg_NOx
                            segment.loc[index, 'hm-0-flow'] = segment.loc[index, 'hm-0-flow'] + 1
                        if PFBZ == '国0' and CLLX == 'H3':
                            segment.loc[index, 'light-0-NOx'] = segment.loc[index, 'light-0-NOx'] + seg_NOx
                            segment.loc[index, 'light-0-flow'] = segment.loc[index, 'light-0-flow'] + 1
                        # 国1
                        if PFBZ == '国1' and CLLX in ['H1', 'H2']:
                            segment.loc[index, 'hm-1-NOx'] = segment.loc[index, 'hm-1-NOx'] + seg_NOx
                            segment.loc[index, 'hm-1-flow'] = segment.loc[index, 'hm-1-flow'] + 1
                        if PFBZ == '国1' and CLLX == 'H3':
                            segment.loc[index, 'light-1-NOx'] = segment.loc[index, 'light-1-NOx'] + seg_NOx
                            segment.loc[index, 'light-1-flow'] = segment.loc[index, 'light-1-flow'] + 1
                        # 国2
                        if PFBZ == '国2' and CLLX in ['H1', 'H2']:
                            segment.loc[index, 'hm-2-NOx'] = segment.loc[index, 'hm-2-NOx'] + seg_NOx
                            segment.loc[index, 'hm-2-flow'] = segment.loc[index, 'hm-2-flow'] + 1
                        if PFBZ == '国2' and CLLX == 'H3':
                            segment.loc[index, 'light-2-NOx'] = segment.loc[index, 'light-2-NOx'] + seg_NOx
                            segment.loc[index, 'light-2-flow'] = segment.loc[index, 'light-2-flow'] + 1
                        # 国3
                        if PFBZ == '国3' and CLLX in ['H1', 'H2']:
                            segment.loc[index, 'hm-3-NOx'] = segment.loc[index, 'hm-3-NOx'] + seg_NOx
                            segment.loc[index, 'hm-3-flow'] = segment.loc[index, 'hm-3-flow'] + 1
                        if PFBZ == '国3' and CLLX == 'H3':
                            segment.loc[index, 'light-3-NOx'] = segment.loc[index, 'light-3-NOx'] + seg_NOx
                            segment.loc[index, 'light-3-flow'] = segment.loc[index, 'light-3-flow'] + 1
                        # 国4
                        if PFBZ == '国4' and CLLX in ['H1', 'H2']:
                            segment.loc[index, 'hm-4-NOx'] = segment.loc[index, 'hm-4-NOx'] + seg_NOx
                            segment.loc[index, 'hm-4-flow'] = segment.loc[index, 'hm-4-flow'] + 1
                        if PFBZ == '国4' and CLLX == 'H3':
                            segment.loc[index, 'light-4-NOx'] = segment.loc[index, 'light-4-NOx'] + seg_NOx
                            segment.loc[index, 'light-4-flow'] = segment.loc[index, 'light-4-flow'] + 1
                        # 国5
                        if PFBZ == '国5' and CLLX in ['H1', 'H2']:
                            segment.loc[index, 'hm-5-NOx'] = segment.loc[index, 'hm-5-NOx'] + seg_NOx
                            segment.loc[index, 'hm-5-flow'] = segment.loc[index, 'hm-5-flow'] + 1
                        if PFBZ == '国5' and CLLX == 'H3':
                            segment.loc[index, 'light-5-NOx'] = segment.loc[index, 'light-5-NOx'] + seg_NOx
                            segment.loc[index, 'light-5-flow'] = segment.loc[index, 'light-5-flow'] + 1
                        # 国6
                        if PFBZ == '国6' and CLLX in ['H1', 'H2']:
                            segment.loc[index, 'hm-6-NOx'] = segment.loc[index, 'hm-6-NOx'] + seg_NOx
                            segment.loc[index, 'hm-6-flow'] = segment.loc[index, 'hm-6-flow'] + 1
                        if PFBZ == '国6' and CLLX == 'H3':
                            segment.loc[index, 'light-6-NOx'] = segment.loc[index, 'light-6-NOx'] + seg_NOx
                            segment.loc[index, 'light-6-flow'] = segment.loc[index, 'light-6-flow'] + 1

                if path[j + 1] == bigseg_node[loc + 1]:
                    loc = loc + 1

        #     print(i)
        # else:
        #     print('No reconstruction path, pass')

    # end = time.perf_counter()
    # opt = end - start
    # print("CPU Time: ", int(opt), "s ", int(opt / 60), "min ", int(opt / 3600), "h")
    # print("平均每条轨迹重构运行时间: ", opt / iter, "s/条")
    # print('Done.')

    # 计算路段的平均车速
    segment['velocity'] = segment['velocity']/segment['flow']

    # 分中重型柴油货车和轻型柴油货车两类统计排放量/车流量
    segment['hm-NOx'] = segment['hm-0-NOx'] + segment['hm-1-NOx'] + segment['hm-2-NOx'] + \
                        segment['hm-3-NOx'] + segment['hm-4-NOx'] + segment['hm-5-NOx'] + \
                        segment['hm-6-NOx']
    segment['light-NOx'] = segment['light-0-NOx'] + segment['light-1-NOx'] + segment['light-2-NOx'] + \
                           segment['light-3-NOx'] + segment['light-4-NOx'] + segment['light-5-NOx'] + \
                           segment['light-6-NOx']
    segment['hm-flow'] = segment['hm-0-flow'] + segment['hm-1-flow'] + segment['hm-2-flow'] + \
                         segment['hm-3-flow'] + segment['hm-4-flow'] + segment['hm-5-flow'] + \
                         segment['hm-6-flow']
    segment['light-flow'] = segment['light-0-flow'] + segment['light-1-flow'] + segment['light-2-flow'] + \
                         segment['light-3-flow'] + segment['light-4-flow'] + segment['light-5-flow'] + \
                         segment['light-6-flow']

    # 提取有污染物排放的路段
    segment_valid = segment[segment['NOx'] != 0]
    segment_valid = segment_valid.reset_index(drop=True)

    return segment, segment_valid


# FUNCTION: 构建路段污染物排放shapefile文件
def build_shapefile(segment_valid, pos_name, pos_coord):
    """

    :param segment_valid: 路段污染物排放数据DataFrame
    :param pos_name: 路网节点
    :param pos_coord: 路网节点对应的经纬度坐标
    :return: shapefile文件
    """

    # 匹配路段的OD经纬度坐标

    segment_coord = []
    # start = time.perf_counter()
    for i in range(len(segment_valid)):
        pos_o = segment_valid.loc[i, 'o']
        pos_d = segment_valid.loc[i, 'd']
        index_o = pos_name.index(pos_o)
        index_d = pos_name.index(pos_d)
        coord_o = pos_coord[index_o]
        coord_d = pos_coord[index_d]
        segment_coord.append([coord_o, coord_d])
        # print(i)

    # end = time.perf_counter()
    # opt = end - start
    # print("CPU Time: ", int(opt), "s ", int(opt / 60), "min ", int(opt / 3600), "h")
    # print('Done.')


    # 构建路网shapefile文件

    info_table = []
    geo_table = []
    for i in range(0, len(segment_valid)):

        # 属性信息
        info_table.append([segment_valid.loc[i, 'o'], segment_valid.loc[i, 'd'], segment_valid.loc[i, 'length'],
                           segment_valid.loc[i, 'od'], segment_valid.loc[i, 'velocity'],
                           segment_valid.loc[i, 'NOx'], segment_valid.loc[i, 'flow'],
                           segment_valid.loc[i, 'hm-NOx'], segment_valid.loc[i, 'light-NOx'],
                           segment_valid.loc[i, 'hm-flow'], segment_valid.loc[i, 'light-flow']])

        # 空间信息
        line = geometry.LineString(segment_coord[i])
        geo_table.append(line)

    segment_shp = gpd.GeoDataFrame(info_table, geometry=geo_table, crs='EPSG:4326')
    segment_shp.columns = ['o', 'd', 'length', 'od', 'velocity', 'NOx', 'flow', 'hm-NOx', 'light-NOx',
                           'hm-flow', 'light-flow', 'geometry']

    return segment_shp