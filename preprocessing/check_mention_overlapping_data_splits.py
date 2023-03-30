# check the entities of the mentions, for each of the datasets:
#       how many validation/test entities are in the training?
#       how many validation/test mentions are in the training?

from tqdm import tqdm
import json

dataset_folder_path = "../data"
list_dataset_names = ["MedMentions-preprocessed/full-2014AB", "MedMentions-preprocessed/full-2017AA_pruned0.1", "MedMentions-preprocessed/full-2017AA_pruned0.2", "share_clef_2013_preprocessed_ori", "NILK-preprocessed-0.001/syn_attr"]

for dataset_name in list_dataset_names:
    print(dataset_name)
    dict_train_mentions = {}
    dict_train_entities = {}
    for data_split_mark in ["train", "valid", "test"]:
        with open("%s/%s/%s.jsonl" % (dataset_folder_path,dataset_name,data_split_mark),encoding='utf-8-sig') as f_content:
            doc = f_content.readlines()
        
        num_men = 0
        num_men_overlap_in_train = 0
        num_ent_overlap_in_train = 0
        num_unique_ent_overlap_in_train = 0
        num_unique_ent = 0
        dict_entities_data_split = {}
        
        for ind, mention_info_json in enumerate(doc):
            mention_info = json.loads(mention_info_json)    
            mention = mention_info["mention"]
            entity_id = mention_info["label_concept"]
            
            # # not counting NIL entities
            # if entity_id == 'CUI-less':
            #     continue

            # get mention and entity (can be repeated) stats
            if data_split_mark == 'train':
                dict_train_mentions[mention] = 1
                dict_train_entities[entity_id] = 1
                num_men_overlap_in_train += 1                
                num_ent_overlap_in_train += 1                
            else:
                if mention in dict_train_mentions:
                    num_men_overlap_in_train += 1
                if entity_id in dict_train_entities:
                    num_ent_overlap_in_train += 1
            num_men += 1
            
            # getting unique ent stats    
            if not entity_id in dict_entities_data_split:
                dict_entities_data_split[entity_id] = 1
                num_unique_ent += 1
                if data_split_mark == 'train':
                    num_unique_ent_overlap_in_train += 1
                else:
                    if entity_id in dict_train_entities:
                        num_unique_ent_overlap_in_train += 1

        percent_men_overlap_in_train = float(num_men_overlap_in_train)/num_men
        percent_ent_overlap_in_train = float(num_ent_overlap_in_train)/num_men
        percent_uni_ent_overlap_in_train = float(num_unique_ent_overlap_in_train)/num_unique_ent

        print('%s overlapping mentions in training set: %.3f(%s/%s)' % (data_split_mark, percent_men_overlap_in_train, num_men_overlap_in_train, num_men))
        print('%s overlapping entities in training set: %.3f(%s/%s)' % (data_split_mark, percent_ent_overlap_in_train, num_ent_overlap_in_train, num_men))
        print('%s zero-shot entities in training set: %.3f(%s/%s)' % (data_split_mark, 1-percent_ent_overlap_in_train, num_men-num_ent_overlap_in_train, num_men))
        print('%s overlapping unique entities in training set: %.3f(%s/%s)' % (data_split_mark, percent_uni_ent_overlap_in_train, num_unique_ent_overlap_in_train, num_unique_ent))

'''
Console output: ~/BLINK/preprocessing$ python check_mention_overlapping_data_splits.py 
MedMentions-preprocessed/full-2014AB
train overlapping mentions in training set: 1.000(6181/6181)
train overlapping entities in training set: 1.000(6181/6181)
train zero-shot entities in training set: 0.000(0/6181)
train overlapping unique entities in training set: 1.000(864/864)
valid overlapping mentions in training set: 0.543(1147/2112)
valid overlapping entities in training set: 0.722(1525/2112)
valid zero-shot entities in training set: 0.278(587/2112)
valid overlapping unique entities in training set: 0.553(228/412)
test overlapping mentions in training set: 0.539(1071/1988)
test overlapping entities in training set: 0.720(1431/1988)
test zero-shot entities in training set: 0.280(557/1988)
test overlapping unique entities in training set: 0.522(203/389)

MedMentions-preprocessed/full-2017AA_pruned0.1
train overlapping mentions in training set: 1.000(6201/6201)
train overlapping entities in training set: 1.000(6201/6201)
train zero-shot entities in training set: 0.000(0/6201)
train overlapping unique entities in training set: 1.000(859/859)
valid overlapping mentions in training set: 0.541(1148/2121)
valid overlapping entities in training set: 0.752(1595/2121)
valid zero-shot entities in training set: 0.248(526/2121)
valid overlapping unique entities in training set: 0.568(217/382)
test overlapping mentions in training set: 0.537(1074/2000)
test overlapping entities in training set: 0.747(1493/2000)
test zero-shot entities in training set: 0.253(507/2000)
test overlapping unique entities in training set: 0.539(202/375)

MedMentions-preprocessed/full-2017AA_pruned0.2
train overlapping mentions in training set: 1.000(6201/6201)
train overlapping entities in training set: 1.000(6201/6201)
train zero-shot entities in training set: 0.000(0/6201)
train overlapping unique entities in training set: 1.000(775/775)
valid overlapping mentions in training set: 0.541(1148/2121)
valid overlapping entities in training set: 0.768(1629/2121)
valid zero-shot entities in training set: 0.232(492/2121)
valid overlapping unique entities in training set: 0.563(197/350)
test overlapping mentions in training set: 0.537(1074/2000)
test overlapping entities in training set: 0.780(1560/2000)
test zero-shot entities in training set: 0.220(440/2000)
test overlapping unique entities in training set: 0.544(180/331)

share_clef_2013_preprocessed_ori
train overlapping mentions in training set: 1.000(5816/5816)
train overlapping entities in training set: 1.000(5816/5816)
train zero-shot entities in training set: 0.000(0/5816)
train overlapping unique entities in training set: 1.000(1011/1011)
valid overlapping mentions in training set: 1.000(173/173)
valid overlapping entities in training set: 1.000(173/173)
valid zero-shot entities in training set: 0.000(0/173)
valid overlapping unique entities in training set: 1.000(58/58)
test overlapping mentions in training set: 0.605(3236/5351)
test overlapping entities in training set: 0.884(4728/5351)
test zero-shot entities in training set: 0.116(623/5351)
test overlapping unique entities in training set: 0.565(450/796)

NILK-preprocessed-0.001/syn_attr
train overlapping mentions in training set: 1.000(86379/86379)
train overlapping entities in training set: 1.000(86379/86379)
train zero-shot entities in training set: 0.000(0/86379)
train overlapping unique entities in training set: 1.000(63433/63433)
valid overlapping mentions in training set: 0.118(1258/10688)
valid overlapping entities in training set: 0.014(154/10688)
valid zero-shot entities in training set: 0.986(10534/10688)
valid overlapping unique entities in training set: 0.000(1/8008)
test overlapping mentions in training set: 0.117(1246/10613)
test overlapping entities in training set: 0.015(158/10613)
test zero-shot entities in training set: 0.985(10455/10613)
test overlapping unique entities in training set: 0.000(1/7987)
'''