import math
import pipeline


CAT_FEATURES = ['Sex', 'Occupation', 'Marriage_Status', 'credit_grade']


def compute_shap(data: dict, model, explainer) -> dict:
    fitted_transformer = model.named_steps['preprocess']
    feature_names_out = fitted_transformer.get_feature_names_out()

    processed_input = pipeline.preprocess_input_for_shap(data, fitted_transformer)
    shap_values = explainer.shap_values(processed_input)

    if isinstance(shap_values, list):
        final_shap_values = shap_values[1][0]
    else:
        final_shap_values = shap_values[0]

    # Aggregate one-hot encoded features back to original names
    aggregated_values = {}
    for name, val in zip(feature_names_out, final_shap_values):
        if name.startswith("cat__"):
            parent_name = name.split("__")[1]
            for original_cat in CAT_FEATURES:
                if original_cat in name:
                    parent_name = original_cat
                    break
        else:
            parent_name = name.split("__")[1]
        aggregated_values[parent_name] = aggregated_values.get(parent_name, 0) + val

    base_value = float(explainer.expected_value)
    shap_sum = sum(aggregated_values.values())
    total_summation = base_value + shap_sum
    probability = 1 / (1 + math.exp(-total_summation))

    return {
        "base_value": base_value,
        "shap_values": {k: round(float(v), 4) for k, v in aggregated_values.items()},
        "log_odds": float(total_summation),
        "probability": round(probability, 4),
    }
