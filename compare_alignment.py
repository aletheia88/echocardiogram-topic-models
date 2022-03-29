import re
import pickle

def format_clusters(annotation_file, communities):
    
    cluster_category_dict = get_clusters_from_annotation(annotation_file)
    formated_clusters_grd = []
    formated_clusters_alg = []
        
    for _, clusters in cluster_category_dict.items():
        formated_clusters_grd.append(clusters)
    
    for community in communities:
        community = [c.split('-')[-1].split('.')[0][-2:] for c in sorted(community)]
        formated_clusters_alg.append(community) 
    
    return formated_clusters_grd, formated_clusters_alg

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
    f.close()
    formated_clusters = format_clusters(annotation_file, communities)
    print(formated_clusters)
