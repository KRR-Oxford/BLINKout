# get entity catalogue of UMLS - Sieve's format
# for ShARe/CLEF 2013: get all UMLS 2012 AB entities as subset of SNOMEDCT and in the disease semantic group (according to Ji, 2020, AMIA)
# for MedMentions: get UMLS2017AA (according to Mohan and Li, 2019, AKBC) or a previous version of UMLS (e.g. UMLS2015AB)'s entity catelogue with source or semantic type filters.
#                  add pruning as random concept selection

## also added preprocessing for tigerchen52/Biomedical-Entity-Linking (Chen et al., 2021)

'''
output format: each line is 
for BLINK:
{"text": " Autism is a developmental disorder characterized by difficulties with social interaction and communication, and by restricted and repetitive behavior. Parents usually notice signs during the first three years of their child's life. These signs often develop gradually, though some children with autism reach their developmental milestones at a normal pace before worsening. Autism is associated with a combination of genetic and environmental factors. Risk factors during pregnancy include certain infections, such as rubella, toxins including valproic acid, alcohol, cocaine, pesticides and air pollution, fetal growth restriction, and autoimmune diseases. Controversies surround other proposed environmental causes; for example, the vaccine hypothesis, which has been disproven. Autism affects information processing in the brain by altering connections and organization of nerve cells and their synapses. How this occurs is not well understood. In the DSM-5, autism and less severe forms of the condition, including Asperger syndrome and pervasive developmental disorder not otherwise specified (PDD-NOS), have been combined into the diagnosis of autism spectrum disorder (ASD). Early behavioral interventions or speech therapy can help children with autism gain self-care, social, and communication skills. Although there is no known cure, there have been cases of children who recovered. Not many children with autism live independently after reaching adulthood, though some are successful. An autistic culture has developed, with some individuals seeking a cure and others believing autism should be accepted as a difference and not treated as a disorder. Globally, autism is estimated to affect 24.8 million people . In the 2000s, the number of people affected was estimated at", "idx": "https://en.wikipedia.org/wiki?curid=25", "title": "Autism", "entity": "Autism"}

for Sieve:
D001819||Bluetongue|Blue Tongue|Tongue, Blue
'''

from tqdm import tqdm
import json
import random,math
import argparse

#output str content to a file
#input: filename and the content (str)
def output_to_file(file_name,str):
    print('saving',file_name)
    with open(file_name, 'w', encoding="utf-8-sig") as f_output:
        f_output.write(str)

# return numeric ID from CUI
# transform CUIs into int, e.g. C0000774 to 774, (and CUI-less into 0)
def CUI2num_id(CUI):
    num_id = int(CUI[1:]) if CUI[1:].isdigit() else 0 
    return num_id

def _delete_rand_items(items,n,random_seed=1234): # random seed is default as 1234
    to_delete = set(random.Random(random_seed).sample(range(len(items)),n)) 
    updated_items = [x for i,x in enumerate(items) if not i in to_delete]
    deleted_items = [x for i,x in enumerate(items) if i in to_delete]
    return updated_items,deleted_items

# pruning by rows in entity_json_str - not suitable for the synonym as entity case
# input entity catelogue list and pruning ratio 
# output updated entity catelogue list and the deleted entity catelogue list
def pruning_old(entity_json_str,pruning_ratio=0.1):
    list_entity_json_str = entity_json_str.split('\n')
    print('before pruning: %d' % len(list_entity_json_str))
    num_to_prune = math.floor(len(list_entity_json_str)*pruning_ratio)
    list_entity_json_str, deleted_entity_json_str = _delete_rand_items(list_entity_json_str,num_to_prune)
    print('after pruning: %d' % len(list_entity_json_str))
    return '\n'.join(list_entity_json_str), '\n'.join(deleted_entity_json_str)

