# transform the format of NILK to BLINK - with random sampling and entity pruning
# debug mode: get the first k mentions (k as 10000, see variable num_files_debugging) 

# extraction of wikipedia texts based on: https://github.com/RaRe-Technologies/gensim/blob/develop/gensim/scripts/segment_wiki.py
# and https://github.com/iurshina/NILK/blob/9383521d73a7dd2a9dcaec1bc44d7134d48840da/extract_from_wiki_dump.py
from gensim.corpora.wikicorpus import get_namespace, RE_P16, filter_wiki, remove_markup, IGNORED_NAMESPACES
import gensim.utils
import re
from extract_from_wiki_dump import extract_page_xmls,segment,extract_mentions
from xml.etree import ElementTree
import pickle

from tqdm import tqdm
import json
import os,sys
import random,math
import argparse

#output str content to a file
#input: filename and the content (str)
def output_to_file(file_name,str):
    with open(file_name, 'w', encoding="utf-8-sig") as f_output:
        f_output.write(str)

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
        
parser = argparse.ArgumentParser(description="transform the NILK dataset into Sieve format")
#parser.add_argument("--do_preprocessing",action="store_true",help="whether do further text preprocessing steps")
parser.add_argument("--debug",action="store_true",help="Whether to debug, to generate a small number of data only, e.g. 10000")
parser.add_argument("--debug_KB",action="store_true",help="Whether to debug the wikidata part, to extract a small number of entities only, e.g. 100")
parser.add_argument("--doc_level",action="store_true",help="Whether to format the data on the document level, if chosen to, each .txt file will be a document instead of a mention-doc (context containing only one mention). This is better for a very large number of mentions, so that the program won't result in too many mentions. But for the pruned setting, it suffices to format the data on the mention level.")
parser.add_argument("--prune",action="store_true",help="Whether to prune the mentions (and also keep only the entities associated with the mentions), based on the keeping ratio below")
parser.add_argument("--keeping_ratio",type=float,help="percentage of mentions to be kept for every data split, only applicable when prune (see above) is set as true", default=0.005)
parser.add_argument("--random_seed",type=int,help="random seed for data shuffling to keep mentions", default=1234)
args = parser.parse_args()

do_preprocessing = False
debug = args.debug
num_files_debugging = 10000
num_files_done_in_train = -1 # number of files generated in the training set - stopped the previous time, -1 if generate all files.
debug_KB = args.debug_KB
doc_level_formatting = args.doc_level
prune = args.prune
keeping_ratio = args.keeping_ratio
random_seed = args.random_seed

#input_data_path = '../../NILK'
input_data_path = '../../data/NILK'
#output_data_folder_path = '../data/NILK'
#output_data_folder_path = '../baselines/Sieve-based/disorder-normalizer/NILK-data/sieve%s' % ('_debug' if debug else '') # for Sieve
output_data_folder_path = '../../data/NILK/sieve%s%s%s' % ('-men-as-doc' if not doc_level_formatting else '', ('-prune-' + str(keeping_ratio)) if (not debug) and prune else '', '-debug' if debug else '') # for Sieve

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

