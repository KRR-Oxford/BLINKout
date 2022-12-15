# transform the format from medmentions to BLINK
# automated NIL generation

## (REMOVED) also added preprocessing for tigerchen52/Biomedical-Entity-Linking (Chen et al., 2021)

from pubtator_loader import PubTatorCorpusReader
from tqdm import tqdm
import json
import os 
import math
import argparse #TODO

#output str content to a file
#input: filename and the content (str)
def output_to_file(file_name,str):
    with open(file_name, 'w', encoding="utf-8-sig") as f_output:
        f_output.write(str)

# intersection of two lists
def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

# return ind of the entity (or CUI)
def ent2id(ent_CUI,dict_CUI_ind):
    #assert ent_CUI in dict_CUI_ind
    if ent_CUI in dict_CUI_ind:
        ind_ent = dict_CUI_ind[ent_CUI]
        return ind_ent
    else:
        return -1

def get_dict_CUI_STY(onto_ver):
    STY_file_path = '../ontologies/UMLS%s/MRSTY.RRF' % onto_ver
    with open(STY_file_path,encoding='utf-8') as f_content:
        doc_STY = f_content.readlines()
    dict_CUI_by_STY = {}
    # get dict of CUI filtered by STY
    for line in tqdm(doc_STY):
        sty_eles = line.split('|')
        CUI = sty_eles[0]
        STY = sty_eles[1]
        if CUI in dict_CUI_by_STY:
            dict_CUI_by_STY[CUI] = dict_CUI_by_STY[CUI] + ',' + STY
        else:
            dict_CUI_by_STY[CUI] = STY 
    return dict_CUI_by_STY

def get_dict_ret_CUI(onto_ver_new='2017AA',onto_ver_old='2014AB'):
    retired_CUI_file_path = '../ontologies/UMLS%s/MRCUI.RRF' % onto_ver_new
    # see https://www.ncbi.nlm.nih.gov/books/NBK9685/table/ch03.T.retired_cui_mapping_file_mrcui_rr/?report=objectonly for detail about this Retried CUI Mapping File.
    with open(retired_CUI_file_path,encoding='utf-8') as f_content:
        doc_ret_CUI = f_content.readlines()
    dict_CUInew_to_CUI_prev = {}
    for line in tqdm(doc_ret_CUI):
        ret_CUI_eles = line.split('|')
        last_ver_valid = ret_CUI_eles[1] # The last release version in which CUI1 was a valid CUI
        if last_ver_valid >= onto_ver_old[:6]:
            #print(last_ver_valid)
            mapping_rel = ret_CUI_eles[2]
            if mapping_rel == 'SY': # only those merged as synonyms
                CUInew = ret_CUI_eles[5]
                CUIprev = ret_CUI_eles[0]
                if CUInew != '':
                    if CUInew in dict_CUInew_to_CUI_prev:
                        dict_CUInew_to_CUI_prev[CUInew] = dict_CUInew_to_CUI_prev[CUInew] + ',' + CUIprev
                    else:
                        dict_CUInew_to_CUI_prev[CUInew] = CUIprev
    return dict_CUInew_to_CUI_prev

def get_dict_CUI(onto_ver,filter_by_SNOMEDCT=True):
    UMLS_file_path = '../ontologies/UMLS%s/MRCONSO.RRF' % onto_ver
    dict_CUI={}
    with open(UMLS_file_path,encoding='utf-8') as f_content:
        doc = f_content.readlines()
    for line in tqdm(doc):
        data_eles = line.split('|')
        lang = data_eles[1]
        if lang == 'ENG':
            CUI = data_eles[0]
            source = data_eles[11]
            if filter_by_SNOMEDCT:
                if source=='SNOMEDCT_US':
                    dict_CUI[CUI] = 1                      
    return dict_CUI

def get_dict_title2CUI(onto_ver):
    UMLS_file_path = '../ontologies/UMLS%s/MRCONSO.RRF' % onto_ver
    dict_title2CUIs={}
    with open(UMLS_file_path,encoding='utf-8') as f_content:
        doc = f_content.readlines()
    for line in tqdm(doc):
        data_eles = line.split('|')
        lang = data_eles[1]
        if lang == 'ENG':
            CUI = data_eles[0]        
            tit = data_eles[14].lower() # entity label is lower cased
            if tit in dict_title2CUIs:
                list_CUIs_from_tit = dict_title2CUIs[tit]
                if not CUI in list_CUIs_from_tit:
                    list_CUIs_from_tit.append(CUI)
                    dict_title2CUIs[tit] = list_CUIs_from_tit
            else:
                list_CUIs_from_tit = [CUI]
                dict_title2CUIs[tit] = list_CUIs_from_tit            
    return dict_title2CUIs

