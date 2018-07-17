import glob
import os

from flask import Flask
from sbir_app import absviews
from sklearn.externals import joblib
from utils import utilsvectorizer as uv


# create app instance
app = Flask(__name__)

# load model at app startup
gs_reg = joblib.load(os.path.join('.','models', 'Lasso_reg_phase1.pkl'))


# dictionary of agency acronym to agency denomination
agency_name = {'usda' : 'Department of Agriculture',
                'doc' : 'Department of Commerce',
                'dod' : 'Department of Defense',
                'ed' : 'Department of Education',
                'doe' : 'Department of Energy',
                'hhs' : 'Department of Health and Human Services',
                'dhs' : 'Department of Homeland Security',
                'dot' : 'Department of Transportation',
                'epa' : 'Environmental Protection Agency',
                'nasa' : 'National Aeronautics and Space Administration',
                'nsf' : 'National Science Foundation'}

# mapping for agency logo
agency_logo = {'usda' : 'usda.png',
                'doc' : 'department-of-commerce.png',
                'dod' : 'dod.png',
                'ed' : 'department-of-education.png',
                'doe' : 'department-of-energy.png',
                'hhs' : 'department-of-health.png',
                'dhs' : 'dhs.png',
                'dot' : 'department-of-transportation.png',
                'epa' : 'enviromental-protection-agency.png',
                'nasa' : 'nasa.png',
                'nsf' : 'nsf.png'}
