#!/bin/bash
IDIR=$1
SDIR=$2
MAXLINES=$3

if [ ! -d ${IDIR} ]; then
	mkdir ${IDIR}
fi

# 2. Run from command line
#    $ ./get_grants.sh

# Variables that only need to be updated if url changes 
URL=https://prod-grants-gov-chatbot.s3.amazonaws.com/extracts/
DATE=$(date +%Y%m%d)
FILENAME=GrantsDBExtract${DATE}v2
TMP=${IDIR}temp

# Function definitions to keep the script readable
function download () { 
	wget -q --show-progress -P ${IDIR} ${URL}$1;}
function decompress () { 
	unzip -n -q ${IDIR}/$1 -d ${IDIR}
	rm ${IDIR}/$1
}
function to_utf8 () {
	iconv -f us-ascii -t utf-8 ${IDIR}$1 | cat > ${TMP}
	mv ${TMP} ${IDIR}/$1
}

if ! test -f ${IDIR}/${FILENAME}.xml; then
	download ${FILENAME}.zip
	sleep 5
	decompress ${FILENAME}.zip
	sleep 5
	#to_utf8 ${FILENAME}.xml
	#sleep 5
else
	echo "${FILENAME}.xml exists in ${IDIR}"
	#to_utf8 ${FILENAME}.xml
	#sleep 5
fi

python ${SDIR}/xml2csv.py ${IDIR}/${FILENAME}.xml

tail -n +2 ${IDIR}/${FILENAME}.csv > body
head -1 ${IDIR}/${FILENAME}.csv > columns
split -l ${MAXLINES} -a 3 -d body ${IDIR}/GRANTS_S

for filename in ${IDIR}/GRANTS_S*; do
	cat columns ${filename} > ${TMP}
	cp ${TMP} ${filename}
done
rm ${TMP} ${IDIR}/${FILENAME}.csv columns body