# filter NIL concepts from the gap concepts between the earlier, current ver of ontology and the original target ontology
# 1) STY-based filtering: see how many CUIs are in the full UMLS but not the same STY - default as False
# 2) retired-CUI filtering: see how many CUIs are retired between current ver (e.g. 2015AB/active) and new ontology (e.g. 2017AA/active) - default as True
# 3) exact-matching filtering: see how many CUIs have mention exactly matched in current ver (e.g. 2015AB), regardless of STY - default as False
def filter_concept_NIL(concept,mention,dict_CUI_by_STY,dict_CUI_by_SNOMEDCT,dict_CUInew_to_CUI_prev,dict_title2CUIs,do_STY_stat=False,do_retired_concept_filt=True,do_extact_matching_filt=False,filter_by_SNOMEDCT=False,match_uncase=True):
    #if filter_by_SNOMEDCT:
    #    if not concept in dict_CUI_by_SNOMEDCT:
    #        return False
    if do_STY_stat:
        if concept in dict_CUI_by_STY:
            if concept in dict_CUI_by_SNOMEDCT:           
                return False        
    if do_retired_concept_filt:
        if concept in dict_CUInew_to_CUI_prev:
            return False
    if do_extact_matching_filt:
        if match_uncase:
            mention = mention.lower()       
        if len(mention)>=5 and mention in dict_title2CUIs:
            print('filtered by exact-matching:', concept, mention)
            return False
    return True

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

parser = argparse.ArgumentParser(description="format the medmention dataset with different ontology settings")
parser.add_argument('--onto_ver', type=str,
                    help="UMLS version, pruned or prev: using 2017AA_pruned0.1, 2017AA_pruned0.2, or 2014AB, 2015AB for \'full\' data_setting; 2015AB/active, 2017AA/active for st21pv", default='2017AA_pruned0.1')
parser.add_argument("--add_synonyms_as_ents",action="store_true",help="Whether to add synonyms to the generated training data, with each synonym as an \'entity\'")
parser.add_argument("--filter_by_STY",action="store_true",help="Whether to filter the entities by STY")
parser.add_argument("--use_newer_ontology",action="store_true",help="whether using a newer ontology as the full set of concepts to decide NILs (this allows to limit the new ontology, e.g. only SNOMEDCT_US in 2017AA); if False, treat all unfound concept as NIL.")
parser.add_argument("--new_NIL_mention_only_for_eval",action="store_true",help="whether or not to ensure that NIL mentions in train, valid, and test are disjoint - suggested as True - but this did not affect the result (there was no repeated NIL mention in valid and in test vs. in train).")
parser.add_argument('--data_setting', type=str,
                    help="data setting for medmentions: full or st21pv", default='full') 
parser.add_argument('--filter_potential_NILs',action="store_true",help="whether or not to filter the NILs if using the versioning approach (e.g. 2014AB vs. 2017AA).")                    
args = parser.parse_args()

onto_ver = args.onto_ver
#onto_ver = '2015AB' #pruned or prev: using 2017AA_pruned0.1, 2017AA_pruned0.2, or 2014AB, 2015AB for 'full' data_setting; 2015AB/active for st21pv
#onto_ver = '2017AA' #original: 2017AA for 'full' data_setting; 2017AA/active for st21pv
if '_prune' in onto_ver:
    onto_ver_old = onto_ver[0:onto_ver.find('_prune')] # the older version of UMLS, e.g. 2014AB or the original version of the pruned ontology
else:
    onto_ver_old = onto_ver

add_synonyms_as_ents = args.add_synonyms_as_ents
#add_synonyms_as_ents = True
filter_by_STY = args.filter_by_STY
#filter_by_STY = True
STYs_filter_list = ['T047'] # only Disease or Syndrome (T047)
#STYs_filter_list = ['T038','T039']#,'T040','T041','T042','T043','T044','T045','T046','T047','T048','T191','T049','T050','T033','T034','T184'] # all under Biologic Function (T038) and Finding (T033)
use_newer_ontology = args.use_newer_ontology
#use_newer_ontology = True # whether using a newer ontology as the full set of concepts to decide NILs (this allows to limit the new ontology, e.g. only SNOMEDCT_US in 2017AA); if False, treat all unfound concept as NIL.
new_NIL_mention_only_for_eval = args.new_NIL_mention_only_for_eval
#new_NIL_mention_only_for_eval = False # whether or not to ensure that NIL mentions in train, valid, and test are disjoint - suggested as True - but this did not affect the result (there was no repeated NIL mention in valid and in test vs. in train)

