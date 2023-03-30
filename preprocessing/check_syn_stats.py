# check the stats of the datasets w.r.t synonyms
#	Percentage of entities w. synonyms
#	Average #syn per ent
#	Average #syn per ent having syns
#   Randomly sample a set of syns (e.g. between 5 and 20) and have a check

from tqdm import tqdm
import json
import random 
import statistics as stat

def get_random_sample_indicies(max_num,num_to_keep,random_seed=1234):
    list_random_indicies = list(range(0,max_num))
    random.Random(random_seed).shuffle(list_random_indicies)
    list_random_indicies = list_random_indicies[:num_to_keep]
    set_random_indicies = set(list_random_indicies)
    return set_random_indicies

def check_jsonl_file_syns(dataset_folder_path,dataset_name,show_examples=True):
    print(dataset_name)
    with open("%s/%s" % (dataset_folder_path,dataset_name),encoding='utf-8-sig') as f_content:
        doc = f_content.readlines()
    num_men = 0
    num_men_has_syns = 0
    num_syn = 0
    list_num_syn = []
    list_num_syn_above_zero = []
    if show_examples:
        set_rand_inds = get_random_sample_indicies(len(doc),num_to_keep=50)
        print("\texamples:")
    for ind, mention_info_json in enumerate(doc):
        mention_info = json.loads(mention_info_json)
        if "synonyms" in mention_info:
            synonyms = mention_info["synonyms"]
            if synonyms != '':
                num_syn_of_ent = len(synonyms.split("|"))
                num_syn += num_syn_of_ent
                list_num_syn.append(num_syn_of_ent)
                if num_syn_of_ent > 1:
                    list_num_syn_above_zero.append(num_syn_of_ent)
            else:
                list_num_syn.append(0)        
        else:
            #print('no syn mention:', mention_info_json)
            synonyms = ''
        if synonyms != '':
            num_men_has_syns+=1
        num_men+=1
        if show_examples:
            if ind in set_rand_inds:
                if synonyms != '':
                    print("\t\tentity:", mention_info["label_title"] if "label_title" in mention_info else mention_info["title"])
                    print("\t\tsynonyms:",synonyms)

    print('list_num_syn[:50]',list_num_syn[:50])
    print('list_num_syn_above_zero[:50]',list_num_syn_above_zero[:50])
    
    percent_men_has_syns = float(num_men_has_syns)/num_men
    ave_syn_per_ent = float(num_syn)/num_men
    std_syn_per_ent = stat.stdev(list_num_syn)
    ave_syn_per_ent_w_syn = float(num_syn)/num_men_has_syns
    std_syn_per_ent_w_syn = stat.stdev(list_num_syn_above_zero)
    print("\t%.3f (%d/%d) rows have synonyms" % (percent_men_has_syns,num_men_has_syns,num_men))    
    print("\tave syn per ent: %.2f±%.2f" % (ave_syn_per_ent,std_syn_per_ent))
    print("\tave syn per ent with at least 1 syn: %.2f±%.2f" % (ave_syn_per_ent_w_syn,std_syn_per_ent_w_syn))

show_examples = False

# check the entities of the mentions
dataset_folder_path = "../data"
list_dataset_names = ["MedMentions-preprocessed/full-2014AB/train.jsonl", "MedMentions-preprocessed/full-2017AA_pruned0.1/train.jsonl", "MedMentions-preprocessed/full-2017AA_pruned0.2/train.jsonl", "share_clef_2013_preprocessed_ori/train.jsonl", "NILK-preprocessed-0.001/syn_attr/train.jsonl"]

for dataset_name in list_dataset_names:
    check_jsonl_file_syns(dataset_folder_path,dataset_name,show_examples=show_examples)

# check the entities in the ontology
ontology_folder_name = '../ontologies'
list_ent_catalogue_names = ["UMLS2012AB_syn_attr.jsonl", "UMLS2014AB_syn_attr.jsonl", "UMLS2017AA_pruned0.1_syn_attr.jsonl", "UMLS2017AA_pruned0.2_syn_attr.jsonl", "WikiData_pruned_0.001_syn_attr.jsonl","WikiData_pruned_0.005_syn_attr.jsonl","WikiData_syn_attr.jsonl"]

for entity_catalogue_name in list_ent_catalogue_names:
    check_jsonl_file_syns(ontology_folder_name,entity_catalogue_name,show_examples=show_examples)

