import networkx as nx
from networkx.algorithms import community
from networkx.algorithms.community import greedy_modularity_communities
import os
import tqdm
import numpy as np
import pydicom as dicom
import json
import cv2
import itertools
from random import sample
from sklearn.metrics.pairwise import cosine_similarity

def reconstruct(data_type_file, patient_clusters_file, file_to_write):
    
    '''
    Add back the nodes represented by the sample nodes that were missed when
    aggregating clusters to form distinct data types
    '''
    
    with open(data_type_file, "r") as f:
        data_type_dict = json.load(f)
    
    with open(patient_clusters_file, "r") as ff:
        patient_cluster_dict = json.load(ff)

    for typ, file_names in data_type_dict.items():

        for file_name in file_names:

            patient_id = file_name.split('/')[0]
            file_id = file_name.split('/')[1]

            for cluster in patient_cluster_dict[patient_id]:

                if file_id in cluster:
                    
                    print(f'find {file_id} in {cluster}')
                    
                    cluster.remove(file_id)
                    patient_cluster_dict[patient_id].remove(cluster)

                    print(f'added_files are {cluster}')

                    if cluster != None:
                        
                        print(f'Extend {typ} by adding {cluster}')
                        data_type_dict[typ].extend([f"{patient_id}/{f_name}" for f_name in cluster])
                        break
    
    with open(file_to_write, "w") as f:
        json.dump(data_type_dict, f, indent=2)

def group(ds_name, clusters_file, threshold):

    with open(clusters_file, "r") as f:
        all_types = json.load(f)
    '''
    # test a small sample
    all_types = dict(itertools.islice(all_types.items(), 4))
    '''
    nodes = []

    for _, types in all_types.items():
        nodes += [f"{sample(types, 1)[0]}"]
    
    G = nx.Graph()
    G.add_nodes_from(nodes)

    file_graph = build_graph(nodes, G, ds_name, threshold)
    
    frozensets = get_communities(file_graph)
    
    communities = []

    for fs in frozensets:
        communities.append([c for c in fs])
    
    print(f'communities - \n {communities}')
    print(f'{len(communities)}')

    data_type_dict = {}

    for i, community in enumerate(communities):
        data_type_dict[str(i+1)] = community

    print(data_type_dict)

    with open("dcm_data_types_v2.json", "w") as f:
        json.dump(data_type_dict, f, indent=2)

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
                
                #print(f'comparing {fileA} & {fileB}...')
                dsB = dicom.dcmread(f'{img_path}/{fileB}')
                pixel_array_B = format_pixel_array(dsB.pixel_array)

            elif fileB.split('.')[-1] == 'png':
                
                pixel_array_B = cv2.imread(f'{img_path}/{fileB}')
            
            cos_similarity = cosine_similarity(
                                pixel_array_A.reshape(1,-1),
                                pixel_array_B.reshape(1,-1))

            print(f'similarity bw {fileA} & {fileB} is {cos_similarity[0][0]}')
            
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
    '''
    # Step 3
    communities = aggregate_clusters("dcm_data", "clusters_per_patient.json", 0.8)
    print(communities)
    print(len(communities))
    '''

    # group("dcm_data", "dcm_data_types.json", 0.6)

    reconstruct("dcm_data_types.json", "clusters_per_patient.json", "data_types_reconstructed.json")
