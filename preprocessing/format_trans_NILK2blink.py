# transform the format of NILK to BLINK - with random sampling (by mention) and entity pruning

from tqdm import tqdm
import json
import os 
import random,math
import argparse
from numpy import argsort

#get the row length of a file
#https://stackoverflow.com/a/68385697/5319143
def buf_count_newlines_gen(fname):
    def _make_gen(reader):
        while True:
            b = reader(2 ** 16)
            if not b: break
            yield b

    with open(fname, "rb") as f:
        count = sum(buf.count(b"\n") for buf in _make_gen(f.raw.read))
    return count

#output str content to a file
#input: filename and the content (str)
def output_to_file(file_name,str):
    with open(file_name, 'w', encoding="utf-8-sig") as f_output:
        f_output.write(str)

# count the number of NILs in the list of data_json_str
def countNILs(list_data_json_str):
    num_NILs = 0
    for data_json_str_ in list_data_json_str:
        data_eles = json.loads(data_json_str_)
        if data_eles['label_concept'] == 'CUI-less':
            num_NILs += 1
    return num_NILs

# add an element to a dict of list of elements for the id
def add_dict_list(dict,id,ele):
    if not id in dict:
        dict[id] = [ele] # one-element list
    else:
        list_ele = dict[id]
        list_ele.append(ele)
        dict[id] = list_ele
    return dict

def display_dict(dict):
    for key, value in dict.items():
        print('\t', key, ':', value)

parser = argparse.ArgumentParser(description="transform the NILK dataset into BLINK format")
parser.add_argument("--add_synonyms_as_ents",action="store_true",help="Whether to add synonyms to the generated training data, with each synonym as an \'entity\'")
#parser.add_argument("--do_preprocessing",action="store_true",help="whether do further text preprocessing steps")
parser.add_argument("--debug",action="store_true",help="Whether to debug, to generate a small number of data only, e.g. 10000")
parser.add_argument("--prune",action="store_true",help="Whether to prune the mentions (and also keep only the entities associated with the mentions), based on the keeping ratio below")
parser.add_argument("--keeping_ratio",type=float,help="percentage of mentions to be kept for every data split, only applicable when prune (see above) is set as true", default=0.005)
parser.add_argument("--random_seed",type=int,help="random seed for data shuffling to keep mentions", default=1234)
args = parser.parse_args()

do_preprocessing = False
add_synonyms_as_ents = args.add_synonyms_as_ents
debug = args.debug
num_files_debugging = 10000
prune = args.prune
keeping_ratio = args.keeping_ratio
random_seed = args.random_seed

input_data_folder_path = '../../data/NILK'
#input_data_folder_path = '../../data-local/NILK'
output_data_folder_path = '../data/NILK-preprocessed%s%s/%s' % ('-debug' if debug else '', ('-' + str(keeping_ratio)) if (not debug) and prune else '', 'syn_full' if add_synonyms_as_ents else 'syn_attr')
# create the output folder if not existed
if not os.path.exists(output_data_folder_path):
    os.makedirs(output_data_folder_path)

dict_split_row_len = {
    "train":86379803,
    "valid":10688055,
    "test":10613623
}
'''
consistent with the data statistics in the NILK paper
$ wc -l data/NILK/train.jsonl
86379803 data/NILK/train.jsonl
$ wc -l data/NILK/valid.jsonl
10688055 data/NILK/valid.jsonl
$ wc -l data/NILK/test.jsonl
10613623 data/NILK/test.jsonl
'''

'''
NILK data format
{"mention":"Walter Damrosch",
"offset":348,
"length":15,
"context":"...the conductor Walter Damrosch. He scored the piece for the standard instruments of the symphony orchestra plus celesta, saxophone, and automobile horns...",
"wikipedia_page_id":"309",
"wikidata_id":"Q725579",
"nil":false}

BLINK data format
{"context_left": "...the conductor ", "mention": "Walter Damrosch", "context_right": ". He scored the piece for the standard instruments of the symphony orchestra plus celesta, saxophone, and automobile horns...", "label_concept": "Q725579", "label": "A collection of fluid in a body cavity. It may be the result of a non-neoplastic disorder (e.g. heart failure) or a tumor (e.g. carcinoma of the lung). -- 2003", "label_id": 1129, "label_title": "effusion"}

'''

