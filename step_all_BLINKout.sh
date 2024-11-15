#!/bin/bash

# setting for BLINKout - BLINK + syn handling + NIL representation and prediction

source activate blink37

# setting which GPU
export CUDA_VISIBLE_DEVICES=1
#export CUDA_LAUNCH_BLOCKING=1 # for debugging 

# in the scripts below
#  --use_NIL_tag       corresponds to "NIL-tag"
#  --use_NIL_desc      corresponds to "NIL-tag-desc" (both above)
#  --use_NIL_desc_tag  corresponds to "NIL-tag-descWtag" (all above)

# pipeline as script
dataset=nilk #nilk or share_clef or mm (which is medmentions)
mm_data_setting=full # for mm only, full or st21pv (only tested full to ensure a larger number of mentions and NILs)
mm_onto_ver_model_mark=2017AA_pruned0.2 # for mm only, 2017AA_pruned0.1 or 2017AA_pruned0.2, 2014AB, 2015AB
mm_onto_ver=2017AA_pruned0.2 # for mm only, 2017AA_pruned0.1 or 2017AA_pruned0.2, 2014AB, 2015AB
use_best_top_k=false

if [ "$dataset" = nilk ]
then
  data_name_w_syn=NILK-preprocessed-0.001/syn_full
  data_name=NILK-preprocessed-0.001/syn_attr
  onto_ver_model_mark=''
  onto_ver=''
  
  onto_name='WikiData_pruned_0.001'
  NIL_ent_ind_w_syn=121190
  NIL_ent_ind=79411

  #onto_name='WikiData_pruned_0.005'
  #NIL_ent_ind_w_syn=421819
  #NIL_ent_ind=304935

  #onto_name='WikiData_pruned'
  #NIL_ent_ind_w_syn=686966
  #NIL_ent_ind=516367

  #onto_name='WikiData'
  #NIL_ent_ind_w_syn=17773906
  #NIL_ent_ind=14593338

  max_cand_length=32
  max_seq_length=64 
  eval_interval=10000 #10000 for NILK-sample and 2000 for the other datasets
  aggregating_factor=50 # 50 for NILK-sample, default as 20 for the other datasets, predicting more times top-k, so that after synonym aggregation there is still top-k candidates.
  num_train_epochs_bi_enc=1
  num_train_epochs_cross_enc=1

  if [ "$use_best_top_k" = true ]
  then
    top_k_cross=50
  else 
    top_k_cross=4 #default as 4 for NILK-sample and 10 for the other datasets; the best BLINKout model had 𝑘 as 150 for ShARe/CLEF 2013, 50 for MM-pruned-0.1, MM-2014AB, and NILK-sample, and 100 for MM-pruned-0.2.
  fi
  lambda_NIL=0.01

  cross_enc_epoch_name=''
  further_result_mark='-new'
fi

if [ "$dataset" = share_clef ]
then
  data_name_w_syn=share_clef_2013_preprocessed_ori_syn_full
  data_name=share_clef_2013_preprocessed_ori
  onto_ver_model_mark=''
  onto_name='UMLS'
  onto_ver=2012AB
  NIL_ent_ind_w_syn=288490
  NIL_ent_ind=88150

  max_cand_length=128
  max_seq_length=160
  eval_interval=2000
  aggregating_factor=20 # 50 for NILK-sample, default as 20 for the other datasets, predicting more times top-k, so that after synonym aggregation there is still top-k candidates.
  if [ "$use_best_top_k" = true ]
  then
    top_k_cross=150
  else 
    top_k_cross=10 #default as 4 for NILK-sample and 10 for the other datasets; the best BLINKout model had 𝑘 as 150 for ShARe/CLEF 2013, 50 for MM-pruned-0.1, MM-2014AB, and NILK-sample, and 100 for MM-pruned-0.2.
  fi
  lambda_NIL=0.25
  num_train_epochs_bi_enc=3
  num_train_epochs_cross_enc=4

  #cross_enc_epoch_name='/epoch_3' # get last epoch (when the validation set is small)
  #further_result_mark='last-epoch'
  cross_enc_epoch_name=''
  further_result_mark='-ZS'
fi

