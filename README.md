# BLINKout-anonymous

This is the anonymous repository for BLINKout.

# Running

See `step_all_BLINK.sh` for running BLINK models with Threshold-based and NIL-rep-based methods.

See `step_all_BLINKout.sh` for running BLINKout models and the dynamic feature baseline.

See `step_all_BM25+cross-enc.sh` for all BM25+BERT models.

See `baselines/Feature-based` for "Ft-based classifer" baseline.

See `baselines/Sieve-based` for "Rule-based Sieve-based" baseline.

# Data sources
* ShARe/CLEF 2013 dataset is from `https://physionet.org/content/shareclefehealth2013/1.0/`
* MedMention dataset is from `https://github.com/chanzuckerberg/MedMentions`
* UMLS is from `https://www.nlm.nih.gov/research/umls/index.html`
* SNOMED CT is from `https://www.nlm.nih.gov/healthit/snomedct/index.html`

# Data scripts

See files under the `preprocessing` folder, where running scripts to create the datasets are in `run_preprocess_ents_and_data.sh`.

# Acknowledgement
The repository is based on [`BLINK`](https://github.com/facebookresearch/BLINK) under the MIT license.