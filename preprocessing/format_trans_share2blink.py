# transform the format from share/clef to blink
# added further preprocessing: tokenisation
## (REMOVED) formatting the dataset for training mode (tr_mode, by setting for_training as True): added 'label' and 'label_title' fields for training data - need to run get_all_UMLS_entities.py first

## (REMOVED) the same dataset has two different formats for training and for inference, controlled by for_training boolean variable. We now use loop to generate both settings. 

# avoid same mentions of NIL appear in the test set as those in the training data - just filter them out when they apear.

## (REMOVED) also added preprocessing for tigerchen52/Biomedical-Entity-Linking (Chen et al., 2021)

# TODO: (i) allow train_full to be the same as full data when setting new_NIL_mention_only_for_eval as True
#       so far this is done by copying the _ori train_full data
#       (ii) use UMLS2011AA instead of UMLS2012AB

import os
import math
import json
#for tokenisation
from nltk.tokenize import RegexpTokenizer
from tqdm import tqdm
from preprocess_texts_util import preprocess_pipeline, _load_add_abbr_dict
import random
import argparse

#https://stackoverflow.com/a/5389547/5319143
def grouped(iterable, n=2):
    "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
    return zip(*[iter(iterable)]*n)

def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)

#output str content to a file
#input: filename and the content (str)
def output_to_file(file_name,str):
    with open(file_name, 'w', encoding="utf-8-sig") as f_output:
        f_output.write(str)

def preprocess(text):
    #simple prepreprocessing
    #set the tokenizer: retain only alphanumeric and dots
    #tokenizer = RegexpTokenizer(r'\w+.') # original
    #return ' '.join([t for t in tokenizer.tokenize(text)])

    #preprocessing used in https://github.com/tigerchen52/Biomedical-Entity-Linking
    dict_ab3p_abbr =  _load_add_abbr_dict('abbreviation_shareclef_ab3p.dict')
    dict_add_abbr = _load_add_abbr_dict('abbreviation.dict')
    text_preprocessed = preprocess_pipeline(text,ab3p_abbr_dict=dict_ab3p_abbr,additional_abbr_dict=dict_add_abbr)
    return text_preprocessed

# return numeric ID from CUI
# transform CUIs into int, e.g. C0000774 to 774, (and CUI-less into 0)
def CUI2num_id(CUI):
    num_id = int(CUI[1:]) if CUI[1:].isdigit() else 0 
    return num_id

# return ind of the entity (or CUI)
# def ∂(ent_CUI,dict_CUI_ind):
#     #assert ent_CUI in dict_CUI_ind
#     if ent_CUI in dict_CUI_ind:
#         list_ind_ent = dict_CUI_ind[ent_CUI]
#         return list_ind_ent
#     else:
#         return [-1] # the CUI for the mention is not in the entity catalogue

# count the number of NILs in the list of data_json_str
## the function works when for_training is False
def countNILs(list_data_json_str):
    num_NILs = 0
    for data_json_str_ in list_data_json_str:
        data_eles = json.loads(data_json_str_)
        if data_eles['label_concept'] == 'CUI-less':
            num_NILs += 1
    return num_NILs

# get the NIL stats as a dictionary of NIL mention to freq
def getNILstatsDict(list_data_json_str):
    dict_NIL_mentions_freq={}
    for data_json_str_ in list_data_json_str:
        data_eles = json.loads(data_json_str_)
        if data_eles['label_concept'] == 'CUI-less':
            NIL_mention = data_eles['mention'].replace('\n','') # remove the newline sign in mentions here
            if NIL_mention in dict_NIL_mentions_freq:
                dict_NIL_mentions_freq[NIL_mention] += 1
            else:
                dict_NIL_mentions_freq[NIL_mention] = 1
    return dict_NIL_mentions_freq

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

parser = argparse.ArgumentParser(description="format the medmention dataset with different ontology settings")
parser.add_argument('--onto_ver', type=str,
                    help="UMLS version", default='2012AB')
