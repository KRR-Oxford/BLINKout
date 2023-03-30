#step1: get all files for an UMLS onto ver for medmentions dataset
#NILK wikidata
python get_all_wikidata_entities.py -f BLINK --add_synonyms --synonym_as_entity
python get_all_wikidata_entities.py -f BLINK --add_synonyms
python get_all_wikidata_entities.py -f BLINK
python get_all_wikidata_entities.py -f Sieve
python get_all_wikidata_entities.py -f Sieve --add_synonyms

#mm 2017AA 0.1
python get_all_UMLS_entities.py -d medmentions -f BLINK --add_synonyms --synonym_as_entity --onto_ver 2017AA --prune_entity_catalogue --pruning_ratio 0.1
python get_all_UMLS_entities.py -d medmentions -f BLINK --add_synonyms --onto_ver 2017AA --prune_entity_catalogue --pruning_ratio 0.1
python get_all_UMLS_entities.py -d medmentions -f BLINK --onto_ver 2017AA --prune_entity_catalogue --pruning_ratio 0.1
python get_all_UMLS_entities.py -d medmentions -f Sieve --onto_ver 2017AA --prune_entity_catalogue --pruning_ratio 0.1
python get_all_UMLS_entities.py -d medmentions -f Sieve --add_synonyms --onto_ver 2017AA --prune_entity_catalogue --pruning_ratio 0.1

#mm 2017AA 0.2
python get_all_UMLS_entities.py -d medmentions -f BLINK --add_synonyms --synonym_as_entity --onto_ver 2017AA --prune_entity_catalogue --pruning_ratio 0.2
python get_all_UMLS_entities.py -d medmentions -f BLINK --add_synonyms --onto_ver 2017AA --prune_entity_catalogue --pruning_ratio 0.2
python get_all_UMLS_entities.py -d medmentions -f BLINK --onto_ver 2017AA --prune_entity_catalogue --pruning_ratio 0.2
python get_all_UMLS_entities.py -d medmentions -f Sieve --onto_ver 2017AA --prune_entity_catalogue --pruning_ratio 0.2
python get_all_UMLS_entities.py -d medmentions -f Sieve --add_synonyms --onto_ver 2017AA --prune_entity_catalogue --pruning_ratio 0.2

#mm 2014AB
python get_all_UMLS_entities.py -d medmentions -f BLINK --add_synonyms --synonym_as_entity --onto_ver 2014AB
python get_all_UMLS_entities.py -d medmentions -f BLINK --add_synonyms --onto_ver 2014AB
python get_all_UMLS_entities.py -d medmentions -f BLINK --onto_ver 2014AB
python get_all_UMLS_entities.py -d medmentions -f Sieve --onto_ver 2014AB
python get_all_UMLS_entities.py -d medmentions -f Sieve --add_synonyms --onto_ver 2014AB

#step2:generating medmention formatted data
python format_trans_NILK2blink.py --prune --keeping_ratio 0.001 > processing_log_NILK_prune_0.001.txt
python format_trans_medmentions2blink.py --onto_ver 2017AA_pruned0.1 --filter_by_STY --use_newer_ontology --data_setting full > processing_log_mm2017AA_pruned0.1.txt
python format_trans_medmentions2blink.py --onto_ver 2017AA_pruned0.2 --filter_by_STY --use_newer_ontology --data_setting full > processing_log_mm2017AA_pruned0.2.txt
python format_trans_medmentions2blink.py --onto_ver 2014AB --filter_by_STY --use_newer_ontology --data_setting full --filter_potential_NILs > processing_log_mm2014AB.txt
## with NIL filtered if appeared previously
python format_trans_medmentions2blink.py --onto_ver 2017AA_pruned0.1 --filter_by_STY --use_newer_ontology --new_NIL_mention_only_for_eval --data_setting full > processing_log_mm2017AA_pruned0.1_NIL_filtered.txt
python format_trans_medmentions2blink.py --onto_ver 2017AA_pruned0.2 --filter_by_STY --use_newer_ontology --new_NIL_mention_only_for_eval --data_setting full > processing_log_mm2017AA_pruned0.2_NIL_filtered.txt
python format_trans_medmentions2blink.py --onto_ver 2014AB --filter_by_STY --use_newer_ontology --new_NIL_mention_only_for_eval --data_setting full --filter_potential_NILs > processing_log_mm2014AB_NIL_filtered.txt
##add synonyms as entities
python format_trans_NILK2blink.py --add_synonyms_as_ents --prune --keeping_ratio 0.001 > processing_log_NILK_prune_0.001_syn_full.txt
python format_trans_medmentions2blink.py --onto_ver 2017AA_pruned0.1 --add_synonyms_as_ents --filter_by_STY --use_newer_ontology --data_setting full
python format_trans_medmentions2blink.py --onto_ver 2017AA_pruned0.2 --add_synonyms_as_ents --filter_by_STY --use_newer_ontology --data_setting full
python format_trans_medmentions2blink.py --onto_ver 2014AB --add_synonyms_as_ents --filter_by_STY --use_newer_ontology --data_setting full --filter_potential_NILs

## for Sieve
python format_trans_NILK2sieve.py --prune --keeping_ratio 0.001 > processing_log_NILK_Sieve_prune_0.001.txt
python format_trans_medmentions2sieve.py --onto_ver 2017AA_pruned0.1 --filter_by_STY --use_newer_ontology --data_setting full #> processing_log_2017AA_pruned0.1.txt
python format_trans_medmentions2sieve.py --onto_ver 2017AA_pruned0.2 --filter_by_STY --use_newer_ontology --data_setting full
python format_trans_medmentions2sieve.py --onto_ver 2014AB --filter_by_STY --use_newer_ontology --data_setting full --filter_potential_NILs
## with NIL filtered if appeared previously
python format_trans_medmentions2sieve.py --onto_ver 2017AA_pruned0.1 --filter_by_STY --use_newer_ontology --new_NIL_mention_only_for_eval --data_setting full #> processing_log_2017AA_pruned0.1_NIL_filtered.txt
python format_trans_medmentions2sieve.py --onto_ver 2017AA_pruned0.2 --filter_by_STY --use_newer_ontology --new_NIL_mention_only_for_eval --data_setting full
python format_trans_medmentions2sieve.py --onto_ver 2014AB --filter_by_STY --use_newer_ontology --new_NIL_mention_only_for_eval --data_setting full --filter_potential_NILs

# generating share/clef formatted data (_ori means original, w/o _ori means _NIL_filtered in mm)
python format_trans_share2blink.py > processing_log_share2clef_ori.txt
python format_trans_share2blink.py --new_NIL_mention_only_for_eval > processing_log_share2clef.txt
python format_trans_share2blink.py --add_synonyms_as_ents
python format_trans_share2blink.py --add_synonyms_as_ents --new_NIL_mention_only_for_eval
## for Sieve
python format_trans_share2sieve.py # need to adjust the boolean parameters of add_synonyms_as_ents and new_NIL_mention_only_for_eval in the program before running. 

# analysis synonyms stats in all data and onto (entity catalogues)
python check_syn_stats.py > syn_stats_log_all_data_and_onto.txt

# get zero-shot data split for the validation and test set (by removing the entities appeared in the training set)
python get_zero_shot_data.py