# pruning by CUI id
# input entity catelogue list and pruning ratio 
# output updated entity catelogue list and the deleted entity catelogue list
def pruning(dict_CUI_entity_row_str,pruning_ratio=0.1):
    list_CUI = list(dict_CUI_entity_row_str.keys())
    print('before pruning: %d' % len(list_CUI))
    num_to_prune = math.floor(len(list_CUI)*pruning_ratio)
    list_CUI, deleted_list_CUI = _delete_rand_items(list_CUI,num_to_prune)
    print('after pruning: %d' % len(list_CUI))
    list_entity_json_str = [dict_CUI_entity_row_str[CUI] for CUI in list_CUI]
    deleted_entity_json_str = [dict_CUI_entity_row_str[deleted_CUI] for deleted_CUI in deleted_list_CUI]
    return '\n'.join(list_entity_json_str), '\n'.join(deleted_entity_json_str)

def get_dict_CUI2SNOMEDCT(UMLS_file_path):
    # get dict of CUI to the list of SNOMEDCT_US IDs
    dict_CUI2SCTID = {}
    with open(UMLS_file_path,encoding='utf-8') as f_content:
        doc = f_content.readlines()

    for line in tqdm(doc):
        data_eles = line.split('|')
        source = data_eles[11]
        if source == 'SNOMEDCT_US':
            CUI = data_eles[0]
            SCTID = data_eles[13]
            if CUI in dict_CUI2SCTID:
                list_SCTID = dict_CUI2SCTID[CUI]
                if not SCTID in list_SCTID:
                    list_SCTID.append(SCTID)
                    dict_CUI2SCTID[CUI] = list_SCTID
            else:            
                list_SCTID = [SCTID]
                dict_CUI2SCTID[CUI] = list_SCTID
    return dict_CUI2SCTID

# transform the entity catelogy json file to iri list
# format of each element in the output list 'http://snomed.info/id/244925001'
# keep *all* the IRIs (or SCTIDs) linked to a CUI
def transform_entity_cat_to_iri_list(entity_json_str,dict_CUI2SCTID, output_format='BLINK'):
    dict_IRI = {}
    list_entity_json_str = entity_json_str.split('\n')
    for an_entity_json_str in list_entity_json_str:
        if output_format == 'Sieve':
            CUI = get_CUI_from_entity_row_str_Sieve(an_entity_json_str)
        else:
            #assert output_format == 'BLINK'
            CUI = get_CUI_from_entity_row_str_BLINK(an_entity_json_str)
        list_SCTID = dict_CUI2SCTID[CUI]
        for SCTID in list_SCTID:
            dict_IRI['http://snomed.info/id/' + SCTID] = 1
    list_IRI = dict_IRI.keys()
    return list_IRI

def get_CUI_from_entity_row_str_BLINK(entity_row_str):
    entity_info = json.loads(entity_row_str)
    CUI = entity_info['idx']
    return CUI

def get_CUI_from_entity_row_str_Sieve(entity_row_str):
    assert "||" in entity_row_str
    CUI = entity_row_str[:entity_row_str.find("||")]
    return CUI

def form_str_ent_row_BLINK(CUI_def,CUI,default_name,list_synonyms,add_synonyms=True,synonym_concat_w_title=False,synonym_as_entity=True):
    dict_entity_row = {}
    dict_entity_row['text'] = CUI_def
    dict_entity_row['idx'] = CUI # CUI2num_id(CUI) # from CUI to its numeric ID
    dict_entity_row['title'] = default_name
    dict_entity_row['entity'] = default_name
    if add_synonyms:
        if synonym_as_entity:
        # if each synonym as a single entity - return the json entities (as a string of *multiple* rows), each using a synonym as the title
            list_json_dump = []
            list_json_dump.append(json.dumps(dict_entity_row))
            for synonym in list_synonyms:
                dict_entity_row['title'] = synonym
                list_json_dump.append(json.dumps(dict_entity_row))
            return '\n'.join(list_json_dump)
        # otherwise, synonym as a part of entity - return the json entity (as a string of a *single* row) with synonym concatenated or as an attribute.
        elif synonym_concat_w_title:
            synonyms_str = ' '.join(list_synonyms)
            dict_entity_row['title'] = default_name + ((' ' + synonyms_str) if add_synonyms else '')
            dict_entity_row['title'] = dict_entity_row['title'].strip()
        else:
            # synonyms as an attribute in the json output            
            synonyms_str = '|'.join(list_synonyms)
            dict_entity_row['synonyms'] = synonyms_str      
    return json.dumps(dict_entity_row)

