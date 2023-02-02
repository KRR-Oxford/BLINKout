#!/bin/bash

# setting for BLINKout - BLINK + syn handling + NIL representation and prediction

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
mm_onto_ver_model_mark=2014AB # for mm only, 2017AA_pruned0.1 or 2017AA_pruned0.2, 2014AB, 2015AB
mm_onto_ver=2014AB # for mm only, 2017AA_pruned0.1 or 2017AA_pruned0.2, 2014AB, 2015AB

if [ "$dataset" = share_clef ]
then
  data_name_w_syn=share_clef_2013_preprocessed_ori_syn_full
  data_name=share_clef_2013_preprocessed_ori
  onto_ver_model_mark=''
  onto_ver=2012AB
  NIL_ent_ind_w_syn=288490
  NIL_ent_ind=88150
  cross_enc_epoch_name='/epoch_3' # get last epoch (as our validation set is small)
  further_result_mark='last-epoch'
fi

if [ "$dataset" = mm ]
then
  data_name_w_syn=MedMentions-preprocessed/${mm_data_setting}-${mm_onto_ver}_syn_full
  data_name=MedMentions-preprocessed/${mm_data_setting}-${mm_onto_ver}
  onto_ver_model_mark=${mm_onto_ver_model_mark}
  onto_ver=${mm_onto_ver}
  #dataset=${dataset}${onto_ver} # for mm only
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
  cross_enc_epoch_name='' # get best validation epoch
  further_result_mark=''
fi

use_synonyms=true
#bi_enc_model_size=large
bi_enc_model_size=base
lowercase=true
#bi_enc_bertmodel=bert-${bi_enc_model_size}-uncased
#bi_enc_bertmodel=dmis-lab/biobert-base-cased-v1.2;lowercase=false # remember to set lowercase to false if using this model
#bi_enc_bertmodel=bionlp/bluebert_pubmed_mimic_uncased_L-24_H-1024_A-16
#bi_enc_bertmodel=bionlp/bluebert_pubmed_uncased_L-24_H-1024_A-16
#bi_enc_bertmodel=microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
bi_enc_bertmodel=cambridgeltl/SapBERT-from-PubMedBERT-fulltext
train_bi=true
rep_ents=true # set to true if transfering one biencoder to another dataset
chunk_every_k=300  # for entity representation - chunk_every_k default as 100, max 128 for 48G GPU, smaller (like 50) for memory reason.
use_debug_cross_enc=false
train_cross=true
dynamic_emb_extra_ft_baseline=false
use_NIL_tag=true
use_NIL_desc=false
use_NIL_desc_tag=false
inference=true
top_k_cross=10
crossencoder_model_size=base #base #vs. large
#cross_enc_bertmodel=bert-${crossencoder_model_size}-uncased
#cross_enc_bertmodel=dmis-lab/biobert-base-cased-v1.2
#cross_enc_bertmodel=bionlp/bluebert_pubmed_mimic_uncased_L-12_H-768_A-12
#cross_enc_bertmodel=bionlp/bluebert_pubmed_uncased_L-12_H-768_A-12
#cross_enc_bertmodel=microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
cross_enc_bertmodel=cambridgeltl/SapBERT-from-PubMedBERT-fulltext
use_debug_inference=false
#NIL_param_tuning=true
further_model_mark=''
#further_model_mark='-biobert'
#further_model_mark='-bluebert'
#further_model_mark='-bluebert-pubm-only'
#further_model_mark='-pubmedbert'
further_model_mark='-sapbert'
#further_result_mark=${further_result_mark}'-transformers'
#further_result_mark=${further_result_mark}'-cross-large'
get_cands_only=false # if set true - the inference won't finish, but only saves the bi-encoder candidates

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
  #lambda_NIL=0.25 # as default
  lambda_NIL=0.2
  #arg_dynamic_emb_extra_ft_baseline='--use_NIL_classification --lambda_NIL ${lambda_NIL} --use_score_features --use_score_pooling --use_men_only_score_ft --use_extra_features --use_NIL_classification_infer';joint_learning_mark='full-features-NIL-infer'
  arg_dynamic_emb_extra_ft_baseline='--use_NIL_classification --lambda_NIL ${lambda_NIL} --use_men_only_score_ft';joint_learning_mark='gu2021'
  #arg_dynamic_emb_extra_ft_baseline='--use_NIL_classification --lambda_NIL ${lambda_NIL} --use_men_only_score_ft --use_score_features --use_score_pooling --use_extra_features';joint_learning_mark='full-features'
  #arg_dynamic_emb_extra_ft_baseline='--use_NIL_classification --lambda_NIL ${lambda_NIL} --use_score_features --use_score_pooling --use_extra_features';joint_learning_mark='rao2013'
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
biencoder_batch_size=16

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
  biencoder_model_name=${dataset/_/-}${onto_ver_model_mark/_/-}-tl${further_model_mark}-NIL-tag-bs$biencoder_batch_size
  entity_catalogue_postfix=_with_NIL_syn_attr
  NIL_enc_mark=${entity_catalogue_postfix/_with_/_w_}${further_model_mark}
  entity_catalogue_postfix_for_cross=$entity_catalogue_postfix  
  NIL_enc_mark_for_cross=${entity_catalogue_postfix_for_cross/_with_/_w_}${further_model_mark}
  NIL_ent_ind=${NIL_ent_ind}
  post_fix_cand=''
  crossenc_syn_mark=''
  arg_syn=''
