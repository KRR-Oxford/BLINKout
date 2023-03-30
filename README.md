# BLINKout-anonymous

This is the anonymous repository for BLINKout.

# Model Training and Inference

See `step_all_BLINK.sh` for running BLINK models with Threshold-based and NIL-rep-based methods.

See `step_all_BLINKout.sh` for running BLINKout models and the dynamic feature baseline.

See `step_all_BM25+cross-enc.sh` for all BM25+BERT models.

# Data Sources
* ShARe/CLEF 2013 dataset is from https://physionet.org/content/shareclefehealth2013/1.0/
* MedMention dataset is from https://github.com/chanzuckerberg/MedMentions
* UMLS (versions 2012AB, 2014AB, 2017AA) is from https://www.nlm.nih.gov/research/umls/index.html
* SNOMED CT (corresponding versions) is from https://www.nlm.nih.gov/healthit/snomedct/index.html

* NILK dataset is from https://zenodo.org/record/6607514
* WikiData 2017 dump is from https://archive.org/download/enwiki-20170220/enwiki-20170220-pages-articles.xml.bz2

# Data Scripts

See files under the `preprocessing` folder, where running scripts to create the datasets are in `run_preprocess_ents_and_data.sh`.

# Acknowledgement
The repository is based on [`BLINK`](https://github.com/facebookresearch/BLINK) under the MIT license.