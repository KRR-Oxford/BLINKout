from sklearn.svm import LinearSVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_classification
from sklearn.pipeline import Pipeline
from sklearn import preprocessing
from sklearn.datasets import make_hastie_10_2
from sklearn.ensemble import GradientBoostingClassifier
import json
import DataPre
import os
import numpy as np
from scipy.spatial.distance import hamming
# full_trng_for_inference_2017AA_pruned0.1_vs_2017AAfiltered.jsonl"
def get_coefs(word, *arr): return word, np.asarray(arr, dtype='float32')
def TestData_Gen2(train_men2can_file,text,kbfull):
    count=0
    embeddings_index = dict(
        get_coefs(*o.strip().split(" ")) for o in open("crawl-300d-2M.vec", encoding='utf8') if len(o) > 100)
    mentionList, mentionLabel = MentionList_Gen(text)
    title2ID, ID2title= KBEntityList_Gen(kbfull)
    mentionFre = MentionFre_Gen(text)
    mentionContext = MentionContext_Gen(text)
    mention2candidate={}
    testKeyList=[]
    KeyList=[]
    AllmenFeaturelists=[]
    menCanEmpty=0
    trainLabel=[]
    with open(train_men2can_file, "r",encoding='Utf-8-sig') as fin:
        lines = fin.readlines()
        for line in lines:
            count+=1
            menFeaturelist=[]
            candidate_list=line.strip().split("\t")
            # print(candidate_list)
            # # candidate_list[1]: row number
            # print(candidate_list[0])
            # print(candidate_list[1])
            if len(candidate_list)>1:
                mention2candidate[candidate_list[0]+"\t"+candidate_list[1]]=set()
                KeyList.append(candidate_list[0] + "\t" + candidate_list[1])
                list1=[]
                list2=[]
                list3 = []
                list4 = []
                list5 = []
                list6 = []
                list7 = []
                mention_list=candidate_list[0].split(" ")

                if len(candidate_list)==2:
                    menCanEmpty+=1
                    continue
                if candidate_list[0] + "\t" + candidate_list[1] in mentionLabel.keys():
                    testKeyList.append(candidate_list[0]+"\t"+candidate_list[1])
                    canScore_list = []
                    contextEmbedding = np.random.randn(300)
                    entityCount = 0
                    for entityName in title2ID.keys():
                        if entityName in mentionContext[candidate_list[0]]:
                            entityCount += 1
                            noun1_vec = np.zeros(300, np.float32)
                            temp_str1 = entityName.strip().split(" ")
                            if entityName in embeddings_index.keys():
                                noun1_vec = embeddings_index[entityName]
                            else:
                                for str in temp_str1:
                                    if str in embeddings_index.keys():
                                        noun1_vec += embeddings_index[str]
                                    else:
                                        noun1_vec += np.random.randn(300)
                                noun1_vec = noun1_vec * (1.0 / len(temp_str1))
                            contextEmbedding += noun1_vec
                    if entityCount != 0:
                        contextEmbedding = contextEmbedding * (1.0 / entityCount)
                    if count%2==0:
                        trainLabel.append(mentionLabel[candidate_list[0] + "\t" + candidate_list[1]])
                    else:
                        trainLabel.append(mentionLabel[candidate_list[0] + "\t" + candidate_list[1]])
                    for i in range(2,len(candidate_list)):
                        sub_candidate_list = candidate_list[i].split(" ")
                        # print(sub_candidate_temp,sub_candidate_list)
                        # print(mention_list,sub_candidate_list)
                        canScore_list.append(
                            fastText_sim((candidate_list[0]), candidate_list[i], embeddings_index))
                        score_list=DataPre.get_is_men_str_matchable_features_SVM(mention_list,sub_candidate_list,2)
                        # print(score_list[0])
                        # print(score_list[1])
                        list1.append(score_list[0])
                        list2.append(score_list[1])
                        list3.append(score_list[2])
                        list4.append(score_list[3])
                        list5.append(score_list[4])
                        list6.append(score_list[5])
                        list7.append(score_list[6])
                    list1.sort(reverse=True)
                    list2.sort(reverse=True)
                    list3.sort(reverse=True)
                    list4.sort(reverse=True)
                    list5.sort(reverse=True)
                    list6.sort(reverse=True)
                    list7.sort(reverse=True)
                    sum=0
                    for score in list1:
                        sum+=score
                    avg1=sum*1.0/len(list1)
                    sum = 0
                    for score in list2:
                        sum+=score
                    avg2=sum*1.0/len(list2)
                    sum = 0
                    for score in list3:
                        sum+=score
                    avg3=sum*1.0/len(list3)
                    sum = 0
                    for score in list4:
                        sum+=score
                    avg4=sum*1.0/len(list4)
                    sum = 0
                    for score in list5:
                        sum+=score
                    avg5=sum*1.0/len(list5)
                    sum = 0
                    for score in list6:
                        sum+=score
                    avg6=sum*1.0/len(list6)
                    sum = 0
                    for score in list7:
                        sum+=score
                    avg7=sum*1.0/len(list7)
                    menFeaturelist.append(list1[0])
                    menFeaturelist.append(list2[0])
                    menFeaturelist.append(list3[0])
                    menFeaturelist.append(list4[0])
                    menFeaturelist.append(list5[0])
                    menFeaturelist.append(list6[0])
                    menFeaturelist.append(list7[0])
                    menFeaturelist.append(avg1)
                    menFeaturelist.append(avg2)
                    menFeaturelist.append(avg3)
                    menFeaturelist.append(avg4)
                    menFeaturelist.append(avg5)
                    menFeaturelist.append(avg6)
                    menFeaturelist.append(avg7)
                    menFeaturelist.append(list1[0]-avg1)
                    menFeaturelist.append(list2[0]-avg2)
                    menFeaturelist.append(list3[0]-avg3)
                    menFeaturelist.append(list4[0]-avg4)
                    menFeaturelist.append(list5[0]-avg5)
                    menFeaturelist.append(list6[0]-avg6)
                    menFeaturelist.append(list7[0]-avg7)
                    # menFeaturelist.append(mentionFre[candidate_list[0]])
                    canScore_list.sort(reverse=True)
                    menFeaturelist.append(canScore_list[0])
                    for embeddingScore in contextEmbedding:
                        menFeaturelist.append(embeddingScore)
                    AllmenFeaturelists.append(menFeaturelist)
            else:
                print("----error---")
    # print("the number of mentions (candidate list is not empty) "+str(len(AllmenFeaturelists)))
    # print("the number of mentions (candidate list is empty) "+str(menCanEmpty))
    # print(AllmenFeaturelists)
    # print(trainLabel)

    return AllmenFeaturelists,KeyList,testKeyList
    # print (mention2candidate)