context_length = 256 # the overall length of context (left + right)
data_setting = args.data_setting
#data_setting = 'full' # full or st21pv
data_path = '../data/MedMentions/%s/data/corpus_pubtator.txt' % data_setting
output_data_folder_path = '../data/MedMentions-preprocessed/%s-%s%s%s' % (data_setting,onto_ver.replace('/','-'), '_filt' if new_NIL_mention_only_for_eval else '', '_syn_full' if add_synonyms_as_ents else '')

#filter_potential_NILs = not '_prune' in onto_ver
filter_potential_NILs = args.filter_potential_NILs
if '_prune' in onto_ver: # never filter NILs if using the pruning approach
    assert filter_potential_NILs == False

#analyse_potential_NILs = not '_prune' in onto_ver
analyse_potential_NILs = filter_potential_NILs
do_STY_stat = False #whether check STY changes as a cause for 'NIL'.
do_retired_concept_filt = True
do_extact_matching_filt = False
match_uncase = True
filter_by_SNOMEDCT = True


# get dict of CUI to UMLS concept title and definition - from UMLS2015AB_with_NIL.jsonl - limited with SNOMEDCT-US (the output of get_all_UMLS_entities.py)
dict_CUI_title = {}
dict_CUI_DEF = {}
dict_CUI_ind = {}
dict_CUI_syn = {}
entity_catalogue_fn = '../ontologies/UMLS%s_with_NIL%s.jsonl' % (onto_ver.replace('/','_'),'_syn_full' if add_synonyms_as_ents else '_syn_attr') # you need the version with NIL here to format the data with NIL.
with open(entity_catalogue_fn,encoding='utf-8-sig') as f_content:
    doc = f_content.readlines()
for ind_ent, entity_info_json in tqdm(enumerate(doc)):
    entity_info = json.loads(entity_info_json)
    concept_def = entity_info["text"]
    concept_tit = entity_info["title"]
    concept_CUI = entity_info['idx']
    dict_CUI_DEF[concept_CUI] = concept_def # same def for all variations (different defs? TODO)
    dict_CUI_title = add_dict_list(dict_CUI_title,concept_CUI,concept_tit)
    dict_CUI_ind = add_dict_list(dict_CUI_ind,concept_CUI,ind_ent)
    if not add_synonyms_as_ents:
        assert 'synonyms' in entity_info # here 'synonyms' should be attributes in json
        concept_syns = entity_info['synonyms']    
        dict_CUI_syn[concept_CUI] = concept_syns
print(entity_catalogue_fn,':',len(dict_CUI_ind))

if use_newer_ontology:
    # get the dict of CUI in a newer entity catalogue - from UMLS2017AA_with_NIL.jsonl - limited with SNOMEDCT-US (the output of get_all_UMLS_entities.py)
    dict_CUI_newer_ind = {}
    entity_catalogue_new_fn = '../ontologies/UMLS2017AA%s_with_NIL.jsonl' % ('_active' if 'active' in onto_ver else '')
    #entity_catalogue_fn = '../ontologies/UMLS2017AA_with_NIL.jsonl'
    #entity_catalogue_fn = '../ontologies/UMLS2017AA_active_with_NIL.jsonl'
    with open(entity_catalogue_new_fn,encoding='utf-8-sig') as f_content:
        doc = f_content.readlines()
    for ind_ent, entity_info_json in tqdm(enumerate(doc)):
        entity_info = json.loads(entity_info_json)    
        concept_CUI = entity_info['idx']
        dict_CUI_newer_ind[concept_CUI] = ind_ent
    print(entity_catalogue_new_fn,':',len(dict_CUI_newer_ind))

if filter_potential_NILs:
    # construct dicts for NIL entity filtering
    dict_CUI_by_STY = get_dict_CUI_STY(onto_ver_old)
    dict_CUInew_to_CUI_prev = get_dict_ret_CUI(onto_ver_new = '2017AA/active' if 'active' in onto_ver_old else '2017AA',onto_ver_old=onto_ver_old)
    dict_CUI_by_SNOMEDCT = get_dict_CUI(onto_ver_old,filter_by_SNOMEDCT=filter_by_SNOMEDCT)
    dict_title2CUIs = get_dict_title2CUI(onto_ver_old)

# create training/validation/testing data
'''
Input format:
00176-102920-ECHO_REPORT.txt||Disease_Disorder||C0031039||120||140
document in the .txt file
there is a folder of documents： ‘ALLREPORTS test’

Output format for testing: Each line is of form - where we just keep context_left, mention, context_right, and label_id.
{"context_left": "CRICKET -", "mention": "LEICESTERSHIRE", "context_right": "TAKE", "query_id": "947testa CRICKET:0", "label_id": "1622318", "Wikipedia_ID": "1622318", "Wikipedia_URL": "http://en.wikipedia.org/wiki/Leicestershire_County_Cricket_Club", "Wikipedia_title": "Leicestershire County Cricket Club"}

Output format for training: additionally with "label" (description of the label) and "label_title" (canonical name of the label).
'''

