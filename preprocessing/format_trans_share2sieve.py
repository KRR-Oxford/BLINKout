import os
import math
#import json
#for tokenisation
#from nltk.tokenize import RegexpTokenizer
from tqdm import tqdm
#from preprocess_texts_util import preprocess_pipeline, _load_add_abbr_dict
import random

#https://stackoverflow.com/a/5389547/5319143
def grouped(iterable, n=2):
    "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
    return zip(*[iter(iterable)]*n)

#output str content to a file
#input: filename and the content (str)
def output_to_file(file_name,str):
    with open(file_name, 'w', encoding="utf-8-sig") as f_output:
        f_output.write(str)

# create training/testing data
'''
Input format:
filename: 00176-102920-ECHO_REPORT.txt
00176-102920-ECHO_REPORT.txt||Disease_Disorder||C0031039||120||140
document in the .txt file
there is a folder of documents： ‘ALLREPORTS test’

Output format:
a folder containing two files for each document
File 1: 00176-102920-ECHO_REPORT.txt - which only contains the document
File 2: 00176-102920-ECHO_REPORT.concept
00176-102920-ECHO_REPORT||120|140||Disease_Disorder||mention||C0031039
where mention is the mention in the text
'''

debug = False
num_files_debugging = 10 if debug else None

precent_split_for_valid = 0.05 # the percentage of validation set, from the original training data; this is used only when create_valid_set is True.

input_data_folder_path = '../data/shareclef-ehealth-2013-natural-language-processing-and-information-retrieval-for-clinical-care-1.0'
train_doc_folder_name = 'ALLREPORTS train'
test_doc_folder_name = 'ALLREPORTS test'
train_mentions_folder_name = 'CLEFPIPEDELIMITED NoDuplicates 3:7:2013'
#test_mentions_folder_name = 'Gold_SN2011'
test_mentions_folder_name = 'Gold_SN2012' # Gold_SN2011 (what's the difference? very little, we use Gold_SN2012)

new_NIL_mention_only_for_eval = True # whether or not to ensure that NIL mentions in train, valid, and test are disjoint - suggested as True
output_data_folder_path = '../data/share_clef_2013_preprocessed_sieve%s' % ('' if new_NIL_mention_only_for_eval else '_ori')

keep_all_positions = False # if True, keeping all position for disjoint mentions.

num_mention_train = None
#for for_training in [True,False]:
# create data.json
dict_split_mark_to_data = {} # the dict from data split mark (one of train_full,train,dev,test) to the data as list_data_json_str (for BLINK)
# dict_split_mark_to_data_bio_el = {} # (for Biomedical-Entity-Linking)
dict_mentions_NIL_train = {} # dict of all NIL mentions in the training data - to avoid they appear in the validation set
dict_mentions_NIL_train_full = {} # dict of all NIL mentions in the training and validation data - to avoid they appear in the test set
for data_split_mark in ['train','test']:
    output_data_folder_path_w_split = output_data_folder_path + '/' + data_split_mark
    if not os.path.exists(output_data_folder_path_w_split):
        os.makedirs(output_data_folder_path_w_split)
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
        list_doc_men_str = [] 
        # record the number of mentions in the splitted training data
        if data_split_mark == 'train' and ind_doc_fn == num_doc_fns_train:
            num_mention_train = len(list_doc_men_str) 
                        
        #print(os.path.join(input_data_doc_folder_path, filename))
        print(filename)
        # get doc_fn and doc_concept_fn for output
        doc_fn = filename
        if doc_fn.endswith('.txt'):
            doc_id = doc_fn[:len(doc_fn)-len(".txt")]
            doc_concept_fn = doc_id + '.concept'
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
            print(doc_fn)
            mention_records = ''        
        #print(doc)
        #print(mentions)    

        #loop over mention_records to form the output json format - as each doc has many mentions
        for mention_record in mention_records:
            #print(len(mention.split('||')))
            mention_eles = mention_record.strip().split('||')
            # doc_fn = mention_eles[0]
            # if doc_fn.endswith('.txt'):
            #     doc_id = doc_fn[:len(doc_fn)-len(".txt")]
            #     doc_concept_fn = doc_id + '.concept'
            concept_type = mention_eles[1]            
            concept = mention_eles[2]            
            positions = mention_eles[3:]
            if not keep_all_positions:
                position_left = positions[0]
                position_right = positions[-1]
                positions_formatted = position_left + '|' + position_right
            else:
                positions_formatted = '|'.join(positions)    
            mention = ''
            # aggregating the discontinous entities, and get the context between the mentions
            #context_between = ''
            for mention_pos_start,mention_pos_end in grouped(positions,2):
                mention_pos_end_prev = mention_pos_end
                mention = mention + doc[int(mention_pos_start):int(mention_pos_end)]
                #context_between = context_between + doc[int(mention_pos_end_prev):int(mention_pos_start)]                
            mention = mention.replace('\n', '')
            #print(mention + ' ' + concept)   
            
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
            assert concept != ''
            men_str = '||'.join([doc_id,positions_formatted,concept_type,mention,concept])
            assert len(men_str.split('||')) == 5  
            list_doc_men_str.append(men_str)

        output_to_file('%s/%s' % (output_data_folder_path_w_split, doc_fn),doc)
        if len(list_doc_men_str) > 0: # only output if there is mention
            output_to_file('%s/%s' % (output_data_folder_path_w_split, doc_concept_fn),'\n'.join(list_doc_men_str))