def form_str_ent_row_Sieve(CUI,default_name,list_synonyms,add_synonyms=True):
    if add_synonyms:
        synonyms_str = '|'.join(list_synonyms)
    entity_row_str = CUI + '||' + default_name + (('|' + synonyms_str) if add_synonyms else '')
    return entity_row_str

#clean synonyms - remove starting square brackets and trailing round brackets in the snomed-ct entity synonyms
def clean_synonym(str_name):
    # make it in lower cases 
    str_name = str_name.lower() 
    # remove '[ambiguous]'
    str_name = str_name.replace('[ambiguous]','')
    str_name = str_name.strip()
    # remove starting [X], [D], etc.
    if str_name.find('[') == 0 and str_name.find(']') == 2:
        str_name = str_name[3:]
    # remove trailing ()s.
    if str_name[-1] == ')' and '(' in str_name:
        str_name = str_name[:str_name.rindex('(')].strip()
    # remove trailing retired signs.
    if ('-retired' in str_name):
        str_name = str_name[:str_name.find('-retired')]
    #if ('-RETIRED' in str_name):
    #    str_name = str_name[:str_name.find('-RETIRED')]        
    # remove unspecified or nos
    str_name = str_name.replace('unspecified', '')
    str_name = str_name.replace('nos', '')
    # strip trailinng spaces and remove the trailing ',' (which can come with ', nos')
    str_name = str_name.strip()
    if str_name[-1] == ',':
        str_name = str_name[:-1]
    return str_name

parser = argparse.ArgumentParser(description="get the list file of UMLS entities")
parser.add_argument('-d','--dataset', type=str,
                    help="dataset name", default='medmentions') #'share_clef2013'
parser.add_argument('-o','--output_data_folder_path', type=str,
                    help="output data folder path", default='../ontologies')
parser.add_argument('-f','--output_format', type=str,
                    help="output data format, BLINK or Sieve", default='BLINK')                         
parser.add_argument("--add_synonyms",action="store_true",help="Whether to add synonyms to the entity list")
parser.add_argument("--clean_synonyms",action="store_true",help="Whether to clean the raw synonyms")
parser.add_argument("--synonym_concat_w_title",action="store_true",help="Whether to concat synonyms with title")
parser.add_argument("--synonym_as_entity",action="store_true",help="Whether to treat each synonym as an entity")
#parser.add_argument("--synonym_as_attr",action="store_true",help="Whether to add the synonyms as an attribute of the entity")
parser.add_argument('--onto_ver', type=str,
                    help="UMLS version", default='2012AB')
parser.add_argument("--prune_entity_catalogue",action="store_true",help="Whether to prune the entities")
parser.add_argument("--pruning_ratio",type=float,help="percentage of entities to be pruned", default=0.1)
args = parser.parse_args()

# dataset = 'medmentions' #'share_clef2013'
# output_data_folder_path = '../ontologies'
# output_format = 'Sieve' # 'BLINK' or 'Sieve'
# add_synonyms = True # whether to use synonyms
# clean_synonyms = False # whether to clean the synonyms

# synonym_concat_w_title = False # whether to concat synonyms with title
# synonym_as_entity = False # whether to treat each synonym as a single entity

dataset = args.dataset
output_data_folder_path = args.output_data_folder_path
output_format = args.output_format
add_synonyms = args.add_synonyms
clean_synonyms = args.clean_synonyms
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
        if clean_synonyms:
            output_syn_mark = '_clean'
    if synonym_as_attr:
        output_syn_mark = '_attr'         

