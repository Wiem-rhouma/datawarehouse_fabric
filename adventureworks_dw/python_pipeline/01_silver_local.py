import pandas as pd
from datetime import datetime
from db_connection import get_engine

engine = get_engine()


def load(query: str) -> pd.DataFrame:
    """Charge le résultat d'une requête SQL dans un DataFrame pandas."""
    return pd.read_sql(query, engine)


def save(df: pd.DataFrame, table_name: str) -> None:
    """Écrit un DataFrame dans la base locale, en remplaçant la table."""
    df.to_sql(table_name, engine, schema="dbo", if_exists="replace",
               index=False, chunksize=5000)


def add_technical_columns(df: pd.DataFrame, source: str) -> pd.DataFrame:
    """Ajoute les deux colonnes de traçabilité communes à tous les modèles."""
    df = df.copy()
    df["_ingested_at"] = datetime.now()
    df["_source"] = source
    return df


# ---------------------------------------------------------------------
# 1/11 — Customer
# ---------------------------------------------------------------------
def build_stg_customer():
    df = load("SELECT * FROM Sales.Customer")
    before = len(df)

    df = df.drop_duplicates(subset=["CustomerID"])
    df = df[df["CustomerID"].notna()]
    df = add_technical_columns(df, "AdventureWorks2019.Sales.Customer")

    save(df, "stg_customer")
    print(f"[1/11] stg_customer — avant : {before} | après : {len(df)}")


# ---------------------------------------------------------------------
# 2/11 — Product
# ---------------------------------------------------------------------
def build_stg_product():
    df = load("SELECT * FROM Production.Product")
    before = len(df)

    df = df.drop_duplicates(subset=["ProductID"])
    df = df[df["ProductID"].notna()]
    df = df[(df["ListPrice"] >= 0) & (df["StandardCost"] >= 0)]
    df = add_technical_columns(df, "AdventureWorks2019.Production.Product")

    save(df, "stg_product")
    print(f"[2/11] stg_product — avant : {before} | après : {len(df)}")


# ---------------------------------------------------------------------
# 3/11 — SalesOrderHeader
# ---------------------------------------------------------------------
def build_stg_sales_order_header():
    df = load("SELECT * FROM Sales.SalesOrderHeader")
    before = len(df)

    df = df.drop_duplicates(subset=["SalesOrderID"])
    df = df[df["CustomerID"].notna()]
    df = df[df["ShipDate"].isna() | (df["ShipDate"] >= df["OrderDate"])]
    df = add_technical_columns(df, "AdventureWorks2019.Sales.SalesOrderHeader")

    save(df, "stg_sales_order_header")
    print(f"[3/11] stg_sales_order_header — avant : {before} | après : {len(df)}")


# ---------------------------------------------------------------------
# 4/11 — SalesOrderDetail
# ---------------------------------------------------------------------
def build_stg_sales_order_detail():
    df = load("SELECT * FROM Sales.SalesOrderDetail")
    before = len(df)

    df = df.drop_duplicates(subset=["SalesOrderDetailID"])
    df = df[(df["OrderQty"] > 0) & (df["UnitPrice"] >= 0)]
    df = add_technical_columns(df, "AdventureWorks2019.Sales.SalesOrderDetail")

    save(df, "stg_sales_order_detail")
    print(f"[4/11] stg_sales_order_detail — avant : {before} | après : {len(df)}")


# ---------------------------------------------------------------------
# 5/11 — SalesTerritory
# ---------------------------------------------------------------------
def build_stg_sales_territory():
    df = load("SELECT * FROM Sales.SalesTerritory")
    before = len(df)

    df = df.drop_duplicates(subset=["TerritoryID"])
    df = df[df["TerritoryID"].notna()]
    df = add_technical_columns(df, "AdventureWorks2019.Sales.SalesTerritory")

    save(df, "stg_sales_territory")
    print(f"[5/11] stg_sales_territory — avant : {before} | après : {len(df)}")


# ---------------------------------------------------------------------
# 6/11 — ProductCategory
# ---------------------------------------------------------------------
def build_stg_product_category():
    df = load("SELECT * FROM Production.ProductCategory")
    before = len(df)

    df = df.drop_duplicates(subset=["ProductCategoryID"])
    df = df[df["ProductCategoryID"].notna()]
    df = add_technical_columns(df, "AdventureWorks2019.Production.ProductCategory")

    save(df, "stg_product_category")
    print(f"[6/11] stg_product_category — avant : {before} | après : {len(df)}")


