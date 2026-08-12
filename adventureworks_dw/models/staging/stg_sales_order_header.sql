SELECT *,
    CURRENT_TIMESTAMP() AS _ingested_at,
    'AdventureWorks2019.Sales.SalesOrderHeader' AS _source
FROM {{ source('bronze', 'sales_order_header') }}
WHERE CustomerID IS NOT NULL
    AND (ShipDate IS NULL OR ShipDate >= OrderDate)
QUALIFY ROW_NUMBER() OVER (PARTITION BY SalesOrderID ORDER BY SalesOrderID) = 1