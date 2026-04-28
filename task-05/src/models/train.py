from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_validate

def train_models(models, preprocessor, X, y):

    results = {}

    for name, model in models.items():

        pipe = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ])

        scores = cross_validate(
            pipe,
            X,
            y,
            cv=5,
            scoring=[
                'accuracy',
                'precision',
                'recall',
                'f1'
            ],
            return_train_score=False
        )

        results[name] = {
            "Accuracy": scores['test_accuracy'].mean(),
            "Precision": scores['test_precision'].mean(),
            "Recall": scores['test_recall'].mean(),
            "F1": scores['test_f1'].mean()
        }

    return results