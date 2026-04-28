def print_results(results):

    print("\n=== Model Comparison ===")

    for model, metrics in results.items():

        print(f"\n{model}")

        for metric, value in metrics.items():

            print(f"{metric}: {value:.3f}")