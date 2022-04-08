Our goal is to compare how similar are the categories found through a
community detection algorithm (i.e. greedy modularity) and categories created by
a cardiologist, which we consider as the ground truth of categorization. We run 
the algorithms mutiple times with different threshold values that range from 
0.8 to 0.9. The results are compared with the ground truth by computing the rand
score between two **lists**.

**How the lists that we compare are formed**

The results of clustering are presentd in a list of the following format -

[0, `file_id_1's cluster`, `file_id_2's cluster`, ..., `file_id_k's cluster`]

The dcm file ids are in the format of `IM-0001-0069.dcm`. We use the last two
digits for indexing our list.

Typically, the last digits of file ids in `dcm_data` are consecutive numbers,
that means they go like 1, 2, 3, ..., 69. But sometimes a few numbers are
skipped, so the files id sequence could be like 65, 67, 69. 

*Note: since no file name has 0 as it's last digit, the first element in the 
list is always kept 0.*


To fix this problem, we take the maximum number we found in the the last two
digits of our file ids to be the length of our list.

So, a sample output might be like
`
[ 0. 34.  1.  1.  3.  3.  3.  3.  3.  8.  8. 32.  7.  7.  1.  1.  1.  1.
  1. 12. 14. 13. 16.  1. 10. 11.  1.  1.  1.  1.  1.  1.  1.  9. 15.  2.
  2. 17. 33.  2.  2.  2.  2. 22. 18.  0.  0.  5. 30. 31.  5.  5. 20. 19.
 25. 24. 21. 23. 26.  5. 29.  4.  4.  4.  4.  4. 27. 28.  6.  6.]
`