if dataset == 'share_clef2013':
    onto_ver = args.onto_ver # '2012AB' # used in Ji et al, 2020
    #onto_ver = '2011AA' # according to the annotation guideline
    UMLS_file_path = '../ontologies/UMLS%s/MRCONSO.RRF' % onto_ver # two split file combined via linux command 'cat MRCONSO.RRF.?? > MRCONSO.RRF'
    #UMLS_file_path1 = '../ontologies/UMLS%s/MRCONSO.RRF.aa' % onto_ver
    #UMLS_file_path2 = '../ontologies/UMLS%s/MRCONSO.RRF.ab' % onto_ver
    #about MRCONSO, see https://www.ncbi.nlm.nih.gov/books/NBK9685/table/ch03.T.concept_names_and_sources_file_mr/
    STY_file_path = '../ontologies/UMLS%s/MRSTY.RRF' % onto_ver
    #note: for STY file, use the one in mmsys/config/2011AA/
    DEF_file_path = '../ontologies/UMLS%s/MRDEF.RRF' % onto_ver

    prune_entity_catalogue = args.prune_entity_catalogue # whether to prune the ontology - randomly (false for share_clef as there is NILs annotated, no need to prune ontology to create NILs)
    
    filter_by_STY = True
    STYs_filter_list =   ['Congenital Abnormality',
                        'Acquired Abnormality',
                        'Injury or Poisoning',
                        'Pathologic Function',
                        'Disease or Syndrome',
                        'Mental or Behavioral Dysfunction',
                        'Cell or Molecular Dysfunction',
                        'Experimental Model of Disease',
                        'Anatomical Abnormality',
                        'Neoplastic Process',
                        'Sign or Symptom']    
    filter_by_lang = True
    filter_by_sources = True                            
    sources_list = ['SNOMEDCT']       
elif dataset == 'medmentions':
    onto_ver = args.onto_ver
    # 2014AB, 2015AB (for NIL generation with full data setting), 
    # 2017AA (for full data setting) or 2017AA/active (for st21pv)
    UMLS_file_path = '../ontologies/UMLS%s/MRCONSO.RRF' % onto_ver
    STY_file_path = '../ontologies/UMLS%s/MRSTY.RRF' % onto_ver
    DEF_file_path = '../ontologies/UMLS%s/MRDEF.RRF' % onto_ver

    prune_entity_catalogue = args.prune_entity_catalogue #True # whether to prune the ontology - randomly
    pruning_ratio = args.pruning_ratio #0.2 # percentage of concepts or CUIs to be pruned

    filter_by_STY = True
    STYs_filter_list = ['T047'] # only Disease or Syndrome (T047)
    #STYs_filter_list = ['T109','T114','T116'] 
            # Organic Chemical T109
            #Nucleic Acid, Nucleoside, or Nucleotide T114
            #Amino Acid, Peptide, or Protein T116
    #STYs_filter_list = ['T038','T039'] # for testing
    #STYs_filter_list = ['T038','T039','T040','T041','T042','T043','T044','T045','T046','T047','T048','T191','T049','T050','T033','T034','T184'] # all under Biologic Function (T038) and Finding (T033)
    filter_by_lang = True
    filter_by_sources = True # setting to False for the original setting in medmentions, but we set it True to focus on a particular ontology
    sources_list = ['SNOMEDCT_US'] # focus on the SNOMEDCT_US concepts 
    # sources_list = '''
    # CPT Current Procedural Terminology 
    # FMA Foundational Model of Anatomy 
    # GO Gene Ontology 
    # HGNC HUGO Gene Nomenclature Committee 
    # HPO Human Phenotype Ontology 
    # ICD10 International Classification of Diseases, Tenth Revision 
    # ICD10CM ICD10 Clinical Modification 
    # ICD9CM ICD9 Clinical Modification 
    # MDR Medical Dictionary for Regulatory Activities 
    # MSH Medical Subject Headings 
    # MTH UMLS Metathesaurus Names 
    # NCBI National Center for Biotechnology Information Taxonomy 
    # NCI National Cancer Institute Thesaurus 
    # NDDF First DataBank MedKnowledge 
    # NDFRT National Drug File – Reference Terminology 
    # OMIM Online Mendelian Inheritance in Man 
    # RXNORM NLM’s Nomenclature for Clinical Drugs for Humans 
    # SNOMEDCT US US edn. of the Systematized Nomenclature of Medicine-Clinical Terms
    # '''

    # sources_list = [source.split(' ')[0] for source in sources_list.split('\n')]
    # print(' '.join(sources_list))
dict_CUI_by_STY = {}
dict_CUI_synonyms = {} # dict CUI to dict synonyms
dict_CUI_DEF = {}
dict_CUI_default_name = {}
dict_CUI_default_name_Eng = {}

