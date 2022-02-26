### Strategy for checking file types ###

There are different folders in our dataset;
the current folders are
`10026_20171208		10651_20171118		15751_20180728		20218_20171201		21104_20180322
10377_20180815		14369_20180420	20198_20180511		20596_20171118		22444_20180404`

Under each folder, we have a number of (around 70) .dcm files, which include different types of data, either videos or images.
Our objective is to find similar files types across different folders. In order to do that, we can divide this task into two steps.

1. identify different categories of files in *each* folder
    - we will organize this information in one json file
    - expected file looks like the following
        * {"10026_20171208": 
                {
                    label_1 : [file_id_1, file_id_2, ...., file_id_k],
                    label_2 : [file_id, ..., file_id_n]
                    ...
                    label_m : [...]

                }
            "10651_20171118":
                {
                    ...
                }
            }

2. compare across different folders to figure out which ones are similar with each other
    
    - we will organize this information in one json file
    - we can draw from each folder one file with a particular label at random, which we will compare it to files with other labels in other folders 
    - expected output is as follows
        
        * {
            label_1 : [folder_id/file_id, ..., ]
            label_2 : [folder_id/file_id, ..., ] 
            ...
            }

