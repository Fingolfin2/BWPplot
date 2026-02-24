# 路径规划相关函数
# 2023/04/04 by chenxinyi

import networkx as nx
from heapq import heappush, heappop
from itertools import count
import copy


def get_path_attr(G, k_durations, k_paths, source_time, target_time):
    # 创建决策属性表
    n = len(k_paths)
    if len(k_paths) == 1:
        attr = []
    elif len(k_paths) == 2:
        attr = [[], []]
    elif len(k_paths) == 3:
        attr = [[], [], []]
    elif len(k_paths) == 4:
        attr = [[], [], [], []]
    elif len(k_paths) == 5:
        attr = [[], [], [], [], []]
    else:
        attr = [[]] * n
    for k in range(0, len(k_paths)):
        # 计算路径距离
        length = get_path_weight(G, k_paths[k], 'length')
        # 统计路径途经交叉口数量
        crossing_num = 0
        for node in k_paths[k]:
            if "LINK" in node:
                crossing_num = crossing_num+1
        # 计算路径行程时间相符程度
        real_duration = (target_time-source_time).total_seconds()
        if real_duration == 0:
            duration_rate = 0
        else:
            duration_rate = abs(real_duration-k_durations[k])/real_duration
        # 计算路径的道路类型指数
        kind_index = get_path_kindindex(G, k_paths[k])
        if len(k_paths) > 1:
            attr[k].extend((length, crossing_num, kind_index, duration_rate))
        else:
            attr.extend((length, crossing_num, kind_index, duration_rate))
        # print("路径%s: 路径长度%.4f 途经交叉口数%.0f 道路类型(1-7)%.2f 行程时间相符程度%.2f" % (k+1, length, crossing_num, kind_index, duration_rate))
    return attr


def get_path_coords(path, pos_name, pos_coord):
    points = []
    for p in path:
        index = pos_name.index(p)
        coord = pos_coord[index]
        points.append(coord)
    return points


def get_path_kindindex(G, path):
    total_length = 0
    total_value = 0
    if len(path) > 1:
        for i in range(len(path)-1):
            u = path[i]
            v = path[i+1]
            length_uv = G.edges[u,v]['length']
            kind_uv = G.edges[u,v]['kind']
            value_uv = kind_uv*length_uv
            total_value += value_uv
            total_length += length_uv
        total_kind = total_value/total_length
    return total_kind


def get_path_weight(G, path, weight):
    value = 0
    if len(path) > 1:
        for i in range(len(path)-1):
            u = path[i]
            v = path[i+1]
            value += G.edges[u,v][weight]
    return value


def k_shortest_paths_origin(G, source, target, k=3, weight='duration'):
    """
    原始k则最短路径算法（dijkstra）
    Returns the k-shortest paths from source to target in a weighted graph G.
    Parameters
    ----------
    G : NetworkX graph
    source : node
       Starting node
    target : node
       Ending node
    k : integer, optional (default=3)
       The number of shortest paths to find
    weight: string, optional (default='weight')
       Edge data key corresponding to the edge weight
    Returns
    ----------
    worths, paths : lists
       Returns a tuple with two lists.
       The first list stores the worth of each k-shortest path.
       The second list stores each k-shortest path.
    Raises
    ----------
    NetworkXNoPath
       If no path exists between source and target.
    Notes
    ----------
    Edge weight attributes must be numerical and non-negative.
    Distances are calculated as sums of weighted edges traversed.
    """

    if source == target:
        return ([], [])

    try:
        # dijkstra
        worth, path = nx.single_source_dijkstra(G, source, target, weight=weight)

    except:
        print("node %s not reachable from %s" % (source, target))
        return ([], [])

    worths = [worth]
    paths = [path]
    c = count()
    B = []
    G_original = copy.deepcopy(G)
    G_renew = copy.deepcopy(G)

    for i in range(1, k):
        for j in range(len(paths[-1]) - 1):
            spur_node = paths[-1][j]
            root_path = paths[-1][:j + 1]

            edges_removed = []
            for c_path in paths:
                if len(c_path) > j and root_path == c_path[:j + 1]:
                    u = c_path[j]
                    v = c_path[j + 1]
                    if G_renew.has_edge(u, v):
                        edge_attr = G_renew.edges[u, v]
                        G_renew.remove_edge(u, v)
                        edges_removed.append((u, v, edge_attr))

            for n in range(len(root_path) - 1):
                node = root_path[n]
                # out-edges
                for u, v, edge_attr in list(G_renew.edges(node, data=True)):
                    G_renew.remove_edge(u, v)
                    edges_removed.append((u, v, edge_attr))

                if G_renew.is_directed():
                    # in-edges
                    for u, v, edge_attr in list(G_renew.in_edges(node, data=True)):
                        G_renew.remove_edge(u, v)
                        edges_removed.append((u, v, edge_attr))
            try:
                # dijkstra
                spur_path_length, spur_path = nx.single_source_dijkstra(G_renew, spur_node, target, weight=weight)
                # astar
                # spur_path = nx.astar_path(G_renew, spur_node, target, heuristic=None, weight=weight)
                # spur_path_length = nx.astar_path_length(G_renew, spur_node, target, heuristic=None, weight=weight)
                total_path = root_path[:-1] + spur_path
                total_path_length = get_path_weight(G_original, root_path, weight) + spur_path_length
                heappush(B, (total_path_length, next(c), total_path))
                for e in edges_removed:
                    u, v, edge_attr = e
                    G_renew.add_edge(u, v, weight=edge_attr[weight])
            except:
                # print("Starting at %s, there is no spur path" % spur_node)
                continue

        if B:
            (l, _, p) = heappop(B)
            worths.append(l)
            paths.append(p)
        else:
            break

    return worths, paths