def TrainingData_Gen(train_men2can_file,text,kbfull):
    count=0
    embeddings_index = dict(
        get_coefs(*o.strip().split(" ")) for o in open("crawl-300d-2M.vec", encoding='utf8') if len(o) > 100)
    mentionList, mentionLabel = MentionList_Gen(text)
    title2ID, ID2title= KBEntityList_Gen(kbfull)
    mentionFre=MentionFre_Gen(text)
    mentionContext=MentionContext_Gen(text)
    mention2candidate={}
    AllmenFeaturelists=[]
    menCanEmpty=0
    trainLabel=[]
    entityCountZero=0
    with open(train_men2can_file, "r",encoding='Utf-8-sig') as fin:
        lines = fin.readlines()
        for line in lines:
            count+=1
            menFeaturelist=[]
            candidate_list=line.strip().split("\t")
            # print(candidate_list)
            # # candidate_list[1]: row number
            # print(candidate_list[0])
            # print(candidate_list[1])
            if len(candidate_list)>1:
                mention2candidate[candidate_list[0]+"\t"+candidate_list[1]]=set()
                list1=[]
                list2=[]
                list3 = []
                list4 = []
                list5 = []
                list6 = []
                list7 = []
                mention_list=candidate_list[0].split(" ")
                if len(candidate_list)==2:
                    menCanEmpty+=1
                    continue
                if candidate_list[0] + "\t" + candidate_list[1] in mentionLabel.keys():
                    canScore_list = []
                    contextEmbedding=np.random.randn(300)
                    entityCount=0
                    for entityName in title2ID.keys():
                        if entityName in mentionContext[candidate_list[0]]:
                            entityCount+=1
                            noun1_vec = np.zeros(300, np.float32)
                            temp_str1 = entityName.strip().split(" ")
                            if entityName in embeddings_index.keys():
                                noun1_vec = embeddings_index[entityName]
                            else:
                                for str in temp_str1:
                                    if str in embeddings_index.keys():
                                        noun1_vec += embeddings_index[str]
                                    else:
                                        noun1_vec += np.random.randn(300)
                                noun1_vec = noun1_vec * (1.0 / len(temp_str1))
                            contextEmbedding+=noun1_vec
                    if entityCount!=0:
                        entityCountZero+=1
                        contextEmbedding = contextEmbedding * (1.0 / entityCount)
                    if count%2==0:
                        trainLabel.append(mentionLabel[candidate_list[0] + "\t" + candidate_list[1]])
                    else:
                        trainLabel.append(mentionLabel[candidate_list[0] + "\t" + candidate_list[1]])
                    for i in range(2,len(candidate_list)):
                        sub_candidate_list = candidate_list[i].split(" ")
                        # print(sub_candidate_temp,sub_candidate_list)
                        # print(mention_list,sub_candidate_list)
                        canScore_list.append(fastText_sim((candidate_list[0]), candidate_list[i], embeddings_index))
                        score_list=DataPre.get_is_men_str_matchable_features_SVM(mention_list,sub_candidate_list,2)
                        # print(score_list[0])
                        # print(score_list[1])
                        list1.append(score_list[0])
                        list2.append(score_list[1])
                        list3.append(score_list[2])
                        list4.append(score_list[3])
                        list5.append(score_list[4])
                        list6.append(score_list[5])
                        list7.append(score_list[6])
                    list1.sort(reverse=True)
                    list2.sort(reverse=True)
                    list3.sort(reverse=True)
                    list4.sort(reverse=True)
                    list5.sort(reverse=True)
                    list6.sort(reverse=True)
                    list7.sort(reverse=True)
                    sum=0
                    for score in list1:
                        sum+=score
                    avg1=sum*1.0/len(list1)
                    sum = 0
                    for score in list2:
                        sum+=score
                    avg2=sum*1.0/len(list2)
                    sum = 0
                    for score in list3:
                        sum+=score
                    avg3=sum*1.0/len(list3)
                    sum = 0
                    for score in list4:
                        sum+=score
                    avg4=sum*1.0/len(list4)
                    sum = 0
                    for score in list5:
                        sum+=score
                    avg5=sum*1.0/len(list5)
                    sum = 0
                    for score in list6:
                        sum+=score
                    avg6=sum*1.0/len(list6)
                    sum = 0
                    for score in list7:
                        sum+=score
                    avg7=sum*1.0/len(list7)
                    menFeaturelist.append(list1[0])
                    menFeaturelist.append(list2[0])
                    menFeaturelist.append(list3[0])
                    menFeaturelist.append(list4[0])
                    menFeaturelist.append(list5[0])
                    menFeaturelist.append(list6[0])
                    menFeaturelist.append(list7[0])
                    menFeaturelist.append(avg1)
                    menFeaturelist.append(avg2)
                    menFeaturelist.append(avg3)
                    menFeaturelist.append(avg4)
                    menFeaturelist.append(avg5)
                    menFeaturelist.append(avg6)
                    menFeaturelist.append(avg7)
                    menFeaturelist.append(list1[0]-avg1)
                    menFeaturelist.append(list2[0]-avg2)
                    menFeaturelist.append(list3[0]-avg3)
                    menFeaturelist.append(list4[0]-avg4)
                    menFeaturelist.append(list5[0]-avg5)
                    menFeaturelist.append(list6[0]-avg6)
                    menFeaturelist.append(list7[0]-avg7)
                    # menFeaturelist.append(mentionFre[candidate_list[0]])
                    canScore_list.sort(reverse=True)
                    menFeaturelist.append(canScore_list[0])
                    for embeddingScore in contextEmbedding:
                        menFeaturelist.append(embeddingScore)
                    AllmenFeaturelists.append(menFeaturelist)
    # 21/517
    # 22/455
    # print("the number of mentions (candidate list is not empty) "+str(len(AllmenFeaturelists)))
    # print("the number of mentions (candidate list is empty) "+str(menCanEmpty))

    # print(AllmenFeaturelists)
    # print(trainLabel)
    # print(entityCountZero)
    return AllmenFeaturelists, trainLabel
    # print (mention2candidate)

