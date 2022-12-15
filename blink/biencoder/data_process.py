# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import logging
import torch
from tqdm import tqdm, trange
from torch.utils.data import DataLoader, TensorDataset

#from pytorch_transformers.tokenization_bert import BertTokenizer

from blink.biencoder.zeshel_utils import world_to_id
from blink.common.params import ENT_START_TAG, ENT_END_TAG, ENT_TITLE_TAG, ENT_SYN_TAG, ENT_NIL_TAG


def select_field(data, key1, key2=None):
    if key2 is None:
        return [example[key1] for example in data]
    else:
        return [example[key1][key2] for example in data]


def get_context_representation(
    sample,
    tokenizer,
    max_seq_length,
    mention_key="mention",
    context_key="context",
    ent_start_token=ENT_START_TAG,
    ent_end_token=ENT_END_TAG,
    #max_mention_length=20, # only for extra feature calculation. Deprecated, just using max_seq_length
):
    mention_tokens = []
    if sample[mention_key] and len(sample[mention_key]) > 0:
        mention_tokens = tokenizer.tokenize(sample[mention_key])
        mention_tokens = [ent_start_token] + mention_tokens + [ent_end_token]

    context_left = sample[context_key + "_left"]
    context_right = sample[context_key + "_right"]
    context_left = tokenizer.tokenize(context_left)
    context_right = tokenizer.tokenize(context_right)

    left_quota = (max_seq_length - len(mention_tokens)) // 2 - 1
    right_quota = max_seq_length - len(mention_tokens) - left_quota - 2
    left_add = len(context_left)
    right_add = len(context_right)
    if left_add <= left_quota:
        if right_add > right_quota:
            right_quota += left_quota - left_add
    else:
        if right_add <= right_quota:
            left_quota += right_quota - right_add

    context_tokens = (
        context_left[-left_quota:] + mention_tokens + context_right[:right_quota]
    )

    context_tokens = ["[CLS]"] + context_tokens + ["[SEP]"]
    input_ids = tokenizer.convert_tokens_to_ids(context_tokens)
    padding = [0] * (max_seq_length - len(input_ids))
    input_ids += padding
    assert len(input_ids) == max_seq_length

    mention_ids = tokenizer.convert_tokens_to_ids(mention_tokens)
    if len(mention_ids) < max_seq_length:
        padding = [0] * (max_seq_length - len(mention_ids))
        mention_ids += padding
    else:
        print('mention_id beyond length of %d' % max_seq_length)    
    #print('mention_ids:',mention_ids)
    return {
        "mention_tokens": mention_tokens, # add mention tokens (with ent_start_token and ent_end_token)
        "mention_ids": mention_ids, # add mention token ids (with ent_start_token and ent_end_token)
        "tokens": context_tokens,
        "ids": input_ids,
    }

