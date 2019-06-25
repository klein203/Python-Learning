'''
@author: xusheng
'''

import math
import numpy as np

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
        return h(x, '>', 0.0)
    
    
    train_set = np.array([[0, 1], [1, 1], [2, 1], [3, -1], [4, -1], 
                          [5, -1], [6, 1], [7, 1], [8, 1], [9, -1]])
    x_data = train_set[:, 0:-1]
    y_label = train_set[:, -1]
    m = train_set.shape[0]
    
    max_epoches = 10
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
        
if __name__=='__main__':
    adaboost()