def TestData_Gen(train_men2can_file,text,kbfull,kbattr):
    mentionList, mentionLabel = MentionList_Gen(text)
    title2ID, ID2title,entity2entity = KBEntityList_Gen(kbfull,kbattr)
    mention2candidate={}
    AllmenFeaturelists=[]
    menCanEmpty=0
    trainLabel=[]
    with open(train_men2can_file, "r",encoding='Utf-8-sig') as fin:
        lines = fin.readlines()
        for line in lines:
            menFeaturelist=[]
            candidate_list=line.strip().split("\t")
            # candidate_list[1]: row number
            mention2candidate[candidate_list[0]+"\t"+candidate_list[1]]=set()
            list1=[]
            list2=[]
            list3 = []
            list4 = []
            list5 = []
            list6 = []
            list7 = []
            mention_list=[]
            sub_mention_temp=candidate_list[0].split(" ")
            for i in range(len(sub_mention_temp)):
                mention_list.append(sub_mention_temp[i])
            if len(candidate_list)==2:
                menCanEmpty+=1
                continue
            trainLabel.append(mentionLabel[candidate_list[0] + "\t" + candidate_list[1]])
            for i in range(2,len(candidate_list)):
                sub_candidate_list=[]
                sub_candidate_temp = ID2title[candidate_list[i]].split(" ")
                for j in range(len(sub_candidate_temp)):
                    sub_candidate_list.append(sub_candidate_temp[j])
                # print(mention_list,sub_candidate_list)
                score_list=DataPre.get_is_men_str_matchable_features_SVM(mention_list,sub_candidate_list,2)

                # print(score_list[0])
                # print(score_list[1])
                list1.append(score_list[0])
                list2.append(score_list[1])
                list3.append(score_list[2])
                list4.append(score_list[3])
                list5.append(score_list[4])
                list6.append(score_list[5])
                list7.append(score_list[6])
            list1.sort(reverse=True)
            list2.sort(reverse=True)
            list3.sort(reverse=True)
            list4.sort(reverse=True)
            list5.sort(reverse=True)
            list6.sort(reverse=True)
            list7.sort(reverse=True)
            sum=0
            for score in list1:
                sum+=score
            avg1=sum*1.0/len(list1)
            sum = 0
            for score in list2:
                sum+=score
            avg2=sum*1.0/len(list2)
            sum = 0
            for score in list3:
                sum+=score
            avg3=sum*1.0/len(list3)
            sum = 0
            for score in list4:
                sum+=score
            avg4=sum*1.0/len(list4)
            sum = 0
            for score in list5:
                sum+=score
            avg5=sum*1.0/len(list5)
            sum = 0
            for score in list6:
                sum+=score
            avg6=sum*1.0/len(list6)
            sum = 0
            for score in list7:
                sum+=score
            avg7=sum*1.0/len(list7)
            menFeaturelist.append(list1[0])
            menFeaturelist.append(list2[0])
            menFeaturelist.append(list3[0])
            menFeaturelist.append(list4[0])
            menFeaturelist.append(list5[0])
            menFeaturelist.append(list6[0])
            menFeaturelist.append(list7[0])
            menFeaturelist.append(avg1)
            menFeaturelist.append(avg2)
            menFeaturelist.append(avg3)
            menFeaturelist.append(avg4)
            menFeaturelist.append(avg5)
            menFeaturelist.append(avg6)
            menFeaturelist.append(avg7)
            menFeaturelist.append(list1[0]-avg1)
            menFeaturelist.append(list2[0]-avg2)
            menFeaturelist.append(list3[0]-avg3)
            menFeaturelist.append(list4[0]-avg4)
            menFeaturelist.append(list5[0]-avg5)
            menFeaturelist.append(list6[0]-avg6)
            menFeaturelist.append(list7[0]-avg7)
            AllmenFeaturelists.append(menFeaturelist)

    print("the number of mentions (candidate list is not empty) "+str(len(AllmenFeaturelists)))
    print("the number of mentions (candidate list is empty) "+str(menCanEmpty))
    # print(AllmenFeaturelists)
    # print(trainLabel)
    return AllmenFeaturelists, trainLabel
    # print (mention2candidate)

