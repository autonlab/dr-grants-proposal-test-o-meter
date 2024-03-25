
IDIR=$1
RDIR=$2
SDIR=$3
MAXLINES=$4

cut -d$'\t' -f1-8 ${RDIR}/scs_active.tsv > SCS_ACTIVE
cut -d$'\t' -f1-8 ${RDIR}/scs_unpublished.tsv > SCS_UNPUBLISHED
cat SCS_ACTIVE <(tail +2 SCS_UNPUBLISHED) > ${RDIR}/SCS.tsv

#cut -d$'\t' -f1 --complement ${RDIR}/SCS.tsv > ${IDIR}/SCS.tsv
cp ${RDIR}/SCS.tsv ${IDIR}/SCS.tsv
rm SCS_ACTIVE SCS_UNPUBLISHED

python ${SDIR}/scs2csv.py ${IDIR}/SCS.tsv ${MAXLINES}

rm ${IDIR}/SCS.tsv
