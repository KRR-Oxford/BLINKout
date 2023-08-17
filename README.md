# BLINKout: Out-of-KB Mention Discovery
This is the official repository for [Reveal the Unknown: Out-of-Knowledge-Base Mention Discovery with Entity Linking](https://arxiv.org/abs/2302.07189), accepted for CIKM 2023. 

The study adapts BERT-based Entity Linking (BLINK) to identify mentions that do not have corresponding KB entities by matching them to a special NIL entity, with NIL entity representation and classification, and synonym enhancement. 

The study also applies KB Pruning and Versioning strategies to automatically construct out-of-KB datasets from common in-KB Entity Linking datasets. Please see the model training and data construction scripts below.

# Model Training and Inference
See `step_all_BLINK.sh` for running BLINK models with Threshold-based and NIL-rep-based methods.

See `step_all_BLINKout.sh` for running BLINKout models and the dynamic feature baseline.

See `step_all_BM25+cross-enc.sh` for all BM25+BERT models.

For all scripts above:
* setting `dataset` (and `mm_onto_ver_model_mark` for MedMentions)
* setting `bi_enc_bertmodel` and `cross_enc_bertmodel` (and change `further_model_mark` accordingly)
* setting `train_bi` (except BM25), `rep_ents`, `train_cross`, `inference` to `true` to perform each step. 
* setting `use_best_top_k` as `true` if using tuned top-k, otherwise using default

For `step_all_BLINK.sh`, further
* setting `use_NIL_threshold` to `true` when using the Threshold-based approach (and the corresponding `th2` as threshold value for each dataset)
* setting `use_NIL_ranking` to `true` when using the NIL-rep-based approach (and setting NIL representation binary parameters of `use_NIL_tag`, `use_NIL_desc`, and `use_NIL_desc_tag`)

For `step_all_BLINKout.sh`, further
* setting NIL representation binary parameters of `use_NIL_tag`, `use_NIL_desc`, and `use_NIL_desc_tag`.
* setting `dynamic_emb_extra_ft_baseline` to `true` and select the corresponding line (around 273-274) to use either the NIL regulariser (`gu2021`) or the dynamic feature baseline (`full-features-NIL-infer`), also setting the value of `lambda_NIL`.

For `step_all_BM25+cross-enc.sh`
* requiring the tokenizer of the saved biencoder model, so run `step_all_BLINK.sh` with the same biencoder model first before running this script.

# Data Availability and Data Sources

Link to out-of-KB mention discovery datasets: https://zenodo.org/record/8228371. 

We acknowledge the sources below for data construction:

* ShARe/CLEF 2013 dataset is from https://physionet.org/content/shareclefehealth2013/1.0/
* MedMention dataset is from https://github.com/chanzuckerberg/MedMentions
* UMLS (versions 2012AB, 2014AB, 2017AA) is from https://www.nlm.nih.gov/research/umls/index.html
* SNOMED CT (corresponding versions) is from https://www.nlm.nih.gov/healthit/snomedct/index.html

* NILK dataset is from https://zenodo.org/record/6607514
* WikiData 2017 dump is from https://archive.org/download/enwiki-20170220/enwiki-20170220-pages-articles.xml.bz2

# Data Scripts
See files under the `preprocessing` folder, where running scripts to create the datasets are in `run_preprocess_ents_and_data.sh`.

# Acknowledgement
The repository is based on [`BLINK`](https://github.com/facebookresearch/BLINK) under the MIT license. Also, we acknowledge the data sources above.