if [ "$dataset" = mm ]
then
  data_name_w_syn=MedMentions-preprocessed/${mm_data_setting}-${mm_onto_ver}_syn_full
  data_name=MedMentions-preprocessed/${mm_data_setting}-${mm_onto_ver}
  onto_ver_model_mark=${mm_onto_ver_model_mark}
  onto_name='UMLS'
  onto_ver=${mm_onto_ver}
  
  #dataset=${dataset}${onto_ver} # for mm only
  if [ "$onto_ver" = 2017AA_pruned0.1 ]
  then
    NIL_ent_ind_w_syn=126188
    NIL_ent_ind=35392

    if [ "$use_best_top_k" = true ]
    then
      top_k_cross=50
    else 
      top_k_cross=10 #default as 4 for NILK-sample and 10 for the other datasets; the best BLINKout model had 𝑘 as 150 for ShARe/CLEF 2013, 50 for MM-pruned-0.1, MM-2014AB, and NILK-sample, and 100 for MM-pruned-0.2.
    fi
    lambda_NIL=0.2
  fi
  if [ "$onto_ver" = 2017AA_pruned0.2 ]
  then
    NIL_ent_ind_w_syn=112097
    NIL_ent_ind=31460

    if [ "$use_best_top_k" = true ]
    then
      top_k_cross=100
    else 
      top_k_cross=10 #default as 4 for NILK-sample and 10 for the other datasets; the best BLINKout model had 𝑘 as 150 for ShARe/CLEF 2013, 50 for MM-pruned-0.1, MM-2014AB, and NILK-sample, and 100 for MM-pruned-0.2.
    fi
    lambda_NIL=0.25
  fi
  if [ "$onto_ver" = 2014AB ]
  then
    NIL_ent_ind_w_syn=124132
    NIL_ent_ind=35398

    if [ "$use_best_top_k" = true ]
    then
      top_k_cross=50 # to be tuned
    else 
      top_k_cross=10 #default as 4 for NILK-sample and 10 for the other datasets; the best BLINKout model had 𝑘 as 150 for ShARe/CLEF 2013, 50 for MM-pruned-0.1, MM-2014AB, and NILK-sample, and 100 for MM-pruned-0.2.
    fi
    lambda_NIL=0.05
  fi

  max_cand_length=128
  max_seq_length=160
  eval_interval=2000
  aggregating_factor=20 # 50 for NILK-sample, default as 20 for the other datasets, predicting more times top-k, so that after synonym aggregation there is still top-k candidates.
  num_train_epochs_bi_enc=3
  num_train_epochs_cross_enc=4

  cross_enc_epoch_name='' # get best validation epoch
  further_result_mark='-ZS'
fi