def MentionFre_Gen(filename):
    mentionFreDict={}
    mentionFreDictOut={}
    with open(filename, "r",encoding='Utf-8-sig') as fin:
        lines = fin.readlines()
        for line in lines:
            record = json.loads(line)
            if record['mention'] in mentionFreDict.keys():
                mentionFreDict[record['mention']]+=1
            else:
                mentionFreDict[record['mention']] =1
    sum=0
    for key in mentionFreDict.keys():
        sum+=mentionFreDict[key]
    for key in mentionFreDict.keys():
        mentionFreDictOut[key]=mentionFreDict[key]/sum*1.0
    return mentionFreDictOut

def MentionContext_Gen(filename):
    mentionContext={}
    with open(filename, "r",encoding='Utf-8-sig') as fin:
        lines = fin.readlines()
        for line in lines:
            record = json.loads(line)
            mentionContext[record['mention']]=record['context_left']+" "+record['context_right']
    return mentionContext


def MentionList_Gen(filename):
    mentionLabel={}
    mentionList=[]
    row_id=0
    with open(filename, "r",encoding='Utf-8-sig') as fin:
        lines = fin.readlines()
        for line in lines:
            row_id += 1
            record = json.loads(line)
            mentionList.append(record['mention']+"\t"+str(row_id))
            if record['label_concept']=="CUI-less":
                mentionLabel[record['mention']+"\t"+str(row_id)]=1
                # print("----------")
            else:
                mentionLabel[record['mention']+"\t"+str(row_id)] = 0
    return mentionList,mentionLabel
