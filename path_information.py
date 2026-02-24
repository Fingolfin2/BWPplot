# 计算补全后的路径其他信息：
# 总行驶里程
# 平均速度
# 补全后的卡口序列和路网节点序列
# 经过每一个路网节点/卡口设备的经纬度
# 时间
# 2023/04/04 by chenxinyi

import time
import datetime

def get_path_coords(path, pos_name, pos_coord):
    points = []
    for p in path:
        index = pos_name.index(p)
        coord = pos_coord[index]
        points.append(coord)
    return points


def get_path_weight(G, path, weight):
    value = 0
    if len(path) > 1:
        for i in range(len(path)-1):
            u = path[i]
            v = path[i+1]
            value += G.edges[u,v][weight]
    return value


def get_path_bayonet(path, posname, bayonetname):
    bayonet_array = []
    pos_array = []
    for i in range(0, len(path)):
        try:
            index = posname.index(path[i])
        except:
            continue
        bayonet = bayonetname[index]
        pos = posname[index]
        bayonet_array.append(bayonet)
        pos_array.append(pos)
    return bayonet_array, pos_array


def addinfo(Complete_paths_tf, Complete_paths_pos, paths_travel, pos_names, pos_coords, realpos_names, bayonet_names, G):
    Complete_paths_bayonet = []     # 存储轨迹补全后途经的卡口
    Complete_paths_bayonetpos = []  # 存储卡口对应的路网节点
    Complete_paths_distance = []    # 存储行驶距离 单位:m
    Complete_paths_velocity = []    # 存储平均行驶速度 单位:m/s
    Complete_paths_coords = []      # 存储路网节点的经纬度坐标
    start = time.perf_counter()
    for i in range(0, len(Complete_paths_tf)):
        if Complete_paths_tf[i] == "get":
            try:
                distance = get_path_weight(G, Complete_paths_pos[i], 'length')
            except:
                print(i, ': Function(get_path_weight) fail')
                Complete_paths_tf[i] = 0
                Complete_paths_distance.append("null")
                Complete_paths_velocity.append("null")
                Complete_paths_coords.append("null")
                Complete_paths_bayonet.append("null")
                Complete_paths_bayonetpos.append("null")
                continue

            velocity = distance / paths_travel[i]
            coords = get_path_coords(Complete_paths_pos[i], pos_names, pos_coords)
            bayonets, poses = get_path_bayonet(Complete_paths_pos[i], realpos_names, bayonet_names)
            Complete_paths_distance.append(distance)
            Complete_paths_velocity.append(velocity)
            Complete_paths_coords.append(coords)
            Complete_paths_bayonet.append(bayonets)
            Complete_paths_bayonetpos.append(poses)
            # print(i)
        else:
            Complete_paths_distance.append("null")
            Complete_paths_velocity.append("null")
            Complete_paths_coords.append("null")
            Complete_paths_bayonet.append("null")
            Complete_paths_bayonetpos.append("null")
    # print('Done.')
    # end = time.perf_counter()
    # opt = end - start
    # print("CPU Time: ", opt, "s")
    # print("平均每条轨迹运行时间: ", opt / len(Complete_paths_tf), "s/条")

    return Complete_paths_distance, Complete_paths_velocity, Complete_paths_coords, \
           Complete_paths_bayonet


def addtime(Complete_paths_tf, paths_bayonet, Complete_paths_bayonet, Complete_paths_bayonetpos, Complete_paths_pos, paths_time, G):
    # 存储经过每个卡口的时间
    Complete_paths_time = []
    for i in range(0, len(Complete_paths_tf)):
        if Complete_paths_tf[i] == "get":
            origin_bayonets = paths_bayonet[i]
            bayonets = Complete_paths_bayonet[i]
            poses = Complete_paths_bayonetpos[i]
            complete_poses = Complete_paths_pos[i]
            t1 = paths_time[i][0]
            times = [t1]
            source_index = 0
            target_index = 0
            ss_index = 0
            tt_index = 0
            for j in range(len(origin_bayonets)-1):
                # 查找在原始卡口序列中的卡口在补全后的卡口序列中的位置
                source = origin_bayonets[j]
                target = origin_bayonets[j+1]
                try:
                    source_index = bayonets.index(source, target_index, len(bayonets))
                    target_index = bayonets.index(target, source_index+1, len(bayonets))
                except (Exception, BaseException) as e:
                    print(i)
                    print(repr(e))
                    Complete_paths_tf[i] = 0
                    break
                if (target_index-source_index)>1:
                    # 查找对应卡口之间的路径距离和行驶时间
                    ss_index = complete_poses.index(poses[source_index], tt_index, len(complete_poses))
                    tt_index = complete_poses.index(poses[target_index], ss_index+1, len(complete_poses))
                    # print('【', ss_index, '-', tt_index, '】')
                    Dist = get_path_weight(G, complete_poses[ss_index:tt_index+1], 'length')
                    Travel = (paths_time[i][j+1]-paths_time[i][j]).total_seconds()
                    s_index = 0
                    t_index = 0
                    for z in range(source_index, target_index):
                        if z==(target_index-1):
                            if t1==paths_time[i][j+1]:
                                t1 = paths_time[i][j+1]+datetime.timedelta(seconds=5)
                            else:
                                t1 = paths_time[i][j+1]
                            times.append(t1)
                            break
                        # 查找在卡口对应路网节点序列中的节点在完整路网节点轨迹序列中的位置
                        s = poses[z]
                        t = poses[z+1]
                        s_index = complete_poses.index(s, t_index, len(complete_poses))
                        t_index = complete_poses.index(t, s_index+1, len(complete_poses))
                        d = get_path_weight(G, complete_poses[s_index:t_index+1], 'length')
                        rate = d/Dist
                        tmin = round(Travel*rate)
                        # print(rate, tmin)
                        t1 = t1+datetime.timedelta(seconds=tmin)
                        times.append(t1)
                else:
                    t1 = paths_time[i][j+1]
                    times.append(t1)
            Complete_paths_time.append(times)
        else:
            Complete_paths_time.append("null")
    return Complete_paths_time