'''
MedMentions-preprocessed/full-2014AB/train.jsonl
        0.947 (5851/6181) rows have synonyms
        ave syn per ent: 9.05±6.87
        ave syn per ent with at least 1 syn: 9.56±6.87
MedMentions-preprocessed/full-2017AA_pruned0.1/train.jsonl
        0.924 (5728/6201) rows have synonyms
        ave syn per ent: 8.91±6.98
        ave syn per ent with at least 1 syn: 9.65±6.98
MedMentions-preprocessed/full-2017AA_pruned0.2/train.jsonl
        0.831 (5153/6201) rows have synonyms
        ave syn per ent: 8.15±7.10
        ave syn per ent with at least 1 syn: 9.81±7.10
share_clef_2013_preprocessed_ori/train.jsonl
        0.685 (3986/5816) rows have synonyms
        ave syn per ent: 6.14±8.31
        ave syn per ent with at least 1 syn: 8.96±8.31
NILK-preprocessed-0.001/syn_attr/train.jsonl
        0.360 (31113/86379) rows have synonyms
        ave syn per ent: 1.00±3.34
        ave syn per ent with at least 1 syn: 2.78±3.34
UMLS2012AB_syn_attr.jsonl
        0.990 (87295/88150) rows have synonyms
        ave syn per ent: 2.27±2.37
        ave syn per ent with at least 1 syn: 2.29±2.37
UMLS2014AB_syn_attr.jsonl
        0.993 (35164/35398) rows have synonyms
        ave syn per ent: 2.51±2.65
        ave syn per ent with at least 1 syn: 2.52±2.65
UMLS2017AA_pruned0.1_syn_attr.jsonl
        0.994 (35175/35392) rows have synonyms
        ave syn per ent: 2.57±2.63
        ave syn per ent with at least 1 syn: 2.58±2.63
UMLS2017AA_pruned0.2_syn_attr.jsonl
        0.994 (31264/31460) rows have synonyms
        ave syn per ent: 2.56±2.62
        ave syn per ent with at least 1 syn: 2.58±2.62
WikiData_pruned_0.001_syn_attr.jsonl
        0.255 (20211/79411) rows have synonyms
        ave syn per ent: 0.53±3.06
        ave syn per ent with at least 1 syn: 2.07±3.06
WikiData_pruned_0.005_syn_attr.jsonl
        0.201 (61390/304935) rows have synonyms
        ave syn per ent: 0.38±3.08
        ave syn per ent with at least 1 syn: 1.90±3.08
WikiData_syn_attr.jsonl
        0.118 (1728455/14593338) rows have synonyms
        ave syn per ent: 0.22±1.75
        ave syn per ent with at least 1 syn: 1.84±1.75
(base) hang@KRR-GPU1:~/BLINK/preprocessing$ python
Python 3.9.12 (main, Apr  5 2022, 06:56:58) 
[GCC 7.5.0] :: Anaconda, Inc. on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> "".split("|")
['']
>>> len("".split("|"))
1
>>> len("d|e".split("|"))
2
>>> len("d|e".split("|"))
2
>>> exit()
(base) hang@KRR-GPU1:~/BLINK/preprocessing$ python
Python 3.9.12 (main, Apr  5 2022, 06:56:58) 
[GCC 7.5.0] :: Anaconda, Inc. on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> exit()
(base) hang@KRR-GPU1:~/BLINK/preprocessing$ python check_syn_stats.py 
MedMentions-preprocessed/full-2014AB/train.jsonl
        0.947 (5851/6181) rows have synonyms
        ave syn per ent: 9.05±7.02
        ave syn per ent with at least 1 syn: 9.56±6.74
MedMentions-preprocessed/full-2017AA_pruned0.1/train.jsonl
        0.924 (5728/6201) rows have synonyms
        ave syn per ent: 8.91±7.19
        ave syn per ent with at least 1 syn: 9.65±6.85
MedMentions-preprocessed/full-2017AA_pruned0.2/train.jsonl
        0.831 (5153/6201) rows have synonyms
        ave syn per ent: 8.15±7.44
        ave syn per ent with at least 1 syn: 9.81±6.95
share_clef_2013_preprocessed_ori/train.jsonl
        0.685 (3986/5816) rows have synonyms
        ave syn per ent: 6.14±8.09
        ave syn per ent with at least 1 syn: 8.96±8.27
NILK-preprocessed-0.001/syn_attr/train.jsonl
        0.360 (31113/86379) rows have synonyms
        ave syn per ent: 1.00±2.41
        ave syn per ent with at least 1 syn: 2.78±3.97
        
UMLS2012AB_syn_attr.jsonl
        0.990 (87295/88150) rows have synonyms
        ave syn per ent: 2.27±2.37
        ave syn per ent with at least 1 syn: 2.29±2.80
UMLS2014AB_syn_attr.jsonl
        0.993 (35164/35398) rows have synonyms
        ave syn per ent: 2.51±2.65
        ave syn per ent with at least 1 syn: 2.52±3.06
UMLS2017AA_pruned0.1_syn_attr.jsonl
        0.994 (35175/35392) rows have synonyms
        ave syn per ent: 2.57±2.63
        ave syn per ent with at least 1 syn: 2.58±2.98
UMLS2017AA_pruned0.2_syn_attr.jsonl
        0.994 (31264/31460) rows have synonyms
        ave syn per ent: 2.56±2.62
        ave syn per ent with at least 1 syn: 2.58±2.96
WikiData_pruned_0.001_syn_attr.jsonl
        0.255 (20211/79411) rows have synonyms
        ave syn per ent: 0.53±1.79
        ave syn per ent with at least 1 syn: 2.07±4.48
WikiData_pruned_0.005_syn_attr.jsonl
        0.201 (61390/304935) rows have synonyms
        ave syn per ent: 0.38±1.58
        ave syn per ent with at least 1 syn: 1.90±4.93
WikiData_syn_attr.jsonl
        0.118 (1728455/14593338) rows have synonyms
        ave syn per ent: 0.22±0.85
        ave syn per ent with at least 1 syn: 1.84±2.18
'''        