def KBEntityList_Gen(filename1):
    title2ID={}
    ID2title={}
    entity2entity={}
    with open(filename1, "r",encoding='Utf-8-sig') as fin:
        lines = fin.readlines()
        for line in lines:
            record = json.loads(line)
            title2ID[record['title']]=record['idx'] #Unique title
    with open(filename1, "r", encoding='Utf-8-sig') as fin:
        lines = fin.readlines()
        for line in lines:
            record = json.loads(line)
            ID2title[record['idx']] = record['title']
    # with open(filename2, "r",encoding='Utf-8-sig') as fin:
    #     lines = fin.readlines()
    #     for line in lines:
    #         record = json.loads(line)
    #         entity2entity[record['idx']]=record['synonyms']
    return title2ID, ID2title

def Mention_Candidate_Gen_ForTrain(filename,kbfull,text):
    mention2candidate={}
    title2ID,ID2title=KBEntityList_Gen(kbfull)
    mentionList,mentionLabel=MentionList_Gen(text)
    # initialization
    for mention in mentionList:
        candidateList=set()
        mention2candidate[mention]=candidateList
    # ---------------------------------------------------------------------
    count_exact_match=0
    # Titles that are exact matches for the mention
    for mention in mentionList:
        mentionString=mention.strip().split("\t")[0]
        if mentionString in title2ID.keys():
            mention2candidate[mention].add(mentionString)
            # print(mention +"\t"+title2ID[mention])
            # count_exact_match+=1
    # print(count_exact_match)

    # Titles that are wholly contained in or contain the mention (e.g., Nationwide and Nationwide Insurance)
    count_contain_match = 0
    for mention in mention2candidate.keys():
        mentionString = mention.strip().split("\t")[0]
        for title in title2ID.keys():
            if mentionString in title or title in mentionString:
                mention2candidate[mention].add(title)
                count_contain_match+=1
    # print (count_contain_match)
    # print(mention2candidate)

    count_fistLetters_match=0
    #The first letters of the entity mention match the KB entry title (e.g., OA and Olympic Airlines).
    for mention in mention2candidate.keys():
        mentionString = mention.strip().split("\t")[0]
        for title in title2ID.keys():
            if stringFirstLettersGen(mentionString)== stringFirstLettersGen(title):
                mention2candidate[mention].add(title)
                count_fistLetters_match+=1
    print(count_fistLetters_match)

#The title has a strong string similarity score with the entity mention.
# We include several measures of string similarity, including: character Dice score> 0.9, skip bigram Dice score > 0.6, and Hamming distance <= 2
#     count_hamming_match=0
#     for mention in mention2candidate.keys():
#         mentionString = mention.strip().split("\t")[0]
#         for title in title2ID.keys():
#             if hamming(mentionString, title) * len(mentionString)<=2:
#                 mention2candidate[mention].add(title2ID[title])
#                 count_hamming_match+=1
#     mention2candidateExp={}
#     for mention in mention2candidate.keys():
#         temp_set=set()
#         mention2candidateExp[mention]=set()
#         for synEntityID in mention2candidate[mention]:
#             synEntityList=entity2entity[synEntityID]
#             for aSynEntity in synEntityList.strip().split("|"):
#                 if aSynEntity in title2ID.keys():
#                     temp_set.add(title2ID[aSynEntity])
#             for aSynEntity in temp_set:
#                 mention2candidateExp[mention].add(aSynEntity)
#             # temp_set.add(entity2entity[synEntityID])
#     mention2candidateCom={}
#     for mention in mention2candidate.keys():
#         mention2candidateCom[mention]=mention2candidateExp[mention]|mention2candidate[mention]

    with open(filename,'w',encoding='Utf-8-sig') as f:
        for mention in mention2candidate.keys():
            temp_string = mention.strip()
            for candidate_id in mention2candidate[mention]:
                temp_string+="\t"+ str(candidate_id)
            f.write(temp_string+"\n")