if doc_level_formatting:
    wiki_dump_fn = '../../data/NILK/enwiki-20170220-pages-articles.xml.bz2'
    dict_page_id_filtered_txt_fn = '../../data/NILK/dict_page_id_filtered_txt%s.pkl' % ('_debug' if debug_KB else '')
    #get dict_page_id_filtered_txt from wikipedia dump
    if os.path.exists(dict_page_id_filtered_txt_fn):
        with open(dict_page_id_filtered_txt_fn, 'rb') as data_f:
            print('loading dict_page_id_filtered_txt_fn')
            dict_page_id_filtered_txt = pickle.load(data_f)
            print('dict_page_id_filtered_txt_fn found', type(dict_page_id_filtered_txt), len(dict_page_id_filtered_txt))
    else:
        # create dict - this takes 24-48hs
        dict_page_id_filtered_txt = {}
        with gensim.utils.open(wiki_dump_fn, 'rb') as xml_fileobj:
            page_xmls = extract_page_xmls(xml_fileobj)

            # total - pages in 2017 wikipedia
            ind = 0
            for page_xml in tqdm(page_xmls, total=17_303_347):
                ind+=1
                if debug and ind > 100:
                    break
                elem = ElementTree.fromstring(page_xml)
                namespace = get_namespace(elem.tag)
                ns_mapping = {"ns": namespace}
                text_path = "./{%(ns)s}revision/{%(ns)s}text" % ns_mapping
                title_path = "./{%(ns)s}title" % ns_mapping
                pageid_path = "./{%(ns)s}id" % ns_mapping

                text = elem.find(text_path).text
                title = elem.find(title_path).text
                pageid = elem.find(pageid_path).text

                if any(title.startswith(ignore + ':') for ignore in IGNORED_NAMESPACES):  # filter non-articles
                    continue

                if text is None or len(text) == 0:
                    continue

                filtered = filter_wiki(text, promote_remaining=False, simplify_links=False)
                dict_page_id_filtered_txt[pageid] = remove_markup(filtered)
                #dict_page_id_filtered_txt[pageid] = text
        # store dict to pickle
        with open(dict_page_id_filtered_txt_fn, 'wb') as data_f:
            pickle.dump(dict_page_id_filtered_txt, data_f)
            print('dictionary of wikipedia pageid to filtered texts stored to',dict_page_id_filtered_txt_fn)

# # loop over the dict to filter and remove markup for the texts

# for pageid, text in tqdm(dict_page_id_filtered_txt.items()):
#     filtered = filter_wiki(text, promote_remaining=False, simplify_links=False)
#     dict_page_id_filtered_txt[pageid] = remove_markup(filtered)

#sys.exit(0) # for generating dict_page_id_filtered_txt only

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