# the below numbers are just for checking - since NILK already uses
context_length = 256 # the overall length of context (left + right)
ctx_len_half = math.floor(context_length/2) #math.floor((context_length-1)/2)

syn_sep_sign = "||" # synonym seperation sign
            
# # get dict of ID to wikidata title, synonyms (alias), and descriptions, all in English.
# # check wikidata json format from https://doc.wikimedia.org/Wikibase/master/php/docs_topics_json.html
# dict_CUI_title = {}
# dict_CUI_DEF = {}
# dict_CUI_ind = {}
# dict_CUI_syn = {}
# entity_catalogue_fn = '../../NILK/wikidata-20170213-all.json'
# with open(entity_catalogue_fn,encoding='utf-8') as f_content:
#     for ind_ent, entity_info_json in tqdm(enumerate(f_content)):
#         if debug and ind_ent == num_files_debugging:
#             break
#         # if ind_ent == 0:
#         #     continue
#         entity_info_json = entity_info_json[:-2]
#         if entity_info_json == "":
#             continue
#         entity_info = json.loads(entity_info_json)
#         concept_def,concept_tit,concept_syns = "","",""
#         if "descriptions" in entity_info:
#             if "en" in entity_info["descriptions"]:    
#                 concept_def = entity_info["descriptions"]["en"]["value"]
#         if "en" in entity_info["labels"]:
#             concept_tit = entity_info["labels"]["en"]["value"]
#         if "en" in entity_info["aliases"]:
#             list_concept_syns = entity_info["aliases"]["en"]
#             list_concept_syns = [syn_info["value"] for syn_info in list_concept_syns]
#             for concept_syn in list_concept_syns:
#                 if syn_sep_sign in concept_syn:
#                     print(concept_syn, ':', syn_sep_sign, 'replaced to space')
#                     concept_syn = concept_syn.replace(syn_sep_sign, ' ')
#                 #assert not syn_sep_sign in concept_syn    
#             concept_syns = syn_sep_sign.join(list_concept_syns)
#         concept_CUI = entity_info['id']
#         dict_CUI_DEF[concept_CUI] = concept_def # same def for all variations (different defs? TODO)
#         dict_CUI_title = add_dict_list(dict_CUI_title,concept_CUI,concept_tit)
#         dict_CUI_ind = add_dict_list(dict_CUI_ind,concept_CUI,ind_ent)
#         dict_CUI_syn[concept_CUI] = concept_syns

# get dict of CUI/ID to Wikidata concept title and definition - from Wikidata_with_NIL.jsonl (the output of get_all_wikidata_entities.py)
dict_CUI_title = {}
dict_CUI_DEF = {}
dict_CUI_ind = {}
dict_CUI_syn = {}
entity_catalogue_fn = '../ontologies/WikiData_with_NIL%s.jsonl' % ('_syn_full' if add_synonyms_as_ents else '_syn_attr') # you need the version with NIL here to format the data with NIL.
with open(entity_catalogue_fn,encoding='utf-8') as f_content:
    doc = f_content.readlines()
for ind_ent, entity_info_json in enumerate(tqdm(doc)):
    entity_info = json.loads(entity_info_json)
    concept_def = entity_info["text"]
    concept_tit = entity_info["title"]
    concept_CUI = entity_info['idx']
    dict_CUI_DEF[concept_CUI] = concept_def # same def for all variations (different defs? TODO)
    dict_CUI_title = add_dict_list(dict_CUI_title,concept_CUI,concept_tit)
    dict_CUI_ind = add_dict_list(dict_CUI_ind,concept_CUI,ind_ent)
    #if ind_ent < 3:
    #    print('add_synonyms_as_ents:',add_synonyms_as_ents)
    if not add_synonyms_as_ents:
        assert 'synonyms' in entity_info # here 'synonyms' should be attributes in json
        concept_syns = entity_info['synonyms']    
        dict_CUI_syn[concept_CUI] = concept_syns
print(entity_catalogue_fn,':',len(dict_CUI_ind))
print('dict_CUI_syn:',len(dict_CUI_syn))

