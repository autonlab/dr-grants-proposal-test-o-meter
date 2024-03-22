#!/bin/bash
IDIR=$1
RDIR=$2
SDIR=$3
MAXLINES=$4

# 2. Run from command line
#    $ ./get_grants.sh

# Variables that only need to be updated if url changes 
URL=https://prod-grants-gov-chatbot.s3.amazonaws.com/extracts/
DATE=$(date +%Y%m%d)
FILENAME=GrantsDBExtract${DATE}v2
TMP=${RDIR}temp

# Function definitions to keep the script readable
function download () { 
	wget -q --show-progress -P ${RDIR} ${URL}$1;}
function decompress () { 
	unzip -n -q ${RDIR}/$1 -d ${RDIR}
	rm ${RDIR}/$1
}

if ! test -f ${RDIR}/${FILENAME}.xml; then
	download ${FILENAME}.zip
	sleep 5
	decompress ${FILENAME}.zip
	sleep 5
else
	echo "${FILENAME}.xml exists in ${RDIR}"
fi

python ${SDIR}/xml2csv.py ${RDIR}/${FILENAME}.xml

tail -n +2 ${RDIR}/${FILENAME}.csv > body
head -1 ${RDIR}/${FILENAME}.csv > columns
split -l ${MAXLINES} -a 3 -d body ${IDIR}/GRANTS_S

for filename in ${IDIR}/GRANTS_S*; do
	cat columns ${filename} > ${TMP}
	cp ${TMP} ${filename}
done
rm ${TMP} ${RDIR}/${FILENAME}.csv columns body
