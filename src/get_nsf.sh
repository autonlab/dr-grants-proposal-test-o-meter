#!/bin/bash
IDIR=$1
RDIR=$2
SDIR=$3
MAXLINES=$4
if [ ! -d ${IDIR} ]; then
	mkdir ${IDIR}
fi
# 2. Run from command line
#    $ ./get_grants.sh

# Variables that only need to be updated if url changes 
URL=https://new.nsf.gov/funding/opps/csv?page
DATE=$(date +%Y%m%d)
FILENAME=${RDIR}/nsf_cfp.csv
TMP=${RDIR}/temp
SPLITNAME=${IDIR}/NSF_S

# Function definitions to keep the script readable
function download () { 
	wget -q -O $1 -P ${RDIR} ${URL};}

download ${FILENAME}
# NSF CFPs are not well structured, newlines can be new records or inserted in free text fields.
# There are 17 CFPs where the title has a single word, meaning that search/replace for \n" won't work
# This first line finds cases where a line ends on a number (seems to be consistent for NSF urls which is last field)
# and continues to a wildcard single word ending with a comma delimiter
# \zs and \ze place the cursor for the substitution, and \0 returns what is matched between \zs and \ze
# encasing in quotes lets the perl and sed substitutions work as expected, yielding a number of records that matches NSF's website
# https://new.nsf.gov/funding/opportunities (755 on 11-1-2023 at time of writing)
vim -es -c '%s/\d\n^\zs\w*\ze,/"\0"/g' -cwq ${FILENAME}
perl -i -pe 's/^"/NEWLINE"/g; s/\n//g; s/NEWLINE/\n/g' ${FILENAME}
sed -i '1s/ [(][^)]*[)]//g; 1s/ /_/g; 1s/"//g; 1s/\//_/g;' ${FILENAME}
vim -es -c '%s/,Biosensing,/,\rBiosensing,/g' -cwq ${FILENAME}

tail -n +2 ${FILENAME} > body
head -1 ${FILENAME} > columns
split -l ${MAXLINES} -a 3 -d body ${SPLITNAME}

for filename in ${SPLITNAME}*; do
	cat columns ${filename} > ${TMP}
	cp ${TMP} ${filename}
done
rm ${TMP} columns body
