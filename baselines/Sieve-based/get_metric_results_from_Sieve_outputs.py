# get metric results from Sieve outputs
#overall P, R, F1
#in-KB P, R, F1
#out-of-KB P, R, F1

import os
from tqdm import tqdm 
import argparse

parser = argparse.ArgumentParser(description="format the medmention dataset with different ontology settings")
parser.add_argument('--data_folder_name', type=str,
                    help="data folder name", default='./disorder-normalizer/clef-data/share_clef_2013_preprocessed_sieve_ori')
parser.add_argument('--data_split_name', type=str,
                    help="data split name", default='test')
parser.add_argument("--debug",action="store_true",help="Whether to use debug mode: looking at first 5 documents only")
args = parser.parse_args()

debug = False
num_files_debugging = 5 if debug else None

# loop over test .concept file
data_folder_name = args.data_folder_name
data_split_name = args.data_split_name
test_data_folder_path = os.path.join(data_folder_name,data_split_name)
list_ann_fns = [filename for filename in os.listdir(test_data_folder_path) if filename.endswith(".concept")]

tp, tp_NIL, tp_in_KB = 0, 0, 0
num_pred, num_pred_NIL, num_pred_in_KB = 0, 0, 0
num_true, num_true_NIL, num_true_in_KB = 0, 0, 0
for ind_ann_doc_fn, filename in enumerate(tqdm(list_ann_fns[:num_files_debugging])):
    with open(os.path.join(test_data_folder_path,filename),encoding='utf-8') as f_content:
        label_doc = f_content.read()
        #print(filename,label_doc)
    #get output prediction file 
    test_data_pred_fn = 'output\\' + filename
    with open(os.path.join(data_folder_name,test_data_pred_fn),encoding='utf-8') as f_content:
        pred_doc = f_content.read()
        #print('---predictions---')
        #print(pred_doc)

    # get num_pred and num_true (for all, in-KB, and NIL)
    list_label_mentions = label_doc.split('\n')
    num_label_mentions = len(list_label_mentions)
    num_true += num_label_mentions

    list_label_mentions_NIL = [label_mention for label_mention in list_label_mentions if "CUI-less" in label_mention]
    num_label_mentions_NIL = len(list_label_mentions_NIL)
    num_label_mentions_in_KB = num_label_mentions - num_label_mentions_NIL
    num_true_NIL += num_label_mentions_NIL
    num_true_in_KB += num_label_mentions_in_KB

    list_pred_mentions = list(dict.fromkeys(pred_doc.split('\n')))
    list_pred_mentions.remove("")
    num_pred_mentions = len(list_pred_mentions)
    num_pred += num_pred_mentions
    #if num_label_mentions != num_pred_mentions:        
    #    print(filename,num_label_mentions,num_pred_mentions)

    list_pred_mentions_NIL = [pred_mention for pred_mention in list_pred_mentions if "CUI-less" in pred_mention]
    num_pred_mentions_NIL = len(list_pred_mentions_NIL)
    num_pred_mentions_in_KB = num_pred_mentions - num_pred_mentions_NIL
    num_pred_NIL += num_pred_mentions_NIL
    num_pred_in_KB += num_pred_mentions_in_KB

    #get tp    
    dict_label_men_cui = {}
    for label_mention in list_label_mentions:
        eles = label_mention.split('||')
        span = eles[1]
        label_cui = eles[-1]
        assert not '|' in label_cui
        #assert not span in dict_label_men_cui
        if not span in dict_label_men_cui:
          dict_label_men_cui[span] = label_cui
        else:
            # print the label entity that changed if there was a prev label for the mention
            if label_cui != dict_label_men_cui[span]:
                print(filename, span, dict_label_men_cui[span])
        
        ##only count the last entity if a mention is predicted more than once
        #dict_label_men_cui[span] = label_cui        

    dict_pred_men_cui = {}
    for pred_mention in list_pred_mentions:
        eles = pred_mention.split('||')
        span = eles[1]
        pred_cui = eles[-1]
        assert not '|' in pred_cui
        #assert not span in dict_pred_men_cui
        if not span in dict_pred_men_cui:
            dict_pred_men_cui[span] = pred_cui
        else:
            # print the pred entity that changed if there was a prev pred for the mention
            if pred_cui != dict_pred_men_cui[span]:
                print(filename, span, dict_pred_men_cui[span])
        
        ##only count the last entity if a mention is predicted more than once
        #dict_pred_men_cui[span] = pred_cui        

    # num_pred_mentions = len(dict_pred_men_cui)
    # num_pred += num_pred_mentions
    # dict_pred_men_NIL = {k: v for k, v in dict_pred_men_cui.items() if v == 'CUI-less'} 
    # num_pred_mentions_NIL = len(dict_pred_men_NIL)
    # num_pred_mentions_in_KB = num_pred_mentions - num_pred_mentions_NIL
    # num_pred_NIL += num_pred_mentions_NIL
    # num_pred_in_KB += num_pred_mentions_in_KB

    for span in dict_pred_men_cui.keys():
        if span in dict_label_men_cui:
            if dict_label_men_cui[span] == dict_pred_men_cui[span]:
                tp+=1
                if dict_label_men_cui[span] == "CUI-less":
                    tp_NIL+=1
                else:
                    tp_in_KB+=1    
        else:
            print(filename, span, dict_pred_men_cui[span])
    

def display_P_R_F1(tp, num_pred, num_true):
    prec=float(tp)/num_pred
    rec=float(tp)/num_true
    f1 = 2*prec*rec/(prec+rec) if prec+rec >0 else -1
    print('tp:',tp, 'num_true:',num_true, 'num_pred:',num_pred,'\n','prec:',prec,'rec:',rec,'f1:',f1)

print('all entities:')
display_P_R_F1(tp, num_true, num_true) # for all entities, num_pred is num_true, and we only report accuracy which either P or R.
print('in-KB entities:')
display_P_R_F1(tp_in_KB, num_pred_in_KB, num_true_in_KB)
print('NIL entities:')
display_P_R_F1(tp_NIL, num_pred_NIL, num_true_NIL)

'''
For original test data
all entities:
tp: 4815 num_true: 5351 num_pred: 5351 
 acc: 0.8998318071388526
in-KB entities:
tp: 3220 num_true: 3628 num_pred: 3457 
 prec: 0.9314434480763668 rec: 0.8875413450937155 f1: 0.9089625970359915
NIL entities:
tp: 1595 num_true: 1723 num_pred: 1883 
 prec: 0.847052575677111 rec: 0.9257109692396982 f1: 0.884636716583472

For data without same NIL mention in test set as those in train
all entities:
tp: 4050 num_true: 4537 num_pred: 4537
 acc: 0.8926603482477407
in-KB entities:
tp: 3220 num_true: 3628 num_pred: 3411
 prec: 0.9440046907065377 rec: 0.8875413450937155 f1: 0.9149026850404886
NIL entities:
tp: 830 num_true: 909 num_pred: 1116
 prec: 0.7437275985663082 rec: 0.9130913091309131 f1: 0.819753086419753
 '''