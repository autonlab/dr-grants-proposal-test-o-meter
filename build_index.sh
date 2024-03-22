#!/bin/bash
IDIR=/home/ngisolfi/github/dr-grants-proposal-test-o-meter/index
SDIR=/home/ngisolfi/github/dr-grants-proposal-test-o-meter/src
MAXLINES=5000

if [ ! -d ${IDIR} ]; then
	mkdir ${IDIR}
fi

for FILE in ${SDIR}/get_*; do
	echo ${FILE}
	${FILE} ${IDIR} ${SDIR} ${MAXLINES}
done

echo 'Building IRIS'
python ${SDIR}/proposal_meter.py ${IDIR}
