
def get_clusters_from_annotation(annotation_file):

    f = open(annotation_file, 'r')
    lines = f.readlines()

    annotation_dict = {}
    clusters = {}
    
    for line in lines:
        
        file_id = line.split(' ')[0]
        
        if len(annotation_dict) == 0:
            annotation_dict['0'] = [line]
        
        else:
            check = exist(line, annotation_dict)

            if check[0] == True:
                annotation_dict[check[1]].extend([file_id])

            elif check[0] == False:
                annotation_dict[len(annotation_dict)] = [line]

    return annotation_dict

def exist(content, annotation_dict):
    
    """ Check if content is the same with any of the annotation dictionary items
    that have been added"""

    for label, annotation in annotation_dict.items():
        
        content_tokens = content.split(' ')
        annotation_tokens = annotation[0].split(' ')

        if content_tokens[1:] == annotation_tokens[1:]:
            return (True, label)

    return (False, None)

if __name__ == "__main__":

    annotation_dict = get_clusters_from_annotation('sam-clusters.txt') 
    print(annotation_dict)