# preprocess the entity candidates into tokens and input_ids using the tokenizer of the BERT models used in bi-encoder
# with synonyms as an option - the second argument
#   when synonyms is None, not using them, otherwise, using them with the special token of ENT_SYN_TAG
def get_candidate_representation(
    candidate_desc, 
    synonyms,
    tokenizer, 
    max_seq_length, 
    candidate_title=None,
    title_tag=ENT_TITLE_TAG,
    syn_tag=ENT_SYN_TAG,
    use_NIL_tag=False,
    NIL_tag=ENT_NIL_TAG,
    use_NIL_desc=False,
    use_NIL_desc_tag=False,
    use_synonyms=True,
):
    cls_token = tokenizer.cls_token
    sep_token = tokenizer.sep_token
    cand_tokens = tokenizer.tokenize(candidate_desc)
    #print('candidate_title:',candidate_title)
    #print('use_NIL_tag in data_process.get_candidate_representation:',use_NIL_tag)
    #print('use_NIL_desc in data_process.get_candidate_representation:',use_NIL_desc)
    if candidate_title is not None:
        if candidate_title == 'NIL':
            if use_NIL_tag:
                title_tokens = [NIL_tag]
            else:
                title_tokens = tokenizer.tokenize(candidate_title)      
            if use_NIL_desc:
                if use_NIL_desc_tag: #TODO and run
                    cand_tokens = tokenizer.tokenize("It is a") + [NIL_tag] + tokenizer.tokenize("option.") 
                else:
                    cand_tokens = tokenizer.tokenize("It is a NIL option.")
        else:
            title_tokens = tokenizer.tokenize(candidate_title)
        
        if use_synonyms and not synonyms is None:
            #print('synonyms found')
            all_syns_tokens = []
            list_synonyms = synonyms.split('|')
            for synonym in list_synonyms:
                syn_tokens = tokenizer.tokenize(synonym)
                all_syns_tokens = all_syns_tokens + syn_tokens + [syn_tag]
            cand_tokens = title_tokens + [title_tag] + all_syns_tokens + cand_tokens # title + synonyms + description/definition
        else:
            cand_tokens = title_tokens + [title_tag] + cand_tokens # title + description/definition
        #print('cand_tokens:',cand_tokens)
        '''
        e.g. for {"text": "A disorder characterized by a defect in mitral valve function or structure.", "idx": "C0026265", "title": "Diseases of mitral valve", "entity": "Diseases of mitral valve"} 
        Label tokens : [CLS] mit ##ral valve ins ##uf ##fi ##ciency [unused2] blood flows backward because the mit ##ral valve closes improper ##ly [SEP]
        for {"text": "", "idx": "CUI-less", "title": "NIL", "entity": "NIL"}
        Label tokens : [CLS] ni ##l [unused2] [SEP] 
        - so NIL entity is treated here too.

        another example with synonyms
        cand_tokens: ['ta', '##chy', '##p', '##nea', '[unused2]', 'ta', '##chy', '##p', '##no', '##ea', '[unused3]', 'rapid', 'breathing', '[unused3]', 'ta', '##chy', '##p', '##ne', '##ic', '[unused3]', 'ta', '##chy', '##p', '##no', '##ei', '##c', '[unused3]', '[', 'd', ']', 'ta', '##chy', '##p', '##nea', '[unused3]', '[', 'd', ']', 'ta', '##chy', '##p', '##no', '##ea', '[unused3]', 'rapid', 'res', '##piration', '[unused3]', '[', 'd', ']', 'ta', '##chy', '##p', '##nea', '(', 'context', '-', 'dependent', 'category', ')', '[unused3]', 'ta', '##chy', '##p', '##nea', '(', 'finding', ')', '[unused3]', '[', 'd', ']', 'ta', '##chy', '##p', '##nea', '(', 'situation', ')', '[unused3]', '[', 'd', ']', 'ta', '##chy', '##p', '##no', '##ea', '(', 'situation', ')', '[unused3]', 'z', '##vy', '##sen', '##a', 'ry', '##ch', '##los', '##t', 'd', '##ych', '##ani', '(', 'dec', '##ho', '##va', 'fr', '##ek', '##ven', '##ce', ')', '.']
        '''
    cand_tokens = cand_tokens[: max_seq_length - 2]
    cand_tokens = [cls_token] + cand_tokens + [sep_token]

    input_ids = tokenizer.convert_tokens_to_ids(cand_tokens)
    padding = [0] * (max_seq_length - len(input_ids))
    input_ids += padding
    assert len(input_ids) == max_seq_length

    return {
        "tokens": cand_tokens,
        "ids": input_ids,
    }

# remove the synonym rows from data (for the synonym as entities setting)
# ignore the cases when synonyms are used as the entitiy; this appears when using the _syn_full data setting and when the mention and contexts repeats (the first appearance is the canonical name of the entity). 
def remove_syn_rows_from_data(samples,mention_key="mention",context_key="context",):
    dict_mention_in_context = {}
    sample_w_o_syn_rows = []
    for sample in samples:
        mention = sample[mention_key]
        context_left = sample[context_key + "_left"]
        context_right = sample[context_key + "_right"]
        triple_men_in_contexts = (mention,context_left,context_right)
        if not triple_men_in_contexts in dict_mention_in_context:
            dict_mention_in_context[triple_men_in_contexts] = 1
            sample_w_o_syn_rows.append(sample)                
    return sample_w_o_syn_rows
    