use_synonyms=true
#bi_enc_model_size=large
bi_enc_model_size=base
lowercase=true
#max_ctx_length=`expr $max_seq_length - $max_cand_length` # so far hard coded to 32``
bi_enc_bertmodel=bert-${bi_enc_model_size}-uncased
#bi_enc_bertmodel=dmis-lab/biobert-base-cased-v1.2;lowercase=false # remember to set lowercase to false if using this model
#bi_enc_bertmodel=bionlp/bluebert_pubmed_mimic_uncased_L-24_H-1024_A-16
#bi_enc_bertmodel=bionlp/bluebert_pubmed_uncased_L-24_H-1024_A-16
#bi_enc_bertmodel=microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
#bi_enc_bertmodel=cambridgeltl/SapBERT-from-PubMedBERT-fulltext
#bi_enc_bertmodel=sentence-transformers/all-MiniLM-L12-v2 # see https://www.sbert.net/docs/pretrained_models.html
#bi_enc_bertmodel=sentence-transformers/all-MiniLM-L6-v2
#bi_enc_bertmodel=prajjwal1/bert-tiny
biencoder_batch_size=16
use_debug_bi_enc=false
train_bi=true
rep_ents=true # set to true if transfering one biencoder to another dataset
bs_cand_enc=50 # for entity representation bs as 2000 (max 2300) for NILK with BERT-base around 40g memory use
use_debug_cross_enc=false
train_cross=true
dynamic_emb_extra_ft_baseline=false
use_NIL_tag=true
use_NIL_desc=false
use_NIL_desc_tag=false
inference=true
bs_inference=8 # max around 444 (for 48G GPU) with the mini setting
crossencoder_model_size=base #base #vs. large
cross_enc_bertmodel=bert-${crossencoder_model_size}-uncased
#cross_enc_bertmodel=dmis-lab/biobert-base-cased-v1.2
#cross_enc_bertmodel=bionlp/bluebert_pubmed_mimic_uncased_L-12_H-768_A-12
#cross_enc_bertmodel=bionlp/bluebert_pubmed_uncased_L-12_H-768_A-12
#cross_enc_bertmodel=microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
#cross_enc_bertmodel=cambridgeltl/SapBERT-from-PubMedBERT-fulltext
#cross_enc_bertmodel=distilbert-base-uncased
#cross_enc_bertmodel=sentence-transformers/all-MiniLM-L12-v2
#cross_enc_bertmodel=sentence-transformers/all-MiniLM-L6-v2
#cross_enc_bertmodel=prajjwal1/bert-tiny
use_debug_inference=false
#NIL_param_tuning=true
further_model_mark=''
#further_model_mark='-mini' # L12, as in NASTyLinker (ESWC 2023)
#further_model_mark='-miniL6'
#further_model_mark='-tiny'
#further_model_mark='-biobert'
#further_model_mark='-bluebert'
#further_model_mark='-bluebert-pubm-only'
#further_model_mark='-pubmedbert'
#further_model_mark='-sapbert'
#further_result_mark=${further_result_mark}'-transformers'
#further_result_mark=${further_result_mark}'-cross-large'
get_cands_only=false # if set true - the inference won't finish, but only saves the bi-encoder candidates
use_fix_seeds=true # using fix random seeds for initialisation, false if do multiple runs
run_mark='-run2' # used to mark the run when use_fix_seeds is set to False

if [ "$max_cand_length" = 128 ]
then
  can_len_mark='' #default setting
else
  can_len_mark='-cand'${max_cand_length}
fi
further_model_mark=${further_model_mark}${can_len_mark}

if [ "$use_fix_seeds" = true ]
then
  arg_using_fix_seeds='--fix_seeds'
else
  arg_using_fix_seeds=''
  further_result_mark=${further_result_mark}${run_mark}
fi

if [ "$lowercase" = true ]
then
  arg_lowercase='--lowercase'
else
  arg_lowercase=''
fi

if [ "$use_NIL_tag" = true ]
then
  arg_NIL_tag='--use_NIL_tag'
  tag_mark='-tag'
else
  arg_NIL_tag=''
  tag_mark=''
fi

if [ "$use_NIL_desc" = true ]
then
  arg_NIL_desc='--use_NIL_desc'
  desc_mark='-desc'
else
  arg_NIL_desc=''
  desc_mark=''
fi

if [ "$use_NIL_desc_tag" = true ]
then
  arg_NIL_desc_tag='--use_NIL_desc_tag'
  desc_tag_mark='Wtag'
else
  arg_NIL_desc_tag=''
  desc_tag_mark=''
fi

if [ "$dynamic_emb_extra_ft_baseline" = true ]
then
  #arg_dynamic_emb_extra_ft_baseline=--use_NIL_classification\ --lambda_NIL\ ${lambda_NIL}\ --use_score_features\ --use_score_pooling\ --use_men_only_score_ft\ --use_extra_features\ --use_NIL_classification_infer;joint_learning_mark='full-features-NIL-infer';lambda_NIL=0.25 # as default for dynamic feature-based baseline
  arg_dynamic_emb_extra_ft_baseline=--use_NIL_classification\ --lambda_NIL\ ${lambda_NIL}\ --use_men_only_score_ft;joint_learning_mark='gu2021' #lambda_NIL=0.01 # 0.25 for ShARe/CLEF 2013 and MM-pruned-0.2 datasets, 0.2 for MM-pruned-0.1, 0.05 for MM-2014AB, and 0.01 for NILK-sample.

else
  arg_dynamic_emb_extra_ft_baseline=''
  joint_learning_mark=''
