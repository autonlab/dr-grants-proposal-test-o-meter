#this is a CMU subscription service with a 600 entry download limit daily
# day 1 - 'artificial intelligence'
# day 2 - 'machine learning'
IDIR=$1
RDIR=$2
SDIR=$3
MAXLINES=$4

if [ ! -d ${IDIR} ]; then
	mkdir ${IDIR}
fi


REFERENCE_FILE=${RDIR}/proquestpivot
#cat ${RDIR}/proquestpivot.txt > ${REFERENCE_FILE}

#cat /local_data/grants/iris/hand_downloaded/proquestpivot_ai.txt \
		#/local_data/grants/iris/hand_downloaded/proquestpivot_aimlds.txt > ${REFERENCE_FILE}.txt

python ${SDIR}/ppivot2csv.py ${REFERENCE_FILE}.txt

FILENAME=${IDIR}/PIVOT

cp ${REFERENCE_FILE}.csv ${FILENAME}_S000
#rm ${REFERENCE_FILE}.csv  ${REFERENCE_FILE}.txt

#cp ${REFERENCE_FILE} ${FILENAME}
#vim -es -c '%s/  / /g' -cwq ${FILENAME}
#vim -es -c '%s/|/,/g' -cwq ${FILENAME}
#vim -es -c '%s/\n Funder:/\rFunder:/g' -cwq ${FILENAME}
#vim -es -c '%s/Eligibility: \n/Eligibility: NA\r/g' -cwq ${FILENAME}
#vim -es -c '%s/^CFDA Number.*\n//g' -cwq ${FILENAME}
#vim -es -c '%s/^Amount.*\n//g' -cwq ${FILENAME}
#vim -es -c '%s/^Related Funders.*//g' -cwq ${FILENAME}
#vim -es -c '%s/^Funder Type.*/\0/g' -cwq ${FILENAME}
#vim -es -c '%s/^Funder Location.*//g' -cwq ${FILENAME}
#vim -es -c '%s/\n / -- /g' -cwq ${FILENAME}
#
##Reference file doesn't have a header, so these are hard coded
#echo "Ex Libris Pivot-RP ID|Title|Funder|Funder ID|Upcoming deadlines|Note|Eligibility|Applicant/Institution Location|Citizenship|Activity location|Applicant type|Career stage|Abstract|Website|Link to Pivot-RP|Keywords|Funding type" > columns
#
#vim -es -c '%s/^.\{-}: //g' -cwq ${FILENAME}
#vim -es -c '%s/<.\{-}>//g' -cwq ${FILENAME}
#vim -es -c '%s/^.[0-9]*\n//g' -cwq ${FILENAME}
#vim -es -c '%s/\n\n/NEWLINECHARACTER/g' -cwq ${FILENAME}
#vim -es -c '%s/\n/|/g' -cwq ${FILENAME}
#vim -es -c '%s/NEWLINECHARACTER/\r/g' -cwq ${FILENAME}
#head -n -1 ${FILENAME} | cat columns - > ${FILENAME}_S000
