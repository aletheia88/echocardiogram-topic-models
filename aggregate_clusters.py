import json
import numpy as np
import math
import cv2
import pydicom as dicom
from random import sample
from sklearn.metrics.pairwise import cosine_similarity

def aggregate(cluster_file, file_to_write):

    f = open(cluster_file, 'r')
    clusters_dict = json.load(f)
    
    all_graphs = list(clusters_dict.keys())

    compare(all_graphs[0], all_graphs[1], clusters_dict, 0.8, file_to_write)

def compare(graphA, graphB, clusters_dict, threshold, file_to_write):
    
    file_type_dict = {}

    # e.g. graphA = "20198_20180511", graph_B = "22444_20180404"
    sample_nodes_A = [sample(cluster, 1)[0] for cluster in
            clusters_dict[graphA]]
    
    sample_nodes_B = [sample(cluster, 1)[0] for cluster in
            clusters_dict[graphB]]

    print(f'sample_nodes_A: {len(sample_nodes_A)}\n {len(clusters_dict[graphA])}')
    print(f'sample_nodes_B: {len(sample_nodes_B)}\n {len(clusters_dict[graphB])}')
    
    for i, node_A in enumerate(sample_nodes_A):

        if node_A.split('.')[-1] == 'dcm':
            dsA = dicom.dcmread(f'dcm_data/{graphA}/{node_A}')
            pixel_array_A = format_pixel_array(dsA.pixel_array)

        elif node_A.split('.')[-1] == 'png':
            pixel_array_A = cv2.imread(f'dcm_data/{graphA}/{node_A}')

        for j, node_B in enumerate(sample_nodes_B):

            print(f'comparing {graphA}/{node_A} and {graphB}/{node_B}...')
            if node_B.split('.')[-1] == 'dcm':
                dsB = dicom.dcmread(f'dcm_data/{graphB}/{node_B}')
                pixel_array_B = format_pixel_array(dsB.pixel_array)
            
            elif node_B.split('.')[-1] == 'png':
                pixel_array_B = cv2.imread(f'dcm_data/{graphB}/{node_B}')
            
            cos_similarity = cosine_similarity(pixel_array_A.reshape(1,-1),
                                            pixel_array_B.reshape(1,-1))
            
            print(f'cos_similarity: {cos_similarity[0][0]}\n')
            ''' 
            if cos_similarity > 0.9:
                print(f'comparing {graphA}/{node_A} and {graphB}/{node_B}')
                print(f'cos_similarity = {cos_similarity}\n')
            '''

            clusterA = [f"{graphA}/{clus}" for clus in clusters_dict[graphA][i]]
            clusterB = [f"{graphB}/{clus}" for clus in clusters_dict[graphB][j]]

            file_type_dict = update_data_types(cos_similarity[0][0], f"{graphA}/{node_A}",
                    f"{graphB}/{node_B}", clusterA, clusterB, threshold, file_type_dict)
           
            f = open(file_to_write, "w")
            json.dump(file_type_dict, f, indent=2)
        
        print(f'\n---------finish {graphA}/{node_A}---------\n')
        
        if i == 0: break

def update_data_types(cos_sim, fileA, fileB, clusterA, clusterB, 
                      threshold, file_type_dict):
    
    '''
    fileA and fileB are similar
        * both fileA and fileB are uncategorized files
            - create one new label
        * either fileA or fileB has already been categorized
            - append the new file to existing list of file ids under the correps category
        * both are categorized
            - great!

    fileA and fileB are not similar
        * both fileA and fileB are new uncategorized files
            - create two different labels
            - append each to its own list under its label
        * either fileA or fileB has already been categorized
            - create 1 new label for the uncategorized file
        * both are categorized
            - hooray~ 
    '''
    
    ### Check if fileA and fileB exists in file_labels ###
    fileA_status = file_exists(fileA, file_type_dict)
    fileB_status = file_exists(fileB, file_type_dict)
    
    if fileA_status != "-1" or fileB_status != "-1":
        print(f'fileA_status: {fileA_status}---fileB_status:{fileB_status}')

    # fileA and fileB are similar types
    if cos_sim > threshold:
        
        # both fileA and fileB are uncategorized files
        # -> the clusters they represent are also uncategorized
        if fileA_status == "-1" and fileB_status == "-1":
            
            new_type = len(file_type_dict)+1
            file_type_dict[str(new_type)] = clusterA + clusterB
            
        # fileB has not been categorized        
        elif fileB_status == "-1":
            file_type_dict[fileA_status].extend(clusterB) 
        
        # fileA has not been categorized
        elif fileA_status == "-1":
            file_type_dict[fileB_status].extend(clusterA)

    # fileA and fileB are not similar types
    else:
        # both fileA and fileB are uncategorized files
        if fileA_status == "-1" and fileB_status == "-1":

            new_type_1, new_type_2 = len(file_type_dict)+1,len(file_type_dict)+2
            
            file_type_dict[str(new_type_1)] = clusterA
            file_type_dict[str(new_type_2)] = clusterB

        elif fileA_status != "-1" or fileB_status != "-1":

            new_cluster = clusterA if fileA_status == "-1" else clusterB
            file_type_dict[str(len(file_type_dict)+1)] = new_cluster

    return file_type_dict

def format_pixel_array(pixel_array):

    if pixel_array.ndim == 3:
        return pixel_array

    elif pixel_array.ndim == 4:
        # suppose shape = (52, 720, 960, 3)
        # then return averaged pixel values over 52 frames
        return np.mean(pixel_array, axis=0)

def file_exists(f, file_type_dict):
    
    if len(file_type_dict) == 0:
        return str(-1)
    else:
        for f_type, files in file_type_dict.items():
            if f in files:
                return f_type
            else: 
                return str(-1)

if __name__ == "__main__":
    
    aggregate("clusters_per_patient.json", "dcm_data_types.json")
