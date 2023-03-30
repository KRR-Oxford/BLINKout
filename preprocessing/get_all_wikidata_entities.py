# get entity catalogue of wikidata - BLINK and Sieve formats

from tqdm import tqdm
import json
import argparse

#output str content to a file
#input: filename and the content (str)
def output_to_file(file_name,str):
    print('saving',file_name)
    with open(file_name, 'w', encoding="utf-8") as f_output:
        f_output.write(str)

def form_str_ent_row_BLINK(CUI_def,CUI,default_name,list_synonyms,add_synonyms=True,synonym_concat_w_title=False,synonym_as_entity=True,syn_sep_sign="|"):
    dict_entity_row = {}
    dict_entity_row['text'] = CUI_def
    dict_entity_row['idx'] = CUI # CUI2num_id(CUI) # from CUI to its numeric ID
    dict_entity_row['title'] = default_name
    dict_entity_row['entity'] = default_name
    if add_synonyms:
        if synonym_as_entity:
        # if each synonym as a single entity - return the json entities (as a string of *multiple* rows), each using a synonym as the title
            list_json_dump = []
            list_json_dump.append(json.dumps(dict_entity_row,ensure_ascii=False)) 
            for synonym in list_synonyms:
                dict_entity_row['title'] = synonym
                list_json_dump.append(json.dumps(dict_entity_row,ensure_ascii=False))
            return '\n'.join(list_json_dump)
        # otherwise, synonym as a part of entity - return the json entity (as a string of a *single* row) with synonym concatenated or as an attribute.
        elif synonym_concat_w_title:
            synonyms_str = ' '.join(list_synonyms)
            dict_entity_row['title'] = default_name + ((' ' + synonyms_str) if add_synonyms else '')
            dict_entity_row['title'] = dict_entity_row['title'].strip()
        else:
            # synonyms as an attribute in the json output        
            list_synonyms_clean = syn_sign_clear(list_synonyms)
            synonyms_str = syn_sep_sign.join(list_synonyms_clean)
            dict_entity_row['synonyms'] = synonyms_str      
    return json.dumps(dict_entity_row,ensure_ascii=False) # see https://stackoverflow.com/a/58447399/5319143 for avoiding \u escape sequence

def form_str_ent_row_Sieve(CUI,default_name,list_synonyms,add_synonyms=True,syn_sep_sign="|"):
    if add_synonyms:
        list_synonyms_clean = syn_sign_clear(list_synonyms)
        synonyms_str = syn_sep_sign.join(list_synonyms_clean)
    entity_row_str = CUI + '||' + default_name + (('|' + synonyms_str) if add_synonyms else '')
    return entity_row_str

def syn_sign_clear(list_synonyms,syn_sep_sign="|"):
    list_synonyms_clean = []    
    for concept_syn in list_synonyms:
        if syn_sep_sign in concept_syn:
            print(concept_syn, ':', syn_sep_sign, 'replaced to space')
            concept_syn = concept_syn.replace(syn_sep_sign, ' ')
        list_synonyms_clean.append(concept_syn)
    return list_synonyms_clean
    
parser = argparse.ArgumentParser(description="get the list file of UMLS entities")
# parser.add_argument('-d','--dataset', type=str,
#                     help="dataset name", default='medmentions') #'share_clef2013'
parser.add_argument('-o','--output_data_folder_path', type=str,
                    help="output data folder path", default='../ontologies')
parser.add_argument('-f','--output_format', type=str,
                    help="output data format, BLINK or Sieve", default='BLINK')                         
parser.add_argument("--add_synonyms",action="store_true",help="Whether to add synonyms to the entity list")
# parser.add_argument("--clean_synonyms",action="store_true",help="Whether to clean the raw synonyms")
parser.add_argument("--synonym_concat_w_title",action="store_true",help="Whether to concat synonyms with title")
parser.add_argument("--synonym_as_entity",action="store_true",help="Whether to treat each synonym as an entity")
#parser.add_argument("--synonym_as_attr",action="store_true",help="Whether to add the synonyms as an attribute of the entity")
# parser.add_argument('--onto_ver', type=str,
#                     help="UMLS version", default='2012AB')
# parser.add_argument("--prune_entity_catalogue",action="store_true",help="Whether to prune the entities")
# parser.add_argument("--pruning_ratio",type=float,help="percentage of entities to be pruned", default=0.1)
parser.add_argument("--debug",action="store_true",help="Whether to debug, with a smaller ontology file")

args = parser.parse_args()

#dataset = args.dataset
output_data_folder_path = args.output_data_folder_path
output_format = args.output_format
add_synonyms = args.add_synonyms
#clean_synonyms = args.clean_synonyms
synonym_concat_w_title = args.synonym_concat_w_title
synonym_as_entity = args.synonym_as_entity
synonym_as_attr = (not synonym_concat_w_title) and (not synonym_as_entity) # if both above are false - then it puts synonyms as another attribute in the json output for each entity

# setting the output_syn_mark to differentiate the file names of the output .jsonl, for BLINK only
output_syn_mark = ''
if add_synonyms and output_format == 'BLINK':
    if synonym_concat_w_title: 
        output_syn_mark = '_concat'
    if synonym_as_entity:
        output_syn_mark = '_full'
        #if clean_synonyms:
        #     output_syn_mark = '_clean'
    if synonym_as_attr:
        output_syn_mark = '_attr'

