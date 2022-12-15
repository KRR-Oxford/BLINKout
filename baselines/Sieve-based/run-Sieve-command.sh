#!/bin/bash

# to run with command similar to
# ./run-Sieve-command.sh > sieve-full-2014AB-results.txt

source activate blink37
cd /home/hang/BLINK/baselines/Sieve-based/disorder-normalizer/src

# compile some .java (if there is new edit of a .java file)
# javac tool/util/Abbreviation.java

#data_folder_name=share_clef_2013_preprocessed_sieve
train_data_folder_name=sieve-full-2017AA_pruned0.2 #sieve-full-2017AA_pruned0.2
#test_data_folder_name=${train_data_folder_name}
test_data_folder_name=sieve-full-2014AB
onto_ver=2014AB #2012AB #2017AA_pruned0.1 #2017AA_pruned0.2
syn_mark=_syn #_syn_full or ''
entity_catelogue_fn=UMLS${onto_ver}${syn_mark}_Sieve.jsonl 
data_split_train_mark=trng #train
data_split_test_mark=dev #valid (for share/clef) #test #trng #dev (for mm)
data_folder_name_Sieve=mm-data #clef-data

# remove previous prediction outputs
rm -r ../${data_folder_name_Sieve}/${test_data_folder_name}/output\\*

# run Sieve tool
java tool.Main ../${data_folder_name_Sieve}/${train_data_folder_name}/${data_split_train_mark}/ ../${data_folder_name_Sieve}/${test_data_folder_name}/${data_split_test_mark}/ ../${data_folder_name_Sieve}/${entity_catelogue_fn} 10

# get results
cd /home/hang/BLINK/baselines/Sieve-based
python get_metric_results_from_Sieve_outputs.py --data_folder_name ./disorder-normalizer/${data_folder_name_Sieve}/${test_data_folder_name} --data_split_name ${data_split_test_mark}
