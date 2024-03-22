#this is a CMU subscription service with a 600 entry download limit daily
# day 1 - 'artificial intelligence'
# day 2 - 'machine learning'
IDIR=$1
RDIR=$2
SDIR=$3
MAXLINES=$4

#TMP=${IDIR}temp
REFERENCE_FILE=${IDIR}/GFORWARD

echo "============================================
">spacer

#cat /local_data/grants/iris/hand_downloaded/grantforward_disjunction.txt spacer \
cat	${RDIR}/grantforward_artificialintelligence.txt spacer \
		${RDIR}/grantforward_machinelearning.txt spacer \
		${RDIR}/grantforward_datasciencealgorithm.txt spacer \
		${RDIR}/grantforward_healthcaredata.txt \
		> ${REFERENCE_FILE}.txt
rm spacer
FILENAME=GFORWARD

python ${SDIR}/gforward2csv.py ${REFERENCE_FILE}.txt $MAXLINES
#Python script that splits paragraphs of description into new rows
#cp ${REFERENCE_FILE}.csv /local_data/grants/iris/index/${FILENAME}_S000

#head -n -1 ${REFERENCE_FILE}.csv > body #| cat columns - > /local_data/grants/iris/index/${FILENAME}_S000
#head -1 ${REFERENCE_FILE}.csv > columns
#split -l ${MAXLINES} -a 3 -d body ${IDIR}${FILENAME}_S

#for filename in ${IDIR}${FILENAME}_S*; do
	#cat columns ${filename} > ${TMP}
	#cp ${TMP} ${filename}
#done

rm ${REFERENCE_FILE}.txt # ${REFERENCE_FILE}.csv
#tail -n +2 ${REFERENCE_FILE} > ${FILENAME}
