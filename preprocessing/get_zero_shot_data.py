# get zero-shot versions of the data (ShARe/CLEF, MedMentions) 
# after preprocessing with format_trans_xxx2blink.py
# i.e. only keep the valid/test entities which are not in the training data

from tqdm import tqdm
import json
import os 

#output str content to a file
#input: filename and the content (str)
def output_to_file(file_name,str):
    with open(file_name, 'w', encoding="utf-8-sig") as f_output:
        f_output.write(str)

dataset_folder_path = "../data"
#list_dataset_names = ["MedMentions-preprocessed/full-2017AA_pruned0.1"]
#list_dataset_names = ["share_clef_2013_preprocessed"]
list_dataset_names = ["MedMentions-preprocessed/full-2014AB", "MedMentions-preprocessed/full-2017AA_pruned0.1", "MedMentions-preprocessed/full-2017AA_pruned0.2", "share_clef_2013_preprocessed_ori", "share_clef_2013_preprocessed", "NILK-preprocessed-0.001/syn_attr"]

for dataset_name in list_dataset_names:
    print(dataset_name)
    #dict_train_mentions = {}
    dict_train_entities = {}
    for data_split_mark in ["train", "valid", "test"]:
        with open("%s/%s/%s.jsonl" % (dataset_folder_path,dataset_name,data_split_mark),encoding='utf-8-sig') as f_content:
            doc = f_content.readlines()

        if data_split_mark != 'train':
            list_data_row_updated = []    

        for ind, mention_info_json in enumerate(doc):
            mention_info = json.loads(mention_info_json)    
            #mention = mention_info["mention"]
            entity_id = mention_info["label_concept"]

            # get mention and entity (can be repeated) stats
            if data_split_mark == 'train':
                #dict_train_mentions[mention] = 1
                dict_train_entities[entity_id] = 1
            else:
                if (not entity_id in dict_train_entities) or entity_id == 'CUI-less': # also keep the CUI-less or NIL entity 
                    list_data_row_updated.append(mention_info_json.strip())

        if data_split_mark != 'train':
            new_ZS_folder_path = "%s/%s-ZS" % (dataset_folder_path,dataset_name)
            # create the output folder if not existed
            if not os.path.exists(new_ZS_folder_path):
                os.makedirs(new_ZS_folder_path)
            output_to_file("%s/%s.jsonl" % (new_ZS_folder_path,data_split_mark),'\n'.join(list_data_row_updated))