Sieve data format
a folder containing two files for each document
File 1: 27773526.txt - which only contains the document
File 2: 27773526.concept
27773526||1423|1436||T047||mention||C0020456
where mention is the mention in the text, e.g. hyperglycemic
'''

context_length = 256 # the overall length of context (left + right)
ctx_len_half = math.floor(context_length/2) #math.floor((context_length-1)/2)
syn_sep_sign = "||" # synonym seperation sign

# create data
dict_concept_id_by_mention = {} # the dictionary of all concept ids associated with the mentions
for data_split_mark in ['train','valid','test']:
#for data_split_mark in ['valid','test']: # not using training set
    data_path = '%s/%s.jsonl' % (input_data_path,data_split_mark)

    if prune:
        #get the list of random indices for mention pruning
        num_mentions = dict_split_row_len[data_split_mark] # use pre-counted number of mentions
        list_random_indicies = list(range(0,num_mentions))
        print('shuffling mention/row indicies for prunning')
        random.Random(random_seed).shuffle(list_random_indicies)
        num_mentions_to_keep = int(keeping_ratio*num_mentions)
        list_random_indicies = list_random_indicies[:num_mentions_to_keep]
        set_random_indicies = set(list_random_indicies)

    list_NIL_mention_concept = []

    output_data_folder_path_w_split = output_data_folder_path + '/' + data_split_mark
    if not os.path.exists(output_data_folder_path_w_split):
        os.makedirs(output_data_folder_path_w_split)

    n_doc_data_split = 0
    num_mention = 0
    num_mention_NIL = 0
    
    num_doc_omitted = 0
    dict_page_id_list_mention_strs = {} # dict of pageid to all of the mention_strs in sieve format
    with open(data_path,encoding='utf-8') as f_content:
        for ind, mention_row in enumerate(tqdm(f_content)):
            if debug:
                # generate only a certain number of files for debugging
                if ind == num_files_debugging:
                    break
            else:
                # continue the previously stopped place
                if data_split_mark == 'train' and ind <= num_files_done_in_train:
                    continue
            if (not debug) and prune and (not ind in set_random_indicies):
                if ind < 100:
                    print(ind,'pruned, go next')                
                continue
            mention_data = json.loads(mention_row)
            mention = mention_data["mention"]
            
            # get pos_start and pos_end for the context
            pageid = mention_data["wikipedia_page_id"]
            pos_start = mention_data["offset"]
            pos_end = pos_start + mention_data["length"]
            context = mention_data["context"]
            assert context[pos_start:pos_end] == mention
            
            if doc_level_formatting:
                # get pos_start and pos_end for the document
                doc = dict_page_id_filtered_txt[pageid]
               
                #assert context in doc
                context_w_o_markup = remove_markup(context)
                if not context_w_o_markup in doc:
                    print('mention:', mention, 
                    '\npositions:', pos_start, pos_end, 
                    '\ncontext:',context_w_o_markup,
                    '\n\ndoc:', doc)
                    num_doc_omitted+=1
                    continue
                pos_context = doc.find(context_w_o_markup)
                pos_start = pos_start + pos_context
                pos_end = pos_end + pos_context

            #get left and right contexts
            # context_left = context[:pos_start]
            # doc_ctx_left_tokens = context_left.split(' ')
            # context_left_len = len(doc_ctx_left_tokens)
            # if context_left_len > ctx_len_half:
            #     print('row %d left context len %d beyond %d' % (ind,context_left_len,ctx_len_half))
            # context_left = ' '.join(doc_ctx_left_tokens[-ctx_len_half:])
            # context_right = context[pos_end:]
            # doc_ctx_right_tokens = context_right.split(' ')
            # context_right_len = len(doc_ctx_right_tokens)
            # if context_right_len > ctx_len_half:
            #     print('row %d right context len %d beyond %d' % (ind,context_right_len,ctx_len_half))
            # context_right =  ' '.join(doc_ctx_right_tokens[0:ctx_len_half])
            concept = mention_data["wikidata_id"]
            is_mention_NIL = mention_data["nil"]

            n_doc_data_split+=1
            num_mention+=1
            if is_mention_NIL:
                list_NIL_mention_concept.append((mention, concept + ' -> NIL'))
                concept = 'CUI-less'
                num_mention_NIL+=1
            positions_formatted = str(pos_start) + '|' + str(pos_end)
            STYs = "" # semantic type info not used
            
            men_str = '||'.join([str(ind),positions_formatted,STYs,mention,concept])
            dict_page_id_list_mention_strs = add_dict_list(dict_page_id_list_mention_strs,pageid,men_str)
            
            dict_concept_id_by_mention[concept] = 1 # add the concept id to the dict of concept ids associated with the mentions
            
            # the default mention-level formatting
            if not doc_level_formatting:
                doc_fn = str(ind) + '.txt'
                output_to_file('%s/%s' % (output_data_folder_path_w_split, doc_fn),context)
                doc_concept_fn = str(ind) + '.concept'
                output_to_file('%s/%s' % (output_data_folder_path_w_split, doc_concept_fn),men_str)

    if doc_level_formatting:
        for pageid in dict_page_id_list_mention_strs:
            #save the doc file
            doc_fn = str(pageid) + '.txt'
            doc = dict_page_id_filtered_txt[pageid]
            output_to_file('%s/%s' % (output_data_folder_path_w_split, doc_fn),doc)
            #save the concept file
            doc_concept_fn = str(pageid) + '.concept'
            list_doc_men_str = dict_page_id_list_mention_strs[pageid]
            output_to_file('%s/%s' % (output_data_folder_path_w_split, doc_concept_fn),'\n'.join(list_doc_men_str))       
    
    n_doc_data_split = len(dict_page_id_list_mention_strs) # number of documents recorded in this data split
    # get data statistics
    if data_split_mark == 'train':
        num_doc_fns_train = n_doc_data_split
        num_doc_fns_train_full = n_doc_data_split + num_doc_omitted
        num_mention_train = num_mention
        num_NIL_train = num_mention_NIL
    elif data_split_mark == 'valid':
        num_doc_fns_valid = n_doc_data_split
        num_doc_fns_valid_full = n_doc_data_split + num_doc_omitted
        num_mention_valid = num_mention
        num_NIL_valid = num_mention_NIL
    else:
        num_doc_fns_test = n_doc_data_split
        num_doc_fns_test_full = n_doc_data_split + num_doc_omitted
        num_mention_test = num_mention
        num_NIL_test = num_mention_NIL
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
    assert num_mention_NIL == NIL_mention_freq

# update the list of entities if chosen to (by "prune")
if prune:
    print('updating entity catalogue: keeping those associated with mentions')
    for w_syn in [True,False]:
        entity_catalogue_fn = "../ontologies/WikiData%s_Sieve.jsonl" % ('_syn' if w_syn else '')
        with open(entity_catalogue_fn,encoding='utf-8') as f_content:
            doc = f_content.readlines()
            list_kept_entity_rows = []
            for entity_info in tqdm(doc):
                concept_CUI = entity_info.split('||')[0]
                if concept_CUI in dict_concept_id_by_mention:
                    list_kept_entity_rows.append(entity_info.strip()) # .strip() to remove \n
        entity_catalogue_pruned_fn = '../ontologies/WikiData_pruned%s%s_Sieve.jsonl' % ('_' + str(keeping_ratio), '_syn' if w_syn else '')
        output_to_file(entity_catalogue_pruned_fn,'\n'.join(list_kept_entity_rows))
        num_entities=len(list_kept_entity_rows)

# display data statistics
print('training data:%d/%d docs, %d/%d NILs/mentions' % (num_doc_fns_train,num_doc_fns_train_full,num_NIL_train,num_mention_train)) 
print('validation data:%d/%d docs, %d/%d NILs/mentions' % (num_doc_fns_valid,num_doc_fns_valid_full,num_NIL_valid,num_mention_valid))
print('testing data:%d/%d docs, %d/%d NILs/mentions' % (num_doc_fns_test,num_doc_fns_test_full,num_NIL_test,num_mention_test))   
if prune:
    print('entities:%d' % num_entities)
'''
First 10k mentions
training data:124/1975 docs, 129/8149 NILs/mentions
validation data:736/2040 docs, 97/8696 NILs/mentions
testing data:771/2075 docs, 79/8696 NILs/mentions

pruned-by-keeping-0.01
training data:631737/631737 docs, 13306/863798 NILs/mentions
validation data:98918/98918 docs, 1626/106880 NILs/mentions
testing data:98444/98444 docs, 1639/106136 NILs/mentions
entities:516367
'''

'''
~/data/NILK/sieve-men-as-doc-prune$ cd train/
~/data/NILK/sieve-men-as-doc-prune/train$ ls | wc -l
1727596
~/data/NILK/sieve-men-as-doc-prune/train$ cd ..
~/data/NILK/sieve-men-as-doc-prune$ cd valid/
~/data/NILK/sieve-men-as-doc-prune/valid$ ls | wc -l
213760
~/data/NILK/sieve-men-as-doc-prune/valid$ cd ..
~/data/NILK/sieve-men-as-doc-prune$ cd test/
~/data/NILK/sieve-men-as-doc-prune/test$ ls | wc -l
212272

~/BLINK/ontologies$ wc -l WikiData_pruned_Sieve.jsonl 
516366 WikiData_pruned_Sieve.jsonl
~/BLINK/ontologies$ wc -l WikiData_pruned_syn_Sieve.jsonl 
516366 WikiData_pruned_syn_Sieve.jsonl
'''