fi

if [ "$get_cands_only" = true ]
then
  arg_get_cand='--save_cand --cand_only'
else
  arg_get_cand=''
fi

NIL_rep_mark=${tag_mark}${desc_mark}${desc_tag_mark}

if [ "$use_synonyms" = true ]
then
  data_name=${data_name_w_syn} # data (syn-augmented) to train bi-encoder
  #biencoder_model_name=${dataset/_/-}${onto_ver_model_mark/_/-}-tl-syn-NIL-tag
  biencoder_model_name=${dataset/_/-}${onto_ver_model_mark/_/-}-syn-full-tl${further_model_mark}-NIL${NIL_rep_mark}-bs$biencoder_batch_size
  #biencoder_model_name=${dataset/_/-}${onto_ver_model_mark/_/-}-syn-full-tl-NIL-tag-desc-bs$biencoder_batch_size
  #biencoder_model_name=${dataset/_/-}${onto_ver_model_mark/_/-}-syn-full-tl-NIL-tag-descWtag-bs$biencoder_batch_size
  entity_catalogue_postfix=_with_NIL_syn_full
  NIL_enc_mark=${entity_catalogue_postfix/_with_/_w_}${NIL_rep_mark/-/_}_bs$biencoder_batch_size${further_model_mark}
  #NIL_enc_mark=${entity_catalogue_postfix/_with_/_w_}_tag_desc_bs$biencoder_batch_size
  #NIL_enc_mark=${entity_catalogue_postfix/_with_/_w_}_tag_descWtag_bs$biencoder_batch_size
  entity_catalogue_postfix_for_cross=_with_NIL_syn_attr
  NIL_enc_mark_for_cross=${entity_catalogue_postfix_for_cross/_with_/_w_}${further_model_mark}
  NIL_ent_ind=${NIL_ent_ind_w_syn}
  post_fix_cand='-cand-syn-full'
  crossenc_syn_mark=-syn
  arg_syn=--use_synonyms
else
  data_name=${data_name} # data name (non-syn-augmented) to generate cross-encoder data
  biencoder_model_name=${dataset/_/-}${onto_ver_model_mark/_/-}-tl${further_model_mark}-NIL${NIL_rep_mark}-bs$biencoder_batch_size
  entity_catalogue_postfix=_with_NIL_syn_attr
  NIL_enc_mark=${entity_catalogue_postfix/_with_/_w_}${further_model_mark} #TODO: add ${NIL_rep_mark/-/_}_bs$biencoder_batch_size
  entity_catalogue_postfix_for_cross=$entity_catalogue_postfix  
  NIL_enc_mark_for_cross=${entity_catalogue_postfix_for_cross/_with_/_w_}${further_model_mark}
  NIL_ent_ind=${NIL_ent_ind}
  post_fix_cand=''
  crossenc_syn_mark=''
  arg_syn=''
fi

#max_num_train_steps_bi_enc=20000
warmup_proportion=0.1
gen_extra_features=true # if generating the men-entity string matching features as well
optimize_NIL=false # optimise NIL metrics when training cross-encoder
#max_num_train_steps_cross_enc=40000
crossencoder_model_name=original${crossenc_syn_mark}-NIL${NIL_rep_mark}-top${top_k_cross}${post_fix_cand}${further_model_mark}${joint_learning_mark}

if [ "$use_debug_bi_enc" = true ]
then
  arg_debug_for_bienc='--debug'
  biencoder_model_name=${biencoder_model_name}-debug
else
  arg_debug_for_bienc=''
fi

if [ "$crossencoder_model_size" = large ]
then
  crossencoder_model_name=original-large-${crossenc_syn_mark}-NIL${NIL_rep_mark}-top${top_k_cross}${post_fix_cand}${further_model_mark}
fi

if [ "$use_debug_cross_enc" = true ]
then
  arg_debug_for_cross='--debug'
  crossencoder_model_name=${crossencoder_model_name}-debug
else
  arg_debug_for_cross=''
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
  arg_debug='--debug'
else
  arg_debug=''
fi

