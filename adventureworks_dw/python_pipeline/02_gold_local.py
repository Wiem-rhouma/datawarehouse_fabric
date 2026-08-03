import pandas as pd
import numpy as np
from db_connection import get_engine

engine = get_engine()


def load(table_name: str) -> pd.DataFrame:
    return pd.read_sql(f"SELECT * FROM dbo.{table_name}", engine)


def save(df: pd.DataFrame, table_name: str) -> None:
    df.to_sql(table_name, engine, schema="dbo", if_exists="replace",
               index=False, chunksize=5000)


# ---------------------------------------------------------------------
# Dimension 1/5 — dim_customer
# ---------------------------------------------------------------------
def build_dim_customer():
    df = load("stg_customer")

    dim = df[["CustomerID", "PersonID", "StoreID", "TerritoryID"]].copy()
    dim["CustomerType"] = np.where(dim["StoreID"].notna(), "Entreprise", "Particulier")

    save(dim, "dim_customer")
    print(f"dim_customer — {len(dim)} lignes")


# ---------------------------------------------------------------------
# Dimension 2/5 — dim_vendor
# ---------------------------------------------------------------------
def build_dim_vendor():
    df = load("stg_vendor")

    dim = df.rename(columns={"BusinessEntityID": "VendorID", "Name": "VendorName"})
    dim = dim[["VendorID", "VendorName", "CreditRating", "ActiveFlag"]]

    save(dim, "dim_vendor")
    print(f"dim_vendor — {len(dim)} lignes")


# ---------------------------------------------------------------------
# Dimension 3/5 — dim_employee (partagée ventes / achats)
# ---------------------------------------------------------------------
def build_dim_employee():
    df = load("stg_employee")

    dim = df.rename(columns={"BusinessEntityID": "EmployeeID"})
    dim = dim[["EmployeeID", "JobTitle", "HireDate", "Gender"]]

    save(dim, "dim_employee")
    print(f"dim_employee — {len(dim)} lignes")


# ---------------------------------------------------------------------
# Dimension 4/5 — dim_territory
# ---------------------------------------------------------------------
def build_dim_territory():
    df = load("stg_sales_territory")

    dim = df.rename(columns={"Name": "TerritoryName", "Group": "TerritoryGroup"})
    dim = dim[["TerritoryID", "TerritoryName", "CountryRegionCode", "TerritoryGroup"]]

    save(dim, "dim_territory")
    print(f"dim_territory — {len(dim)} lignes")


# ---------------------------------------------------------------------
# Dimension 5/5 — dim_product (fusion produit + sous-catégorie + catégorie)
# ---------------------------------------------------------------------
def build_dim_product():
    product = load("stg_product")
    subcat = load("stg_product_subcategory")
    cat = load("stg_product_category")

    dim = product.merge(
        subcat[["ProductSubcategoryID", "ProductCategoryID", "Name"]]
            .rename(columns={"Name": "SubcategoryName"}),
        on="ProductSubcategoryID", how="left"
    ).merge(
        cat[["ProductCategoryID", "Name"]].rename(columns={"Name": "CategoryName"}),
        on="ProductCategoryID", how="left"
    )

    dim = dim.rename(columns={"Name": "ProductName"})
    dim = dim[["ProductID", "ProductName", "ListPrice", "StandardCost",
               "SubcategoryName", "CategoryName"]]

    save(dim, "dim_product")
    print(f"dim_product — {len(dim)} lignes")


# ---------------------------------------------------------------------
# Dimension bonus — dim_date (générée, pas issue d'une source)
# ---------------------------------------------------------------------
def build_dim_date():
    dates = pd.date_range(start="2011-01-01", end="2014-12-31", freq="D")

    dim = pd.DataFrame({"FullDate": dates})
    dim["DateKey"] = dim["FullDate"].dt.strftime("%Y%m%d").astype(int)
    dim["Year"] = dim["FullDate"].dt.year
    dim["Quarter"] = dim["FullDate"].dt.quarter
    dim["Month"] = dim["FullDate"].dt.month
    dim["MonthName"] = dim["FullDate"].dt.strftime("%B")
    dim["DayOfWeek"] = dim["FullDate"].dt.dayofweek + 1  # 1=lundi
    dim["DayName"] = dim["FullDate"].dt.strftime("%A")

    save(dim, "dim_date")
    print(f"dim_date — {len(dim)} lignes")


# ---------------------------------------------------------------------
# Fait 1/2 — fct_sales (grain : une ligne de commande de vente)
# ---------------------------------------------------------------------
def build_fct_sales():
    soh = load("stg_sales_order_header")
    sod = load("stg_sales_order_detail")

    fact = sod.merge(soh, on="SalesOrderID", how="inner", suffixes=("", "_soh"))

    fact["EmployeeID"] = fact["SalesPersonID"]
    fact["DeliveryDelayDays"] = (fact["ShipDate"] - fact["OrderDate"]).dt.days
    fact["SalesChannel"] = np.where(fact["SalesPersonID"].isna(), "Online", "Sales Rep")

    fact = fact[[
        "SalesOrderDetailID", "SalesOrderID", "OrderDate", "CustomerID",
        "EmployeeID", "TerritoryID", "ProductID", "OrderQty", "UnitPrice",
        "UnitPriceDiscount", "LineTotal", "ShipDate",
        "DeliveryDelayDays", "SalesChannel"
    ]]

    save(fact, "fct_sales")
    print(f"fct_sales — {len(fact)} lignes")


# ---------------------------------------------------------------------
# Fait 2/2 — fct_purchases (grain : une ligne de commande d'achat)
# ---------------------------------------------------------------------
def build_fct_purchases():
    poh = load("stg_purchase_order_header")
    pod = load("stg_purchase_order_detail")

    fact = pod.merge(poh, on="PurchaseOrderID", how="inner", suffixes=("", "_poh"))

    fact["ReceptionDelayDays"] = (fact["ShipDate"] - fact["OrderDate"]).dt.days

    fact = fact[[
        "PurchaseOrderDetailID", "PurchaseOrderID", "OrderDate", "VendorID",
        "EmployeeID", "ProductID", "OrderQty", "UnitPrice", "LineTotal",
        "ShipDate", "ReceptionDelayDays"
    ]]

    save(fact, "fct_purchases")
    print(f"fct_purchases — {len(fact)} lignes")


# ---------------------------------------------------------------------
# Exécution complète (respecte l'ordre des dépendances)
# ---------------------------------------------------------------------
def main():
    print("=== Couche Gold — exécution locale ===\n")
    build_dim_customer()
    build_dim_vendor()
    build_dim_employee()
    build_dim_territory()
    build_dim_product()
    build_dim_date()
    build_fct_sales()
    build_fct_purchases()
    print("\n=== Couche Gold terminée : 6 dimensions + 2 faits créés ===")


if __name__ == "__main__":
    main()