# create data
dict_data_split_mark_to_list_output = {}
dict_concept_id_by_mention = {} # the dictionary of all concept ids associated with the mentions
for data_split_mark in ['train','valid','test']:
#for data_split_mark in ['valid','test']: # not using training set
    data_path = '%s/%s.jsonl' % (input_data_folder_path, data_split_mark)
    
    if prune:
        #get the list of random indices for mention pruning
        #num_mentions = buf_count_newlines_gen(data_path)
        #print(num_mentions)
        num_mentions = dict_split_row_len[data_split_mark] # use pre-counted number of mentions
        list_random_indicies = list(range(0,num_mentions))
        print('shuffling mention/row indicies for prunning')
        random.Random(random_seed).shuffle(list_random_indicies)
        num_mentions_to_keep = int(keeping_ratio*num_mentions)
        list_random_indicies = list_random_indicies[:num_mentions_to_keep]
        set_random_indicies = set(list_random_indicies)

    list_data_json_str = []
    n_doc_data_split = 0
    list_NIL_mention_concept = [] # record a tuple of NIL mention (mention) and concept (original -> NIL)
    with open(data_path,encoding='utf-8') as f_content:
        for ind, mention_row in tqdm(enumerate(f_content), total=num_mentions):
            if debug and ind == num_files_debugging:
                break
            if (not debug) and prune and (not ind in set_random_indicies):
                if ind < 100:
                    print(ind,'pruned, go next')                
                continue
            n_doc_data_split+=1
            mention_data = json.loads(mention_row)
            mention = mention_data["mention"]
            pos_start = mention_data["offset"]
            pos_end = pos_start + mention_data["length"]
            context = mention_data["context"]
            assert context[pos_start:pos_end] == mention
            #get left and right contexts
            context_left = context[:pos_start]
            doc_ctx_left_tokens = context_left.split(' ')
            context_left_len = len(doc_ctx_left_tokens)
            if context_left_len > ctx_len_half:
                print('row %d left context len %d beyond %d' % (ind,context_left_len,ctx_len_half))
            context_left = ' '.join(doc_ctx_left_tokens[-ctx_len_half:])
            context_right = context[pos_end:]
            doc_ctx_right_tokens = context_right.split(' ')
            context_right_len = len(doc_ctx_right_tokens)
            if context_right_len > ctx_len_half:
                print('row %d right context len %d beyond %d' % (ind,context_right_len,ctx_len_half))
            context_right =  ' '.join(doc_ctx_right_tokens[0:ctx_len_half])
            concept = mention_data["wikidata_id"]
            is_mention_NIL = mention_data["nil"]

            if is_mention_NIL:
                #dict_NIL_mention_concept[mention] = concept + ' -> NIL'
                list_NIL_mention_concept.append((mention, concept + ' -> NIL'))
                concept = 'CUI-less'

            #form the data format for BLINK
            #form the dictionary for this data row
            dict_data_row = {}
            dict_data_row['context_left'] = context_left
            dict_data_row['mention'] = mention
            dict_data_row['context_right'] = context_right
            dict_data_row['label_concept'] = concept
            dict_concept_id_by_mention[concept] = 1 # add it to the dict of concept ids associated with the mentions                
            # dict_data_row['label_id'] = label_id
            # dict_data_row['label_title'] = concept_tit
            # data_json_str = json.dumps(dict_data_row)
            # list_data_json_str.append(data_json_str)
            concept_def = dict_CUI_DEF[concept] if concept in dict_CUI_DEF else ''
            dict_data_row['label'] = concept_def
            if (not add_synonyms_as_ents) and (data_split_mark == 'train'): # only add synonyms as attributes when chosen to and only in the training data
                if ind < 3:
                    print('setting synonyms in data')
                concept_syns = dict_CUI_syn[concept] if concept in dict_CUI_syn else ''
                dict_data_row['synonyms'] = concept_syns

            list_label_ids = dict_CUI_ind.get(concept) #ent2id(concept,dict_CUI_ind)# if for_training else concept #CUI2num_id(concept) # the format for training and inference is different for the "label_id", for training, it is the row index in the entity catalogue, for inference it is the CUI or ID in the original ontology.
            if list_label_ids: # if the label exists in the entity catalogue
                list_concept_tits = dict_CUI_title[concept]
                if (not add_synonyms_as_ents) or (data_split_mark != 'train'):
                    # only use the default name, i.e. the first element in the list, if chosen not to add synonyms or when in the valid or test data.
                    list_label_ids,list_concept_tits = list_label_ids[:1],list_concept_tits[:1]
                for label_id, concept_tit in zip(list_label_ids,list_concept_tits):
                    dict_data_row['label_id'] = label_id
                    dict_data_row['label_title'] = concept_tit
                    data_json_str = json.dumps(dict_data_row,ensure_ascii=False)
                    list_data_json_str.append(data_json_str)
            else:
                print('label non-exist in the entity catalogue:', concept)
                dict_data_row['label_id'] = -1
                dict_data_row['label_title'] = ""
                data_json_str = json.dumps(dict_data_row,ensure_ascii=False)
                list_data_json_str.append(data_json_str)
    
    # store the output list to the dict of key as data split mark
    dict_data_split_mark_to_list_output[data_split_mark] = list_data_json_str
    
    # get data statistics
    #if not for_training:
    if data_split_mark == 'train':
        num_doc_fns_train = n_doc_data_split
        num_mention_train = len(list_data_json_str)
        num_NIL_train = countNILs(list_data_json_str)
    elif data_split_mark == 'valid':
        num_doc_fns_valid = n_doc_data_split
        num_mention_valid = len(list_data_json_str)
        num_NIL_valid = countNILs(list_data_json_str)
    else:
        num_doc_fns_test = n_doc_data_split
        num_mention_test = len(list_data_json_str)
        num_NIL_test = countNILs(list_data_json_str)
    # display NIL mentions in the data split
    print(data_split_mark, 'NIL mentions:')
    dict_NIL_concept_to_freq_and_mentions = {} # dict of NIL concept to a 2-tuple of overall freq and NIL mentions. 
    for NIL_mention, NIL_concept in list_NIL_mention_concept:
        if NIL_concept in dict_NIL_concept_to_freq_and_mentions:
            freq_mentions = dict_NIL_concept_to_freq_and_mentions[NIL_concept][0] + 1
            str_mentions = dict_NIL_concept_to_freq_and_mentions[NIL_concept][1] + ';' + NIL_mention
            dict_NIL_concept_to_freq_and_mentions[NIL_concept] = (freq_mentions,str_mentions)
        else:
            dict_NIL_concept_to_freq_and_mentions[NIL_concept] = (1,NIL_mention)
    display_dict(dict_NIL_concept_to_freq_and_mentions)
    # check NIL mention freqs
    NIL_mention_freq = 0
    for freq_ , _ in dict_NIL_concept_to_freq_and_mentions.values():
        NIL_mention_freq += freq_
    assert countNILs(list_data_json_str) == NIL_mention_freq

