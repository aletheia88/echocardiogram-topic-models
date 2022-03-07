import networkx as nx
from networkx.algorithms import community
from networkx.algorithms.community import greedy_modularity_communities

import os
import numpy as np
import pydicom as dicom
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances

def categorize(path, folder_id):

    # create empty graph for each file
    G = nx.Graph()
    
    # add nodes
    nodes = [files for _, _, files in os.walk(f'{path}/{folder_id}')][0]
    G.add_nodes_from(nodes)
    
    # build graph
    file_graph = build_graph(nodes, G, f'{path}/{folder_id}')
    # find communities
    file_communities = greedy_modularity_communities(file_graph)
    
    return file_communities

def build_graph(nodes, graph, img_path):
    
    threshold = 0.9

    for i, fileA in enumerate(nodes):
        dsA = dicom.dcmread(f'{img_path}/{fileA}')
        pixel_array_A = format_pixel_array(dsA.pixel_array)

        for fileB in nodes[i+1:]:
            dsB = dicom.dcmread(f'{img_path}/{fileB}')
            print(f'comparing {fileA} & {fileB}...')
            pixel_array_B = format_pixel_array(dsB.pixel_array)
            cos_similarity = cosine_similarity(pixel_array_A.reshape(1,-1),
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
    
    categorize('dcm_data', '22444_20180404')
