import re

def get_clusters_from_annotation(annotation_file):

    f = open(annotation_file, 'r')
    lines = f.readlines()

    annotation_dict = {}
    clusters = {}
    
    for line in lines:
        
        line.rstrip()
        #line = re.sub(r'[\\*n*]', "", line)
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
        #print(content_tokens)
        annotation_tokens = annotation[0].split(' ')[1:]

        if content_tokens == annotation_tokens:
            return (True, label)

    return (False, None)

if __name__ == "__main__":

    annotation_dict = get_clusters_from_annotation('sam-clusters.txt') 
    print(annotation_dict)
