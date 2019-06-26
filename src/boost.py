'''
@author: xusheng
'''

import math
import numpy as np
# import matplotlib.pyplot as plt

def adaboost():
    def h(x, op, criteria):
        if op == '<':
            if x <= criteria:
                return 1
            else:
                return -1
        elif op == '>':
            if x >= criteria:
                return 1
            else:
                return -1
    
    def sign(x):
        if x > 0:
            return 1
        elif x < 0:
            return -1
        else:
            return 0
    
    
    train_set = np.array([[0, 1], [1, 1], [2, 1], [3, -1], [4, -1], 
                          [5, -1], [6, 1], [7, 1], [8, 1], [9, -1]])
    x_data = train_set[:, 0:-1]
    y_label = train_set[:, -1]
    m = train_set.shape[0]
    
    max_epoches = 1000
    cur_epoch = 1

    criteria_set = [2.5, 5.5, 8.5]
    criteria_op = ['<', '>', '<']
    alpha_set = [0., 0., 0.]
    h_num = len(criteria_set)
    
    D = np.ones(m) / m
    print('D_0', D)
    
    while True and cur_epoch <= max_epoches:
        print('---------------------epoch #%d---------------------' % cur_epoch)

        # pick index of min_h
        G = None
        E = None
        min_index = 0
        sum_err = 10000
        for i in range(h_num):
            G_temp = np.array([h(x, criteria_op[i], criteria_set[i]) for x in x_data])
            E_temp = np.array(y_label != G_temp).astype(int)
            sum_err_temp = sum(E_temp * D)
#             print('#%d, E_temp %s' % (i, E_temp))
#             print('#%d, sum_err_temp %f' % (i, sum_err_temp))
            if sum_err_temp < sum_err:
                min_index = i
                G = G_temp
                E = E_temp
                sum_err = sum_err_temp
        # pick index of min_h end
        
        print('min h(x%s%s), idx %d' % (criteria_op[min_index], criteria_set[min_index], min_index))
#         print('G', G)
#         print('E', E)
        print('sum_total_err_%d %s' % (cur_epoch, sum_err))
        
        alpha_set[min_index] = math.log((1 - sum_err) / sum_err) / 2
        print('alpha_set_%d[%d] %f' % (cur_epoch, min_index, alpha_set[min_index]))
        
        z = 2 * math.sqrt(sum_err * (1 - sum_err))
#         print('z', z)
        
        # new D
        D = D * np.exp(-alpha_set[min_index] * y_label * G) / z
        print('D_%d %s' % (cur_epoch, D))
        
        print('alpha_set_%d %s' % (cur_epoch, alpha_set))
        
        # verify train_set
        G_valid = np.zeros((h_num, m))
        for i in range(h_num):
            G_valid[i, :] = [h(x, criteria_op[i], criteria_set[i]) for x in x_data]

        G_sign = [sign(x) for x in np.dot(np.array(alpha_set).reshape(1, h_num), G_valid).reshape(m,)]
#         print(G_sign)
        if sum((y_label != G_sign).astype(int)) == 0:
            msg = ''
            for i in range(h_num):
                msg += '%s * h(x%s%s)' % (alpha_set[i], criteria_op[i], criteria_set[i])
                if i < h_num - 1:
                    msg += ' + '
            print('---------------------------------------------------')
            print('H(x) = %s' % msg)
            break
        # verify train_set end
        
        cur_epoch += 1

 
# 读取本地文件，python3 list(map)
def loadDataSet(fileName):
    dataMat = []
    fr = open(fileName)
    for line in fr.readlines():
        curLine = line.strip().split('\t')
        fltLine = list(map(float,curLine))  # python3问题修改
        dataMat.append(fltLine)
    return dataMat
 
# 根据特征值划分数据集，得到两个数据集
def binSplitDataSet(dataSet, feature, value):   # nonzero返回真（True）值的下标
    mat0 = dataSet[np.nonzero(dataSet[:,feature] > value)[0],:] # 取该列某值大于特征值的行
    mat1 = dataSet[np.nonzero(dataSet[:,feature] <= value)[0],:]   # python3问题修改
    return mat0, mat1
 
# 返回一个值，生成叶子节点（目标变量均值）
def regLeaf(dataSet):
    return np.mean(dataSet[:,-1])
 
# 误差计算函数 返回方差总和
def regErr(dataSet):
    return np.var(dataSet[:,-1]) * np.shape(dataSet)[0]   # var方差计算函数
 
# 选择最佳的特征、特征值   （一旦不满足划分的条件便返回叶子节点）
def chooseBestSplit(dataSet, leafType=regLeaf, errType=regErr, ops=(1,4)):
    tolS = ops[0]
    tolN = ops[1]
    if len(set(dataSet[:,-1].T.tolist()[0])) == 1:  # 特征值唯一，返回None和叶子节点
        return None, leafType(dataSet)
    m,n = np.shape(dataSet)
    S = errType(dataSet)    # 获得数据集的混乱程度误差，后面求混乱程度减少了多少
    bestS = np.inf
    bestIndex = 0
    bestValue = 0
    for featIndex in range(n-1):
        for splitVal in set((dataSet[:, featIndex].T.A.tolist())[0]):   # python3问题修改
            mat0, mat1 = binSplitDataSet(dataSet, featIndex, splitVal)      # 二分 划分数据集
            if (np.shape(mat0)[0] < tolN) or (np.shape(mat1)[0] < tolN): continue # 若划分效果不好（数据集太小），继续划分
            newS = errType(mat0) + errType(mat1)    # 两个数据集的混乱程度求和，与bestS相比较
            if newS < bestS:
                bestIndex = featIndex
                bestValue = splitVal
                bestS = newS
    # 如果混乱程度减少不大，则返回叶子节点
    if (S - bestS) < tolS:
        return None, leafType(dataSet)
    mat0, mat1 = binSplitDataSet(dataSet, bestIndex, bestValue) # 根据最佳的特征、特征值来二分划分数据
    if (np.shape(mat0)[0] < tolN) or (np.shape(mat1)[0] < tolN):  # 若划分效果不好（数据集太小），返回叶子节点
        return None, leafType(dataSet)
    return bestIndex,bestValue # 返回最佳特征、特征值
 
# 数据集、创建叶子节点、误差计算函数、（1：最小的误差下降阈值 4：切分的最少样本数要求）
def createTree(dataSet, leafType=regLeaf, errType=regErr, ops=(1,4)):
    feat, val = chooseBestSplit(dataSet, leafType, errType, ops) # 选择最佳特征、特征值
    if feat == None: return val  # 若特征为None，返回叶子节点值
    retTree = {}    # 创建字典，用于保存树节点的信息
    retTree['spInd'] = feat
    retTree['spVal'] = val
    lSet, rSet = binSplitDataSet(dataSet, feat, val)    # 根据已经划分返回的特征、特征值继续划分数据集
    retTree['left'] = createTree(lSet, leafType, errType, ops)  # 这两个函数为递归，直到叶子节点
    retTree['right'] = createTree(rSet, leafType, errType, ops)
    return retTree


if __name__=='__main__':
    myDat2 = loadDataSet('ex00.txt')
    myMat2 = np.mat(myDat2)
    result = createTree(myMat2)
    print(result)
