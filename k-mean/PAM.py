#!coding:utf-8
from __future__ import division
import matplotlib.pyplot as plt
import numpy as np
import copy

'''
k-mean中心点聚类算法数据挖掘，将数据进行聚类分析，实验数据为data.txt
k-mediods
'''
debug_flag = False
marker_color = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
marker_size = 121
maker_alpha = 0.4
# 聚类cluster K
K = 5


def assert_config(data_set):
    if len(marker_color) <= K:
        raise Exception("Marker color is insufficient")
    if data_set.shape[0] < K:
        raise Exception("K is above samples")


def plt_help(allocate, data_set, plt_type='allocate'):
    if plt_type == 'allocate':
        # 原图像
        plt.subplot(1, 2, 1)
        plt.title("raw data")
        plt.scatter(data_set[:, 0], data_set[:, 1], color=marker_color[0], s=marker_size, alpha=maker_alpha)
        # 聚类之后的图像
        plt.subplot(1, 2, 2)
        for i in xrange(0, K):
            cluster_list = find(allocate[:], i)
            plt.scatter(data_set[cluster_list, 0], data_set[cluster_list, 1], color=marker_color[i], s=marker_size,
                        alpha=maker_alpha)
    elif plt_type == 'data_set':
        # 聚类之后的质心
        plt.subplot(1, 2, 2)
        for i in xrange(0, K):
            plt.scatter(data_set[i, 0], data_set[i, 1], color=marker_color[i], s=marker_size, marker='v',
                        alpha=maker_alpha)
    elif plt_type == 'title':
        plt.subplot(1, 2, allocate)
        plt.title(data_set)
    elif plt_type == 'show':
        plt.show()


# 欧式距离
def dist(data_set, centroid):
    return sum(pow((data_set - centroid), 2))


# 查找质心中所对应的样本
def find(cluster_allocate, i):
    tunnel_list = []
    iterator = 0
    for tunnel in cluster_allocate:
        if tunnel == i:
            tunnel_list.append(iterator)
        iterator += 1
    return tunnel_list


def np_floor(np_array):
    l = len(np_array)
    picked = []
    inc = int(l / K)
    t = 0
    for i in xrange(0, l, inc):
        picked.append(i)
        t += 1
        if t >= K:
            break
    return picked


# 查找最小代价所对应的index
def find_index(cost_array):
    l = len(cost_array)
    min_cost = cost_array[1]
    min_index = 0
    for i in xrange(1, l):
        if cost_array[i] < min_cost:
            min_cost = cost_array[i]
            min_index = i
    return min_index


def kam(data_set, iterator_time):
    row, col = data_set.shape

    # 存储当前质心的样本对象，迭代的时候用于判断是否为中心点
    picked_array = np_floor(data_set)
    # 存储当前质心
    centroid = data_set[picked_array, :]
    if debug_flag:
        print "centroid: \n", centroid
        print "picked_array: \n", picked_array

    # 用于存储每个样本被分配到的簇cluster，allocate[:, 1]存储到质心的距离
    allocate = np.zeros((row, 1))
    allocate.fill(-1)

    changed = True
    iterator = 0
    # 当前非中心点是否已经被选取过了中心点，防止选取中心点绕圈，死循环
    has_picked = []
    while changed:
        changed = False

        # 指派每个剩余对象给离他最近的中心点所表示的簇
        for i in xrange(0, row):
            # 将距离第一个质心的距离作为当前最小值
            min_dist = dist(data_set[i, :], centroid[0, :])
            min_index = 0
            for j in xrange(1, K):
                cur_dist = dist(data_set[i, :], centroid[j, :])
                if cur_dist < min_dist:
                    min_dist = cur_dist
                    min_index = j
            # 样本所在的cluster发生改变
            if min_index != allocate[i, 0]:
                changed = True
                allocate[i] = min_index

        # 0 不限制迭代次数
        if (iterator_time > 0) & (iterator >= iterator_time):
            break
        iterator += 1

        if changed:
            # [cost, i, j]
            cur_cost_list = np.zeros((1, 3))
            cur_cost_list.fill(-1)

            print "iterator : ", iterator
            if debug_flag:
                print "before picked_array: \n", picked_array
                print "before centroid: \n", centroid[:]
                print "allocate: \n", allocate

            # TCij 用非中心点j替换当前中心点i，每次计算代价替换一个中心点
            if debug_flag:
                print "picked_array: ", picked_array
                print "has_picked: ", has_picked
            for i in xrange(0, K):
                if debug_flag:
                    print "K: ", i

                if picked_array[i] not in has_picked:
                    has_picked.append(picked_array[i])
                for j in xrange(0, row):
                    if j in picked_array or j in has_picked:
                        continue
                    if debug_flag:
                        print "j: ", j

                    # 计算替换代价
                    cur_centroid = copy.deepcopy(centroid[:])
                    cur_centroid[i, :] = data_set[j, :]

                    if debug_flag:
                        print "cur_centroid: \n", cur_centroid
                    cost = 0
                    for p in xrange(0, row):
                        min_dist = dist(data_set[p, :], cur_centroid[0, :])
                        min_index = 0
                        for q in xrange(1, K):
                            cur_dist = dist(data_set[p, :], cur_centroid[q, :])
                            if cur_dist < min_dist:
                                min_dist = cur_dist
                                min_index = q
                        # 新中心点样本发生了改变
                        if min_index != allocate[p]:
                            if debug_flag:
                                print p, "from: ", int(allocate[p]), " changed to: ", min_index
                            cost += dist(data_set[p, :], cur_centroid[min_index, :]) - \
                                dist(data_set[p, :], centroid[int(allocate[p]), :])
                    cur_cost_list = np.vstack((cur_cost_list, np.array([cost, i, j])))
            if debug_flag:
                print "cur_cost_list: \n", cur_cost_list[1:, :]
            # 选取代价最小，且为负的非中心点j替换当前中心点i，略过第一个无意义的填充点
            index = find_index(cur_cost_list[1:, 0]) + 1
            # 用第j个元素替换第i个中心点
            if cur_cost_list[index, 0] < 0:
                print int(cur_cost_list[index, 2]), " sub ", picked_array[int(cur_cost_list[index, 1])]
                picked_array[int(cur_cost_list[index, 1])] = int(cur_cost_list[index, 2])
                centroid[int(cur_cost_list[index, 1]), :] = data_set[int(cur_cost_list[index, 2]), :]
            else:
                break
            if debug_flag:
                print "after picked_array: \n", picked_array
                print "after centroid: \n", centroid

    if debug_flag:
        print "after while centroid: \n", centroid
        print "after while allocate: \n", allocate
    return centroid, allocate, iterator

if __name__ == '__main__':
    if debug_flag:
        data_test = np.array([[1, 3], [-1, -2], [2, 3], [2, 4], [2, -1], [0, 5], [3, 4]])
    else:
        data_test = np.loadtxt("data.txt")

    # 颜色种类数要大于K的聚类数，还有一个颜色用于着色质心，便于着色区分
    assert_config(data_test)
    cluster, alloc, real_iter = kam(data_test, 0)

    plt_help(alloc, data_test)
    plt_help(2, 'after {iter} iterator && K = {clu}'.format(iter=real_iter, clu=K), 'title')
    plt_help(None, cluster, plt_type='data_set')
    plt_help(None, None, plt_type='show')