parser.add_argument("--add_synonyms_as_ents",action="store_true",help="Whether to add synonyms to the generated training data, with each synonym as an \'entity\'")
parser.add_argument("--do_preprocessing",action="store_true",help="whether do further text preprocessing steps")
parser.add_argument("--new_NIL_mention_only_for_eval",action="store_true",help="whether or not to ensure that NIL mentions in train, valid, and test are disjoint - suggested as True - but this did not affect the result (there was no repeated NIL mention in valid and in test vs. in train).")
args = parser.parse_args()

# create training/testing data
'''
Input format:
00176-102920-ECHO_REPORT.txt||Disease_Disorder||C0031039||120||140
document in the .txt file
there is a folder of documents： ‘ALLREPORTS test’

Output format for testing: Each line is of form - where we just keep context_left, mention, context_right, and label_id.
{"context_left": "CRICKET -", "mention": "LEICESTERSHIRE", "context_right": "TAKE", "query_id": "947testa CRICKET:0", "label_id": "1622318", "Wikipedia_ID": "1622318", "Wikipedia_URL": "http://en.wikipedia.org/wiki/Leicestershire_County_Cricket_Club", "Wikipedia_title": "Leicestershire County Cricket Club"}

Output format for training: additionally with "label" (description of the label) and "label_title" (canonical name of the label).
'''

onto_ver = args.onto_ver #'2012AB'
context_length = 256 # the overall length of context (left + right)

debug = False
num_files_debugging = 10 if debug else None

do_preprocessing = args.do_preprocessing
#for_training = False # formatting the data for the purpose of training (if False, just for inference)
#create_valid_set = True # to create validation set from training
precent_split_for_valid = 0.05 # the percentage of validation set, from the original training data; this is used only when create_valid_set is True.
shuffle_mentions = False

input_data_folder_path = '../data/shareclef-ehealth-2013-natural-language-processing-and-information-retrieval-for-clinical-care-1.0'
train_doc_folder_name = 'ALLREPORTS train'
test_doc_folder_name = 'ALLREPORTS test'
train_mentions_folder_name = 'CLEFPIPEDELIMITED NoDuplicates 3:7:2013'
#test_mentions_folder_name = 'Gold_SN2011'
test_mentions_folder_name = 'Gold_SN2012' # Gold_SN2011 (what's the difference? very little, we use Gold_SN2012)

add_synonyms_as_ents = args.add_synonyms_as_ents
new_NIL_mention_only_for_eval = args.new_NIL_mention_only_for_eval # whether or not to ensure that NIL mentions in train, valid, and test are disjoint - suggested as True
#output_data_folder_path = '../data/share_clef_2013_preprocessed_%s%s' % (test_mentions_folder_name,'' if new_NIL_mention_only_for_eval else '_ori')
output_data_folder_path = '../data/share_clef_2013_preprocessed%s%s' % ('' if new_NIL_mention_only_for_eval else '_ori', '_syn_full' if add_synonyms_as_ents else '')

# get dict of CUI to UMLS concept title and definition - from UMLS2012AB_with_NIL.jsonl (the output of get_all_UMLS_entities.py)
dict_CUI_title = {}
dict_CUI_DEF = {}
dict_CUI_ind = {}
dict_CUI_syn = {}
entity_catalogue_fn = '../ontologies/UMLS%s_with_NIL%s.jsonl' % (onto_ver,'_syn_full' if add_synonyms_as_ents else '_syn_attr') # you need the version with NIL here to format the data with NIL.
with open(entity_catalogue_fn,encoding='utf-8-sig') as f_content:
    doc = f_content.readlines()
