import networkx as nx
from networkx.algorithms import community
from networkx.algorithms.community import greedy_modularity_communities
import os
import tqdm
import numpy as np
import pydicom as dicom
import json
import cv2
from random import sample
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances

def aggregate_clusters(ds_name, clusters_file, threshold):

    # Takes in json file that contains clusters for each patient file graph and
    # the threshold to use for further clustering across alll patient graphs

    with open(clusters_file, "r") as f:

        patient_clusters = json.load(f)

    # generate nodes for our new graph
    
    nodes = []

    for patient_id, clusters in patient_clusters.items():    
        for cluster in clusters:
            nodes += [f"{patient_id}/{sample(cluster, 1)[0]}"]
    
    G = nx.Graph()
    G.add_nodes_from(nodes)

    file_graph = build_graph(nodes, G, ds_name, threshold)
    frozensets = get_communities(file_graph)
    
    communities = []

    for fs in frozensets:
        communities.append([c for c in fs])
        
    return communities
    
def categorize_all_patient_files(path, threshold):

    folder_ids = [folders for _, folders, _ in os.walk(f'{path}')][0]

    # 10377_20180815 -> folder_ids[5] 
    
    for folder_id in folder_ids[6:]:

        cluster = categorize_one_patient_files(path, folder_id, threshold)
        
        print(f'{folder_id} : {cluster}')

        f = open("clusters_per_patient.json", "r")
        all_clusters = json.load(f)
        f.close()
        
        ff = open("clusters_per_patient.json", "w")
        all_clusters[folder_id] = cluster
        json.dump(all_clusters, ff, indent=2)
        ff.close()

def categorize_one_patient_files(path, folder_id, threshold):
    
    frozensets = get_communities(get_fileGraph(path, folder_id, threshold))
    communities = []

    for fs in frozensets:
        communities.append([c for c in fs])
    
    return communities
    
def get_fileGraph(path, folder_id, threshold):

    # create empty graph for each file
    G = nx.Graph()
    
    # add nodes
    print(f'path - {path}, folder_id - {folder_id}')
    nodes = [files for _, _, files in os.walk(f'{path}/{folder_id}')][0]

    '''
    # temporary treatment for IM-0001-10000.dcm in 10377_20180815
    nodes.remove('IM-0001-10000.dcm')
    '''

    G.add_nodes_from(nodes)
    
    # build graph
    file_graph = build_graph(nodes, G, f'{path}/{folder_id}', threshold)
    
    return file_graph

def get_communities(file_graph):

    # find communities
    file_communities = greedy_modularity_communities(file_graph)
    
    return file_communities

def build_graph(nodes, graph, img_path, threshold):
    
    print(f'All nodes - {len(nodes)}')

    for i, fileA in enumerate(nodes):
        
        #print(f'reading file A {img_path}/{fileA}')
        
        # check file type - dcm or png
        if fileA.split('.')[-1] == 'dcm':

            dsA = dicom.dcmread(f'{img_path}/{fileA}')
            pixel_array_A = format_pixel_array(dsA.pixel_array)

        elif fileA.split('.')[-1] == 'png':

            pixel_array_A = cv2.imread(f'{img_path}/{fileA}')
    
        for fileB in nodes[i+1:]:
            
            #print(f'reading file B {img_path}/{fileB}')

            if fileB.split('.')[-1] == 'dcm':
                
                print(f'comparing {fileA} & {fileB}...')
                dsB = dicom.dcmread(f'{img_path}/{fileB}')
                pixel_array_B = format_pixel_array(dsB.pixel_array)
                cos_similarity = cosine_similarity(pixel_array_A.reshape(1,-1),
                                                   pixel_array_B.reshape(1,-1))

            elif fileB.split('.')[-1] == 'png':
                
                pixel_array_B = cv2.imread(f'{img_path}/{fileB}')
            
            cos_similarity = cosine_similarity(
                                pixel_array_A.reshape(1,-1),
                                pixel_array_B.reshape(1,-1))

            if cos_similarity > threshold:
                graph.add_edge(fileA, fileB)

    return graph

def format_pixel_array(pixel_array):

    if pixel_array.ndim == 3:
        return pixel_array

    elif pixel_array.ndim == 4:
        # suppose shape = (52, 720, 960, 3)
        # then return averaged pixel values over 52 frames
        return np.mean(pixel_array, axis=0)

if __name__ == "__main__":
    
    # Step 1 - 2
    # categorize_all_patient_files('dcm_data', 0.9)

    # Step 3
    communities = aggregate_clusters("dcm_data", "clusters_per_patient.json", 0.8)
    print(communities)
    print(len(communities))

