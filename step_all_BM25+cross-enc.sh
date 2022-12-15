#!/bin/bash

# setting for BM25 w NIL handling

source activate blink37

# setting which GPU
export CUDA_VISIBLE_DEVICES=1

# in the scripts below
#  --use_NIL_tag       corresponds to "NIL-tag"
#  --use_NIL_desc      corresponds to "NIL-tag-desc" (both above)
#  --use_NIL_desc_tag  corresponds to "NIL-tag-descWtag" (all above)

# pipeline as script
dataset=mm #share_clef or mm (which is medmentions)
mm_data_setting=full # for mm only, full or st21pv (only tested full to ensure a larger number of mentions and NILs)
mm_onto_ver_model_mark=2017AA_pruned0.2 # for mm only, 2017AA_pruned0.1 or 2017AA_pruned0.2, 2014AB, 2015AB
mm_onto_ver=2017AA_pruned0.2 # for mm only, 2017AA_pruned0.1 or 2017AA_pruned0.2, 2014AB, 2015AB
if [ "$dataset" = share_clef ]
then
  data_name_w_syn=share_clef_2013_preprocessed_ori_syn_full
  data_name=share_clef_2013_preprocessed_ori
  onto_ver_model_mark=''
  onto_ver=2012AB
  NIL_ent_ind_w_syn=288490
  NIL_ent_ind=88150
  cross_enc_epoch_name='/epoch_3' #''
  further_result_mark='last-epoch' #'' #'-rerun'
  th1=0.00
  th2=0.95
fi

if [ "$dataset" = mm ]
then
  data_name_w_syn=MedMentions-preprocessed/${mm_data_setting}-${mm_onto_ver}_syn_full
  data_name=MedMentions-preprocessed/${mm_data_setting}-${mm_onto_ver}
  onto_ver_model_mark=${mm_onto_ver_model_mark}
  onto_ver=${mm_onto_ver}
  if [ "$onto_ver" = 2017AA_pruned0.1 ]
  then
    NIL_ent_ind_w_syn=126188
    NIL_ent_ind=35392
  fi
  if [ "$onto_ver" = 2017AA_pruned0.2 ]
  then
    NIL_ent_ind_w_syn=112097
    NIL_ent_ind=31460
  fi
  if [ "$onto_ver" = 2015AB ]
  then
    NIL_ent_ind_w_syn=128974
    NIL_ent_ind=36907
  fi
  if [ "$onto_ver" = 2014AB ]
  then
    NIL_ent_ind_w_syn=124132
    NIL_ent_ind=35398
  fi
  cross_enc_epoch_name='' #'/epoch_3' #''
  further_result_mark='' #'last-epoch' #'' #'-rerun'
  th1=0.00
  th2=0.80
fi

use_synonyms=true
# this bi-encoder model was only used for tokenization - to control the same approch for tokenization between BERT and BM25
bi_enc_model_size=large
#bi_enc_model_size=base
bi_enc_bertmodel=bert-${bi_enc_model_size}-uncased
#bi_enc_bertmodel=dmis-lab/biobert-base-cased-v1.2
#bi_enc_bertmodel=cambridgeltl/SapBERT-from-PubMedBERT-fulltext
lowercase=true
rep_ents=false
chunk_every_k=25 # chunk_every_k default as 100, max 128 for 48G GPU, smaller (like 50) for memory reason.
use_debug_cross_enc=false
train_cross=true
use_NIL_threshold=true
use_NIL_ranking=false
inference=true
top_k_cross=10
crossencoder_model_size=base #base #vs. large
cross_enc_bertmodel=bert-${crossencoder_model_size}-uncased
#cross_enc_bertmodel=dmis-lab/biobert-base-cased-v1.2 # as in Ji et al., 2020
#cross_enc_bertmodel=cambridgeltl/SapBERT-from-PubMedBERT-fulltext
use_debug_inference=false
NIL_param_tuning=false
further_model_mark=''
#further_model_mark='-biobert'
#further_model_mark='-sapbert'

if [ "$lowercase" = true ]
then
  arg_lowercase='--lowercase'
else
  arg_lowercase=''
fi

biencoder_batch_size=16

if [ "$use_synonyms" = true ]
then
  data_name=${data_name_w_syn} # data (syn-augmented) to train bi-encoder
  #biencoder_model_name=share-clef-tl-syn  # this model is just used for tokenization.
  biencoder_model_name=${dataset/_/-}${onto_ver_model_mark/_/-}-syn-full-tl${further_model_mark}-NIL-tag-bs${biencoder_batch_size} # this model is just used for tokenization.
  #biencoder_model_name=${dataset/_/-}${onto_ver_model_mark/_/-}-tl-syn${further_model_mark}
  entity_catalogue_postfix=_syn_full
  NIL_enc_mark=${entity_catalogue_postfix/_with_/_w_}_blink${further_model_mark} # here the further model mark represents the tokenizer of that model
  entity_catalogue_postfix_for_cross=_syn_attr  
  NIL_enc_mark_for_cross=${entity_catalogue_postfix_for_cross/_with_/_w_}_blink${further_model_mark}
  NIL_ent_ind=${NIL_ent_ind_w_syn}
  post_fix_cand=BM25-cand-syn-full
  crossenc_syn_mark=-syn
  arg_syn=--use_synonyms
  
