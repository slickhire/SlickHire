from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Histogram
from prometheus_client import Summary
from prometheus_client import Info
from prometheus_client import Enum

candidates_count = Counter( 'slickhire_candidates_count', \
							'Total number of candidates count per each state', \
							['company_name', 'job_profile', 'candidate_state'])

candidates_state_transition = Histogram( 'slickhire_candidates_state_transition',
										 'Helps to understand the transition of candidates from one state to another in terms of time (hours)', \
										 ['company_name', 'job_profile', 'candidate_state'], \
										 buckets=[0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 78, 84, 90, 96, 102, 108, 114, 120, 126, 132, 138, 144, 150, 156, 162, 168])