if [ "$train_bi" = true ]
then
  #train bi-encoder
  PYTHONPATH=. python blink/biencoder/train_biencoder.py \
    --data_path data/$data_name \
    --output_path models/biencoder/$biencoder_model_name  \
    --learning_rate 3e-05  \
    --num_train_epochs ${num_train_epochs_bi_enc}  \
    --max_context_length 32  \
    --max_cand_length ${max_cand_length} \
    --max_seq_length ${max_seq_length} \
    --train_batch_size $biencoder_batch_size  \
    --eval_batch_size $biencoder_batch_size  \
    --bert_model ${bi_enc_bertmodel}  \
    --type_optimization all_encoder_layers  \
    --print_interval  100 \
    --eval_interval ${eval_interval} \
    ${arg_lowercase} \
    --shuffle \
    --data_parallel \
    --use_triplet_loss_bi_enc \
    ${arg_using_fix_seeds} \
    --NIL_ent_ind ${NIL_ent_ind} \
    ${arg_NIL_tag} \
    ${arg_NIL_desc} \
    ${arg_NIL_desc_tag} \
    ${arg_syn} \
    ${arg_debug_for_bienc}
    #--limit_by_train_step \
    #--max_num_train_steps ${max_num_train_steps_bi_enc} \
fi

if [ "$rep_ents" = true ]
then
  # to generate entity token ids and encoding - with NIL as 'NIL'
  PYTHONPATH=. python scripts/generate_cand_ids.py  \
      --path_to_model_config "models/biencoder_custom_${bi_enc_model_size}.json" \
      --path_to_model "models/biencoder/$biencoder_model_name/pytorch_model.bin" \
      --bert_model ${bi_enc_bertmodel} \
      --max_cand_length ${max_cand_length} \
      ${arg_lowercase} \
      --saved_cand_ids_path "preprocessing/saved_cand_ids_${onto_name@L}${onto_ver}${NIL_enc_mark}_re_tr.pt" \
      --entity_list_json_file_path "ontologies/${onto_name}${onto_ver}${entity_catalogue_postfix}.jsonl" \
      ${arg_NIL_tag} \
      ${arg_NIL_desc} \
      ${arg_NIL_desc_tag} \
      ${arg_syn}
  if [ "$use_synonyms" = true ]
  then
    PYTHONPATH=. python scripts/generate_cand_ids.py  \
        --path_to_model_config "models/biencoder_custom_${bi_enc_model_size}.json" \
        --path_to_model "models/biencoder/$biencoder_model_name/pytorch_model.bin" \
        --bert_model ${bi_enc_bertmodel} \
        --max_cand_length ${max_cand_length} \
        ${arg_lowercase} \
        --saved_cand_ids_path "preprocessing/saved_cand_ids_${onto_name@L}${onto_ver}${NIL_enc_mark_for_cross}_re_tr.pt" \
        --entity_list_json_file_path "ontologies/${onto_name}${onto_ver}${entity_catalogue_postfix_for_cross}.jsonl" \
        ${arg_NIL_tag} \
        ${arg_NIL_desc} \
        ${arg_NIL_desc_tag} \
        ${arg_syn}
  fi
  PYTHONPATH=. python scripts/generate_candidates_blink.py \
      --path_to_model_config "models/biencoder_custom_${bi_enc_model_size}.json" \
      --path_to_model="models/biencoder/$biencoder_model_name/pytorch_model.bin" \
      --bert_model ${bi_enc_bertmodel} \
      --entity_dict_path="ontologies/${onto_name}${onto_ver}${entity_catalogue_postfix}.jsonl" \
      --saved_cand_ids="preprocessing/saved_cand_ids_${onto_name@L}${onto_ver}${NIL_enc_mark}_re_tr.pt" \
      --encoding_save_file_dir="models/${onto_name}${onto_ver:0:6}_ent_enc_re_tr" \
      --encoding_save_file_name="${onto_name}${onto_ver}${NIL_enc_mark}_ent_enc_re_tr.t7" \
      --batch_size ${bs_cand_enc}
      #--chunk_every_k ${chunk_every_k}
fi