dict_NIL_ori_concept2mention = {}
dict_mentions_NIL_train = {} # dict of all NIL mentions in the training data - to avoid they appear in the validation set
dict_mentions_NIL_train_dev = {} # dict of all NIL mentions in the training and validation data - to avoid they appear in the test set
for data_split_mark in ['trng','dev','test']:
    ## setting to add synonyms or not
    #if data_split_mark == 'test' or data_split_mark == 'dev':
    #    add_synonyms_as_ents = False
    list_data_json_str = [] # gather all the jsons (each for a mention and its entity) from the document (for BLINK) 
    #list_data_bio_el_str = [] # (for Biomedical-Entity-Linking)

    #dict_NIL_mention_concept = {}
    list_NIL_mention_concept = [] # record a tuple of NIL mention (mention) and concept (original -> NIL)

    pmids_split_fn = '../data/MedMentions/full/data/corpus_pubtator_pmids_%s.txt' % data_split_mark

    with open(pmids_split_fn) as f_content:
        pmids_list = f_content.readlines()
    pmids_list = [pmid.strip() for pmid in pmids_list]
    #print(pmids_list[:3])
    dataset_reader = PubTatorCorpusReader(data_path)

    corpus = dataset_reader.load_corpus() 
    # corpus will be a List[PubtatorDocuments]
    
    n_doc_data_split = 0
    for doc in tqdm(corpus):
        #print(doc)
        pmid_doc = str(doc.id)
        #print(pmid_doc)
        if pmid_doc in pmids_list:
            n_doc_data_split += 1
            #print('in')
            entities = doc.entities
            #print(entities)
            for entity in entities:
                if filter_by_STY:
                    STYs = entity.semantic_type_id
                    STYs_list = STYs.split(',')
                    # if there is overlapping of STYs between the filter list and the actual list for the mention
                    if len(intersection(STYs_filter_list,STYs_list)) == 0:
                        continue
                    #else:
                    #    print(STYs_list)    
                concept = entity.entity_id
                concept = concept[5:] if concept[:5] == 'UMLS:' else concept
                mention = entity.text_segment
                title_text = doc.title_text
                abstract_text = doc.abstract_text
                doc_text = title_text + ' ' + abstract_text
                mention_pos_start = entity.start_index
                mention_pos_end = entity.end_index
                assert mention == doc_text[mention_pos_start:mention_pos_end] # there is no discontinuous mentions in medmentions data
                doc_ctx_left = doc_text[:int(mention_pos_start)]
                doc_ctx_left_tokens = doc_ctx_left.split(' ')
                ctx_len_half = math.floor(context_length/2) #math.floor((context_length-1)/2)
                context_left = ' '.join(doc_ctx_left_tokens[-ctx_len_half:])
                doc_ctx_right = doc_text[int(mention_pos_end):]
                doc_ctx_right_tokens = doc_ctx_right.split(' ')
                context_right = ' '.join(doc_ctx_right_tokens[0:ctx_len_half])            

                #check if concept (or CUI) is in the entity catalogue
                # if onto_ver == '2014AB': 
                #     assert 'C0040115' in dict_CUI_ind # check the concept that is in data generated with UMLS2014AB but not in later versions
                if not concept in dict_CUI_ind:
                    #print(concept)
                    if use_newer_ontology: # set the new (sub-)onto as the 'complete' onto, entities not in it are treated as candidates for NIL.
                        if concept in dict_CUI_newer_ind:
                            #print('NIL concept created:',concept,'not in',onto_ver)
                            #save potential NILs
                            dict_NIL_ori_concept2mention[concept] = mention 
                            if filter_potential_NILs:
                                #filter NILs
                                is_mention_NIL = filter_concept_NIL(concept,mention,dict_CUI_by_STY,dict_CUI_by_SNOMEDCT,dict_CUInew_to_CUI_prev,dict_title2CUIs,do_STY_stat=do_STY_stat,do_retired_concept_filt=do_retired_concept_filt,do_extact_matching_filt=do_extact_matching_filt,filter_by_SNOMEDCT=filter_by_SNOMEDCT,match_uncase=match_uncase)
                            else:
                                is_mention_NIL = True
                            if is_mention_NIL:
                                #dict_NIL_mention_concept[mention] = concept + ' -> NIL'
                                list_NIL_mention_concept.append((mention, concept + ' -> NIL'))
                                concept = 'CUI-less'
                            else:
                                # TODO: add these to the hard evaluation set if possible (we only know that they are in-KB, but they do not have a CUI in the new ontology)                              
                                #pass
                                continue                                   
                        else:
                            # if concept == 'C0040115': # the concept that is in data generated with UMLS2014AB but not in later versions
                            #     print('found ya!')
                            continue # if the concept is not in the new ontology, then we do not record this mention (since we treat this new ontology as the 'complete' ontology).
                    else:
                        #save potential NILs
                        dict_NIL_ori_concept2mention[concept] = mention 
                        if filter_potential_NILs:
                            #filter NILs
                            is_mention_NIL = filter_concept_NIL(concept,mention,dict_CUI_by_STY,dict_CUI_by_SNOMEDCT,dict_CUInew_to_CUI_prev,dict_title2CUIs,do_STY_stat=do_STY_stat,do_retired_concept_filt=do_retired_concept_filt,do_extact_matching_filt=do_extact_matching_filt,filter_by_SNOMEDCT=filter_by_SNOMEDCT,match_uncase=match_uncase)
                        else:
                            is_mention_NIL = True    
                        if is_mention_NIL:
                            #dict_NIL_mention_concept[mention] = concept + ' -> NIL'
                            list_NIL_mention_concept.append((mention, concept + ' -> NIL'))
                            concept = 'CUI-less' 

                # record the NIL mentions in training and avoid them in the valid and the testing set
                # also ensure that the NIL mentions in train, valid, and test are all disjoint.
                if new_NIL_mention_only_for_eval:
                    if concept == 'CUI-less':
                    #    print('\t', 'ctx_left:',len(context_left.split()), context_left)
                    #    print('\t', 'mention and concept:',mention, concept)#
                    #    print('\t', 'ctx_right:',len(context_left.split()), context_right)
                        #print('NIL concept found')
                        if data_split_mark == 'trng':
                            dict_mentions_NIL_train_dev[mention] = 1
                            dict_mentions_NIL_train[mention] = 1                                
                        elif data_split_mark == 'dev':
                            dict_mentions_NIL_train_dev[mention] = 1
                            if mention in dict_mentions_NIL_train:
                                #dict_NIL_mention_concept.pop(mention, None) # remove the mention from the dict of NIL mentions
                                assert list_NIL_mention_concept[-1][0] == mention # check whether the last element in the list of the mention
                                list_NIL_mention_concept = list_NIL_mention_concept[:-1]
                                continue
                        else:                            
                            if mention in dict_mentions_NIL_train_dev:
                                #dict_NIL_mention_concept.pop(mention, None) # remove the mention from the dict of NIL mentions
                                assert list_NIL_mention_concept[-1][0] == mention # check whether the last element in the list of the mention
                                list_NIL_mention_concept = list_NIL_mention_concept[:-1]
                                continue

                #form the data format for BLINK
                #form the dictionary for this data row
                dict_data_row = {}
                dict_data_row['context_left'] = context_left
                dict_data_row['mention'] = mention
                dict_data_row['context_right'] = context_right
                dict_data_row['label_concept'] = concept
                concept_def = dict_CUI_DEF[concept] if concept in dict_CUI_DEF else ''
                dict_data_row['label'] = concept_def
                if (not add_synonyms_as_ents) and data_split_mark == 'trng': # only add synonyms as attributes when chosen to and only in the training data
                    concept_syns = dict_CUI_syn[concept] if concept in dict_CUI_syn else ''
                    dict_data_row['synonyms'] = concept_syns
                list_label_ids = dict_CUI_ind.get(concept) # ent2id(concept,dict_CUI_ind)# if for_training else concept #CUI2num_id(concept) # the format for training and inference is different for the "label_id", for training, it is the row index in the entity catalogue, for inference it is the CUI or ID in the original ontology.
                if list_label_ids: # if the label exists in the entity catalogue
                    list_concept_tits = dict_CUI_title[concept]
                    if (not add_synonyms_as_ents) or data_split_mark != 'trng': 
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
                    #concept_syns = dict_CUI_syn[concept] if concept in dict_CUI_syn else ''
                    #dict_data_row['synonyms'] = concept_syns

                    #data_json_str = json.dumps(dict_data_row)
                    #list_data_json_str.append(data_json_str)

                ##form the data format for Biomedical-Entity-Linking
                #data_bio_el_str = str(pmid_doc) + '\t' + mention.replace('\n', ' ') + '\t' + concept + '\t' + concept_tit
                #list_data_bio_el_str.append(data_bio_el_str)

    # get data statistics
    #if not for_training:
    if data_split_mark == 'trng':
        num_doc_fns_train = n_doc_data_split
        num_mention_train = len(list_data_json_str)
        num_NIL_train = countNILs(list_data_json_str)
    elif data_split_mark == 'dev':
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

    # create the output folder if not existed
    if not os.path.exists(output_data_folder_path):
        os.makedirs(output_data_folder_path)
    # generate onto_ver mark for the output file (including curr ver, original ver, filtered new ver of ontologies)
    onto_ver_mark = '_' + onto_ver.replace('/','_') + '_vs_2017AA' + 'filtered' if use_newer_ontology else ''
    # update data split mark
    if data_split_mark == 'trng':
        data_split_mark_final = 'train'
    elif data_split_mark == 'dev':
        data_split_mark_final = 'valid'
    else:
        data_split_mark_final = data_split_mark 
    # output the full, original training/testing set            
    #output_to_file('%s/%s_%s%s.jsonl' % (output_data_folder_path, data_setting, data_split_mark_final, onto_ver_mark),'\n'.join(list_data_json_str)) # for BLINK
    output_to_file('%s/%s.jsonl' % (output_data_folder_path, data_split_mark_final),'\n'.join(list_data_json_str)) # for BLINK
    #output_to_file('%s/%s_%s%s.jsonl' % (output_data_folder_path, data_setting, data_split_mark_final, onto_ver_mark),'\n'.join(list_data_bio_el_str)) # for Biomedical-Entity-Linking
    
    # get a randomly sampled subset for quick training/testing
    # shuffle the data list if not shuffled previously for splitting the validation set
    import random
    random.Random(1234).shuffle(list_data_json_str)

    n_data_selected = 100
    # create the output folder if not existed
    output_to_file('%s/%s_%s%s_sample%d.jsonl' % (output_data_folder_path, data_setting, data_split_mark_final,onto_ver_mark,n_data_selected),'\n'.join(list_data_json_str[:n_data_selected]))

