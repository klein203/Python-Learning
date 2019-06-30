'''
@author: xusheng
'''

import pandas as pd
import math
import logging

logger = logging.getLogger(__file__)

def load_data():
    data = pd.DataFrame({'water':[1, 1, 1, 0, 0, 1], 'feet':[1, 1, 0, 1, 1, 1], 'survive':['yes', 'yes', 'no', 'no', 'no', 'no']})
    return data

def load_test_data():
    data = pd.DataFrame({'water':[1, 0], 'feet':[1, 1], 'survive':['yes', 'no']})
    return data

def calc_entropy(data):
    labels = data[data.columns[-1]]
    m = len(labels)

#     cnt_labels = {}
    entropy = 0
    logging.debug('y_labels:\n%s' % labels.value_counts())
    for _, cnt in labels.value_counts().items():
#         cnt_labels[label] = cnt
        p = cnt / m
        entropy += - p * math.log(p, 2)
    
    logging.debug('entropy: %s' % entropy)
    return entropy

def choose_best_feature(data):
    columns = data.columns[:-1]
    logging.debug('data:\n%s' % data)
    
#     sub_data = None
    c_entropy = 1000000000.  # big enough
    best_feature = None
    for feature in columns:
        unique_feature_vals = data[feature].unique()
        logging.debug('feature: %s, unique_val: %s' % (feature, unique_feature_vals))
        
        c_entropy_temp = 0.
        for unique_feature_val in unique_feature_vals:
            sub_data_temp = split_data(data, feature, unique_feature_val)
            logging.debug('sub_data:\n%s' % sub_data_temp)
            
            c_entropy_temp += calc_entropy(sub_data_temp)
        
        logging.debug('choose feature: %s, entropy: %.6f' % (feature, c_entropy_temp))
        # I(Y|X) = H(Y) - H(Y|X), as H(Y) is fixed in the same data set, tp get the biggest I means to get the smallest H(Y|X)
        if c_entropy_temp < c_entropy:
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
    m = len(labels)
    
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
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    
    # model train
    data = load_data()
#     base_entropy = calc_entropy(data)
    model = create_tree(data)
    logging.info('model: %s' % model)
    
    # test
    test_data = load_test_data()
    rating = fit(model, test_data)
    logging.debug('test_data:\n%s' % test_data)
    logging.info('rating: %.2f%%' % (rating * 100))