def k_shortest_paths(G, source, target, k=3, weight='duration'):
    """
    改进的k则最短路径算法（dijkstra→astar）
    """

    if source == target:
        return ([], [])

    try:
        # dijkstra
        # worth, path = nx.single_source_dijkstra(G, source, target, weight=weight)
        # astar
        path = nx.astar_path(G, source, target, heuristic=None, weight=weight)
        worth = nx.astar_path_length(G, source, target, heuristic=None, weight=weight)

    except:
        # print("node %s not reachable from %s" % (target, source))
        return ([], [])

    worths = [worth]
    paths = [path]
    c = count()
    B = []
    G_original = copy.deepcopy(G)
    G_renew = copy.deepcopy(G)

    for i in range(1, k):
        for j in range(len(paths[-1]) - 1):
            spur_node = paths[-1][j]
            root_path = paths[-1][:j + 1]

            edges_removed = []
            for c_path in paths:
                if len(c_path) > j and root_path == c_path[:j + 1]:
                    u = c_path[j]
                    v = c_path[j + 1]
                    if G_renew.has_edge(u, v):
                        edge_attr = G_renew.edges[u, v]
                        G_renew.remove_edge(u, v)
                        edges_removed.append((u, v, edge_attr))

            for n in range(len(root_path) - 1):
                node = root_path[n]
                # out-edges
                for u, v, edge_attr in list(G_renew.edges(node, data=True)):
                    G_renew.remove_edge(u, v)
                    edges_removed.append((u, v, edge_attr))

                if G_renew.is_directed():
                    # in-edges
                    for u, v, edge_attr in list(G_renew.in_edges(node, data=True)):
                        G_renew.remove_edge(u, v)
                        edges_removed.append((u, v, edge_attr))
            try:
                # dijkstra
                # spur_path_length, spur_path = nx.single_source_dijkstra(G_renew, spur_node, target, weight=weight)
                # astar
                spur_path = nx.astar_path(G_renew, spur_node, target, heuristic=None, weight=weight)
                spur_path_length = nx.astar_path_length(G_renew, spur_node, target, heuristic=None, weight=weight)
                total_path = root_path[:-1] + spur_path
                total_path_length = get_path_weight(G_original, root_path, weight) + spur_path_length
                heappush(B, (total_path_length, next(c), total_path))
                for e in edges_removed:
                    u, v, edge_attr = e
                    G_renew.add_edge(u, v, weight=edge_attr[weight])
            except:
                # print("Starting at %s, there is no spur path" % spur_node)
                continue

        if B:
            (l, _, p) = heappop(B)
            worths.append(l)
            paths.append(p)
        else:
            break

    return worths, paths