fi

num_train_epochs_bi_enc=3
warmup_proportion=0.1
gen_extra_features=true # if generating the men-entity string matching features as well
optimize_NIL=false # optimise NIL metrics when training cross-encoder
num_train_epochs_cross_enc=4 #10 #4
crossencoder_max_cand_length=128
crossencoder_max_seq_length=160
crossencoder_model_name=original${crossenc_syn_mark}-NIL${NIL_rep_mark}-top${top_k_cross}${post_fix_cand}${further_model_mark}${joint_learning_mark}

if [ "$crossencoder_model_size" = large ]
then
  crossencoder_model_name=original-large-${crossenc_syn_mark}-NIL${NIL_rep_mark}-top${top_k_cross}${post_fix_cand}${further_model_mark}
fi

if [ "$use_debug_cross_enc" = true ]
then
  arg_debug_for_cross='--debug'
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
    --max_cand_length 128 \
    --max_seq_length 160 \
    --train_batch_size $biencoder_batch_size  \
    --eval_batch_size $biencoder_batch_size  \
    --bert_model ${bi_enc_bertmodel}  \
    --type_optimization all_encoder_layers  \
    --print_interval  100 \
    --eval_interval 2000 \
    ${arg_lowercase} \
    --shuffle \
    --data_parallel \
    --use_triplet_loss_bi_enc \
    --fix_seeds \
    --NIL_ent_ind ${NIL_ent_ind} \
    ${arg_NIL_tag} \
    ${arg_NIL_desc} \
    ${arg_NIL_desc_tag} \
    ${arg_syn}
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
        ${arg_lowercase} \
        --saved_cand_ids_path "preprocessing/saved_cand_ids_umls${onto_ver}${NIL_enc_mark_for_cross}_re_tr.pt" \
        --entity_list_json_file_path "ontologies/UMLS${onto_ver}${entity_catalogue_postfix_for_cross}.jsonl" \
        ${arg_NIL_tag} \
        ${arg_NIL_desc} \
        ${arg_NIL_desc_tag} \
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
      --bert_model ${bi_enc_bertmodel}  \
      --path_to_model models/biencoder/$biencoder_model_name/pytorch_model.bin \
      --data_parallel \
      --mode train,valid \
      --entity_dict_path "ontologies/UMLS${onto_ver}${entity_catalogue_postfix}.jsonl" \
      --cand_pool_path preprocessing/saved_cand_ids_umls${onto_ver}${NIL_enc_mark_for_cross}_re_tr.pt \
      --cand_encode_path models/UMLS${onto_ver:0:6}_ent_enc_re_tr/UMLS${onto_ver}${NIL_enc_mark}_ent_enc_re_tr.t7 \
      --save_topk_result \
      --top_k $top_k_cross \
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
    ${arg_dynamic_emb_extra_ft_baseline} \
    --fix_seeds \      
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
    --set_NIL_as_cand \
    ${arg_NIL_tag} \
    ${arg_NIL_desc} \
    ${arg_NIL_desc_tag} \
    ${arg_syn} \
    -top_k ${top_k_cross} \
    ${arg_lowercase} \
    --biencoder_bert_model ${bi_enc_bertmodel} \
    --biencoder_model_name ${biencoder_model_name} \
    --biencoder_model_size ${bi_enc_model_size} \
    --NIL_enc_mark "${NIL_enc_mark}" \
    --crossencoder_bert_model ${cross_enc_bertmodel} \
    --cross_model_setting ${crossencoder_model_name}${cross_enc_epoch_name} \
    --cross_model_size ${crossencoder_model_size} \
    -m ${NIL_enc_mark}_top${top_k_cross}${post_fix_cand}${further_model_mark}${further_result_mark}${joint_learning_mark} \
    ${arg_debug} \
    ${arg_get_cand}
fi