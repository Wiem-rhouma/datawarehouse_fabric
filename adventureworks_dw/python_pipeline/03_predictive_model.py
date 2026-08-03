import pandas as pd
import numpy as np
from prophet import Prophet
from db_connection import get_engine

engine = get_engine()


def load_quarterly_sales() -> pd.DataFrame:
    """
    Agrège le CA total par trimestre à partir de fct_sales.
    Exclut tout le T2 2014 (avril-juin), car juin 2014 est incomplet
    dans la base source, ce qui rend le trimestre entier non comparable.
    """
    query = """
        SELECT
            DATEFROMPARTS(YEAR(OrderDate), ((DATEPART(quarter, OrderDate) - 1) * 3) + 1, 1) AS ds,
            SUM(LineTotal) AS y
        FROM dbo.fct_sales
        WHERE OrderDate < '2014-04-01'
        GROUP BY YEAR(OrderDate), DATEPART(quarter, OrderDate)
        ORDER BY ds
    """
    df = pd.read_sql(query, engine)
    df["ds"] = pd.to_datetime(df["ds"])
    return df


def train_model(train: pd.DataFrame) -> Prophet:
    """Entraîne un modèle Prophet sur les données d'entraînement."""
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False
    )
    model.fit(train)
    return model


def rolling_cv_prophet(df: pd.DataFrame, initial_train: int) -> pd.DataFrame:
    """
    Cross-validation temporelle (rolling-origin, horizon = 1 trimestre).
    Pour chaque pli : entraîne sur tout l'historique disponible jusqu'au
    point courant, prédit le trimestre suivant, avance d'un point.
    """
    results = []
    n = len(df)

    for cutoff in range(initial_train, n):
        train = df.iloc[:cutoff].copy()
        actual_row = df.iloc[cutoff]

        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False
        )
        model.fit(train)

        future = pd.DataFrame({"ds": [actual_row["ds"]]})
        forecast = model.predict(future)
        predicted = forecast["yhat"].iloc[0]

        results.append({
            "ds": actual_row["ds"],
            "train_size": cutoff,
            "reel": actual_row["y"],
            "predit_prophet": predicted
        })

    return pd.DataFrame(results)


def baseline_naive_seasonal(df: pd.DataFrame, initial_train: int) -> pd.DataFrame:
    """
    Baseline naïve saisonnière : prédit que le trimestre suivant sera égal
    au même trimestre de l'année précédente (décalage de 4 trimestres).
    Si l'historique est trop court (< 4 trimestres avant le cutoff),
    utilise la dernière valeur connue à la place (naïve simple).
    """
    results = []
    n = len(df)

    for cutoff in range(initial_train, n):
        actual_row = df.iloc[cutoff]

        if cutoff >= 4:
            predicted = df.iloc[cutoff - 4]["y"]
        else:
            predicted = df.iloc[cutoff - 1]["y"]

        results.append({
            "ds": actual_row["ds"],
            "predit_baseline": predicted
        })

    return pd.DataFrame(results)


def compare_prophet_vs_baseline(df: pd.DataFrame, initial_train: int = 6) -> pd.DataFrame:
    """Exécute la CV pour Prophet et la baseline, puis compare les erreurs."""
    cv_prophet = rolling_cv_prophet(df, initial_train)
    cv_baseline = baseline_naive_seasonal(df, initial_train)

    comparison = cv_prophet.merge(cv_baseline, on="ds")

    comparison["erreur_pct_prophet"] = (
        (comparison["reel"] - comparison["predit_prophet"]).abs() / comparison["reel"]
    ) * 100
    comparison["erreur_pct_baseline"] = (
        (comparison["reel"] - comparison["predit_baseline"]).abs() / comparison["reel"]
    ) * 100

    print(f"\n--- Cross-validation temporelle ({len(comparison)} plis) ---")
    print(comparison[[
        "ds", "train_size", "reel", "predit_prophet", "erreur_pct_prophet",
        "predit_baseline", "erreur_pct_baseline"
    ]].round(2).to_string(index=False))

    mape_prophet = comparison["erreur_pct_prophet"].mean()
    mape_baseline = comparison["erreur_pct_baseline"].mean()

    print(f"\nMAPE moyen Prophet   (sur {len(comparison)} plis) : {mape_prophet:.2f}%")
    print(f"MAPE moyen Baseline  (sur {len(comparison)} plis) : {mape_baseline:.2f}%")

    if mape_prophet < mape_baseline:
        print(f"\n=> Prophet fait mieux que la baseline naïve ({mape_prophet:.2f}% vs {mape_baseline:.2f}%).")
    else:
        print(f"\n=> ATTENTION : la baseline naïve fait aussi bien ou mieux que Prophet "
              f"({mape_baseline:.2f}% vs {mape_prophet:.2f}%). À signaler honnêtement.")

    return comparison


if __name__ == "__main__":
    df = load_quarterly_sales()
    print(f"Total trimestres disponibles (T2 2014 exclu) : {len(df)}")
    print(df)

    comparison = compare_prophet_vs_baseline(df, initial_train=6)