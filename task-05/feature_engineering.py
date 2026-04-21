import numpy as np
import pandas as pd
def feature_transform(df):
    df['avg_monthly_spend'] = df['total_spend'] / (df['tenure_months'] + 1)
    df['days_since_last_login'] = (pd.Timestamp.today() - pd.to_datetime(df['last_login'])).dt.days

    df['tenure_bin'] = pd.cut(df['tenure_months'], bins=[0,12,24,48,100],
                             labels=['0-1yr','1-2yr','2-4yr','4yr+'])   

    return df