# The first letters of the entity mention
def stringFirstLettersGen(mention):
    # print(mention)
    temp=mention.split(" ")
    outputString=""
    for i in temp:
        # print(i[0])
        # print(i)
        # print(i[0])
        if i !="":
            outputString+=i[0]
    # outstring
    # print(len(temp))
    # print(outputString)
    return outputString

def SVMlinear_sample_test():
    X, y = make_classification(n_features=4, random_state=0)
    clf = make_pipeline(StandardScaler(), LinearSVC(random_state=0, tol=1e-5))
    clf.fit(X, y)
    print(X)
    print(y)
    Pipeline(steps=[('standardscaler', StandardScaler()),
                    ('linearsvc', LinearSVC(random_state=0, tol=1e-04))])

    print(clf.named_steps['linearsvc'].coef_)
    print(clf.named_steps['linearsvc'].intercept_)
    print(clf.predict([[-1.13058206e+00,-2.02959251e-02,-7.10233633e-01,-1.44099108e+00],[0, 0.2, 0.2, 0.5],[0.4, 0.5, 0.4, 0],[0, 1, 0, 0],[1, 0, 0, 0]]))

# SVMlinear_sample_test()
# read_json_file("full_trng_2017AA_pruned0.1_vs_2017AAfiltered.jsonl")
# Mention_Candidate_Gen()
def trainAndTest(train_men2can_file,textTrain,kbfull,textTest):
    # train_men2can_file="mention2candidate.text"
    # # textTrain="trng.jsonl"
    # textTrain="sample-trng.jsonl"
    # kb = "UMLS2017AA_pruned0.1_with_NIL.jsonl"
    # # textTest = "full_test_for_inference_2017AA_pruned0.1_vs_2017AAfiltered.jsonl"
    # textTest="test.jsonl"
    # textTest=textTrain
    # textTrain=textTest
    # textTrain = "train_for_inference.jsonl"
    # kb = "UMLS2012AB_with_NIL.jsonl"
    # textTest = "test_for_inference.jsonl"
    # ---------generate train_men2can_file------------
    Mention_Candidate_Gen_ForTrain(train_men2can_file,kbfull,textTrain)
    # ------------------------------------------------
    AllmenFeaturelists, trainLabel = TrainingData_Gen(train_men2can_file,textTrain,kbfull)
    # ---------------svm ----------------------------------------------
    # clf = make_pipeline(StandardScaler(), LinearSVC(penalty='l2', loss='squared_hinge', dual=True, tol=1e-4,
    #          C=0.00001, multi_class='ovr', fit_intercept=True,
    #          intercept_scaling=1, class_weight=None, verbose=0,
    #          random_state=None, max_iter=1000))
    # clf.fit(preprocessing.MinMaxScaler().fit_transform(np.array(AllmenFeaturelists)), trainLabel)
    # -------------------------------------------------------------------------
    # --------------random tree-----------------------------------------
    clf = GradientBoostingClassifier(n_estimators=150, learning_rate=1.0,
                                     max_depth=15, random_state=0)
    clf.fit(preprocessing.MinMaxScaler().fit_transform(np.array(AllmenFeaturelists)), trainLabel)
    # ------------------------------------------------------------------
    test_men2can_file = "mention2candidateTest.text"
    Mention_Candidate_Gen_ForTrain(test_men2can_file, kbfull, textTest)
    AllmenFeaturelists,KeyList,testKeyList = TestData_Gen2(test_men2can_file,textTest,kbfull)
    predictFile="prediction.txt"
    with open(predictFile, 'w',encoding='Utf-8-sig') as fout:
        predictLabels=clf.predict(preprocessing.MinMaxScaler().fit_transform(np.array(AllmenFeaturelists)))
        for i in range(0,len(KeyList)):
            if KeyList[i] in testKeyList:
                fout.write(str(KeyList[i]) + "\t"+str(predictLabels[testKeyList.index(KeyList[i])])+"\n")
            else:
                fout.write(str(KeyList[i]) + "\t"+"null"+"\n")
            # for predictLable in clf.predict(preprocessing.MinMaxScaler().fit_transform(np.array(AllmenFeaturelists))):

