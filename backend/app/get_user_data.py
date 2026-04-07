def get_test_user(scenario="default"):
    scenarios = {
        "high_risk": {
            "Sex": 'Male',
            "Occupation": 'Salaried_Employee',
            "Salary": 55000.0,
            "Marriage_Status": 'Single',
            "credit_score": 652,
            "credit_grade": 'FF',
            "outstanding": 601387.0,
            "overdue": 60,
            "Coapplicant": 0,
            "loan_amount": 800000.0,
            "loan_term": 26,
            "Interest_rate": 5.83
        },
        "default": {
            "Sex": 'Female',
            "Occupation": 'SME_Owner',
            "Salary": 35581.0,
            "Marriage_Status": 'Single',
            "credit_score": 695,
            "credit_grade": 'DD',
            "outstanding": 576390,
            "overdue": 0,
            "Coapplicant": 0,
            "loan_amount": 500000.0,
            "loan_term": 26,
            "Interest_rate": 5.78
        },
        "fifty_fifty": {
            "Sex": "Male",
            "Occupation": "Salaried_Employee",
            "Salary": 55000,
            "Marriage_Status": "Single",
            "credit_score": 700,
            "credit_grade": "CC",
            "outstanding": 70000,
            "overdue": 15,
            "Coapplicant": 0,
            "loan_amount": 1100000,
            "loan_term": 2727,
            "Interest_rate": 5.82
        }
    }
            
    user_dict = scenarios.get(scenario, scenarios["default"]).copy()
    user_dict["scenario"] = scenario
    return user_dict