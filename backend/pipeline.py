import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# 1. Define Column Lists
col_names_cat = ['Sex', 'Occupation', 'Marriage_Status', 'credit_grade']
col_names_num = [
    'Salary', 'credit_score', 'outstanding', 'overdue', 'Coapplicant', 
    'loan_amount', 'loan_term', 'Interest_rate', 'dti', 'lti', 'has_overdue'
]

# 2. Feature Engineering Function
def apply_feature_engineering(df):
    df = df.copy()
    df['dti'] = df['outstanding'] / df['Salary']
    df['lti'] = df['loan_amount'] / df['Salary']
    df['has_overdue'] = (df['overdue'] > 0).astype(int)
    return df

# 3. Create the ColumnTransformer (as defined in the training file)
# Note: In production, the StandardScaler and OneHotEncoder should be the 
# ones PRE-FITTED during training (e.g., loaded via joblib)
preprocess_ct = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), col_names_cat),
        ('num', StandardScaler(), col_names_num)
    ]
)

# 4. Final Pipeline structure
def preprocess_input_for_shap(raw_json_input, fitted_transformer):
    df = pd.DataFrame([raw_json_input])
    
    # 1. Feature Engineering
    df = apply_feature_engineering(df)
    
    # 2. Transform using the transformer passed from the model
    # We don't use the global preprocess_ct anymore
    processed_array = fitted_transformer.transform(df)
    
    return processed_array

