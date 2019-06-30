'''
@author: xusheng
'''

import pandas as pd
import math
import logging

logger = logging.getLogger(__file__)

def load_data():
    data = pd.DataFrame({'年龄':['青年', '青年', '青年', '青年', '青年', '中年', '中年', '中年', '中年', '中年', '老年', '老年', '老年', '老年', '老年'], 
                         '有工作':['否', '否', '是', '是', '否', '否', '否', '是', '否', '否', ' 否', '否', '是', '是', '否'], 
                         '有房子':['否', '否', '否', '是', '否', '否', '否', '是', '是', '是', ' 是', '是', '否', '否', '否'], 
                         '信贷情况':['一般', '好', '好', '一般', '一般', '一般', '好', '好', '非常好', '非常好', ' 非常好', '好', '好', '非常好', '一般'], 
                         '类别':['否', '否', '是', '是', '否', '否', '否', '是', '是', '是', ' 是', '是', '是', '是', '否']})
    return data

def load_test_data():
    data = pd.DataFrame({'code':[1, 3], 'type':[5, 6], 'label':['yes', 'yes']})
    return data

def calc_entropy(data):
    labels = data[data.columns[-1]]
    m = len(data)

#     cnt_labels = {}
    entropy = 0
#     logging.debug('y_labels:\n%s' % labels.value_counts())
    for _, cnt in labels.value_counts().items():
#         cnt_labels[label] = cnt
        p = cnt / m
        entropy += - p * math.log(p, 2)
    
#     logging.debug('entropy: %s' % entropy)
    return entropy

def choose_best_feature(data):
    columns = data.columns[:-1]
    m = len(data)
    logging.debug('data:\n%s' % data)
    
#     sub_data = None
    c_entropy = calc_entropy(data)  # big enough
    best_feature = None
    for feature in columns:
        unique_feature_vals = data[feature].unique()
        logging.debug('feature: %s, unique_val: %s' % (feature, unique_feature_vals))
        
        c_entropy_temp = 0.
        for unique_feature_val in unique_feature_vals:
            sub_data_temp = split_data(data, feature, unique_feature_val)
            m_sub = len(sub_data_temp)
            delta_c_entropy = m_sub / m * calc_entropy(sub_data_temp)
            logging.debug('%s: %s, [%d/%d], delta_c_entropy: %.6f, sub_data:\n%s' % (feature, unique_feature_val, m_sub, m, delta_c_entropy, sub_data_temp))
            c_entropy_temp += delta_c_entropy
        
        logging.debug('feature: %s, total_c_entropy: %.6f' % (feature, c_entropy_temp))
        # I(Y|X) = H(Y) - H(Y|X), as H(Y) is fixed in the same data set, tp get the biggest I means to get the smallest H(Y|X)
        if c_entropy_temp <= c_entropy:
            c_entropy = c_entropy_temp
            best_feature = feature
    
    logging.info('best feature: %s, c_entropy: %.6f' % (best_feature, c_entropy))
    return best_feature

def split_data(data, feature, value):
    sub_data_temp = data[data[feature] == value].copy()
    sub_data_temp.drop(feature, axis=1, inplace=True)
    return sub_data_temp

def major_label(labels):
    value_counts = labels.value_counts().sort_values(ascending=False)
    logging.info('label conflict exists:\n%s' % (value_counts))
    return value_counts.index[0]

def create_tree(data):
    print('create_tree', data)
    labels = data[data.columns[-1]]
    unique_labels = labels.unique()
    
    # if only one unique label left, just pick this label
    if len(unique_labels) == 1:
        return unique_labels[0]
    
    # if some conflicts on labels with same input, pick the label with highest probability
    if len(data.columns) == 1:
        return major_label(labels)
    
    best_feature = choose_best_feature(data)
    tree = {best_feature: {}}
    
    unique_feature_vals = data[best_feature].unique()
    for val in unique_feature_vals:
        tree[best_feature][val] = create_tree(split_data(data, best_feature, val))
    
    return tree

def fit(model, data):
    labels = data[data.columns[-1]]
    m = len(data)
    
    pred_data = pd.DataFrame()
    for row in data.iterrows():
        node = model
        while True:
            if type(node) != dict:
                pred_data = pred_data.append(pd.DataFrame({'pred_labels': [node]}), ignore_index=True)
                break
                
            for k in node.keys():
                feature = k
                break
            
            feature_vals = node[feature].keys()
            for feature_val in feature_vals:
                # row is a tuple of (#, pandas series)
                if row[-1][feature] == int(feature_val):
                    node = node[feature][feature_val]
                    break
    
    
    results = pred_data[pred_data['pred_labels'] == labels]
    ratings = len(results) / m
    return ratings

if __name__ == '__main__':
    # logging setting
#     logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    logging.basicConfig(level=logging.INFO, format='%(filename)s[%(lineno)d] - %(message)s')
    # model train
    data = load_data()
    base_entropy = calc_entropy(data)
    logging.info('base entropy: %s' % base_entropy)
    
    model = create_tree(data)
    logging.info('model: %s' % model)
    
    # test
#     test_data = load_test_data()
#     rating = fit(model, test_data)
#     logging.debug('test_data:\n%s' % test_data)
#     logging.info('rating: %.2f%%' % (rating * 100))