'''
output format: each line is 
for BLINK:
{"text": " Autism is a developmental disorder characterized by difficulties with social interaction and communication, and by restricted and repetitive behavior. Parents usually notice signs during the first three years of their child's life. These signs often develop gradually, though some children with autism reach their developmental milestones at a normal pace before worsening. Autism is associated with a combination of genetic and environmental factors. Risk factors during pregnancy include certain infections, such as rubella, toxins including valproic acid, alcohol, cocaine, pesticides and air pollution, fetal growth restriction, and autoimmune diseases. Controversies surround other proposed environmental causes; for example, the vaccine hypothesis, which has been disproven. Autism affects information processing in the brain by altering connections and organization of nerve cells and their synapses. How this occurs is not well understood. In the DSM-5, autism and less severe forms of the condition, including Asperger syndrome and pervasive developmental disorder not otherwise specified (PDD-NOS), have been combined into the diagnosis of autism spectrum disorder (ASD). Early behavioral interventions or speech therapy can help children with autism gain self-care, social, and communication skills. Although there is no known cure, there have been cases of children who recovered. Not many children with autism live independently after reaching adulthood, though some are successful. An autistic culture has developed, with some individuals seeking a cure and others believing autism should be accepted as a difference and not treated as a disorder. Globally, autism is estimated to affect 24.8 million people . In the 2000s, the number of people affected was estimated at", "idx": "https://en.wikipedia.org/wiki?curid=25", "title": "Autism", "entity": "Autism"}

for Sieve:
D001819||Bluetongue|Blue Tongue|Tongue, Blue
'''

debug = args.debug
#num_files_debugging = 100
#syn_sep_sign = "|"

entity_catalogue_fn = '../../data/NILK/wikidata-20170213-all%s.json' % ('-debug' if debug else '')
# check wikidata json format from https://doc.wikimedia.org/Wikibase/master/php/docs_topics_json.html
list_entity_json_str = []
with open(entity_catalogue_fn,encoding='utf-8') as f_content:
    for ind_ent, entity_info_json in tqdm(enumerate(f_content)):
        #if debug and ind_ent == num_files_debugging:
        #    break
        # if ind_ent == 0:
        #     continue
        entity_info_json = entity_info_json.strip()
        if entity_info_json[-1] == ',':
            entity_info_json = entity_info_json[:-1]
        if entity_info_json == "[" or entity_info_json == "]":
            continue
        entity_info = json.loads(entity_info_json)
        CUI = entity_info["id"]
        concept_def = ""
        concept_tit = ""
        list_synonyms = []
        if "descriptions" in entity_info:
            if "en" in entity_info["descriptions"]:    
                concept_def = entity_info["descriptions"]["en"]["value"]
        if "en" in entity_info["labels"]:
            concept_tit = entity_info["labels"]["en"]["value"]
        if "en" in entity_info["aliases"]:
            list_synonyms = entity_info["aliases"]["en"]
            list_synonyms = [syn_info["value"] for syn_info in list_synonyms]
            # for concept_syn in list_synonyms:
            #     if syn_sep_sign in concept_syn:
            #         print(concept_syn, ':', syn_sep_sign, 'replaced to space')
            #         concept_syn = concept_syn.replace(syn_sep_sign, ' ')
            #     #assert not syn_sep_sign in concept_syn    
            # concept_syns = syn_sep_sign.join(list_synonyms)
        
        # entity must have an english label
        if concept_tit == "":
            continue

        if concept_tit.lower() in list_synonyms:
            # remove canonical name (lowercased) if it is also in the synonyms
            list_synonyms.remove(concept_tit.lower())
            #print(concept_tit, 'removed from', prev_CUI)
        
        #list_synonyms = set(list_synonyms) # turning it into a set - not making it faster 
        if output_format == 'BLINK':
            entity_row_str = form_str_ent_row_BLINK(concept_def,CUI,concept_tit,list_synonyms,add_synonyms=add_synonyms,synonym_concat_w_title=synonym_concat_w_title,
            synonym_as_entity=synonym_as_entity)

        elif output_format == 'Sieve':
            entity_row_str = form_str_ent_row_Sieve(CUI,concept_tit,list_synonyms,add_synonyms=add_synonyms)
        list_entity_json_str.append(entity_row_str)
entity_json_str = '\n'.join(list_entity_json_str)

# save the entity catalogue (and the one with a NIL entity)
# for BLINK/Sieve
output_to_file('%s/WikiData%s%s%s.jsonl' % (output_data_folder_path, '_syn' if add_synonyms else '', output_syn_mark, ('_' + output_format) if output_format != 'BLINK' else ''),entity_json_str)

# we add a general out-of-KB / NIL entity to the list - so that all out-of-KB entities share a common ID. - only for BLINK (i.e. not for Sieve)
if output_format == 'BLINK':
    entity_row_str = form_str_ent_row_BLINK(CUI_def='',CUI='CUI-less',default_name='NIL',list_synonyms=[],add_synonyms=add_synonyms,synonym_concat_w_title=synonym_concat_w_title,synonym_as_entity=synonym_as_entity)
    entity_json_str = entity_json_str + '\n' + entity_row_str
#elif output_format == 'Sieve':
#    entity_row_str = form_str_ent_row_Sieve(CUI='CUI-less',default_name='NIL',list_synonyms=[])
    output_to_file('%s/WikiData_with_NIL%s%s%s.jsonl' % (output_data_folder_path, '_syn' if add_synonyms else '', output_syn_mark, ('_' + output_format) if output_format != 'BLINK' else ''),entity_json_str)