if [ "$train_cross" = true ]
then
  # create dataset for cross-encoder w_NIL
  # adjust the top_k value here
  PYTHONPATH=. python blink/biencoder/eval_biencoder.py   \
      --data_path data/$data_name    \
      --output_path models/biencoder/$biencoder_model_name  \
      --max_context_length 32   \
      --max_cand_length ${max_cand_length}   \
      --eval_batch_size 8    \
      --bert_model ${bi_enc_bertmodel}  \
      --path_to_model models/biencoder/$biencoder_model_name/pytorch_model.bin \
      --data_parallel \
      --mode train,valid \
      --entity_dict_path "ontologies/${onto_name}${onto_ver}${entity_catalogue_postfix}.jsonl" \
      --cand_pool_path preprocessing/saved_cand_ids_${onto_name@L}${onto_ver}${NIL_enc_mark_for_cross}_re_tr.pt \
      --cand_encode_path models/${onto_name}${onto_ver:0:6}_ent_enc_re_tr/${onto_name}${onto_ver}${NIL_enc_mark}_ent_enc_re_tr.t7 \
      --save_topk_result \
      --top_k $top_k_cross \
      --aggregating_factor ${aggregating_factor} \
      ${arg_lowercase} \
      --add_NIL_to_bi_enc_pred \
      --NIL_ent_ind $NIL_ent_ind \
      ${arg_NIL_tag} \
      ${arg_NIL_desc} \
      ${arg_NIL_desc_tag} \
      ${arg_syn} \
      ${arg_debug_for_cross} \
      ${arg_gen_extra_features}

  #train cross-encoder
 PYTHONPATH=. python blink/crossencoder/train_cross.py \
    --data_path models/biencoder/$biencoder_model_name/top${top_k_cross}_candidates \
    --output_path models/crossencoder/${dataset}${onto_ver_model_mark}/${crossencoder_model_name}  \
    --learning_rate 3e-05  \
    --num_train_epochs ${num_train_epochs_cross_enc}  \
    --warmup_proportion ${warmup_proportion} \
    --max_context_length 32  \
    --max_cand_length ${max_cand_length} \
    --max_seq_length ${max_seq_length} \
    --train_batch_size 1  \
    --eval_batch_size 1  \
    --bert_model ${cross_enc_bertmodel}  \
    --type_optimization all_encoder_layers  \
    --data_parallel \
    --print_interval  100 \
    --eval_interval ${eval_interval}  \
    ${arg_lowercase} \
    --top_k $top_k_cross  \
    --add_linear  \
    --out_dim 1  \
    --use_ori_classification \
    ${arg_dynamic_emb_extra_ft_baseline} \
    ${arg_using_fix_seeds} \
    --NIL_ent_ind $NIL_ent_ind \
    --save_model_epoch_parts \
    ${arg_optimize_NIL}
    #--limit_by_train_step \
    #--max_num_train_steps ${max_num_train_steps_cross_enc} \
fi

#inference
if [ "$inference" = true ]
then
  PYTHONPATH=. python blink/run_bio_benchmark.py \
    --data ${dataset}${onto_ver_model_mark} \
    --onto_name ${onto_name} \
    --onto_ver "${onto_ver}" \
    --set_NIL_as_cand \
    ${arg_NIL_tag} \
    ${arg_NIL_desc} \
    ${arg_NIL_desc_tag} \
    ${arg_syn} \
    -top_k ${top_k_cross} \
    --aggregating_factor ${aggregating_factor} \
    ${arg_lowercase} \
    --biencoder_bert_model ${bi_enc_bertmodel} \
    --biencoder_model_name ${biencoder_model_name} \
    --biencoder_model_size ${bi_enc_model_size} \
    --max_cand_length ${max_cand_length} \
    --eval_batch_size ${bs_inference} \
    --NIL_enc_mark "${NIL_enc_mark}" \
    --crossencoder_bert_model ${cross_enc_bertmodel} \
    --cross_model_setting ${crossencoder_model_name}${cross_enc_epoch_name} \
    --cross_model_size ${crossencoder_model_size} \
    -m ${NIL_enc_mark}_top${top_k_cross}${post_fix_cand}${further_model_mark}${further_result_mark}${joint_learning_mark} \
    ${arg_debug} \
    ${arg_get_cand}
fi