#     # for BLINK
#     if data_split_mark == 'train':
#         if num_mention_train is None:
#             num_mention_train = len(list_data_json_str)
#         dict_split_mark_to_data['train_full'] = list_data_json_str
#         dict_split_mark_to_data['train'] = list_data_json_str[:num_mention_train]
#         dict_split_mark_to_data['valid'] = list_data_json_str[num_mention_train:]
#         num_mention_valid = len(list_data_json_str) - num_mention_train
#         #if not for_training:
#         num_NIL_train = countNILs(list_data_json_str[:num_mention_train])
#         num_NIL_valid = countNILs(list_data_json_str[num_mention_train:])                
#     else:   
#         dict_split_mark_to_data['test'] = list_data_json_str
#         num_mention_test = len(list_data_json_str)
#         #if not for_training:
#         num_NIL_test = countNILs(list_data_json_str)

#     # # for Biomedical-Entity-Linking
#     # if data_split_mark == 'train':
#     #     dict_split_mark_to_data_bio_el['train_full'] = (list_data_bio_el_str,list_mention_context_bio_el_str)
#     #     dict_split_mark_to_data_bio_el['train'] = (list_data_bio_el_str[:num_mention_train],list_mention_context_bio_el_str[:num_mention_train])
#     #     dict_split_mark_to_data_bio_el['valid'] = (list_data_bio_el_str[num_mention_train:],list_mention_context_bio_el_str[num_mention_train:])
#     # else:   
#     #     dict_split_mark_to_data_bio_el['test'] = (list_data_bio_el_str,list_mention_context_bio_el_str)
        
# # output the full, original training/testing set            
# # create the output folder if not existed
# if not os.path.exists(output_data_folder_path):
#     os.makedirs(output_data_folder_path)
# for output_data_mark, list_data_json_str_ in dict_split_mark_to_data.items():
#     if shuffle_mentions:
#         random.Random(1234).shuffle(list_data_json_str_)
#     output_to_file('%s/%s%s.jsonl' % (output_data_folder_path, output_data_mark, '_preprocessed' if do_preprocessing else ''),'\n'.join(list_data_json_str_))
# # # for Biomedical-Entity-Linking data format
# # for output_data_mark, data_mention_cxt_tuple in dict_split_mark_to_data_bio_el.items():
# #     list_data_bio_el_str_, list_mention_context_bio_el_str_ = data_mention_cxt_tuple
# #     output_to_file('%s/%s%s%s.txt' % (output_data_folder_path, output_data_mark, '_preprocessed' if do_preprocessing else '', '' if for_training else '_for_inference'),'\n'.join(list_data_bio_el_str_))
# #     output_to_file('%s/%s%s_context%s.txt' % (output_data_folder_path, output_data_mark, '_preprocessed' if do_preprocessing else '', '' if for_training else '_for_inference'),'\n'.join(list_mention_context_bio_el_str_))
# # output a randomly sampled subset for quick training/validation/testing
# n_data_selected = 100
# # create the output folder if not existed
# output_data_folder_path_for_sampled = output_data_folder_path + '_sampled_%d' % n_data_selected
# if not os.path.exists(output_data_folder_path_for_sampled):
#     os.makedirs(output_data_folder_path_for_sampled)
# for output_data_mark, list_data_json_str_ in dict_split_mark_to_data.items():
#     random.Random(1234).shuffle(list_data_json_str_)
#     output_to_file('%s/%s%s.jsonl' % (output_data_folder_path_for_sampled, output_data_mark, '_preprocessed' if do_preprocessing else ''),'\n'.join(list_data_json_str_[:n_data_selected]))