for ind_ent, entity_info_json in tqdm(enumerate(doc)):
    entity_info = json.loads(entity_info_json)
    concept_def = entity_info["text"]
    concept_tit = entity_info["title"]
    concept_CUI = entity_info['idx']
    dict_CUI_DEF[concept_CUI] = concept_def # same def for all variations (different defs? TODO)
    #dict_CUI_title[concept_CUI] = [concept_tit]
    dict_CUI_title = add_dict_list(dict_CUI_title,concept_CUI,concept_tit)
    #dict_CUI_DEF = add_dict_list(dict_CUI_DEF,concept_CUI,concept_def)
    #dict_CUI_ind[concept_CUI] = [ind_ent]
    dict_CUI_ind = add_dict_list(dict_CUI_ind,concept_CUI,ind_ent)
    if not add_synonyms_as_ents:
        assert 'synonyms' in entity_info # here 'synonyms' should be attributes in json
        concept_syns = entity_info['synonyms']    
        dict_CUI_syn[concept_CUI] = concept_syns

num_mention_train = None
#for for_training in [True,False]:
# create data.json
dict_split_mark_to_data = {} # the dict from data split mark (one of train_full,train,dev,test) to the data as list_data_json_str (for BLINK)
# dict_split_mark_to_data_bio_el = {} # (for Biomedical-Entity-Linking)
dict_mentions_NIL_train = {} # dict of all NIL mentions in the training data - to avoid they appear in the validation set
dict_mentions_NIL_train_full = {} # dict of all NIL mentions in the training and validation data - to avoid they appear in the test set
for data_split_mark in ['train','test']:
    list_data_json_str = [] # gather all the jsons (each for a mention and its entity) from the document (for BLINK)
    # list_data_bio_el_str = [] # (for Biomedical-Entity-Linking)
    # list_mention_context_bio_el_str = [] # (for Biomedical-Entity-Linking, mention context)
    if data_split_mark == 'train':
        input_data_doc_folder_path = input_data_folder_path + '/' + train_doc_folder_name
        input_data_mentions_folder_path = input_data_folder_path + '/' + train_mentions_folder_name
    else:
        input_data_doc_folder_path = input_data_folder_path + '/' + test_doc_folder_name
        input_data_mentions_folder_path = input_data_folder_path + '/' + test_mentions_folder_name

    #get the number of docs in the folder
    list_doc_fns = [filename for filename in os.listdir(input_data_doc_folder_path) if filename.endswith(".txt")]
    #random.Random(1234).shuffle(list_doc_fns)
    list_doc_fns.sort() # sort the list as os.listdir returns a list in arbitary order https://docs.python.org/3/library/os.html#os.listdir
    num_doc_fns = len(list_doc_fns)
    print(num_doc_fns)
    
    if data_split_mark == 'train':
        num_doc_fns_valid = math.floor(precent_split_for_valid*num_doc_fns)
        num_doc_fns_train = num_doc_fns - num_doc_fns_valid
    else:
        num_doc_fns_test = num_doc_fns
    if debug:
        num_doc_fns_train = num_files_debugging
        num_doc_fns_valid = 0
        num_doc_fns_test = num_files_debugging
    #for filename in os.listdir(input_data_doc_folder_path):
    #    if filename.endswith(".txt"): 
    for ind_doc_fn, filename in enumerate(tqdm(list_doc_fns[:num_files_debugging])):
        # record the number of mentions in the splitted training data
        if data_split_mark == 'train' and ind_doc_fn == num_doc_fns_train:
            num_mention_train = len(list_data_json_str) 

        ## setting to add synonyms as ents or not
        # if data_split_mark == 'test' or (data_split_mark == 'train' and ind_doc_fn >= num_doc_fns_train):
        #     add_synonyms_as_ents = False                
        #print(os.path.join(input_data_doc_folder_path, filename))
        print(filename)
        #open doc
        with open(os.path.join(input_data_doc_folder_path,filename),encoding='utf-8') as f_content:
            doc = f_content.read()
            #print(doc)
        #open mentions of the doc
        filename = filename[:len(filename)-len('.txt')] + '.pipe.txt' if data_split_mark == 'train' else filename #change filename ending to .pipe.txt for training data            
        mentions_file_path = os.path.join(input_data_mentions_folder_path,filename)
        #print(mentions_file_path)
        if os.path.exists(mentions_file_path):
            #print('exist')
            with open(mentions_file_path,encoding='utf-8') as f_content:
                mention_records = f_content.readlines()
        else:  
            print(filename, 'non-exist!')
            mention_records = ''        
        #print(doc)
        #print(mentions)    

        #loop over mention_records to form the output json format - as each doc has many mentions
        for mention_record in mention_records:
            #print(len(mention.split('||')))
            mention_eles = mention_record.split('||')
            concept = mention_eles[2]
            mention = ''
            # aggregating the discontinous entities, and get the context between the mentions
            context_between = ''
            for mention_pos_start,mention_pos_end in grouped(mention_eles[3:],2):
                mention_pos_end_prev = mention_pos_end
                mention = mention + doc[int(mention_pos_start):int(mention_pos_end)] #TODO later if possible: add a space between the parts in discontinous entities (14 Nov 22)
                context_between = context_between + doc[int(mention_pos_end_prev):int(mention_pos_start)]                
            #print(mention + ' ' + concept)   
            # get the left and right contexts (each as half of context_length tokens)
            doc_ctx_left = doc[:int(mention_pos_start)]
            doc_ctx_left_tokens = doc_ctx_left.split(' ')
            ctx_len_half = math.floor(context_length/2) #math.floor((context_length-1)/2)
            context_left = ' '.join(doc_ctx_left_tokens[-ctx_len_half:])
            ctx_btwn_len = len(context_between.split(' '))
            doc_ctx_right = doc[int(mention_pos_end):]
            doc_ctx_right_tokens = doc_ctx_right.split(' ')
            context_right = context_between + ' '.join(doc_ctx_right_tokens[0:ctx_len_half - ctx_btwn_len])            
            
            # record the NIL mentions in training and avoid them in the valid and the testing set (TODO: also the semantically similar mentions?)
            # also ensure that the NIL mentions in train, valid, and test are all disjoint.
            if new_NIL_mention_only_for_eval:
                if concept == 'CUI-less':
                #    print('\t', 'ctx_left:',len(context_left.split()), context_left)
                #    print('\t', 'mention and concept:',mention, concept)#
                #    print('\t', 'ctx_right:',len(context_left.split()), context_right)
                    print('NIL concept found')
                    if data_split_mark == 'train':
                        dict_mentions_NIL_train_full[mention] = 1
                        if ind_doc_fn<num_doc_fns_train:                            
                            dict_mentions_NIL_train[mention] = 1                                
                        else:
                            if mention in dict_mentions_NIL_train:
                                continue
                    else:                            
                        if mention in dict_mentions_NIL_train_full:
                            continue

            #preprocessing if chosen to
            if do_preprocessing:
                context_left = preprocess(context_left)
                context_right = preprocess(context_right)
            
            #form the data format for BLINK
            #form the dictionary for this data row
            dict_data_row = {}
            dict_data_row['context_left'] = context_left
            dict_data_row['mention'] = mention
            dict_data_row['context_right'] = context_right
            dict_data_row['label_concept'] = concept
            concept_def = dict_CUI_DEF[concept] if concept in dict_CUI_DEF else ''
            dict_data_row['label'] = concept_def
            if (not add_synonyms_as_ents) and (data_split_mark == 'train' and ind_doc_fn < num_doc_fns_train): # only add synonyms as attributes when chosen to and only in the training data
                concept_syns = dict_CUI_syn[concept] if concept in dict_CUI_syn else ''
                dict_data_row['synonyms'] = concept_syns
            list_label_ids = dict_CUI_ind.get(concept) #ent2id(concept,dict_CUI_ind)# if for_training else concept #CUI2num_id(concept) # the format for training and inference is different for the "label_id", for training, it is the row index in the entity catalogue, for inference it is the CUI or ID in the original ontology.
            if list_label_ids: # if the label exists in the entity catalogue
                list_concept_tits = dict_CUI_title[concept]
                if (not add_synonyms_as_ents) or (data_split_mark == 'test') or (data_split_mark == 'train' and ind_doc_fn >= num_doc_fns_train):
                    # only use the default name, i.e. the first element in the list, if chosen not to add synonyms or when in the valid or test data.
                    list_label_ids,list_concept_tits = list_label_ids[:1],list_concept_tits[:1]
                for label_id, concept_tit in zip(list_label_ids,list_concept_tits):
                    dict_data_row['label_id'] = label_id
                    dict_data_row['label_title'] = concept_tit
                    data_json_str = json.dumps(dict_data_row)
                    list_data_json_str.append(data_json_str)
            else:
                dict_data_row['label_id'] = -1
                dict_data_row['label_title'] = ""
                data_json_str = json.dumps(dict_data_row)
                list_data_json_str.append(data_json_str)
                #get additional field required for training if chosen to
                #if for_training:
                #concept_tit = dict_CUI_title[concept] if concept in dict_CUI_title else ''
                
                #data_json_str = json.dumps(dict_data_row)
                #list_data_json_str.append(data_json_str)

            # #form the data format for Biomedical-Entity-Linking
            # data_bio_el_str = filename + '\t' + concept_tit + '\t' + concept + '\t' + mention.replace('\n', ' ')  # replace newline to space in mention
            # list_data_bio_el_str.append(data_bio_el_str)
            # mention_context_bio_el_str = filename + '\t' + mention.replace('\n', ' ') + '\t' + context_left.replace('\n', ' ') + ' ' + context_right.replace('\n', ' ')
            # list_mention_context_bio_el_str.append(mention_context_bio_el_str)

    # for BLINK
    if data_split_mark == 'train':
        if num_mention_train is None:
            num_mention_train = len(list_data_json_str)
        dict_split_mark_to_data['train_full'] = list_data_json_str
        dict_split_mark_to_data['train'] = list_data_json_str[:num_mention_train]
        dict_split_mark_to_data['valid'] = list_data_json_str[num_mention_train:]
        num_mention_valid = len(list_data_json_str) - num_mention_train
        num_NIL_train = countNILs(list_data_json_str[:num_mention_train])
        num_NIL_valid = countNILs(list_data_json_str[num_mention_train:])
        #dict_NIL_mentions_freq_in_train_full = getNILstatsDict(list_data_json_str)
        dict_NIL_mentions_freq_in_train = getNILstatsDict(list_data_json_str[:num_mention_train])
        dict_NIL_mentions_freq_in_valid = getNILstatsDict(list_data_json_str[num_mention_train:])
    else:   
        dict_split_mark_to_data['test'] = list_data_json_str
        num_mention_test = len(list_data_json_str)
        num_NIL_test = countNILs(list_data_json_str)
        dict_NIL_mentions_freq_in_test = getNILstatsDict(list_data_json_str)

    # # for Biomedical-Entity-Linking
    # if data_split_mark == 'train':
    #     dict_split_mark_to_data_bio_el['train_full'] = (list_data_bio_el_str,list_mention_context_bio_el_str)
    #     dict_split_mark_to_data_bio_el['train'] = (list_data_bio_el_str[:num_mention_train],list_mention_context_bio_el_str[:num_mention_train])
    #     dict_split_mark_to_data_bio_el['valid'] = (list_data_bio_el_str[num_mention_train:],list_mention_context_bio_el_str[num_mention_train:])
    # else:   
    #     dict_split_mark_to_data_bio_el['test'] = (list_data_bio_el_str,list_mention_context_bio_el_str)
        
