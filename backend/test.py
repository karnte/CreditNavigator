import json
import os
from pathlib import Path
from pkgutil import get_data
import numpy as np
import shap
import pandas as pd
import pipeline
import main
import get_user_data


# ... model loading ...
main.load_model()

fitted_transformer = main.MODEL.named_steps['preprocess']
lgbm_model_only = main.MODEL.named_steps['lgbm']


user_data = get_user_data.get_test_user("fifty_fifty")
processed_input = pipeline.preprocess_input_for_shap(user_data, fitted_transformer)
explainer = shap.TreeExplainer(lgbm_model_only)
shap_values = explainer.shap_values(processed_input)

print("SHAP values calculated successfully!")

# 1. Extract the feature names from the fitted transformer
feature_names_out = fitted_transformer.get_feature_names_out()
# 2. Extract SHAP values for the positive class (Class 1)
if isinstance(shap_values, list):
    final_shap_values = shap_values[1][0]
else:
    final_shap_values = shap_values[0]

# 3. Aggregate values back to original feature names
# We group by the prefix (cat__Sex, num__Salary, etc.)
aggregated_values = {}

for name, val in zip(feature_names_out, final_shap_values):
    # Determine the "parent" name
    if name.startswith("cat__"):
        # Extract name between 'cat__' and the category value
        # e.g., 'cat__Occupation_Freelancer' -> 'Occupation'
        parent_name = name.split("__")[1].split("_")[0] 
        # Note: If your feature name has underscores like 'Marriage_Status', 
        # use: parent_name = "_".join(name.split("__")[1].split("_")[:-1])
        # A safer way using your known cat list:
        for original_cat in ['Sex', 'Occupation', 'Marriage_Status', 'credit_grade']:
            if original_cat in name:
                parent_name = original_cat
                break
    else:
        # e.g., 'num__Salary' -> 'Salary'
        parent_name = name.split("__")[1]
    
    # Add the SHAP value to the sum for that parent feature
    aggregated_values[parent_name] = aggregated_values.get(parent_name, 0) + val

# 4. Construct final structure
output = {
    "base_value": float(explainer.expected_value),
    "values": {k: round(float(v), 2) for k, v in aggregated_values.items()}
}
# output["values"] = dict(sorted(output["values"].items(), key=lambda item: abs(item[1]), reverse=True))

# print(json.dumps(output, indent=2))

shap_sum = sum(aggregated_values.values())


total_summation = output["base_value"] + shap_sum
output["summation"] = float(total_summation)

import math
probability = 1 / (1 + math.exp(-total_summation))
output["probability"] = round(float(probability), 4)

print(user_data.get("scenario", "N/A"))
print(json.dumps(output, indent=2))