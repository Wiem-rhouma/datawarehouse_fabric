# AdventureWorks 2019 Data Warehouse (Microsoft Fabric, dbt, PySpark)

Data warehouse built during my data engineering internship at Biware Consulting (Jul to Aug 2026), on the public AdventureWorks 2019 sample database. Published with the company's permission.

## Goal

Turn the raw AdventureWorks source (72 tables) into a clean, tested model for sales and purchasing reporting.

## Architecture

Medallion layers (Bronze, Silver, Gold):

- **Bronze:** 11 source tables ingested into a Microsoft Fabric Lakehouse with Copy Job.
- **Silver:** cleaned tables built in PySpark and pandas. 307,407 rows processed with no loss.
- **Gold:** star/constellation model (2 fact tables, 6 dimensions) combining sales and purchases.

## What is in this repository

| Folder | Content |
|---|---|
| `adventureworks_dw/models/staging` | 11 dbt staging models + source definitions |
| `adventureworks_dw/models/marts` | 6 dimensions (customer, date, employee, product, territory, vendor) and 2 facts (sales, purchases), with dbt tests |
| `adventureworks_dw/python_pipeline` | Local Python pipeline: Silver, Gold, and a revenue forecast with Prophet (`03_predictive_model.py`) |

The Fabric notebooks, the Power BI report and the Text-to-SQL assistant are not included in this repository.

## Data model

Fact tables: `fct_sales`, `fct_purchases`
Dimensions: `dim_customer`, `dim_date`, `dim_employee`, `dim_product`, `dim_territory`, `dim_vendor`

## Forecasting

Revenue forecast with Prophet, validated with rolling-origin cross-validation (6 folds) against a naive baseline. In my tests the model became reliable from about 9 quarters of history. A model card is saved as JSON (`model_card_example.json`).

## Data quality findings

Issues found before reporting:

- The last quarter in the source data is incomplete.
- Some bikes have no purchase lines, so their margin is not comparable.

## Run it

```bash
cd adventureworks_dw
pip install -r python_pipeline/requirements.txt
# set your own connection settings (not included), then:
python python_pipeline/01_silver_local.py
python python_pipeline/02_gold_local.py
dbt run
dbt test
```

## Stack

Microsoft Fabric, PySpark, pandas, dbt, SQL Server, Python, Prophet

## Author

Wiem Rhouma, Data Science engineering student, Faculty of Sciences of Sfax.
