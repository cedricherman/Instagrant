from flask import Flask
app = Flask(__name__)

from sklearn.externals import joblib
from utils import utilsvectorizer as uv
import os
import glob

gs_reg = joblib.load(os.path.join('.','models', 'Lasso_reg_phase1.pkl'))


# fed_models = glob.glob(os.path.join('.', 'models', '*.pkl'))
# federal_m = {}
# print('Loading models')
# for fed in fed_models:
#     # get filename (basename) and remove extension
#     model_name = os.path.basename(fed).split('.')[0]
#     # load this model into model dict
#     federal_m[model_name] = joblib.load(fed)


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




from sbir_app import absviews