def testReturn():
    list1=[1,2]
    list2=[3,4]
    dict=[[3,4],[5,9]]
    return list1,list2,dict
def SampleData():
    textTrain = "train.jsonl"
    sampleTextTrain="sample-trng.jsonl"
    output=[]
    row_id = 0
    countneg=0
    with open(textTrain, "r", encoding='Utf-8-sig') as fin:
        lines = fin.readlines()
        for line in lines:
            record = json.loads(line)
            # if row_id > 500:
            #     break
            if record['label_concept'] == "CUI-less":
                output.append(line)
                row_id += 1
            else:
                if countneg>1600:
                    continue
                countneg+=1
                output.append(line)
    with open(sampleTextTrain, 'w') as fout:
        for i in output:
            fout.write(i)

def top1Gen(kbfull):
    embeddings_index = dict(
        get_coefs(*o.strip().split(" ")) for o in open("crawl-300d-2M.vec", encoding='utf8') if len(o) > 100)
    title2ID, ID2title= KBEntityList_Gen(kbfull)
    men2entity={}
    test_men2can_file = "mention2candidateTest.text"
    with open(test_men2can_file, "r", encoding='Utf-8-sig') as fin:
        lines = fin.readlines()
        for line in lines:
            temp = line.strip().split("\t")
            if len(temp) <2:
                continue
            if len(temp)==2:
                continue
            else:
                scoreDict={}
                numberCanEntity=len(temp)-2
                mention=temp[0]
                for i in range(numberCanEntity):
                    canEntity=temp[2+i]
                    scoreDict[canEntity]=fastText_sim(mention, canEntity, embeddings_index)
                list=sorted(scoreDict.items(), key=lambda d:d[1], reverse = True)
                men2entity[temp[0]+"\t"+temp[1]]=title2ID[list[0][0]]
    return men2entity

def evaluate(kbfull):
    men2entity=top1Gen(kbfull)
    countPreone=0
    countPrezero=0
    noCan=0
    predictionFile="prediction.txt"
    predictLabel=[]
    trueLabel=[]
    testFile="test.jsonl"
    with open(predictionFile, "r", encoding='Utf-8-sig') as fin:
        lines = fin.readlines()
        for line in lines:
            temp=line.strip().split("\t")
            if temp[2]=="null":
                predictLabel.append(1)
                countPreone += 1
            else:
                if temp[2] =="1":
                    countPreone+=1
                    predictLabel.append(1)
                else:
                    countPrezero+=1
                    predictLabel.append(men2entity[temp[0]+"\t"+temp[1]])
    menCount=0
    newEntity=0
    oldEntity=0
    with open(testFile, "r", encoding='Utf-8-sig') as fin:
        lines = fin.readlines()
        for line in lines:
            record = json.loads(line)
            menCount+=1
            if record['label_concept'] == "CUI-less":
                trueLabel.append(1)
                newEntity+=1
            else:
                trueLabel.append(record['label_concept'])
                oldEntity+=1
    countP=0
    countN=0
    for i in range(0,len(predictLabel)):
        if predictLabel[i]==1:
            if trueLabel[i]==1:
                countP += 1
        else:
            if predictLabel[i] == trueLabel[i]:
                countN += 1

        # if predictLabel[i]==trueLabel[i]==1:
        #     # print(str(i)+"\n")
        #     countP+=1
        # if predictLabel[i] == trueLabel[i] == 0:
        #     countN+=1
    outKBRecall=countP*1.0/newEntity
    outKBPre=countP*1.0/countPreone
    inKBRecall = countN * 1.0 / oldEntity
    inKBPre = countN * 1.0 / countPrezero
    overall=(countP+countN)*1.0/menCount
    print("----model prediction results-----")
    print("number of novel entity : "+str(countPreone)+" true is : "+str(countP))
    print("out of KB recall : "+str(outKBRecall))
    print("out of KB pre : " + str(outKBPre))
    print("out of KB f1 : "+str(2*outKBRecall*outKBPre/(outKBRecall+outKBPre)))
    print("number of not novel entity : " + str(countPrezero) + " true is : " + str(countN))
    print("in KB recall : "+str(inKBRecall))
    print("in KB pre : " + str(inKBPre))
    print("in KB f1 : "+str(2*inKBRecall*inKBPre/(inKBRecall+inKBPre)))
    print("overall score: "+str(overall))

