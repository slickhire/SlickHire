from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Histogram
from prometheus_client import Summary
from prometheus_client import Info
from prometheus_client import Enum

class PromStats:
	__instance = None
   
	@staticmethod 
	def Instance():
		""" Static access method. """
		if PromStats.__instance == None:
			PromStats()
		return PromStats.__instance
		
	def __init__(self):
		""" Virtually private constructor. """
		if PromStats.__instance != None:
			raise Exception("This class is a PromStats!")
		else:
			PromStats.__instance = self
		 
		self.__candidatesCount = Counter('slickhire_candidates_count', \
								  'Total number of candidates handled by SlickHire', \
								  ['company_name', 'job_profile'])
		self.__discardedCandidatesCount = Counter('slickhire_candidates_discarded_count', \
								  'Total number of candidates discarded for a given job profile', \
								  ['company_name', 'job_profile'])
		self.__optedOutCandidatesCount = Counter('slickhire_candidates_optedout_count', \
								  'Total number of candidates opted out for a given job profile', \
								  ['company_name', 'job_profile'])
		self.__shortlistedCandidatesCount = Counter('slickhire_candidates_shortlisted_count', \
								  'Total number of candidates shortlisted for a given job profile', \
								  ['company_name', 'job_profile'])
		self.__interestedCandidatesCount = Counter('slickhire_candidates_interested_count', \
								  'Total number of interested candidates for a given job profile', \
								  ['company_name', 'job_profile'])
		self.__interviewsScheduledCount = Counter('slickhire_candidates_interviews_scheduled_count', \
								  'Total number of candidates for whom the interview is scheduled for a given job profile', \
								  ['company_name', 'job_profile'])
		self.__interviewedCandidatesCount = Counter('slickhire_candidates_interviewed_count', \
								  'Total number of candidates interviewed for a given job profile', \
								  ['company_name', 'job_profile'])
		self.__rejectedCandidatesCount = Counter('slickhire_candidates_rejected_count', \
								  'Total number of candidates rejected for a given profile', \
								  ['company_name', 'job_profile'])
		self.__onHoldCandidatesCount = Counter('slickhire_candidates_onhold_count', \
								  'Total number of candidates on hold for a given job profile', \
								  ['company_name', 'job_profile'])
	
	def increment_candidates_count(self, company_name, job_profile):
		self.__candidatesCount.labels(company_name, job_profile).inc()
		
	def increment_discarded_candidates_count(self, company_name, job_profile):
		self.__discardedCandidatesCount.labels(company_name, job_profile).inc()
		
	def increment_optedout_candidates_count(self, company_name, job_profile):
		self.__optedOutCandidatesCount.labels(company_name, job_profile).inc()
		
	def increment_interested_candidates_count(self, company_name, job_profile):
		self.__interestedCandidatesCount.labels(company_name, job_profile).inc()
		
	def increment_shortlisted_candidates_count(self, company_name, job_profile):
		self.__shortlistedCandidatesCount.labels(company_name, job_profile).inc()
		
	def increment_interview_scheduled_count(self, company_name, job_profile):
		self.__interviewsScheduledCount.labels(company_name, job_profile).inc()
	
	def increment_interviews_candidates_count(self, company_name, job_profile):
		self.__interviewedCandidatesCount.labels(company_name, job_profile).inc()
		
	def increment_rejected_candidates_count(self, company_name, job_profile):
		self.__rejectedCandidatesCount.labels(company_name, job_profile).inc()
		
	def increment_onhold_candidates_count(self, company_name, job_profile):
		self.__onHoldCandidatesCount.labels(company_name, job_profile).inc()
