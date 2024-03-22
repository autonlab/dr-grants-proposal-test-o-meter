#!/bin/bash
IDIR=./index
RDIR=./raw
SDIR=./src
MAXLINES=5000

if [ ! -d ${IDIR} ]; then
	mkdir ${IDIR}
fi
if [ ! -d ${RDIR} ]; then
	mkdir ${RDIR}
fi

for FILE in ${SDIR}/get_*; do
	echo ${FILE}
	${FILE} ${IDIR} ${RDIR} ${SDIR} ${MAXLINES}
done

echo 'Building index for Dr. Grants Proposal Test-O-Meter'
python ${SDIR}/proposal_meter.py ${IDIR}