# get dict of CUI filtered by STY
if filter_by_STY:
    with open(STY_file_path,encoding='utf-8') as f_content:
        doc_STY = f_content.readlines()
    for line in tqdm(doc_STY):
        for STY in STYs_filter_list:
            if '|%s|' % STY in line:
                CUI = line[:line.find('|')]
                dict_CUI_by_STY[CUI] = 1
                break

# get dict of CUI to DEF
with open(DEF_file_path,encoding='utf-8') as f_content:
    doc_DEF = f_content.readlines()
for line in tqdm(doc_DEF):
    def_eles = line.split('|')
    CUI = def_eles[0]
    DEF = def_eles[5]
    #print(CUI,DEF)
    dict_CUI_DEF[CUI] = DEF

# get dict of CUI to default names (two dicts: one for Eng only and one for all languages)
for UMLS_file_path_ in [UMLS_file_path]: #[UMLS_file_path1,UMLS_file_path2]:
    with open(UMLS_file_path_,encoding='utf-8') as f_content:
        doc = f_content.readlines()

    for line in tqdm(doc):
        data_eles = line.split('|')
        # if len(data_eles) > 11:
        #     source = data_eles[11]
        # else:
        #     source = ''    

        CUI = data_eles[0]
        lang = data_eles[1]
        if (not CUI in dict_CUI_default_name_Eng) and (lang == 'ENG'):
            default_name_Eng_ = data_eles[14]
            dict_CUI_default_name_Eng[CUI] = default_name_Eng_
        if not CUI in dict_CUI_default_name:
            default_name_ = data_eles[14]
            dict_CUI_default_name[CUI] = default_name_

