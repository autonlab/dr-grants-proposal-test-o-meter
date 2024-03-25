from sys import argv
from os import system, environ
import subprocess
from glob import glob
import pandas as pd
import pickle
from sentence_transformers import SentenceTransformer
import torch
from argparse import ArgumentParser
from datetime import datetime
from math import isnan
environ["TOKENIZERS_PARALLELISM"]="false" #parallel GPU encoding makes subprocess run statement throw warning over parllelism

def show_color_banner(message:str,color:float):
    ntiers=11
    rgb = [240,245,250,255,46,33,92,226,202,199]
    subprocess.run(['echo','-e',"\e[1;38;5;%dm[%.4f] %s\e[0m"%
           (rgb[int(color*100)//ntiers],
            color,
            message.replace("'","\'").replace('"',"").replace('\n',' -- '))
           ])
def show_color_banner_no_score(message:str,color:float):
    ntiers=11
    rgb = [240,245,250,255,46,33,92,226,202,199]
    subprocess.run(['echo','-e',"\e[1;38;5;%dm%s\e[0m"%
           (rgb[int(color*100)//ntiers],
            message.replace("'","\'").replace('"',"").replace('\n',' -- '))
           ])

def show_one(key1:str,val1:str):
    if isinstance(val1,str):
        if len(val1)<250 and val1.count('\n')<5:
            subprocess.run(['echo', '-e', "\e[1m%s:\e[0m \e[38;5;8m%s\e[0m"%(key1,val1.replace("'","\'"))])
        elif val1.count('\n')>=5:
            subprocess.run(['echo','-e',"\e[1m%s:\e[0m \e[38;5;8m%s\e[0m"%(key1,val1.replace("'","\'").replace("\n"," -- ")[:250])])
        else:
            subprocess.run(['echo','-e',"\e[1m%s:\e[0m \e[38;5;8m%s%s\e[0m"%(key1,val1[:250].replace("'","\'"),'...See URL for more')])
def show_one_limitless(key1:str,val1:str):
    if isinstance(val1,str):
        subprocess.run(['echo','-e',"\e[1m%s:\e[0m \e[38;5;8m%s\e[0m"%(key1,val1.replace("'","\'"))])
def show_one_underline(key1:str,val1:str):
    if isinstance(val1,str):
        if len(val1)<250:
            subprocess.run(['echo','-e','\e[1;4m%s:\e[0m \e[38;5;8m%s\e[0m'%(key1,val1.replace("'","\'"))])
        else:
            subprocess.run(['echo','-e','\e[1;4m%s:\e[0m \e[38;5;8m%s%s\e[0m'%(key1,val1[:250].replace("'","\'"),'...See URL for more')])

class Raw_Data_Index():
    '''
    Object to handle data wrangling. Find, fetch, extract, parse
    are unique for each data source, and they need to be merged.
    '''
    def __init__(self, filename:str, desc_att:str):
        self.filename=filename
        self.description_attribute=desc_att

    def load_data(self, filename:str):
        '''
            Read in data from files, which have their own unique requirements
        '''
    def get_descriptions(self):
        '''
            Return which attribute should be used for embedding and subsequent
            similarity to user prompts
        '''
    def print(self,row:int,similarity:float):
        '''
            Visualize this element if it is returned
        '''
    def print_title(self,row:int,similarity:float):
        '''
            Print only the title to stdout if saving output to csv
        '''
    def date2MMDDYYYY(self,date:str):
        '''
            Each raw data source may have its own data format
        '''
    def mk_empty_row(self):
        return {'Similarity':None,'Title':None,'DueDates':None,'Posted':None, 'ModifiedDate':None,'CloseDate':None,
                    'Sponsor':None,'SponsorType':None,'Feed':None,'FeedID':None,'ProgramID':None,'AwardType':None,
                    'Eligibility':None,'ApplicantLocation':None,'ApplicantType':None,'CitizenshipReq':None,
                    'ActivityLocation':None,'Status':None,'Amount':None,'MaxAmount':None,'MinAmount':None,
                    'MaxNumAwards':None,'SubmissionDetails':None,'LimitedSubmissionInfo':None,
                    'SubmissionRequirements':None,'CostSharing':None,'RollingDecision':None,
                    'Categories':None,'CFDA':None,'Contacts':None,'URL':None,'SolicitationURL':None,
                    'Description':None,'Prompt':None,'QueryName':None}
    def to_csv(self,row:int,similarity:float):
        vals = self.to_dict(row,similarity)
        keys = ['Similarity','Title','DueDates','Posted','ModifiedDate','CloseDate','Sponsor','SponsorType','Feed','FeedID', \
                'ProgramID','AwardType','Eligibility', \
                'ApplicantLocation','ApplicantType','CitizenshipReq', \
                'ActivityLocation','Status','Amount','MaxAmount', \
                'MinAmount','MaxNumAwards','SubmissionDetails', \
                'LimitedSubmissionInfo','SubmissionRequirements', \
                'CostSharing','RollingDecision','Categories','CFDA', \
                'Contacts','URL','SolicitationURL','Description' \
            ]

        res=pd.DataFrame({key:vals[key] for key in keys},index=[0])
        res['DueDates']=str(vals['DueDates'])
        return res

class NSF(Raw_Data_Index):
    def __init__(self,filename:str,desc_att:str):
        super().__init__(filename,desc_att)
        self.load_data()
    def load_data(self):
        self.df=pd.read_csv(self.filename)
    def get_descriptions(self):
        return pd.DataFrame({'filename':self.filename,'row':self.df.index,'description':self.df[self.description_attribute]})
    def print_title(self,row:int,similarity:float):
        show_color_banner_no_score(self.df.iloc[row].Title,similarity)
    def print(self,idx:int,similarity:float):
        show_color_banner(self.df.iloc[idx].Title,similarity)
        show_one('Posted on','nsf.gov')
        for attname in self.df.columns:
            if attname==self.description_attribute:
                show_one_underline(attname,self.df.iloc[idx][attname])
            else:
                show_one(attname,self.df.iloc[idx][attname])
    def date2MMDDYYYY(self,date:str):
        if isinstance(date,float):
            return ''
        if ' ' in date:
            date=date.split(',')[1].strip()
        return datetime.strptime(date,'%Y-%m-%d').strftime('%m/%d/%Y')

    def to_dict(self,idx:int,similarity:float):
        row=self.df.iloc[idx]
        result = self.mk_empty_row()
        result['Similarity']=similarity
        result['Feed']='NSF'
        result['Title']=row.Title
        result['Posted']=self.date2MMDDYYYY(row.Posted_date)
        result['Description']=row.Synopsis
        result['AwardType']=row.Award_Type
        result['DueDates']=[row['Next_due_date']]# double check
        result['CloseDate']=self.date2MMDDYYYY(row['Next_due_date'])
        result['RollingDecision']=row['Proposals_accepted_anytime']
        result['ProgramID']=row.Program_ID
        result['FeedID']=row.NSF_PD_Num
        result['Status']=row.Status
        result['URL']=row.URL
        result['AwardType']=row.Type
        result['SolicitationURL']=row.Solicitation_URL
        result['SponsorType']='Federal'
        result['Sponsor']='NSF'
        return result
        
class MAILER(Raw_Data_Index):
    def __init__(self,filename:str,desc_att:str):
        super().__init__(filename,desc_att)
        self.load_data()
    def load_data(self):
        self.df=pd.read_csv(self.filename)
    def get_descriptions(self):
        return pd.DataFrame({'filename':self.filename,'row':self.df.index,'description':self.df[self.description_attribute]})
    def print_title(self,row:int,similarity:float):
        show_color_banner_no_score(self.df.iloc[row]['Title'],similarity)
    def print(self,idx:int,similarity:float):
        show_color_banner(self.df.iloc[idx]['Title'],similarity)
        show_one('Posted on','CMU Opportunity Mailer')
        for attname in self.df.columns:
            if attname==self.description_attribute:
                show_one_underline(attname,self.df.iloc[idx][attname])
                print(self.df.iloc[idx][attname])
            else:
                show_one(attname,self.df.iloc[idx][attname])
    def date2MMDDYYYY(self,date:str):
        if isinstance(date,float):
            return None
        formats=['%m/%d/%y']
        dt=None
        for f in formats:
            try:
                dt=datetime.strptime(date.strip(),f).strftime('%m/%d/%Y')
                break
            except:
                pass
        if not dt:
            print(date)
        return dt
    def to_dict(self,idx:int,similarity:float):
        row=self.df.iloc[idx]
        result = self.mk_empty_row()
        result['Similarity']=similarity
        result['Feed']='CMU Opportunity Mailer'
        result['Title']=row['Title']
        result['Sponsor']=row['Agency/Organization']
        result['SponsorType']=row['Type']
        result['Posted']=self.date2MMDDYYYY(row['Post Date'])
        result['CloseDate']=self.date2MMDDYYYY(row['Due Date'])
        result['URL']='https://docs.google.com/spreadsheets/d/19vQMmH0Vsg0tvf4ia3SBqWTQ8lowQCPhyTOt3hQSVHk/edit?usp=sharing'
        result['Amount']=row['Amount/Duration']
        result['Description']=row['Brief Description']
        result['Status']='Open'
        return result

class CMU(Raw_Data_Index):
    def __init__(self,filename:str,desc_att:str):
        super().__init__(filename,desc_att)
        self.load_data()
    def load_data(self):
        self.df=pd.read_csv(self.filename)
    def get_descriptions(self):
        return pd.DataFrame({'filename':self.filename,'row':self.df.index,'description':self.df[self.description_attribute]})
    def print_title(self,row:int,similarity:float):
        show_color_banner_no_score(self.df.iloc[row]['Opportunity Name'],similarity)
    def print(self,idx:int,similarity:float):
        show_color_banner(self.df.iloc[idx]['Opportunity Name'],similarity)
        show_one('Posted on','CMU Limited Submissions')
        for attname in self.df.columns:
            if attname==self.description_attribute:
                show_one_underline(attname,self.df.iloc[idx][attname])
            else:
                show_one(attname,self.df.iloc[idx][attname])
    def date2MMDDYYYY(self,date:str):
        if isinstance(date,float):
            return None
        return datetime.strptime(date,'%m/%d/%Y').strftime('%m/%d/%Y')
    def to_dict(self,idx:int,similarity:float):
        row=self.df.iloc[idx]
        result = self.mk_empty_row()
        result['Similarity']=similarity
        result['Feed']='CMU Foundation Relations'
        result['Title']=row['Opportunity Name']
        result['Sponsor']=row['Organization']
        result['SubmissionDetails']=row['How do I submit a proposal?']
        result['Posted']='NA'
        result['ProgramID']=row['Solicitation Number']
        result['SponsorType']=row['Federal/Non-Federal']
        result['DueDates']={'InternalLOI':self.date2MMDDYYYY(row['Internal Letter of Intent Deadline']),
                'InternalPPD':self.date2MMDDYYYY(row['Internal Pre-Proposal Deadline']),
                'NextDueDate':self.date2MMDDYYYY(row['1st Sponsor Deadline']),
                'FinalDueDate':self.date2MMDDYYYY(row['Final Sponsor Deadline'])
                }
        result['CloseDate']=''
        result['LimitedSubmissionInfo']=row['CMU Limit']
        result['SubmissionRequirements']=row['Proposal Requirements (internal, external nominations)']
        result['URL']='https://www.cmu.edu/osp/limited-submissions/index.html'
        result['SolicitationURL']=row['Website']
        result['Amount']=row['Anticipated Funding Amount']
        result['Description']=row['Summary']
        result['Status']='Open'
        return result

class GFORWARD(Raw_Data_Index):
    def __init__(self,filename:str,desc_att:str):
        super().__init__(filename,desc_att)
        self.load_data()
    def load_data(self):
        self.df=pd.read_csv(self.filename)
    def get_descriptions(self):
        return pd.DataFrame({'filename':self.filename,'row':self.df.index,'description':self.df[self.description_attribute]})
    def print_title(self,row:int,similarity:float):
        show_color_banner_no_score(self.df.iloc[row]['Title'],similarity)
    def print(self,idx:int,similarity:float):
        show_color_banner(self.df.iloc[idx].Title,similarity)
        show_one('Posted on','GrantForward (CMU Subscription)')
        for attname in self.df.columns:
            if attname==self.description_attribute:
                show_one_underline(attname,self.df.iloc[idx][attname])
                #show_one_limitless('Summary',summary_model(self.df.loc[idx][attname], max_length=280, min_length=140, do_sample=False)[0]['summary_text'])
            else:
                show_one(attname,self.df.iloc[idx][attname])
    def date2MMDDYYYY(self,date:str):
        if ':' in date:
            date = date.split(':')[1].strip()
        formats=['%Y-%m-%d','%B %d, %Y']
        dt=None
        for f in formats:
            try:
                dt=datetime.strptime(date.strip(),f).strftime('%m/%d/%Y')
                break
            except:
                pass
        if not dt:
            print(date)
        return dt
    def to_dict(self,idx:int,similarity:float):
        row=self.df.iloc[idx]
        result = self.mk_empty_row()
        result['Similarity']=similarity
        result['Feed']='GrantForward'
        result['Title']=row['Title']
        result['Status']=row['Status']
        result['Description']=row['Description']
        result['SolicitationURL']=row['Source URL']
        result['Sponsor']=row['Sponsors']
        if not isinstance(row['Deadlines'],float):
            result['DueDates']={f'Deadline_{i}':e for i,e in enumerate(row['Deadlines'].split('\n'))}
        else:
            result['DueDates']={'Closed':''}
        for k,v in result['DueDates'].items():
            #if isnan(v): continue
            if 'Submission:' in v:
                result['CloseDate']=self.date2MMDDYYYY(v.split('Submission:')[1])
            if 'Submit Date:' in v:
                result['Posted']=self.date2MMDDYYYY(v.split('Submit Date:')[1])
        if 'Posted' not in result:  
            result['Posted']=''
        if 'CloseDate' not in result:
            result['CloseDate']=''
        #result['Amount']='Unknown'#row['Amount Info']
        result['MaxAmount']=row['Maximum Amount']
        result['MinAmount']=row['Minimum Amount']
        result['AwardType']=row['Grant Types'].strip()
        result['Eligibility']=row['Eligibility']
        result['ApplicantLocation']=row['Applicant Locations']
        result['ActivityLocation']=row['Activity Locations']
        result['SubmissionDetails']=row['Submission Info']
        result['ApplicantType']=row['Applicant Types']
        result['Categories']=row['Categories']
        result['Contacts']=row['Contacts']
        result['DueDates']['Submit Date']=self.date2MMDDYYYY(row['Submit Date'])
        result['ModifiedDate']=self.date2MMDDYYYY(row['Modified Date'])
        result['URL']=row['GrantForward URL']
        result['CitizenshipReq']=row['Citizenships']
        result['MaxNumAwards']=row['Maximum Number of Awards']
        result['MinNumAwards']=row['Minimum Number of Awards']
        result['LimitedSubmissionInfo']=row['Limited Submission Info']
        result['CostSharing']=row['Cost Sharing']
        result['CFDA']=row['CFDA Numbers']
        result['FeedID']=row['GrantForward URL'].split('?grant_id=')[1]#https://www.grantforward.com/grant?grant_id=186134
        return result

class GRANTS(Raw_Data_Index):
    def __init__(self,filename:str,desc_att:str):
        super().__init__(filename,desc_att)
        self.load_data()
    def load_data(self):
        self.df=pd.read_csv(self.filename)
    def get_descriptions(self):
        return pd.DataFrame({'filename':self.filename,'row':self.df.index,'description':self.df[self.description_attribute]})
    def print_title(self,row:int,similarity:float):
        show_color_banner_no_score(self.df.iloc[row]['OpportunityTitle'],similarity)
    def print(self,idx:int,similarity:float):
        show_color_banner(self.df.iloc[idx].OpportunityTitle,similarity)
        show_one('Posted on','grants.gov')
        for attname in self.df.columns:
            if attname==self.description_attribute:
                show_one_underline(attname,self.df.iloc[idx][attname])
                #show_one_limitless('Summary',summary_model(self.df.loc[idx][attname], max_length=280, min_length=140, do_sample=False)[0]['summary_text'])
            else:
                show_one(attname,self.df.iloc[idx][attname])
    def date2MMDDYYYY(self,date:str):
        if isinstance(date,datetime):
            return date.strftime('%m/%d/%Y')
        if isinstance(date,float):
            if isnan(date):
                return ''
            else:
                date=str(int(date))
        dt=None
        for f in ['%m%d%Y','%Y-%m-%d']:
            try:
                dt = datetime.strptime(date,f).strftime('%m/%d/%Y')
            except:
                pass
        if not dt:
            print('stumped!',date)
        return dt
    def to_dict(self,idx:int,similarity:float):
        #https://apply07.grants.gov/help/html/help/index.htm#t=XMLExtract%2FXMLExtract.htm
        row=self.df.iloc[idx]
        result = self.mk_empty_row()
        result['Similarity']=similarity
        result['Feed']='Grants.gov'
        result['FeedID']=row['OpportunityID']
        result['Title']=row['OpportunityTitle']
        result['ProgramID']=row['OpportunityNumber']
        gg_oppcat={'D':'Discretionary','M':'Mandatory','C':'Continuation','E':'Earmark','O':'Other'}
        result['Categories']=gg_oppcat[row['OpportunityCategory']]
        gg_fundinsttype={'G':'Grant','CA':'Cooperative Agreement','O':'Other','PC':'Procurement Contract'}
        result['AwardType']=gg_fundinsttype[row['FundingInstrumentType']]
        #CategoryOfFundingActivity
        #CategoryExplanation
        result['CFDA']=row['CFDANumbers']
        gg_eligapp={99:'Unrestricted',0:'State Governments',1:'County Governments',
            2:'City or township governments',4:'Special district governments',5:'Independent school districts',
            6:'Public and State controlled institutions of higher education',7:'Native American tribal governments (federally recognized)',
            8:'Public housing authorities/Indian housing authorities',11:'Native American tribal organizations (not recognized)',
            12:'Nonprofits having 501 (c)(3) statis with the IRS, other than institutions of higher education',
            13:'Nonprofits that do not have a 501(c)(3) status with the IRS, other than institutions of higher education',
            20:'Private institutions of higher education',21:'Individuals',22:'For-profit organizations other than small business',
            23:'small business',25:'Others'}
        if row['EligibleApplicants'] in gg_eligapp:
            result['ApplicantType']=gg_eligapp[row['EligibleApplicants']]
        result['Eligibility']=row['AdditionalInformationOnEligibility']
        #AgencyCode
        result['Sponsor']=row['AgencyName']
        if isnan(row['PostDate']):
            result['Posted']=''
        else:
            result['Posted']=self.date2MMDDYYYY(str(int(row['PostDate'])))
        result['DueDates']={}
        result['CloseDate']=self.date2MMDDYYYY(row['CloseDate'])
        if isnan(row['LastUpdatedDate']):
            result['ModifiedDate']=''
        else:
            result['ModifiedDate']=self.date2MMDDYYYY(row['CloseDate'])
        result['MaxAmount']=row['AwardCeiling']
        result['MinAmount']=row['AwardFloor']
        result['Amount']=row['EstimatedTotalProgramFunding']
        result['MaxNumAwards']=row['ExpectedNumberOfAwards']
        result['Description']=row['Description']
        #Version
        result['CostSharing']=row['CostSharingOrMatchingRequirement']
        #GrantorContactEmailDescription
        result['Contacts']={'Email':row['GrantorContactEmail'],
            'Contact':row['GrantorContactText'],
            'Name':row['GrantorContactName'],
            'Phone':row['GrantorContactPhoneNumber']
            }
        result['URL']=f'https://www.grants.gov/search-results-detail/{result["FeedID"]}'#'#row['AdditionalInformationURL']
        result['SolicitationURL']=row['AdditionalInformationURL']
        #AdditionalInformationText
        #CloseDateExplanation
        #OpportuintyCategoryExplanation
        #FiscalYear
        #EstimatedSynopsisCloseDateExplanation
        return result
 
class PIVOT(Raw_Data_Index):
    def __init__(self,filename:str,desc_att:str):
        super().__init__(filename,desc_att)
        self.load_data()
    def load_data(self):
        self.df=pd.read_csv(self.filename)
    def get_descriptions(self):
        return pd.DataFrame({'filename':self.filename,'row':self.df.index,'description':self.df[self.description_attribute]})
    def print_title(self,row:int,similarity:float):
        title = self.df.iloc[row]['Title']
        #if len(title.split('Funder: '))>1:
            #title = title.split('Funder: ')[0]
        if '\n' in title:
            title=title.split('\n')[0]
        show_color_banner_no_score(title,similarity)
    def print(self,idx:int,similarity:float):
        show_color_banner(self.df.iloc[idx].Title,similarity)
        show_one('Posted on','Proquest Pivot (CMU Subscription)')
        for attname in self.df.columns:
            if attname==self.description_attribute:
                show_one_underline(attname,self.df.iloc[idx][attname])
                #show_one_limitless('Summary',summary_model(self.df.loc[idx][attname], max_length=280, min_length=140, do_sample=False)[0]['summary_text'])
            elif attname=='Link to Pivot-RP' or attname=='Website':
                show_one(attname,'https:'+self.df.iloc[idx][attname].split(' ')[1])
            else:
                show_one(attname,self.df.iloc[idx][attname])
    def date2MMDDYYYY(self,date:str):
        if 'sponsor' in date:
            return ''
        return datetime.strptime(date.strip(),'%d %b %Y').strftime('%m/%d/%Y')
    def to_dict(self,idx:int,similarity:float):
        row=self.df.iloc[idx]
        result = self.mk_empty_row()
        result['Similarity']=similarity
        result['Feed']='Proquest PIVOT'
        result['FeedID']=row['Ex Libris Pivot-RP ID']
        if len(row['Title'].split('Funder: '))>1:
            result['Sponsor']=row['Title'].split('Funder: ')[1]
            result['Title']=row['Title'].split('Funder: ')[0]
        else:
            result['Title']=row['Title']
            result['Sponsor']=row['Funder']
        result['ProgramID']=row['Funder ID']
        #Funder location
        result['SponsorType']=row['Funder type']
        if not isinstance(row['Upcoming deadlines'],float):
            result['DueDates']={f'Deadline_{i}':e for i,e in enumerate(row['Upcoming deadlines'].split('\n'))}
        else:
            result['DueDates']={}
            #Note
        for k,v in result['DueDates'].items():
            if 'sponsor' in str(v):
                result['CloseDate']=self.date2MMDDYYYY(v.split(' - ')[0])
                if 'Posted' not in result:
                    result['Posted']=self.date2MMDDYYYY(v.split(' - ')[0])
        result['Eligibility']=row['Eligibility']
        result['ApplicantLocation']=row['Applicant/Institution Location']
        result['CitizenshipReq']=row['Citizenship']
        result['ActivityLocation']=row['Activity location']
        result['ApplicantType']=row['Applicant type']
        #Career stage
        result['Description']=row['Abstract']
        result['URL']='https:'+row['Link to Pivot-RP'].split(' ')[1]
        result['SolicitationURL']='https:'+row['Website'].split(' ')[1]
        result['Categories']=row['Keywords']
        result['AwardType']=row['Funding type']
        result['MaxAmount']=row['Amount Upper']
        result['Amount']=row['Amount']
        #Amount Note
        #Related Funders
        #Alternate Title
        result['CFDA']=row['CFDA Numbers']
        #Related Programmes
        #Notice
        return result

class SAM(Raw_Data_Index):
    def __init__(self,filename:str,desc_att:str):
        super().__init__(filename,desc_att)
        self.load_data()
    def load_data(self):
        self.df=pd.read_csv(self.filename)
    def get_descriptions(self):
        return pd.DataFrame({'filename':self.filename,'row':self.df.index,'description':self.df[self.description_attribute]})
    def print_title(self,row:int,similarity:float):
        show_color_banner_no_score(self.df.iloc[row]['Title'],similarity)
    def print(self,idx:int,similarity:float):
        show_color_banner(self.df.iloc[idx].Title,similarity)
        show_one('Posted on','sam.gov')
        for attname in self.df.columns:
            if attname==self.description_attribute:
                show_one_underline(attname,self.df.iloc[idx][attname])
                #show_one_limitless('Summary',summary_model(self.df.loc[idx][attname], max_length=280, min_length=140, do_sample=False)[0]['summary_text'])
            else:
                show_one(attname,self.df.iloc[idx][attname])
    def date2MMDDYYYY(self,date:str):
        if isinstance(date,float):
            if isnan(date):
                return ''
            else: print('stumped',date)
        if '.' in date:
            date=date.split('.')[0].strip()
        formats=['%Y-%m-%d %H:%M:%S-%U','%Y-%m-%d','%Y-%m-%dT%H:%M:%S-%U:%W','%Y-%m-%d %H:%M:%S','%Y-%m-%dT%H:%M:%S','%Y-%m-%dT%H:%M+%S:%U','%Y-%m-%dT%H:%M%:%S+%U:%W']

        dt=None
        for f in formats:
            try:
                dt=datetime.strptime(date,f).strftime('%m/%d/%Y')
                break
            except:
                pass
        if not dt:
            print('stumped!',date)
        return dt
    def to_dict(self,idx:int,similarity:float):
        row=self.df.iloc[idx]
        result = self.mk_empty_row()
        result['Similarity']=similarity
        result['Feed']='SAM.gov'
        result['FeedID']=row['NoticeId']
        result['Title']=row['Title']
        result['ProgramID']=row['Sol#']
        result['Sponsor']=row['Department/Ind.Agency']
        #CGAC
        #Sub-Tier
        #FPDS Code
        #Office
        #AAC Code
        result['Posted']=self.date2MMDDYYYY(row['PostedDate'])
        result['AwardType']=row['Type']
        #BaseType
        #ArchiveType
        result['DueDates']={'ArchiveDate':self.date2MMDDYYYY(row['ArchiveDate']),
                'ResponseDeadLine':self.date2MMDDYYYY(row['ResponseDeadLine']),
                'AwardDate':self.date2MMDDYYYY(row['AwardDate'])
                }
        result['CloseDate']=self.date2MMDDYYYY(row['ResponseDeadLine'])
        #SetASideCode
        #SetASide
        #NaicsCode
        #ClassificationCode
        #PopStreetAddress
        #PopCity
        #PopState
        result['ActivityLocation']=row['PopZip']
        #Pop Country
        result['Status']=row['Active']
        #AwardNumber
        result['Amount']=row['Award$']
        #Awardee
        result['Contacts']={'Title':row['PrimaryContactTitle'],
                'Name':row['PrimaryContactFullname'],
                'Email':row['PrimaryContactEmail'],
                'Phone':row['PrimaryContactPhone'],
                'Fax':row['PrimaryContactFax']
                }
        #SecondaryContactTitle, SecondaryContactFullname, SecondaryContactEmail, SecondaryContactPhone,SecondaryConteactFax
        result['SponsorType']=row['OrganizationType']
        #State, City, ZipCode, CountryCode
        result['SolicitationURL']=row['AdditionalInfoLink']
        result['URL']=row['Link']
        result['Description']=row['Description']
        return result

def encode_narratives( narratives ):
    model=SentenceTransformer('all-mpnet-base-v2')
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if torch.cuda.device_count()>1:
        pool=model.start_multi_process_pool()
        embeddings = model.encode_multi_process(narratives,pool,batch_size=64,chunk_size=len(narratives)/100)
        model.stop_multi_process_pool(pool)
    else:
        embeddings = model.encode(narratives,show_progress_bar=True,batch_size=64,device=device)
    ncols = len(embeddings[0])
    attnames = [f'F{i}' for i in range(ncols)]
    return pd.DataFrame(embeddings,columns=attnames)

if __name__ == "__main__":
    args = argv[1:]
    IDIR=args[0]
    target={'CMU':'Summary','MAILER':'Brief Description','NSF':'Synopsis','GRANTS':'Description','SAM':'Description','PIVOT':'Abstract','GFORWARD':'Description'}
    all_data = pd.concat([eval(file.split('/')[-1].split('_')[0])(filename=file,desc_att=target[file.split('/')[-1].split('_')[0]]).get_descriptions() for file in glob(f'{IDIR}/*_S*')],ignore_index=True)
    df = all_data.drop_duplicates(subset=['description'],keep='last',ignore_index=True)#glob pattern matches GFORWARD first, which we would rather limit
    print('Torch enabled?: ',torch.cuda.is_available())
    embeddings = encode_narratives(df.description.astype(str))
    result = pd.concat([df,embeddings],axis=1)
    result.to_pickle(f'{IDIR}/embeddings.pkl')