else
  data_name=${data_name} # data name (non-syn-augmented) to generate cross-encoder data
  biencoder_model_name=${dataset/_/-}${onto_ver_model_mark/_/-}-tl${further_model_mark}
  entity_catalogue_postfix=""
  NIL_enc_mark=${entity_catalogue_postfix/_with_/_w_}_blink${further_model_mark}
  entity_catalogue_postfix_for_cross=$entity_catalogue_postfix  
  NIL_enc_mark_for_cross=${entity_catalogue_postfix_for_cross/_with_/_w_}_blink${further_model_mark}
  NIL_ent_ind=${NIL_ent_ind}
  post_fix_cand=BM25
  crossenc_syn_mark=""
  arg_syn=""
fi

num_train_epochs_bi_enc=3
warmup_proportion=0.1
gen_extra_features=true # if generating the men-entity string matching features as well
optimize_NIL=false # optimise NIL metrics when training cross-encoder
num_train_epochs_cross_enc=4 #10 #4
crossencoder_max_cand_length=128
crossencoder_max_seq_length=160
crossencoder_model_name=original${crossenc_syn_mark}-top${top_k_cross}${post_fix_cand}${further_model_mark}

if [ "$use_debug_cross_enc" = true ]
then
  arg_debug_for_cross='--debug'
else
  arg_debug_for_cross=''
fi

if [ "$use_NIL_threshold" = true ]
then
  # best paramters after tuning with the validation data
  th2=0.85
  arg_th="--with_NIL_infer --th_NIL_cross_enc ${th2}"
else
  arg_th=""
fi

if [ "$use_NIL_ranking" = true ]
then
  arg_NIL_rank_rep="--set_NIL_as_cand --use_NIL_tag"
  post_fix_cand=${post_fix_cand}-NIL-rank-tag
else
  arg_NIL_rank_rep=""
fi  

if [ "$optimize_NIL" = true ]
then
  arg_optimize_NIL='--optimize_NIL'
else
  arg_optimize_NIL=''
fi

if [ "$gen_extra_features" = true ]
then
  arg_gen_extra_features='--use_extra_features'
else
  arg_gen_extra_features=''
fi

if [ "$use_debug_inference" = true ]
then
  arg_debug="--debug"
else
  arg_debug=""
fi

if [ "$rep_ents" = true ]
then
  # to generate entity token ids and encoding - with NIL as 'NIL'
  PYTHONPATH=. python scripts/generate_cand_ids.py  \
      --path_to_model_config "models/biencoder_custom_${bi_enc_model_size}.json" \
      --path_to_model "models/biencoder/$biencoder_model_name/pytorch_model.bin" \
      --bert_model ${bi_enc_bertmodel} \
      ${arg_lowercase} \
      --saved_cand_ids_path "preprocessing/saved_cand_ids_umls${onto_ver}${NIL_enc_mark}_re_tr.pt" \
      --entity_list_json_file_path "ontologies/UMLS${onto_ver}${entity_catalogue_postfix}.jsonl" \
      ${arg_syn}
  if [ "$use_synonyms" = true ]
  then
    PYTHONPATH=. python scripts/generate_cand_ids.py  \
        --path_to_model_config "models/biencoder_custom_${bi_enc_model_size}.json" \
        --path_to_model "models/biencoder/$biencoder_model_name/pytorch_model.bin" \
        --bert_model ${bi_enc_bertmodel} \
        ${arg_lowercase} \
        --saved_cand_ids_path "preprocessing/saved_cand_ids_umls${onto_ver}${NIL_enc_mark_for_cross}_re_tr.pt" \
        --entity_list_json_file_path "ontologies/UMLS${onto_ver}${entity_catalogue_postfix_for_cross}.jsonl" \
        ${arg_syn}
  fi      
  PYTHONPATH=. python scripts/generate_candidates_blink.py \
      --path_to_model_config "models/biencoder_custom_${bi_enc_model_size}.json" \
      --path_to_model="models/biencoder/$biencoder_model_name/pytorch_model.bin" \
      --bert_model ${bi_enc_bertmodel} \
      --entity_dict_path="ontologies/UMLS${onto_ver}${entity_catalogue_postfix}.jsonl" \
      --saved_cand_ids="preprocessing/saved_cand_ids_umls${onto_ver}${NIL_enc_mark}_re_tr.pt" \
      --encoding_save_file_dir="models/UMLS${onto_ver:0:6}_ent_enc_re_tr" \
      --encoding_save_file_name="UMLS${onto_ver}${NIL_enc_mark}_ent_enc_re_tr.t7" \
      --chunk_every_k ${chunk_every_k}
fi

