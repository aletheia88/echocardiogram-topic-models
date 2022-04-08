import re
import numpy as np
import pickle
from sklearn.metrics import rand_score
from categorize_files import categorize_files
import os

def get_thres_randscore_pairs(annotation_file, path, folder_id):
    
    rand_scores = []
    thresholds = [0.8 + i*0.01 for i in range(11)]
    file_ids = os.listdir(f'{path}/{folder_id}')
    max_file_id = max([int(s.split('.')[0].split('-')[-1]) for s in file_ids])

    clusters_grd = get_clusters_from_annotation(annotation_file)
    labels_grd = format_clusters(clusters_grd, max_file_id, 'grd')
    print(f'labels_grd: {labels_grd}')
    for threshold in thresholds:
        
        clusters_alg = categorize_files(path, folder_id, threshold)
        labels_alg = format_clusters(clusters_alg, max_file_id, 'alg')
        print(f'labels_alg: {labels_alg}')

        rand_scores.append(rand_score(labels_grd, labels_alg))
        print(f'rand_scores for threhold={threshold}: {rand_scores}')
        break

    return list(zip(thresholds, rand_scores))

def format_clusters(clusters, num_files, typ):
    
    if typ == 'grd':
        formated_clusters_grd = []
        labels_grd = np.zeros(num_files+1)

        for _, cls in clusters.items():
            formated_clusters_grd.append(cls)

        for i, cluster in enumerate(formated_clusters_grd):
            for file_id in cluster: labels_grd[int(file_id)] = i + 1
        
        return labels_grd
    
    elif typ == 'alg':
        formated_clusters_alg = []
        labels_alg = np.zeros(num_files+1)

        for cluster in clusters:
            cls = [c.split('-')[-1].split('.')[0][-2:] for c in sorted(cluster)]
            formated_clusters_alg.append(cls)

        for i, cluster in enumerate(formated_clusters_alg):
            for file_id in cluster: labels_alg[int(file_id)] = i + 1

        return labels_alg
    
def get_clusters_from_annotation(annotation_file):

    f = open(annotation_file, 'r')
    lines = f.readlines()

    annotation_dict = {}
    clusters = {}
    
    for line in lines:
        
        line.rstrip()
        file_id = line.split(' ')[0]
        
        if len(annotation_dict) == 0:
            annotation_dict['0'] = [line]
        
        else:
            check = exist(line, annotation_dict)

            if check[0] == True:
                annotation_dict[check[1]].extend([file_id])

            elif check[0] == False:
                annotation_dict[len(annotation_dict)] = [line]

    for label, file_ids in annotation_dict.items():
        
        clusters[label] = [file_ids[0].split(' ')[0]] + file_ids[1:]

    return clusters

def exist(content, annotation_dict):
    
    """ Check if content is the same with any of the annotation dictionary items
    that have been added"""

    for label, annotation in annotation_dict.items():
        
        content_tokens = content.split(' ')[1:]
        annotation_tokens = annotation[0].split(' ')[1:]

        if content_tokens == annotation_tokens:
            return (True, label)

    return (False, None)

if __name__ == "__main__":
    
    annotation_file = 'sam-clusters.txt'
    f = open('sample_communities.pkl', 'rb')
    communities = pickle.load(f)
    path = 'dcm_data'
    folder_id = '22444_20180404'

    get_thres_randscore_pairs(annotation_file, path, folder_id)