# output the full, original training/testing set            
# create the output folder if not existed
if not os.path.exists(output_data_folder_path):
    os.makedirs(output_data_folder_path)
for output_data_mark, list_data_json_str_ in dict_split_mark_to_data.items():
    if shuffle_mentions:
        random.Random(1234).shuffle(list_data_json_str_)
    # to train on full data
    output_data_mark_final = output_data_mark
    if output_data_mark == 'train_full':
        output_data_mark_final = 'train'
    if output_data_mark == 'train':
        output_data_mark_final = 'train_split'
    output_to_file('%s/%s%s.jsonl' % (output_data_folder_path, output_data_mark_final, '_preprocessed' if do_preprocessing else ''),'\n'.join(list_data_json_str_))
# # for Biomedical-Entity-Linking data format
# for output_data_mark, data_mention_cxt_tuple in dict_split_mark_to_data_bio_el.items():
#     list_data_bio_el_str_, list_mention_context_bio_el_str_ = data_mention_cxt_tuple
#     output_to_file('%s/%s%s%s.txt' % (output_data_folder_path, output_data_mark, '_preprocessed' if do_preprocessing else '', '' if for_training else '_for_inference'),'\n'.join(list_data_bio_el_str_))
#     output_to_file('%s/%s%s_context%s.txt' % (output_data_folder_path, output_data_mark, '_preprocessed' if do_preprocessing else '', '' if for_training else '_for_inference'),'\n'.join(list_mention_context_bio_el_str_))
# output a randomly sampled subset for quick training/validation/testing
n_data_selected = 100
# create the output folder if not existed
output_data_folder_path_for_sampled = output_data_folder_path + '_sampled_%d' % n_data_selected
if not os.path.exists(output_data_folder_path_for_sampled):
    os.makedirs(output_data_folder_path_for_sampled)