# generate TensorData for batch iteration from the raw data
def process_mention_data(
    samples,
    tokenizer,
    max_context_length,
    max_cand_length,
    silent,
    mention_key="mention",
    synonym_key="synonyms",
    context_key="context",
    label_key="label",
    title_key='label_title',
    ent_start_token=ENT_START_TAG,
    ent_end_token=ENT_END_TAG,
    title_token=ENT_TITLE_TAG,
    debug=False,
    logger=None,
    NIL_ent_id=88150, # added NIL_ent_id here
    use_NIL_tag=False,
    use_NIL_desc=False,
    use_NIL_desc_tag=False,
    use_synonyms=True,
    remove_syn_rows=False,
):
    processed_samples = []
    # remove the synonym rows from data for inference, but not for training (if there are any, for the synonym as entities setting)
    if remove_syn_rows:
      samples = remove_syn_rows_from_data(samples)
    print('num of samples:',len(samples))
    if debug:
        samples = samples[:200]

    if silent:
        iter_ = samples
    else:
        iter_ = tqdm(samples)

    use_world = True

    for idx, sample in enumerate(iter_):
        context_tokens = get_context_representation(
            sample,
            tokenizer,
            max_context_length,
            mention_key,
            context_key,
            ent_start_token,
            ent_end_token,
        )

        label = sample[label_key] # label/entity description
        title = sample.get(title_key, None) # title or canonical name
        synonyms = sample.get(synonym_key, None)
        #print('use_NIL_tag in process_mention_data:',use_NIL_tag)
        #print('use_NIL_desc in process_mention_data:',use_NIL_desc)
        #print('use_NIL_desc_tag in process_mention_data:',use_NIL_desc_tag)
        label_tokens = get_candidate_representation(
            label, synonyms, tokenizer, max_cand_length, title,
            use_NIL_tag=use_NIL_tag,
            use_NIL_desc=use_NIL_desc,
            use_NIL_desc_tag=use_NIL_desc_tag,
            use_synonyms=use_synonyms,
        )

        # # process UMLS CUI into integers if needed 'C0003507'
        # if type(sample["label_id"]) is int:
        #     label_idx = int(sample["label_id"])
        # else:
        #     label_idx = int(sample["label_id"][1:])
        label_idx = int(sample["label_id"])
        is_label_NIL = label_idx == NIL_ent_id

        record = {
            "context": context_tokens,
            "label": label_tokens,
            "label_idx": [label_idx],
            "is_label_NIL": [is_label_NIL], # is_label_NIL added
        }

        if "world" in sample:
            src = sample["world"]
            src = world_to_id[src]
            record["src"] = [src]
            use_world = True
        else:
            use_world = False

        processed_samples.append(record)

    #if debug and logger:
    if logger:
        logger.info("====Processed samples (first 10): ====")
        for sample in processed_samples[:10]:
            logger.info("Mention tokens : " + " ".join(sample["context"]["mention_tokens"]))
            logger.info(
                "Mention ids : " + " ".join([str(v) for v in sample["context"]["mention_ids"]])
            )
            logger.info("Context tokens : " + " ".join(sample["context"]["tokens"]))
            logger.info(
                "Context ids : " + " ".join([str(v) for v in sample["context"]["ids"]])
            )
            logger.info("Label tokens : " + " ".join(sample["label"]["tokens"]))
            logger.info(
                "Label ids : " + " ".join([str(v) for v in sample["label"]["ids"]])
            )
            if "src" in sample:
                logger.info("Src : %d" % sample["src"][0])
            logger.info("Label_id : %d is %s" % (sample["label_idx"][0], 'NIL' if sample["is_label_NIL"][0] else 'in-KB'))

    mention_vecs = torch.tensor(
        select_field(processed_samples, "context", "mention_ids")
    )
    context_vecs = torch.tensor(
        select_field(processed_samples, "context", "ids"), dtype=torch.long,
    )
    cand_vecs = torch.tensor(
        select_field(processed_samples, "label", "ids"), dtype=torch.long,
    )
    print('cand_vecs:',cand_vecs)
    if use_world:
        src_vecs = torch.tensor(
            select_field(processed_samples, "src"), dtype=torch.long,
        )
    label_idx = torch.tensor(
        select_field(processed_samples, "label_idx"), dtype=torch.long,
    )

    is_label_NIL = torch.tensor(
        select_field(processed_samples, "is_label_NIL"), dtype=torch.bool,
    )

    data = {
        "mention_vecs": mention_vecs,
        "context_vecs": context_vecs,
        "cand_vecs": cand_vecs,
        "label_idx": label_idx,
        "is_NIL": is_label_NIL,
    }

    if use_world:
        data["src"] = src_vecs
        tensor_data = TensorDataset(mention_vecs, context_vecs, cand_vecs, src_vecs, label_idx, is_label_NIL)
    else:
        tensor_data = TensorDataset(mention_vecs, context_vecs, cand_vecs, label_idx, is_label_NIL)
    return data, tensor_data
