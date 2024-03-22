#!/bin/bash
IDIR=./index
SDIR=./src
MAXLINES=5000

if [ ! -d ${IDIR} ]; then
	mkdir ${IDIR}
fi

for FILE in ${SDIR}/get_*; do
	echo ${FILE}
	${FILE} ${IDIR} ${SDIR} ${MAXLINES}
done

echo 'Building index for Dr. Grants Proposal Test-O-Meter'
python ${SDIR}/proposal_meter.py ${IDIR}