def k_shortest_paths_select(G, source, target, k=3, weight='duration'):
    """
    改进的k则最短路径算法（dijkstra→astar）
    当最短路径经过的路网节点数＞10时，才启动k则最短路径算法
    """

    if source == target:
        return ([], [])

    try:
        # astar
        path = nx.astar_path(G, source, target, heuristic=None, weight=weight)
        worth = nx.astar_path_length(G, source, target, heuristic=None, weight=weight)
        if len(path) <= 10:
            worths = [worth]
            paths = [path]
            return worths, paths

    except:
        # print("node %s not reachable from %s" % (source, target))
        return ([], [])

    worths = [worth]
    paths = [path]
    c = count()
    B = []
    G_original = copy.deepcopy(G)
    G_renew = copy.deepcopy(G)

    for i in range(1, k):
        for j in range(len(paths[-1]) - 1):
            spur_node = paths[-1][j]
            root_path = paths[-1][:j + 1]

            edges_removed = []
            for c_path in paths:
                if len(c_path) > j and root_path == c_path[:j + 1]:
                    u = c_path[j]
                    v = c_path[j + 1]
                    if G_renew.has_edge(u, v):
                        edge_attr = G_renew.edges[u, v]
                        G_renew.remove_edge(u, v)
                        edges_removed.append((u, v, edge_attr))

            for n in range(len(root_path) - 1):
                node = root_path[n]
                # out-edges
                for u, v, edge_attr in list(G_renew.edges(node, data=True)):
                    G_renew.remove_edge(u, v)
                    edges_removed.append((u, v, edge_attr))

                if G_renew.is_directed():
                    # in-edges
                    for u, v, edge_attr in list(G_renew.in_edges(node, data=True)):
                        G_renew.remove_edge(u, v)
                        edges_removed.append((u, v, edge_attr))
            try:
                # dijkstra
                # spur_path_length, spur_path = nx.single_source_dijkstra(G_renew, spur_node, target, weight=weight)
                # astar
                spur_path = nx.astar_path(G_renew, spur_node, target, heuristic=None, weight=weight)
                spur_path_length = nx.astar_path_length(G_renew, spur_node, target, heuristic=None, weight=weight)
                total_path = root_path[:-1] + spur_path
                total_path_length = get_path_weight(G_original, root_path, weight) + spur_path_length
                heappush(B, (total_path_length, next(c), total_path))
                for e in edges_removed:
                    u, v, edge_attr = e
                    G_renew.add_edge(u, v, weight=edge_attr[weight])
            except:
                # print("Starting at %s, there is no spur path" % spur_node)
                continue

        if B:
            (l, _, p) = heappop(B)
            worths.append(l)
            paths.append(p)
        else:
            break

    return worths, paths


def topsis(k_paths, attr, W):
    if len(k_paths) == 1:
        index = 0
        best_path = [i for arr in k_paths for i in arr]
        return index, best_path
    # 1.决策矩阵标准化
    n = len(k_paths)
    m = 4
    attr_standard = [[1] * m for i in range(n)]
    max_value = []
    min_value = []
    for j in range(0, m):
        max_value.append(max([i[j] for i in attr]))
        min_value.append(min([i[j] for i in attr]))
    # 成本型属性：路径长度 途经交叉口数量 道路类型
    for j in range(0, (len(max_value) - 1)):
        if max_value[j] != min_value[j]:
            for i in range(0, len(attr)):
                attr_standard[i][j] = (max_value[j] - attr[i][j]) / (max_value[j] - min_value[j])
    # 固定性属性：行程时间相符程度
    if max_value[3] != min_value[3]:
        for i in range(0, len(attr)):
            attr_standard[i][3] = 1 - attr[i][3] / max_value[3]

    # 2.建立加权决策评价矩阵
    if n == 2:
        attr_weight = [[], []]
    elif n == 3:
        attr_weight = [[], [], []]
    elif n == 4:
        attr_weight = [[], [], [], []]
    elif n == 5:
        attr_weight = [[], [], [], [], []]
    else:
        attr_weight = [[]] * n
    for i in range(0, len(attr_standard)):
        for j in range(0, len(attr_standard[i])):
            attr_weight[i].append(attr_standard[i][j] * W[j])

    # 3.计算正、负理想解
    max_value2 = []
    min_value2 = []
    for j in range(0, m):
        max_value2.append(max([i[j] for i in attr_weight]))
        min_value2.append(min([i[j] for i in attr_weight]))
    if n == 2:
        ideal_solution = [[], []]
    elif n == 3:
        ideal_solution = [[], [], []]
    elif n == 4:
        ideal_solution = [[], [], [], []]
    elif n == 5:
        ideal_solution = [[], [], [], [], []]
    else:
        ideal_solution = [[]] * n
    for i in range(0, len(attr_weight)):
        s1_sum = 0
        s2_sum = 0
        for j in range(0, len(attr_weight[i])):
            s1 = (attr_weight[i][j] - max_value2[j]) ** 2
            s2 = (attr_weight[i][j] - min_value2[j]) ** 2
            s1_sum += s1
            s2_sum += s2
        ideal_solution[i].extend((s1_sum ** 0.5, s2_sum ** 0.5))

    # 4.计算评分
    score = []
    for i in range(0, len(ideal_solution)):
        score.append(ideal_solution[i][1] / (ideal_solution[i][0] + ideal_solution[i][1]))
    best_score = max(score)
    index = score.index(best_score)
    best_path = k_paths[index]
    return index, best_path


