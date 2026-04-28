from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from xgboost import XGBClassifier

def tune_xgboost(preprocessor, X, y):

    pipe = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", XGBClassifier(eval_metric='logloss'))
    ])

    param_grid = {
        "model__max_depth": [4, 6, 8],
        "model__learning_rate": [0.01, 0.05, 0.1],
        "model__n_estimators": [100, 200, 300]
    }

    grid = GridSearchCV(
        pipe,
        param_grid,
        cv=5,
        scoring='f1'
    )

    grid.fit(X, y)

    print("\n=== Best Model: XGBoost ===")
    print("Best Params:", grid.best_params_)

    return grid.best_estimator_