entity_json_str = ''
# entity_str_bioel = ''
n_all_sel_UMLS_w_def = 0
n_all_sel_UMLS = 0
prev_CUI = None
dict_CUI_entity_row_str = {} # dict to store CUI to entity_row_str
for UMLS_file_path_ in [UMLS_file_path]: #[UMLS_file_path1,UMLS_file_path2]:
    with open(UMLS_file_path_,encoding='utf-8') as f_content:
        doc = f_content.readlines()

    for line in tqdm(doc):
        data_eles = line.split('|')
        if len(data_eles) > 11:
            source = data_eles[11]
        else:
            source = ''    

        CUI = data_eles[0]
        lang = data_eles[1]
        # filters
        if filter_by_STY:
            if not CUI in dict_CUI_by_STY:
                continue
        if filter_by_sources:
            if not source in sources_list: 
                continue
        if filter_by_lang:
            if lang != 'ENG':
                continue         
        # gather synonyms (before lang filtering)
        #using the the first one in English as the default name
        #filter_by_occurrences = False 
        ##only record the first one in the MRRCONSO for the same concept, thus filter the second and later appearences        
        if CUI in dict_CUI_synonyms:            
            # add synonyms to the CUI
            dict_synonyms = dict_CUI_synonyms[CUI]
            synonym = data_eles[14]
            if clean_synonyms:
                synonym = clean_synonym(synonym)
            dict_synonyms[synonym] = 1
            dict_CUI_synonyms[CUI] = dict_synonyms
            #filter_by_occurrences = True
            continue
        else:
            #first appearence
            dict_CUI_synonyms[CUI] = {}

        #save the previous entity
        #if len(dict_CUI_synonyms) >= 1:    
        if prev_CUI:            
            dict_synonyms = dict_CUI_synonyms[prev_CUI]
            list_synonyms = list(dict_synonyms.keys())
            if default_name.lower() in list_synonyms:
                # remove canonical name (lowercased) if it is also in the synonyms
                list_synonyms.remove(default_name.lower())
                #print(default_name, 'removed from', prev_CUI)
            if output_format == 'BLINK':
                entity_row_str = form_str_ent_row_BLINK(CUI_def,prev_CUI,default_name,list_synonyms,add_synonyms=add_synonyms,synonym_concat_w_title=synonym_concat_w_title,
                synonym_as_entity=synonym_as_entity)

            elif output_format == 'Sieve':
                entity_row_str = form_str_ent_row_Sieve(prev_CUI,default_name,list_synonyms,add_synonyms=add_synonyms)
            #add to the dict of CUI to entity_row_str 
            dict_CUI_entity_row_str[prev_CUI] = entity_row_str

            if entity_json_str == '':
                entity_json_str = entity_row_str
            else:    
                entity_json_str = entity_json_str + '\n' + entity_row_str

        n_all_sel_UMLS += 1
        #title = data_eles[14]      
        #get definition and the statistics *of the next CUI*
        if CUI in dict_CUI_DEF:
            n_all_sel_UMLS_w_def += 1
            CUI_def = dict_CUI_DEF[CUI]
        else:
            CUI_def = ''    
        if CUI in dict_CUI_default_name_Eng:
            default_name = dict_CUI_default_name_Eng[CUI]
        else:
            default_name = dict_CUI_default_name[CUI]    
            print(CUI,default_name,'non-Eng')              
        #print(CUI_def,CUI,title)
        prev_CUI = CUI
        # # construct str of entity lists for BLINK
        # dict_entity_row = {}
        # dict_entity_row['text'] = CUI_def
        # dict_entity_row['idx'] = CUI # CUI2num_id(CUI) # from CUI to its numeric ID
        # dict_entity_row['title'] = default_name
        # #dict_entity_row['title'] = title
        # dict_entity_row['entity'] = default_name
        # if entity_json_str == '':
        #     entity_json_str = json.dumps(dict_entity_row)
        # else:    
        #     entity_json_str = entity_json_str + '\n' + json.dumps(dict_entity_row)

        # # construct str of entity lists for Biomedical-Entity-Linking
        # #TODO: add synonyms
        # if entity_str_bioel == '':
        #     entity_str_bioel = CUI + '\t' + default_name
        # else:
        #     entity_str_bioel = entity_str_bioel + '\n' + CUI + '\t' + default_name

    #save the last entity
    dict_synonyms = dict_CUI_synonyms[prev_CUI]
    list_synonyms = list(dict_synonyms.keys())
    if default_name.lower() in list_synonyms:
        # remove canonical name (lowercased) if it is also in the synonyms
        list_synonyms.remove(default_name.lower())
        #print(default_name, 'removed from', prev_CUI)
    if output_format == 'BLINK':
        entity_row_str = form_str_ent_row_BLINK(CUI_def,prev_CUI,default_name,list_synonyms,add_synonyms=add_synonyms,synonym_concat_w_title=synonym_concat_w_title,
        synonym_as_entity=synonym_as_entity)
    elif output_format == 'Sieve':
        entity_row_str = form_str_ent_row_Sieve(prev_CUI,default_name,list_synonyms,add_synonyms=add_synonyms)
    dict_CUI_entity_row_str[prev_CUI] = entity_row_str
    entity_json_str = entity_json_str + '\n' + entity_row_str

print(len(dict_CUI_synonyms))  # 88150 for share_clef2013
print('percentage of sel UMLS with def:',float(n_all_sel_UMLS_w_def)/n_all_sel_UMLS,n_all_sel_UMLS_w_def,n_all_sel_UMLS)
#UMLS2011AA (share/clef): percentage of sel UMLS with def: 0.072290401460273 6297 87107
#UMLS2012AB (share/clef): percentage of sel UMLS with def: 0.07888825865002837 6954 88150
#UMLS2017AA (medmentions) T047: percentage of sel UMLS with def: 0.08179355477663097 8424 102991
#UMLS2017AA Eng (mm) T047:percentage of sel UMLS with def: 0.08180493491354186 8421 102940
#UMLS2017AA active (medmentions) T047: percentage of sel UMLS with def: 0.08055600550741071 7957 98776
#UMLS2017AA active Eng (mm) T047: percentage of sel UMLS with def: 0.08056723221068625 7954 98725
#UMLS2015AB Eng (mm) T047: percentage of sel UMLS with def: 0.066256288723979 6598 99583
#UMLS2015AB Eng (mm) SNOMEDCT_US: percentage of sel UMLS with def: 0.09347102553734175 33055 353639
#UMLS2017AA Eng (mm) SNOMEDCT_US: percentage of sel UMLS with def: 0.09996912930994446 36593 366043
#UMLS2017AA active Eng (mm) T033> T038> SNOMEDCT_US: percentage of sel UMLS with def: 0.1117222944529808 12288 109987
#UMLS2015AB Eng (mm) T033> T038> SNOMEDCT_US:percentage of sel UMLS with def: 0.09952085763590965 10323 103727
#UMLS2015AB Eng (mm) SNOMEDCT_US T047: percentage of sel UMLS with def: 0.11897472024277238 4391 36907
#UMLS2017AA Eng (mm) SNOMEDCT_US T047: percentage of sel UMLS with def: 0.1512562302919337 5948 39324
#UMLS2014AB Eng (mm) SNOMEDCT_US T047: percentage of sel UMLS with def: 0.10565568676196395 3740 35398

