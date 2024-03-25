#!/bin/bash
IDIR=$1
RDIR=$2
SDIR=$3
MAXLINES=$4

if [ ! -d ${IDIR} ]; then
	mkdir ${IDIR}
fi

# SAM.gov requires account + log-in to download. Data Services > Contract Opportunities > datagov > ContractOpportunitiesFullCSV.csv
#https://sam.gov/data-services/Contract%20Opportunities/datagov?privacy=Public

FILENAME=${RDIR}/ContractOpportunitiesFullCSV.csv
OUTFNAME=SAM_S
TMP=${IDIR}/temp
#echo "NoticeId,Title,SolicitationNum,Department_or_Agency,CGAC,Sub_Tier,FPDS_Code,Office,AAC_Code,PostedDate,Type,BaseType,ArchiveType,ArchiveDate,SetASideCode,SetASide,ResponseDeadLine,NaicsCode,ClassificationCode,PopStreetAddress,PopCity,PopState,PopZip,PopCountry,Active,AwardNumber,AwardDate,AwardAmount,Awardee,PrimaryContactTitle,PrimaryContactFullname,PrimaryContactEmail,PrimaryContactPhone,PrimaryContactFax,SecondaryContactTitle,SecondaryContactFullname,SecondaryContactEmail,SecondaryContactPhone,SecondaryContactFax,OrganizationType,State,City,ZipCode,CountryCode,AdditionalInfoLink,Link,Description" > columns

#You need to register with sam.gov to download data, it doesn't look like there is an automatable way to get data in similar fashion to other sources.
vim -es -c '%s/[^[:print:]]//g' -cwq ${FILENAME}

REFERENCEFILE=${IDIR}/SAM.csv
iconv -f latin1 -t UTF-8 ${FILENAME} > ${REFERENCEFILE}

python ${SDIR}/sam2csv.py ${REFERENCEFILE} ${MAXLINES}

#tail -n +2 ${FILENAME} > body
#head -1 ${FILENAME} > columns
#split -l ${MAXLINES} -a 3 -d body ${IDIR}${OUTFNAME}

#for filename in ${IDIR}${OUTFNAME}*; do
	#cat columns ${filename} > ${TMP}
	#iconv -f latin1 -t UTF-8 ${TMP} > ${filename}
#done
#rm ${TMP} columns body ${REFERENCEFILE}
rm ${REFERENCEFILE}
