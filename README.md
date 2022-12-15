# BLINKout-anonymous

This is the anonymous repository for BLINKout.

# Running

See `step_all_BLINK.sh` for running BLINK models with threshold-based and NIL-rep-based methods.

See  `step_all_BLINKout.sh` for running BLINKout models and the dynamic feature baseline.

See `step_all_BM25+cross-enc.sh` for all BM25+BERT models.

See `baselines/Feature-based' for `Ft-based classifer' baseline.

See `baselines/Sieve-based' for `Rule-based Sieve-based' baseline.

# Data sources
ShARe/CLEF 2013 is from https://physionet.org/content/shareclefehealth2013/1.0/.


# Data scripts
See [`run_preprocess_ents_and_data.sh`](https://github.com/acadTags/BLINKout-anonymous/blob/fefeaa4bce6d187c898cdc14b7c593666cf95b94/preprocessing/run_preprocess_ents_and_data.sh#L1) in the `preprocessing` folder.

# Acknowledgement
The repository is based on [BLINK](https://github.com/facebookresearch/BLINK) under the MIT license.