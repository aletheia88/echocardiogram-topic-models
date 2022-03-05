import os
import numpy as np
import cv2
import pydicom as dicom
import json
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances

def categorize(path):
    
    file_labels_all_folders = {}
    
    folder_ids = ['22444_20180404']
    '''
    folder_ids = ['22444_20180404', '20198_20180511', '20218_20171201', 
                '21104_20180322', '15751_20180728', '10377_20180815', 
                '14369_20180420', '10651_20171118', '20596_20171118', 
                '10026_20171208']
    '''
    for folder_id in folder_ids:
        
        for dirs, _, files in os.walk(f'{path}/{folder_id}'):
            file_id = dirs.split('/')[1]
        
            print(f'Processing {folder_id}')
            file_labels_folder_i = compare_files(files, {}, f'{path}/{folder_id}')
            file_labels_all_folders[folder_id] = file_labels_folder_i
    
    with open('categories_perfolder.json', 'w') as f:
        json.dump(file_labels_all_folders, f)
        f.close()

def compare_files(files, file_labels, img_path):
    
    for i, fileA in enumerate(files):
        
        dsA = dicom.dcmread(f'{img_path}/{fileA}')
        pixel_array_A = format_pixel_array(dsA.pixel_array)

        for fileB in files[i+1:]:
            dsB = dicom.dcmread(f'{img_path}/{fileB}')
            print(f'comparing {fileA} and {fileB}...')
            pixel_array_B = format_pixel_array(dsB.pixel_array)
            
            cos_similarity = cosine_similarity(pixel_array_A.reshape(1,-1),
                                            pixel_array_B.reshape(1,-1))

            file_labels = update_file_labels(cos_similarity, fileA, fileB, file_labels)

    return file_labels

def format_pixel_array(pixel_array):

    if pixel_array.ndim == 3:
        return pixel_array

    elif pixel_array.ndim == 4:
        # suppose shape = (52, 720, 960, 3)
        # then return averaged pixel values over 52 frames
        return np.mean(pixel_array, axis=0)

def update_file_labels(cos_similarity, fileA, fileB, file_labels):

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
    threshold = 0.9
    
    ### Check if fileA and fileB exists in file_labels ###
    fileA_status = file_exists(fileA, file_labels)
    fileB_status = file_exists(fileB, file_labels)
    
    # fileA and fileB are similar types
    if cos_similarity > threshold:
        
        # both fileA and fileB are uncategorized files
        if fileA_status == None and fileB_status == None:
            
            new_label = len(file_labels)+1
            file_labels[str(new_label)] = [fileA, fileB]
            
        # either fileA or fileB has already been categorized        
        elif fileA_status:

            file_labels[fileA_status].extend([fileB]) 
        
        elif fileB_status:

            file_labels[fileB_status].extend([fileA])

    # fileA and fileB are not similar types
    else:
        # both fileA and fileB are uncategorized files
        if fileA_status == None and fileB_status == None:

            new_label_1, new_label_2 = len(file_labels)+1, len(file_labels)+2
            file_labels[str(new_label_1)] = [fileA]
            file_labels[str(new_label_2)] = [fileB]
        
        # either fileA or fileB has already been categorized
        elif fileA_status or fileB_status:

            new_file = fileA if fileA==None else fileB
            file_labels[str(len(file_labels)+1)] = [new_file]
    
    return file_labels

def file_exists(f, file_labels):

    for label, files in file_labels.items():
        if f in files:
            return label

if __name__ == "__main__":
    categorize('dcm_data')
