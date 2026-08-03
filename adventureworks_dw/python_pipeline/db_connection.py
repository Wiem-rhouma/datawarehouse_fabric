"""
db_connection.py
-----------------
Fournit une connexion réutilisable vers la base SQL Server locale
(AdventureWorks2019), utilisée par les scripts 01_silver_local.py
et 02_gold_local.py.

Authentification : Windows Authentication (Trusted Connection).
Utilisable car le script tourne sur le PC local où la base a été
restaurée, avec un compte disposant des droits complets.
"""

from sqlalchemy import create_engine

# ---- Paramètres de connexion --------------------------------------
SERVER = r"localhost\SQLEXPRESS"
DATABASE = "AdventureWorks2019"
DRIVER = "ODBC Driver 18 for SQL Server"


def get_engine():
    """
    Crée et retourne un moteur SQLAlchemy connecté à la base locale.
    fast_executemany=True accélère fortement les écritures de masse
    (utile pour SalesOrderDetail : ~121 000 lignes).
    """
    connection_string = (
        f"mssql+pyodbc://{SERVER}/{DATABASE}"
        f"?driver={DRIVER.replace(' ', '+')}"
        f"&trusted_connection=yes"
        f"&TrustServerCertificate=yes"
    )
    engine = create_engine(connection_string, fast_executemany=True)
    return engine


if __name__ == "__main__":
    # Test rapide de connexion : exécuter ce fichier directement
    # pour vérifier que tout est bien configuré avant de lancer
    # les scripts Silver et Gold.
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.exec_driver_sql("SELECT DB_NAME()")
        print(f"Connexion réussie à la base : {result.fetchone()[0]}")