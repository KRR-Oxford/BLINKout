#get all files for an UMLS onto ver for medmentions dataset
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

#mm 2015AB
python get_all_UMLS_entities.py -d medmentions -f BLINK --add_synonyms --synonym_as_entity --onto_ver 2015AB
python get_all_UMLS_entities.py -d medmentions -f BLINK --add_synonyms --onto_ver 2015AB
python get_all_UMLS_entities.py -d medmentions -f BLINK --onto_ver 2015AB
python get_all_UMLS_entities.py -d medmentions -f Sieve --onto_ver 2015AB
python get_all_UMLS_entities.py -d medmentions -f Sieve --add_synonyms --onto_ver 2015AB

# generating medmention formatted data
python format_trans_medmentions2blink.py --onto_ver 2017AA_pruned0.1 --filter_by_STY --use_newer_ontology --data_setting full > processing_log_mm2017AA_pruned0.1.txt
python format_trans_medmentions2blink.py --onto_ver 2017AA_pruned0.2 --filter_by_STY --use_newer_ontology --data_setting full > processing_log_mm2017AA_pruned0.2.txt
python format_trans_medmentions2blink.py --onto_ver 2015AB --filter_by_STY --use_newer_ontology --data_setting full --filter_potential_NILs > processing_log_mm2015AB.txt
python format_trans_medmentions2blink.py --onto_ver 2014AB --filter_by_STY --use_newer_ontology --data_setting full --filter_potential_NILs > processing_log_mm2014AB.txt
## with NIL filtered if appeared previously
python format_trans_medmentions2blink.py --onto_ver 2017AA_pruned0.1 --filter_by_STY --use_newer_ontology --new_NIL_mention_only_for_eval --data_setting full > processing_log_mm2017AA_pruned0.1_NIL_filtered.txt
python format_trans_medmentions2blink.py --onto_ver 2017AA_pruned0.2 --filter_by_STY --use_newer_ontology --new_NIL_mention_only_for_eval --data_setting full > processing_log_mm2017AA_pruned0.2_NIL_filtered.txt
python format_trans_medmentions2blink.py --onto_ver 2015AB --filter_by_STY --use_newer_ontology --new_NIL_mention_only_for_eval --data_setting full --filter_potential_NILs > processing_log_mm2015AB_NIL_filtered.txt
python format_trans_medmentions2blink.py --onto_ver 2014AB --filter_by_STY --use_newer_ontology --new_NIL_mention_only_for_eval --data_setting full --filter_potential_NILs > processing_log_mm2014AB_NIL_filtered.txt
##add synonyms as entities
python format_trans_medmentions2blink.py --onto_ver 2017AA_pruned0.1 --add_synonyms --filter_by_STY --use_newer_ontology --data_setting full
python format_trans_medmentions2blink.py --onto_ver 2017AA_pruned0.2 --add_synonyms --filter_by_STY --use_newer_ontology --data_setting full
python format_trans_medmentions2blink.py --onto_ver 2015AB --add_synonyms --filter_by_STY --use_newer_ontology --data_setting full --filter_potential_NILs
python format_trans_medmentions2blink.py --onto_ver 2014AB --add_synonyms --filter_by_STY --use_newer_ontology --data_setting full --filter_potential_NILs

## for Sieve
python format_trans_medmentions2sieve.py --onto_ver 2017AA_pruned0.1 --filter_by_STY --use_newer_ontology --data_setting full #> processing_log_2017AA_pruned0.1.txt
python format_trans_medmentions2sieve.py --onto_ver 2017AA_pruned0.2 --filter_by_STY --use_newer_ontology --data_setting full
python format_trans_medmentions2sieve.py --onto_ver 2015AB --filter_by_STY --use_newer_ontology --data_setting full --filter_potential_NILs
python format_trans_medmentions2sieve.py --onto_ver 2014AB --filter_by_STY --use_newer_ontology --data_setting full --filter_potential_NILs
## with NIL filtered if appeared previously
python format_trans_medmentions2sieve.py --onto_ver 2017AA_pruned0.1 --filter_by_STY --use_newer_ontology --new_NIL_mention_only_for_eval --data_setting full #> processing_log_2017AA_pruned0.1_NIL_filtered.txt
python format_trans_medmentions2sieve.py --onto_ver 2017AA_pruned0.2 --filter_by_STY --use_newer_ontology --new_NIL_mention_only_for_eval --data_setting full
python format_trans_medmentions2sieve.py --onto_ver 2015AB --filter_by_STY --use_newer_ontology --new_NIL_mention_only_for_eval --data_setting full --filter_potential_NILs
python format_trans_medmentions2sieve.py --onto_ver 2014AB --filter_by_STY --use_newer_ontology --new_NIL_mention_only_for_eval --data_setting full --filter_potential_NILs

# generating share/clef formatted data (_ori means original, w/o _ori means _NIL_filtered in mm)
python format_trans_share2blink.py > processing_log_share2clef_ori.txt
python format_trans_share2blink.py --new_NIL_mention_only_for_eval > processing_log_share2clef.txt
python format_trans_share2blink.py --add_synonyms_as_ents
python format_trans_share2blink.py --add_synonyms_as_ents --new_NIL_mention_only_for_eval
## for Sieve
python format_trans_share2sieve.py # need to adjust the boolean parameters of add_synonyms_as_ents and new_NIL_mention_only_for_eval in the program before running. 
