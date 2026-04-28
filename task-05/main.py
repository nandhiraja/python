from src.data.load_data import load_data
from src.data.preprocess_data import clean_data, column_transform
from src.features.feature_engineering import feature_transform

from src.models.model_registry import models
from src.models.train import train_models
from src.models.evaluate import print_results
from src.models.tune import tune_xgboost

from src.utils.save_model import save_model


def main():

    df = load_data("data/customer_data.csv")

    df = clean_data(df)

    df = feature_transform(df)

    preprocessor = column_transform(df)

    X = df.drop("churn", axis=1)
    y = df["churn"]

    results = train_models(
        models,
        preprocessor,
        X,
        y
    )

    print_results(results)

    best_model = tune_xgboost(
        preprocessor,
        X,
        y
    )

    save_model(
        best_model,
        "models/churn_xgb_v2.pkl"
    )


if __name__ == "__main__":
    main()