if [ "$train_cross" = true ]
then
  # create dataset for cross-encoder w_NIL
  # adjust the top_k value here
  PYTHONPATH=. python blink/biencoder/eval_biencoder.py   \
      --data_path data/$data_name    \
      --output_path models/biencoder/$biencoder_model_name  \
      --max_context_length 32   \
      --max_cand_length ${crossencoder_max_cand_length}   \
      --eval_batch_size 8    \
      --bert_model ${bi_enc_bertmodel} \
      --path_to_model models/biencoder/$biencoder_model_name/pytorch_model.bin \
      --data_parallel \
      --mode train,valid \
      --entity_dict_path "ontologies/UMLS${onto_ver}${entity_catalogue_postfix}.jsonl" \
      --cand_pool_path preprocessing/saved_cand_ids_umls${onto_ver}${NIL_enc_mark_for_cross}_re_tr.pt \
      --cand_pool_path_for_BM25 preprocessing/saved_cand_ids_umls${onto_ver}${NIL_enc_mark}_re_tr.pt \
      --cand_encode_path models/UMLS${onto_ver:0:6}_ent_enc_re_tr/UMLS${onto_ver}${NIL_enc_mark}_ent_enc_re_tr.t7 \
      --save_topk_result \
      --top_k $top_k_cross \
      ${arg_lowercase} \
      --NIL_ent_ind $NIL_ent_ind \
      ${arg_syn} \
      --use_BM25 \
      ${arg_debug_for_cross} \
      ${arg_gen_extra_features}

  #train cross-encoder
  #note: here cand/data path is top${top_k_cross}_candidates_w_o_NIL
  PYTHONPATH=. python blink/crossencoder/train_cross.py \
    --data_path models/biencoder/$biencoder_model_name/top${top_k_cross}_candidates_BM25_w_o_NIL \
    --output_path models/crossencoder/${dataset}${onto_ver_model_mark}/${crossencoder_model_name}  \
    --learning_rate 3e-05  \
    --num_train_epochs ${num_train_epochs_cross_enc}  \
    --warmup_proportion ${warmup_proportion} \
    --max_context_length 32  \
    --max_cand_length ${crossencoder_max_cand_length} \
    --max_seq_length ${crossencoder_max_seq_length} \
    --train_batch_size 1  \
    --eval_batch_size 1  \
    --bert_model ${cross_enc_bertmodel}  \
    --type_optimization all_encoder_layers  \
    --data_parallel \
    --print_interval  100 \
    --eval_interval 2000  \
    ${arg_lowercase} \
    --top_k $top_k_cross  \
    --add_linear  \
    --out_dim 1  \
    --use_ori_classification \
    --NIL_ent_ind $NIL_ent_ind \
    --save_model_epoch_parts \
    ${arg_optimize_NIL}
fi

#inference
if [ "$inference" = true ]
then
  PYTHONPATH=. python blink/run_bio_benchmark.py \
    --data ${dataset}${onto_ver_model_mark} \
    --onto_ver ${onto_ver} \
    -top_k ${top_k_cross} \
    ${arg_lowercase} \
    --biencoder_bert_model ${bi_enc_bertmodel} \
    --biencoder_model_name ${biencoder_model_name} \
    --biencoder_model_size ${bi_enc_model_size} \
    --NIL_enc_mark "${NIL_enc_mark}" \
    --crossencoder_bert_model ${cross_enc_bertmodel} \
    --cross_model_setting ${crossencoder_model_name}${cross_enc_epoch_name} \
    --cross_model_size ${crossencoder_model_size} \
    -m ${NIL_enc_mark}_top${top_k_cross}_${post_fix_cand}${further_model_mark}${further_result_mark} \
    -BM25 \
    ${arg_syn} \
    ${arg_th} \
    ${arg_NIL_rank_rep} \
    ${arg_debug}
fi

if [ "$NIL_param_tuning" = true ]
then
  #parameter tuning for threshold-based approach
  for th2 in $(seq 0.4 0.05 1)
  do
    arg_th="--with_NIL_infer --th_NIL_cross_enc ${th2}"
    PYTHONPATH=. python blink/run_bio_benchmark.py \
      --data ${dataset}${onto_ver_model_mark} \
      --onto_ver ${onto_ver} \
      -top_k ${top_k_cross} \
      ${arg_lowercase} \
      --biencoder_bert_model ${bi_enc_bertmodel} \
      --biencoder_model_name ${biencoder_model_name} \
      --biencoder_model_size ${bi_enc_model_size} \
      --NIL_enc_mark "${NIL_enc_mark}" \
      --crossencoder_bert_model ${cross_enc_bertmodel} \
      --cross_model_setting ${crossencoder_model_name} \
      --cross_model_size ${crossencoder_model_size} \
      -m ${NIL_enc_mark}_top${top_k_cross}_blink_${post_fix_cand}${further_model_mark}${further_result_mark} \
      -BM25 \
      ${arg_syn} \
      ${arg_th} \
      ${arg_NIL_rank_rep} \
      --debug
  done
fi