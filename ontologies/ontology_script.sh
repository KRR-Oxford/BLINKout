# unzip and merge MRCONSO in UMLS, and other files
gzip -d MRCONSO.RRF.aa.gz
gzip -d MRCONSO.RRF.ab.gz
cat MRCONSO.RRF.?? > MRCONSO.RRF

gzip -d MRDEF.RRF.gz
gzip -d MRSTY.RRF.gz

# generate snomed .owl
java -Xms4g -jar snomed-owl-toolkit*executable.jar -rf2-to-owl -rf2-snapshot-archives SnomedCT_InternationalRF2.zip

# prune snomedct ontology with DeepOnto
cd ..
cd DeepOnto
python onto_prune.py --saved_path ../BLINK/ontologies --src_onto_path ../BLINK/ontologies/SNOMEDCT-US-20170301-new.owl --preserved_iris_path ../BLINK/ontologies/SCTID_to_keep0.2.txt
#python onto_prune.py --saved_path ../BLINK/ontologies --src_onto_path ../BLINK/ontologies/SNOMEDCT-US-20170301-new.owl --preserved_iris_path ../BLINK/ontologies/SCTID_to_keep0.1.txt