for output_data_mark, list_data_json_str_ in dict_split_mark_to_data.items():
    random.Random(1234).shuffle(list_data_json_str_)
    output_to_file('%s/%s%s.jsonl' % (output_data_folder_path_for_sampled, output_data_mark, '_preprocessed' if do_preprocessing else ''),'\n'.join(list_data_json_str_[:n_data_selected]))

# display data statistics 
#print(num_doc_fns_train,num_NIL_train,num_mention_train)
print('training data:%d docs, %d/%d NILs/mentions' % (num_doc_fns_train,num_NIL_train,num_mention_train)) 
print('validation data:%d docs, %d/%d NILs/mentions' % (num_doc_fns_valid,num_NIL_valid,num_mention_valid))
print('testing data:%d docs, %d/%d NILs/mentions' % (num_doc_fns_test,num_NIL_test,num_mention_test))                
# display NIL mentions in the data splits
print('training NIL mentions:')
display_dict(dict_NIL_mentions_freq_in_train)
print('validation NIL mentions:')
display_dict(dict_NIL_mentions_freq_in_valid)
print('testing NIL mentions:')
display_dict(dict_NIL_mentions_freq_in_test)

# updated data statistics
'''
original data stats:
train+valid 5816 (41539)
training data:190 docs, 1588/5643 NILs/mentions
validation data:9 docs, 51/173 NILs/mentions
testing data:100 docs, 1723/5351 NILs/mentions
'''

'''
with disjoint NIL mentions in train, valid, test:
training data:190 docs, 1588/5643 NILs/mentions
validation data:9 docs, 31/153 NILs/mentions
testing data:100 docs, 909/4537 NILs/mentions
'''

# prev data statistics
'''
original data stats:
training data:190 docs, 1567/5606 NILs/mentions
validation data:9 docs, 72/210 NILs/mentions
testing data:100 docs, 1723/5351 NILs/mentions - GOLD_SN2012
testing data:100 docs, 1750/5351 NILs/mentions - GOLD_SN2011

with disjoint NIL mentions in train, valid, test:
training data:190 docs, 1567/5606 NILs/mentions
validation data:9 docs, 34/172 NILs/mentions
testing data:100 docs, 909/4537 NILs/mentions - GOLD_SN2012
testing data:100 docs, 936/4537 NILs/mentions - GOLD_SN2011
'''