# loop over the created dict data splits to output them
for data_split_mark,list_data_json_str in dict_data_split_mark_to_list_output.items():
    # update label ids under the pruning setting
    if prune:
        print('update label ids under the pruning setting')
        set_concept_id_by_mention = set(dict_concept_id_by_mention.keys())
        list_ori_concept_row_id_by_mention = []
        for concept_id in tqdm(dict_CUI_ind.keys()):
            if concept_id in set_concept_id_by_mention:
                list_label_ids = dict_CUI_ind.get(concept_id)    
                if not add_synonyms_as_ents:
                    list_label_ids = list_label_ids[:1]
                for label_id in list_label_ids:
                    list_ori_concept_row_id_by_mention.append(label_id)                    
        list_row_id_by_mention = argsort(list_ori_concept_row_id_by_mention).tolist()
        dict_ori_row_id_to_new_row_id = dict(zip(list_ori_concept_row_id_by_mention,list_row_id_by_mention))
        dict_ori_row_id_to_new_row_id[-1] = -1 # non-exist (-1) translated again to non-exist (-1)

        for i, data_json_str_ in enumerate(tqdm(list_data_json_str)):
            mention_info = json.loads(data_json_str_)
            ori_row_id = mention_info["label_id"]
            new_row_id = dict_ori_row_id_to_new_row_id[ori_row_id]
            mention_info["label_id"] = new_row_id
            data_json_str_updated = json.dumps(mention_info,ensure_ascii=False)
            list_data_json_str[i] = data_json_str_updated

    # output data
    output_data_mark = data_split_mark
    output_to_file('%s/%s%s.jsonl' % (output_data_folder_path, output_data_mark, '_preprocessed' if do_preprocessing else ''),'\n'.join(list_data_json_str))

    # get a randomly sampled subset for quick training/testing
    # shuffle the data list if not shuffled previously for splitting the validation set
    import random
    random.Random(1234).shuffle(list_data_json_str)

    #n_data_selected = 100
    n_data_selected = 1000
    # create the output folder if not existed
    output_to_file('%s/%s%s_sample%d.jsonl' % (output_data_folder_path, output_data_mark, '_preprocessed' if do_preprocessing else '', n_data_selected),'\n'.join(list_data_json_str[:n_data_selected]))

