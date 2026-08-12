SELECT *,
    CURRENT_TIMESTAMP() AS _ingested_at,
    'AdventureWorks2019.Sales.SalesTerritory' AS _source
FROM {{ source('bronze', 'sales_territory') }}
WHERE TerritoryID IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY TerritoryID ORDER BY TerritoryID) = 1