def evaluateNoCan(kbfull):
    men2entity = top1Gen(kbfull)
    countPreone=0
    countPrezero=0
    noCan=0
    predictionFile="prediction.txt"
    predictLabel=[]
    trueLabel=[]
    testFile="test.jsonl"
    with open(predictionFile, "r", encoding='Utf-8-sig') as fin:
        lines = fin.readlines()
        for line in lines:
            temp=line.strip().split("\t")
            if temp[2]=="null":
                predictLabel.append(1)
                countPreone += 1
            else:
                countPrezero+=1
                predictLabel.append(men2entity[temp[0] + "\t" + temp[1]])
    menCount=0
    newEnCount=0
    oldEnCount=0
    with open(testFile, "r", encoding='Utf-8-sig') as fin:
        lines = fin.readlines()
        for line in lines:
            record = json.loads(line)
            menCount+=1
            if record['label_concept'] == "CUI-less":
                trueLabel.append(1)
                newEnCount+=1
            else:
                trueLabel.append(record['label_concept'])
                oldEnCount+=1
    countP=0
    countN=0
    for i in range(0, len(predictLabel)):
        if predictLabel[i] == 1:
            if trueLabel[i] == 1:
                countP += 1
        else:
            if predictLabel[i] == trueLabel[i]:
                countN += 1
    outKBrecall=countP*1.0/newEnCount
    outKBpre=countP * 1.0 / countPreone
    overall=(countN+countP)*1.0/menCount
    print("-----mention no candidate is regarded as a new entity-----")
    print("number of novel entity : "+str(countPreone)+" ||true is : "+str(countP))
    print("out of KB recall : "+str(outKBrecall))
    print("out of KB pre : " + str(outKBpre))
    print("out of KB f1 : "+str(2*outKBrecall*outKBpre/(outKBrecall+outKBpre)))
    inKBrecall=countN*1.0/oldEnCount
    inKBpre=countN*1.0/countPrezero
    print("number of not novel entity : " + str(countPrezero)+" ||true is : "+str(countN))
    print("in KB recall : " + str(inKBrecall))
    print("in KB pre : " + str(inKBpre))
    print("in KB f1 : " + str(2 * inKBrecall * inKBpre / (inKBrecall + inKBpre)))
    print("overall result: "+str(overall))

def fastText_sim(noun1,noun2,embeddings_index):
    noun1_vec = np.zeros(300, np.float32)
    noun2_vec=np.zeros(300, np.float32)
    temp_str1 = noun1.strip().split(" ")
    temp_str2=noun2.strip().split(" ")
    if noun1 in embeddings_index.keys():
        noun1_vec=embeddings_index[noun1]
    else:
        for str in temp_str1:
            if str in embeddings_index.keys():
                noun1_vec += embeddings_index[str]
            else:
                noun1_vec += np.random.randn(300)
        noun1_vec = noun1_vec * (1.0 / len(temp_str1))
    if noun2 in embeddings_index.keys():
        noun2_vec=embeddings_index[noun2]
    else:
        for str in temp_str2:
            if str in embeddings_index.keys():
                noun2_vec += embeddings_index[str]
            else:
                noun2_vec += np.random.randn(300)
        noun2_vec = noun2_vec * (1.0 / len(temp_str2))
    vector_a = np.mat(noun1_vec)
    vector_b = np.mat(noun2_vec)
    num = float(vector_a * vector_b.T)
    # print(num)
    denom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    # print(denom)
    cos = num / denom
    # print(cos)
    return cos

def randomTestFive():
    train_men2can_file = "mention2candidate.text"
    # textTrain="trng.jsonl"
    textTrain = "sample-trng.jsonl"
    # kbattr = "UMLS2017AA_pruned0.1_with_NIL_syn_attr.jsonl"
    kbfull="UMLS2014AB_with_NIL_syn_full.jsonl"
    # kbfull=kbattr
    # textTest = "full_test_for_inference_2017AA_pruned0.1_vs_2017AAfiltered.jsonl"
    textTest = "test.jsonl"
    for i in range(5):
        SampleData()
        trainAndTest(train_men2can_file,textTrain,kbfull,textTest)
        evaluate(kbfull)
    # evaluateNoCan(kbfull)

randomTestFive()