# update the list of entities if chosen to (by "prune")
if prune:
    print('updating entity catalogue: keeping those associated with mentions')
    with open(entity_catalogue_fn,encoding='utf-8') as f_content:
        doc = f_content.readlines()
        list_kept_entity_json_rows = []
        for entity_info_json in tqdm(doc):
            entity_info = json.loads(entity_info_json)
            concept_CUI = entity_info['idx']
            if concept_CUI in dict_concept_id_by_mention:
                list_kept_entity_json_rows.append(entity_info_json.strip()) # .strip() to remove \n
    # w_NIL file
    entity_catalogue_pruned_fn = '../ontologies/WikiData_pruned%s_with_NIL%s.jsonl' % ('_' + str(keeping_ratio), '_syn_full' if add_synonyms_as_ents else '_syn_attr')
    output_to_file(entity_catalogue_pruned_fn,'\n'.join(list_kept_entity_json_rows))
    # w_o_NIL file - simply remove the last row/entity: NIL
    entity_catalogue_pruned_fn = '../ontologies/WikiData_pruned%s%s.jsonl' % ('_' + str(keeping_ratio), '_syn_full' if add_synonyms_as_ents else '_syn_attr')
    output_to_file(entity_catalogue_pruned_fn,'\n'.join(list_kept_entity_json_rows[:-1]))
    
    num_entities=len(list_kept_entity_json_rows)

# display data statistics
print('training data:%d docs, %d/%d NILs/mentions' % (num_doc_fns_train,num_NIL_train,num_mention_train)) 
print('validation data:%d docs, %d/%d NILs/mentions' % (num_doc_fns_valid,num_NIL_valid,num_mention_valid))
print('testing data:%d docs, %d/%d NILs/mentions' % (num_doc_fns_test,num_NIL_test,num_mention_test))   
if prune:
    print('entities:%d' % num_entities)
'''
debug - first 10000 data stats (with-syns)
training data:10000 docs, 148/10000(23066) NILs/mentions
validation data:10000 docs, 112/10000 NILs/mentions
testing data:10000 docs, 96/10000 NILs/mentions
'''

'''
prune-to-keep-0.01 (with-syns)
training data:863798 docs, 13306/863798(1732147) NILs/mentions
validation data:106880 docs, 1626/106880 NILs/mentions
testing data:106136 docs, 1639/106136 NILs/mentions
entities:516368(686967)

prune-to-keep-0.005 (with-syns)
training data:431899 docs, 6626/431899(865810) NILs/mentions
validation data:53440 docs, 819/53440 NILs/mentions
testing data:53068 docs, 850/53068 NILs/mentions
entities:304936(421820)

prune-to-keep-0.001 (with-syns)
training data:86379 docs, 1312/86379(172831) NILs/mentions
validation data:10688 docs, 154/10688 NILs/mentions
testing data:10613 docs, 158/10613 NILs/mentions
entities:79412(121191)
'''

# Note that the command "wc -l BLINK/ontologies/WikiData_pruned_with_NIL_syn_full.jsonl ", gives 686966, showing one line less than the actual rows.

'''
$ wc -l BLINK/ontologies/WikiData_pruned_with_NIL_syn_attr.jsonl 
516367 BLINK/ontologies/WikiData_pruned_with_NIL_syn_attr.jsonl
$ wc -l BLINK/ontologies/WikiData_pruned_with_NIL_syn_full.jsonl 
686966 BLINK/ontologies/WikiData_pruned_with_NIL_syn_full.jsonl
'''