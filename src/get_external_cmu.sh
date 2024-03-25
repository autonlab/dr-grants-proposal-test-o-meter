
#https://www.cmu.edu/engage/partner/foundations/faculty-staff/index.html

#log in with CMU credentials and click download csv for:
#1) Current and Anticipated Opportunities
#2) Past Opportunities

IDIR=$1
RDIR=$2
SDIR=$3
MAXLINES=$4

# upcoming and past don't have the same number of fields, so only use upcoming for now

cp ${RDIR}/external_cmu.csv ${IDIR}/EXTERNAL_S000
#cat ${RDIR}/cmu_limited_upcoming.csv <(tail +2 ${RDIR}/cmu_limited_closed.csv) > ${RDIR}/CMU_LIMITED
#cp ${RDIR}/CMU_LIMITED ${IDIR}/CMU_S000

#cp /local_data/grants/iris/hand_downloaded/cmu_limited_upcoming.csv /local_data/grants/iris/index/CMU_S000
#vim -es -c '%s/,/|/g' -cwq /local_data/grants/iris/index/CMU_S000
