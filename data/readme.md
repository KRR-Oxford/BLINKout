Due to the size limit, this folder only contains data samples. 

For full datasets, please refer to the repository in Zenodo, https://zenodo.org/record/8228371. Also, the full datasets can be constructed using scripts under the `\preprocessing` folder.

Subfolder postfix of `syn_full` means the training data is augmented with synonyms (each as an entity). Alternatively, the corresponding folder *without* `syn_full` (or with `syn_attr`) contains training data having synonyms as an attribute for the entity.

## Datasets for Out-of-KB Mention Discovery 

For MedMentions and NILK datasets, each data setting (as a sub-folder) contains train, valid, test files and also 100 random sample files for each data split for debugging.

Data folder names with “syn_full” at the end are synonym augmented data (each synonym as an entity) for the setting.

Ontology .jsonl files have two version for each, "syn_attr" setting treats synonyms are attributes, "syn_full" setting treats synonyms as entities.

p.s. ShARe/CLEF 2013 dataset is not available due to licence but can be constructed with data scripts after downloading the original data. Data splits for ShARe/CLEF 2013: train as the original train in ShARe/CLEF, train_split as mentions in 95% split of train_full documents, valid as mentions in 5% split of train_full documents (with removing NIL mentions appeared in train), and test as the original test in ShARe/CLEF.

## Acknowledgement to data sources 

ShARe/CLEF 2013 dataset is from https://physionet.org/content/shareclefehealth2013/1.0/

MedMention dataset is from https://github.com/chanzuckerberg/MedMentions

UMLS (versions 2012AB, 2014AB, 2017AA) is from https://www.nlm.nih.gov/research/umls/index.html

SNOMED CT (corresponding versions) is from https://www.nlm.nih.gov/healthit/snomedct/index.html

NILK dataset is from https://zenodo.org/record/6607514

WikiData 2017 dump is from https://archive.org/download/enwiki-20170220/enwiki-20170220-pages-articles.xml.bz2
