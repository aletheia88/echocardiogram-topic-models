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

    compare(all_graphs[0], all_graphs[1], clusters_dict, 0.9, file_to_write)

def compare(graphA, graphB, clusters_dict, threshold, file_to_write):
    
    file_type_dict = {}

    # e.g. graphA = "20198_20180511", graph_B = "22444_20180404"
    sample_nodes_A = [sample(cluster, 1)[0] for cluster in
            clusters_dict[graphA]]
    
    sample_nodes_B = [sample(cluster, 1)[0] for cluster in
            clusters_dict[graphB]]
    
    for node_A in sample_nodes_A:
        
        if node_A.split('.')[-1] == 'dcm':
            dsA = dicom.dcmread(f'dcm_data/{graphA}/{node_A}')
            pixel_array_A = format_pixel_array(dsA.pixel_array)

        elif node_A.split('.')[-1] == 'png':
            pixel_array_A = cv2.imread(f'dcm_data/{graphA}/{node_A}')

        for node_B in sample_nodes_B:
            
            print(f'comparing {node_A} and {node_B}...')
            if node_B.split('.')[-1] == 'dcm':
                dsB = dicom.dcmread(f'dcm_data/{graphB}/{node_B}')
                pixel_array_B = format_pixel_array(dsB.pixel_array)
            
            elif node_B.split('.')[-1] == 'png':
                pixel_array_B = cv2.imread(f'dcm_data/{graphA}/{node_B}')
            
            cos_similarity = cosine_similarity(pixel_array_A.reshape(1,-1),
                                            pixel_array_B.reshape(1,-1))
        
            file_type_dict = update_data_types(cos_similarity[0][0], f"{graphA}/{node_A}",
                    f"{graphB}/{node_B}", threshold, file_type_dict)
           
            f = open(file_to_write, "w")
            json.dump(file_type_dict, f, indent=2)

def update_data_types(cos_sim, fileA, fileB, threshold, file_type_dict):

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
    
    # fileA and fileB are similar types
    if cos_sim > threshold:
        
        # both fileA and fileB are uncategorized files
        if fileA_status == "-1" and fileB_status == "-1":
            
            new_type = len(file_type_dict)+1
            file_type_dict[str(new_type)] = [fileA, fileB]
            
        # either fileA or fileB has already been categorized        
        elif fileA_status != "-1":
            file_type_dict[fileA_status].extend([fileB]) 
        
        elif fileB_status != "-1":
            file_type_dict[fileB_status].extend([fileA])

    # fileA and fileB are not similar types
    else:
        # both fileA and fileB are uncategorized files
        if fileA_status == "-1" and fileB_status == "-1":

            new_type_1, new_type_2 = len(file_type_dict)+1,len(file_type_dict)+2
            
            file_type_dict[str(new_type_1)] = [fileA]
            file_type_dict[str(new_type_2)] = [fileB]

        elif fileA_status != "-1" or fileB_status != "-1":

            new_file = fileA if fileA_status == "-1" else fileB
            file_type_dict[str(len(file_type_dict)+1)] = [new_file]

    return file_type_dict

def format_pixel_array(pixel_array):

    if pixel_array.ndim == 3:
        return pixel_array

    elif pixel_array.ndim == 4:
        # suppose shape = (52, 720, 960, 3)
        # then return averaged pixel values over 52 frames
        return np.mean(pixel_array, axis=0)

def file_exists(f, file_type_dict):

    for f_type, files in file_type_dict.items():
        if f in files: return f_type
        else: return str(-1)

if __name__ == "__main__":
    
    aggregate("clusters_per_patient.json", "dcm_data_types.json")
