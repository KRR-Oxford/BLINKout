# function adapted from https://www.w3resource.com/python-exercises/list/python-data-type-list-exercise-32.php
def is_Sublist(s, l):
	sub_set = False
	if s == []:
		sub_set = True
	elif s == l:
		sub_set = True
	elif len(s) > len(l):
		sub_set = False
	else:
		for i in range(len(l)):
			if l[i] == s[0]:
				n = 1
				while (n < len(s)) and ((i+n) < len(l)) and (l[i+n] == s[n]):
					n += 1
				
				if n == len(s):
					sub_set = True
	return sub_set
    
# count the set diff between two lists, considering both directions if chosen the pair comparision, otherwise just count those in the first set but not in the second set; in all cases, clip the count to 0 if below 0.
def count_list_set_diff(list_a,list_b,pair_comparison=True):
    if pair_comparison:
        return max(0,len(set(list_a) - set(list_b))) + max(0,len(set(list_b) - set(list_a)))
    else:
        return max(0,len(set(list_a) - set(list_b)))

# form a set of features per mention of whether the mention has no, one, or several matching names in the entities through string matching (exact or fuzzy) (Rao, McNamee, and Dredze 2013; McNamee et al. 2009)
# we only consider the entities from the candidate list
# input: (i) list_mention_input, the list of sub-token ids in a mention (as formed in data_process.get_mention_representation())
#        (ii) list_2d_label_input, the list of label titles + descriptions (as formed in data_process.get_context_representation()), where each is a list of sub-token ids; this list can be either the full candidate list or the top-k candidate list after the candidate generation stage
def get_is_men_str_matchable_features(list_mention_input,list_2d_label_input,fuzzy_tolerance=2):
    print("mention_input:",len(list_mention_input),list_mention_input)
    print("label_input:",len(list_2d_label_input),len(list_2d_label_input[0]))

    #for mention_sub_token_list in list_2d_mention_input:
    # clean mention input
    mention_sub_token_list = [sub_token_id for sub_token_id in list_mention_input if sub_token_id >= 3]
    mention_matched_exact = 0
    mention_matched_exact_w_desc = 0
    mention_matched_fuzzy = 0
    mention_matched_fuzzy_w_desc = 0
    for label_sub_token_list in list_2d_label_input:
        # clean label ids
        label_sub_token_list = label_sub_token_list[1:-1]
        # get the position of title mark 
        pos_title_mark = label_sub_token_list.index(3)
        # get title sub tokens as a list
        label_tit_sub_token_list = label_sub_token_list[:pos_title_mark]
        # get desc sub tokens as a list
        #label_desc_sub_token_list = label_sub_token_list[pos_title_mark+1:]
        
        # exact matching
        if mention_matched_exact < 2:
            if mention_sub_token_list == label_tit_sub_token_list:
                mention_matched_exact += 1

        if mention_matched_exact_w_desc < 2:
            if is_Sublist(mention_sub_token_list,label_sub_token_list):
                mention_matched_exact_w_desc += 1
        
        # fuzzy matching
        if mention_matched_fuzzy < 2:
            num_set_diff_men_tit = count_list_set_diff(mention_sub_token_list,label_tit_sub_token_list,pair_comparison=True)
            if num_set_diff_men_tit <= fuzzy_tolerance:
                mention_matched_fuzzy += 1

        if mention_matched_fuzzy_w_desc < 2:
            num_set_diff_men_tit_desc = count_list_set_diff(mention_sub_token_list,label_sub_token_list,pair_comparison=False)
            if num_set_diff_men_tit_desc <= fuzzy_tolerance:
                mention_matched_fuzzy_w_desc += 1
        
    mention_matchable_exact = mention_matched_exact > 0
    mention_matchable_exact_w_desc_one = mention_matched_exact_w_desc == 1
    mention_matchable_exact_w_desc_several = mention_matched_exact_w_desc > 1
    mention_matchable_fuzzy_one = mention_matched_fuzzy == 1
    mention_matchable_fuzzy_several = mention_matched_fuzzy > 1
    mention_matched_fuzzy_w_desc_one = mention_matched_fuzzy_w_desc == 1
    mention_matchable_fuzzy_w_desc_several = mention_matched_fuzzy_w_desc > 1

    is_men_str_matchable_features = [mention_matchable_exact,mention_matchable_exact_w_desc_one,mention_matchable_exact_w_desc_several,mention_matchable_fuzzy_one,mention_matchable_fuzzy_several,mention_matched_fuzzy_w_desc_one,mention_matchable_fuzzy_w_desc_several]

    print('is_men_str_matchable_features:',is_men_str_matchable_features)
    return get_is_men_str_matchable_features
    
list_mention_input = [0,123,345,677,1]
list_2d_label_input = [[123,345,677,688,3, 32,324,566],[321,123,124,677,688,3, 32,324,566],[123,345,3, 32,324,566],[666,677,678,3, 32,324,566]]

get_is_men_str_matchable_features(list_mention_input,list_2d_label_input,fuzzy_tolerance=2)