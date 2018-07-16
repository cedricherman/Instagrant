from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Lasso
from sklearn.pipeline import Pipeline
import os

def PredictAmount(abstract_str=''):
    """
    """
    # load appropriate model
    gs_reg = joblib.load(os.path.join('.','models', 'Lasso_reg_phase1.pkl'))
    # make prediction
    USD_amount = gs_reg.predict([abstract_str])
    #
    return USD_amount


def ModelIt(fromUser  = 'Default', births = []):
 in_month = len(births)
 print('The number born is %i' % in_month)
 result = in_month
 if fromUser != 'Default':
   return result
 else:
   return 'check your input'

if __name__ == "__main__":
    pass
