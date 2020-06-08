from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Histogram
from prometheus_client import Summary
from prometheus_client import Info
from prometheus_client import Enum

subscribed_candidates_count = Counter(	'slickhire_candidates_subscribed_count', \
							'Total number of candidates handled by SlickHire', \
							['company_name', 'job_profile'])

registered_candidates_count = Counter(	'slickhire_candidates_registered_count', \
							'Total number of candidates handled by SlickHire', \
							['company_name', 'job_profile'])

discarded_candidates_count = Counter(	'slickhire_candidates_discarded_count', \
									'Total number of candidates discarded for a given job profile', \
									['company_name', 'job_profile'])

optedout_candidates_count = Counter(	'slickhire_candidates_optedout_count', \
									'Total number of candidates opted out for a given job profile', \
									['company_name', 'job_profile'])

hired_candidates_count = Counter(	'slickhire_candidates_hired_count', \
										'Total number of candidates hired for a given job profile', \
										['company_name', 'job_profile'])

interested_candidates_count = Counter(	'slickhire_candidates_interested_count', \
										'Total number of interested candidates for a given job profile', \
										['company_name', 'job_profile'])

interviews_scheduled_count = Counter(	'slickhire_candidates_interviews_scheduled_count', \
									'Total number of candidates for whom the interview is scheduled for a given job profile', \
									['company_name', 'job_profile'])

interviewed_candidates_count = Counter(	'slickhire_candidates_interviewed_count', \
										'Total number of candidates interviewed for a given job profile', \
										['company_name', 'job_profile'])

rejected_candidates_count = Counter(	'slickhire_candidates_rejected_count', \
									'Total number of candidates rejected for a given profile', \
									['company_name', 'job_profile'])

onhold_candidates_count = Counter(	'slickhire_candidates_onhold_count', \
									'Total number of candidates on hold for a given job profile', \
									['company_name', 'job_profile'])

candidates_state_transition = Histogram( 'slickhire_candidates_state_transition',
										 'Helps to understand the transition of candidates from one state to another in terms of time (hours)', \
										 ['company_name', 'job_profile', 'candidate_state'], \
										 buckets=[0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 78, 84, 90, 96, 102, 108, 114, 120, 126, 132, 138, 144, 150, 156, 162, 168])
