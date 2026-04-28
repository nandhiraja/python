import pandas as pd

def load_data(path):
    df = pd.read_csv(path)

    print(f"\nLoaded {df.shape[0]} records ({df.shape[1]} features)")

    return df