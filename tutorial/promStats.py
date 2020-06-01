from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Histogram
from prometheus_client import Summary
from prometheus_client import Info
from prometheus_client import Enum

candidates_count = Counter(	'slickhire_candidates_count', \
							'Total number of candidates handled by SlickHire', \
							['company_name', 'job_profile'])

discarded_candidates_count = Counter(	'slickhire_candidates_discarded_count', \
									'Total number of candidates discarded for a given job profile', \
									['company_name', 'job_profile'])

optedout_candidates_count = Counter(	'slickhire_candidates_optedout_count', \
									'Total number of candidates opted out for a given job profile', \
									['company_name', 'job_profile'])

shortlisted_candidates_count = Counter(	'slickhire_candidates_shortlisted_count', \
										'Total number of candidates shortlisted for a given job profile', \
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
