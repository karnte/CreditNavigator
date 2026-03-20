import pandas as pd


def preprocess_to_model_input(data: dict, model) -> pd.DataFrame:
    salary = float(data["Salary"])
    denom = salary if salary > 0 else 1e-9

    payload = {
        "Sex": data["Sex"],
        "Occupation": data["Occupation"],
        "Salary": salary,
        "Marriage_Status": data["Marriage_Status"],
        "credit_score": int(data["credit_score"]),
        "credit_grade": data["credit_grade"],
        "outstanding": float(data["outstanding"]),
        "overdue": int(data["overdue"]),
        "Coapplicant": data["Coapplicant"],
        "loan_amount": float(data["loan_amount"]),
        "loan_term": int(data["loan_term"]),
        "Interest_rate": float(data["Interest_rate"]),

        # engineered
        "has_overdue": 1 if data["overdue"] > 0 else 0,
        "dti": float(data["outstanding"]) / denom,
        "lti": float(data["loan_amount"]) / denom,
    }

    df = pd.DataFrame([payload])

    if hasattr(model, "feature_names_in_"):
        required = list(model.feature_names_in_)
        missing = set(required) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required features: {missing}")
        df = df[required]

    return df


def run_prediction(data: dict, model) -> dict:
    model_input = preprocess_to_model_input(data, model)
    classes = model.classes_

    raw_pred = model.predict(model_input)[0]
    proba = model.predict_proba(model_input)[0].tolist() if hasattr(model, "predict_proba") else None
    prob_dict = {str(classes[i]): float(proba[i]) for i in range(len(classes))}

    return {
        "prediction": int(raw_pred),
        "probabilities": prob_dict,
    }