# display data statistics
print('training data:%d docs, %d/%d NILs/mentions' % (num_doc_fns_train,num_NIL_train,num_mention_train)) 
print('validation data:%d docs, %d/%d NILs/mentions' % (num_doc_fns_valid,num_NIL_valid,num_mention_valid))
print('testing data:%d docs, %d/%d NILs/mentions' % (num_doc_fns_test,num_NIL_test,num_mention_test))   

'''
numbers in () - synonym as entity augmented training data
prune0.2
training data:2635 docs, 1031/6201(56768) NILs/mentions
validation data:878 docs, 405/2121 NILs/mentions
testing data:879 docs, 415/2000 NILs/mentions

prune0.2-filt
training data:2635 docs, 1031/6201 NILs/mentions
validation data:878 docs, 200/1916 NILs/mentions
testing data:879 docs, 181/1766 NILs/mentions

prune0.1
training data:2635 docs, 456/6201(61475) NILs/mentions
validation data:878 docs, 201/2121 NILs/mentions
testing data:879 docs, 155/2000 NILs/mentions

prune0.1-filt
training data:2635 docs, 456/6201 NILs/mentions
validation data:878 docs, 141/2061 NILs/mentions
testing data:879 docs, 88/1933 NILs/mentions

2014AB
with filter_potential_NILs - training data:2635 docs, 86/6202(62135) NILs/mentions
with filter_potential_NILs - validation data:878 docs, 44/2122 NILs/mentions
with filter_potential_NILs - testing data:879 docs, 26/2000 NILs/mentions
with filter_potential_NILs ret-SY-only (final) - training data:2635 docs, 307/6181 NILs/mentions
with filter_potential_NILs ret-SY-only (final) - validation data:878 docs, 82/2112 NILs/mentions
with filter_potential_NILs ret-SY-only (final) - testing data:879 docs, 103/1988 NILs/mentions
training data:2635 docs, 328/6202(62135) NILs/mentions
validation data:878 docs, 92/2122 NILs/mentions
testing data:879 docs, 115/2000 NILs/mentions
6202 vs. 6201 -> C0040115 was in 2014AB (as 361201009 in SNOMEDCT) but this changed to C3887666 in later versions (thus 2014AB-generated data has an extra row 2503)

2014AB-filt
with filter_potential_NILs - training data:2635 docs, 86/6202 NILs/mentions
with filter_potential_NILs - validation data:878 docs, 27/2105 NILs/mentions
with filter_potential_NILs - testing data:879 docs, 14/1988 NILs/mentions
with filter_potential_NILs ret-SY-only (final) - training data:2635 docs, 307/6181 NILs/mentions
with filter_potential_NILs ret-SY-only (final) - validation data:878 docs, 44/2074 NILs/mentions
with filter_potential_NILs ret-SY-only (final) - testing data:879 docs, 42/1927 NILs/mentions
training data:2635 docs, 328/6202 NILs/mentions
validation data:878 docs, 53/2083 NILs/mentions
testing data:879 docs, 49/1934 NILs/mentions

2015AB
with filter_potential_NILs - training data:2635 docs, 54/6201(63371) NILs/mentions
with filter_potential_NILs - validation data:878 docs, 18/2122 NILs/mentions
with filter_potential_NILs - testing data:879 docs, 13/2000 NILs/mentions
with filter_potential_NILs ret-SY-only (final) - training data:2635 docs, 140/6192 NILs/mentions
with filter_potential_NILs ret-SY-only (final) - validation data:878 docs, 42/2120 NILs/mentions
with filter_potential_NILs ret-SY-only (final) - testing data:879 docs, 39/1992 NILs/mentions
training data:2635 docs, 149/6201(63371) NILs/mentions
validation data:878 docs, 44/2122 NILs/mentions
testing data:879 docs, 47/2000 NILs/mentions

2015AB-filt
with filter_potential_NILs - training data:2635 docs, 54/6201 NILs/mentions
with filter_potential_NILs - validation data:878 docs, 18/2122 NILs/mentions
with filter_potential_NILs - testing data:879 docs, 13/2000 NILs/mentions
with filter_potential_NILs ret-SY-only (final) - training data:2635 docs, 140/6192 NILs/mentions
with filter_potential_NILs ret-SY-only (final) - validation data:878 docs, 38/2116 NILs/mentions
with filter_potential_NILs ret-SY-only (final) - testing data:879 docs, 27/1980 NILs/mentions
training data:2635 docs, 149/6201 NILs/mentions
validation data:878 docs, 40/2118 NILs/mentions
testing data:879 docs, 33/1986 NILs/mentions
'''
if analyse_potential_NILs:
    # display and analyse potentially NIL concepts
    # 1) see how many CUIs are in the full UMLS but not the same STY
    # 2) see how many CUIs are retired between current ver (2015AB/active) and 2017AA/active
    # 3) see how many CUIs have mention extractly matched in current ver (2015AB)

    if filter_potential_NILs:
        if do_STY_stat:
            dict_CUI_by_STY = get_dict_CUI_STY(onto_ver_old)
        if do_retired_concept_filt:    
            dict_CUInew_to_CUI_prev = get_dict_ret_CUI(onto_ver_new = '2017AA/active' if 'active' in onto_ver_old else '2017AA',onto_ver_old=onto_ver_old)
        if filter_by_SNOMEDCT:
            dict_CUI_by_SNOMEDCT = get_dict_CUI(onto_ver_old,filter_by_SNOMEDCT=filter_by_SNOMEDCT)
        if do_extact_matching_filt:
            dict_title2CUIs = get_dict_title2CUI(onto_ver_old)

    n_not_in_source=0
    n_sty_change=0
    n_cui_ret=0
    n_concept_drift=0
    dict_NIL_ori_concept2mention_filtered = {}
    for concept_ori_,mention_ in dict_NIL_ori_concept2mention.items():
        print('NIL concept created from ori concept:',concept_ori_,'mention as',mention_,'not in',onto_ver)
        if match_uncase:
            mention_ = mention_.lower()
        # start filtering to check the potential non-NILs    
        #if filter_by_SNOMEDCT and (not concept_ori_ in dict_CUI_by_SNOMEDCT):
        #    n_not_in_source+=1
        #    print('\t',concept_ori_,'not in SNOMEDCT')
        if do_STY_stat and (concept_ori_ in dict_CUI_by_STY):
            if filter_by_SNOMEDCT:
                if concept_ori_ in dict_CUI_by_SNOMEDCT:
                    n_sty_change+=1
                    print('\t',concept_ori_,'STY changed, prev:',dict_CUI_by_STY[concept_ori_])
                # then go to the next filter
                elif do_retired_concept_filt and concept_ori_ in dict_CUInew_to_CUI_prev:
                    n_cui_ret+=1
                    print('\t',concept_ori_,'retired, prev:',dict_CUInew_to_CUI_prev[concept_ori_])
                elif do_extact_matching_filt and len(mention_)>=5 and mention_ in dict_title2CUIs: # here to see that the length of mention_ is no less than 5 characters - thus highly ambiguous mentions are not there.
                    n_concept_drift+=1
                    list_cuis_from_mention = dict_title2CUIs[mention_]
                    print('\t',concept_ori_,mention_,'could be matched to',','.join(list_cuis_from_mention))
            else:
                n_sty_change+=1
                print('\t',concept_ori_,'STY changed, prev:',dict_CUI_by_STY[concept_ori_])    
        # then go to the next filter
        elif do_retired_concept_filt and concept_ori_ in dict_CUInew_to_CUI_prev:
            n_cui_ret+=1
            print('\t',concept_ori_,'retired, prev:',dict_CUInew_to_CUI_prev[concept_ori_])
        elif do_extact_matching_filt and len(mention_)>=5 and mention_ in dict_title2CUIs: # here to see that the length of mention_ is no less than 5 characters - thus highly ambiguous mentions are not there.
            n_concept_drift+=1
            list_cuis_from_mention = dict_title2CUIs[mention_]
            print('\t',concept_ori_,mention_,'could be matched to',','.join(list_cuis_from_mention))
        else:
            dict_NIL_ori_concept2mention_filtered[concept_ori_] = mention_

    n_potential_NILs = len(dict_NIL_ori_concept2mention)
    n_in_source = n_potential_NILs-n_not_in_source
    n_not_sty_change_but_in_source = n_in_source-n_sty_change
    n_remaining = n_not_sty_change_but_in_source-n_cui_ret
    print('ratio_not_in_source:', n_not_in_source/(n_potential_NILs+1e-7),'(%d/%d)' % (n_not_in_source,n_potential_NILs))
    print('ratio_sty_change:', n_sty_change/(n_in_source+1e-7),'(%d/%d)' % (n_sty_change,n_in_source))
    # ratio_sty_change: 0.5168539325842697 (46/89)
    print('ratio_cui_ret:', n_cui_ret/(n_not_sty_change_but_in_source+1e-7),'(%d/%d)' % (n_cui_ret,n_not_sty_change_but_in_source)) 
    # ratio_cui_ret: 0.0 (0/89)
    print('ratio_concept_drift:', n_concept_drift/(n_remaining+1e-7),'(%d/%d)' % (n_concept_drift,n_remaining)) # be aware this is solely based on string matching so the n_concept_drift may not be correct.

    # output the final filtered list of NIL
    print('Filtered list of NILs identified in %s:' % onto_ver_mark)
    for concept_ori_,mention_ in dict_NIL_ori_concept2mention_filtered.items():
        print(concept_ori_,mention_)
    # below just prev results (not fully correct)
    '''
    2015AB-SNOMEDCT-US vs 2017AA (full)
    ratio_sty_change: 0.0 (0/19874)
    ratio_cui_ret: 0.015497635101137164 (308/19874)
    ratio_concept_drift: 0.4549729121946233 (8902/19566)
    ratio_concept_drift (case-sensitive): 0.35270366963099253 (6901/19566)
    '''

    '''
    2015AB-SNOMEDCT-US vs 2017AA (full) SNOMEDCT-US
    ratio_sty_change: 0.0 (0/226)
    ratio_cui_ret: 0.13716814159292035 (31/226)
    ratio_concept_drift: 0.38461538461538464 (75/195)                   
    '''
    
    # below is more acc results 
    # NOTE: also old, see results in processing_log_mm2015AB.txt and processing_log_mm2014AB.txt
    '''
    2015AB-SNOMEDCT-US vs 2017AA (full) SNOMEDCT-US T047
    ratio_not_in_source: 0.0 (0/67)
    ratio_sty_change: 0.522388058921809 (35/67)
    ratio_cui_ret: 0.0 (0/32)
    ratio_concept_drift: 0.40624999873046874 (13/32)
    Filtered list of NILs identified in _2015AB_vs_2017AAfiltered:
    C4302339 invasive hib disease
    C4303092 ce
    C4076240 ckd-mbd
    C4302087 silent infarct
    C4076184 metastatic spinal cord compression
    C4255374 ffa
    C4303164 type i aih
    C4302185 ap
    C4274287 trochlear dysplasia
    C4302401 radiation-induced optic neuropathy
    C4303544 adhesions of the fimbrial parts
    C4304383 pandemic influenza
    '''

    '''
    2014AB-SNOMEDCT-US vs 2017AA (full) SNOMEDCT-US T047
    ratio_not_in_source: 0.0 (0/97)
    ratio_sty_change: 0.5051546386544797 (49/97)
    ratio_cui_ret: 0.0 (0/48)
    ratio_concept_drift: 0.35416666592881946 (17/48)
    Filtered list of NILs identified in _2014AB_vs_2017AAfiltered:
    C4302339 invasive hib disease
    C4303092 ce
    C3875321 inflammatory skin disease
    C4076240 ckd-mbd
    C4302087 silent infarct
    C3853962 ev71
    C4076184 metastatic spinal cord compression
    C4255374 ffa
    C3872815 cpfes
    C3875332 csa-nx
    C4303164 type i aih
    C3875265 febrile utis
    C3872816 vx
    C4302185 ap
    C4274287 trochlear dysplasia
    C4302401 radiation-induced optic neuropathy
    C4303544 adhesions of the fimbrial parts
    C4304383 pandemic influenza
    '''