# ---------------------------------------------------------------------
# 7/11 — ProductSubcategory
# ---------------------------------------------------------------------
def build_stg_product_subcategory():
    df = load("SELECT * FROM Production.ProductSubcategory")
    before = len(df)

    df = df.drop_duplicates(subset=["ProductSubcategoryID"])
    df = df[df["ProductSubcategoryID"].notna() & df["ProductCategoryID"].notna()]
    df = add_technical_columns(df, "AdventureWorks2019.Production.ProductSubcategory")

    save(df, "stg_product_subcategory")
    print(f"[7/11] stg_product_subcategory — avant : {before} | après : {len(df)}")


# ---------------------------------------------------------------------
# 8/11 — PurchaseOrderHeader
# ---------------------------------------------------------------------
def build_stg_purchase_order_header():
    df = load("SELECT * FROM Purchasing.PurchaseOrderHeader")
    before = len(df)

    df = df.drop_duplicates(subset=["PurchaseOrderID"])
    df = df[df["VendorID"].notna()]
    df = df[df["ShipDate"].isna() | (df["ShipDate"] >= df["OrderDate"])]
    df = add_technical_columns(df, "AdventureWorks2019.Purchasing.PurchaseOrderHeader")

    save(df, "stg_purchase_order_header")
    print(f"[8/11] stg_purchase_order_header — avant : {before} | après : {len(df)}")


# ---------------------------------------------------------------------
# 9/11 — PurchaseOrderDetail
# ---------------------------------------------------------------------
def build_stg_purchase_order_detail():
    df = load("SELECT * FROM Purchasing.PurchaseOrderDetail")
    before = len(df)

    df = df.drop_duplicates(subset=["PurchaseOrderDetailID"])
    df = df[(df["OrderQty"] > 0) & (df["UnitPrice"] >= 0)]
    df = add_technical_columns(df, "AdventureWorks2019.Purchasing.PurchaseOrderDetail")

    save(df, "stg_purchase_order_detail")
    print(f"[9/11] stg_purchase_order_detail — avant : {before} | après : {len(df)}")


# ---------------------------------------------------------------------
# 10/11 — Vendor
# ---------------------------------------------------------------------
def build_stg_vendor():
    df = load("SELECT * FROM Purchasing.Vendor")
    before = len(df)

    df = df.drop_duplicates(subset=["BusinessEntityID"])
    df = df[df["BusinessEntityID"].notna()]
    df = add_technical_columns(df, "AdventureWorks2019.Purchasing.Vendor")

    save(df, "stg_vendor")
    print(f"[10/11] stg_vendor — avant : {before} | après : {len(df)}")


# ---------------------------------------------------------------------
# 11/11 — Employee (exclusion d'OrganizationNode, incompatible Delta)
# ---------------------------------------------------------------------
def build_stg_employee():
    # OrganizationNode (type hierarchyid) est exclue directement dans la
    # requete SQL : pyodbc ne sait pas lire ce type de colonne, meme pour
    # la rejeter apres coup (erreur "ODBC SQL type -151 is not supported").
    query = """
        SELECT BusinessEntityID, NationalIDNumber, LoginID, OrganizationLevel,
               JobTitle, BirthDate, MaritalStatus, Gender, HireDate,
               SalariedFlag, VacationHours, SickLeaveHours, CurrentFlag,
               rowguid, ModifiedDate
        FROM HumanResources.Employee
    """
    df = load(query)
    before = len(df)

    df = df.drop_duplicates(subset=["BusinessEntityID"])
    df = df[df["BusinessEntityID"].notna()]
    df = add_technical_columns(df, "AdventureWorks2019.HumanResources.Employee")

    save(df, "stg_employee")
    print(f"[11/11] stg_employee — avant : {before} | après : {len(df)}")


# ---------------------------------------------------------------------
# Exécution complète
# ---------------------------------------------------------------------
def main():
    print("=== Couche Silver — exécution locale ===\n")
    build_stg_customer()
    build_stg_product()
    build_stg_sales_order_header()
    build_stg_sales_order_detail()
    build_stg_sales_territory()
    build_stg_product_category()
    build_stg_product_subcategory()
    build_stg_purchase_order_header()
    build_stg_purchase_order_detail()
    build_stg_vendor()
    build_stg_employee()
    print("\n=== Couche Silver terminée : 11/11 tables créées ===")


if __name__ == "__main__":
    main()