# pruning the entity catelogue
if prune_entity_catalogue:
    #for BLINK
    entity_json_str, deleted_entity_json_str = pruning(dict_CUI_entity_row_str,pruning_ratio=pruning_ratio)
    #output deleted entities
    output_to_file('%s/UMLS%s-deleted-entities%s.jsonl' % (output_data_folder_path, onto_ver.replace('/','_'),str(pruning_ratio)),deleted_entity_json_str)

    # #for Biomedical-Entity-Linking
    # entity_str_bioel, deleted_entity_str_bioel = pruning(entity_str_bioel,pruning_ratio=pruning_ratio)
    # #output deleted entities
    # #output_to_file('%s/UMLS%s-deleted-entities%s.jsonl' % (output_data_folder_path, onto_ver.replace('/','_'),str(pruning_ratio)),deleted_entity_json_str)

    dict_CUI2SCTID = get_dict_CUI2SNOMEDCT(UMLS_file_path)
    print('dict_CUI2SCTID:',len(dict_CUI2SCTID))
    list_iris = transform_entity_cat_to_iri_list(entity_json_str,dict_CUI2SCTID, output_format=output_format)
    print('list_iris:',len(list_iris))
    output_to_file('%s/SCTID_to_keep%s.txt' % (output_data_folder_path, str(pruning_ratio)),'\n'.join(list_iris))
    #for prune ratio as 0.1
        #dict_CUI2SCTID: 366043
        #list_iris: 45614
    #for prune ratio as 0.2
        #dict_CUI2SCTID: 366043
        #list_iris: 40803

# save the entity catalogue (and the one with a NIL entity)
# for BLINK/Sieve
output_to_file('%s/UMLS%s%s%s%s%s.jsonl' % (output_data_folder_path, onto_ver.replace('/','_'), '_pruned' + str(pruning_ratio) if prune_entity_catalogue else '', '_syn' if add_synonyms else '', output_syn_mark, ('_' + output_format) if output_format != 'BLINK' else ''),entity_json_str)
# # for Biomedical-Entity-Linking
# output_to_file('%s/UMLS%s%s.txt' % (output_data_folder_path, onto_ver.replace('/','_'), '_pruned' + str(pruning_ratio) if prune_entity_catalogue else ''),entity_str_bioel)

# we add a general out-of-KB / NIL entity to the list - so that all out-of-KB entities share a common ID. - only for BLINK (i.e. not for Sieve)
if output_format == 'BLINK':
    entity_row_str = form_str_ent_row_BLINK(CUI_def='',CUI='CUI-less',default_name='NIL',list_synonyms=[],add_synonyms=add_synonyms,synonym_concat_w_title=synonym_concat_w_title,synonym_as_entity=synonym_as_entity)
    entity_json_str = entity_json_str + '\n' + entity_row_str
#elif output_format == 'Sieve':
#    entity_row_str = form_str_ent_row_Sieve(CUI='CUI-less',default_name='NIL',list_synonyms=[])
    output_to_file('%s/UMLS%s%s_with_NIL%s%s%s.jsonl' % (output_data_folder_path, onto_ver.replace('/','_'), '_pruned' + str(pruning_ratio) if prune_entity_catalogue else '', '_syn' if add_synonyms else '', output_syn_mark, ('_' + output_format) if output_format != 'BLINK' else ''),entity_json_str)
