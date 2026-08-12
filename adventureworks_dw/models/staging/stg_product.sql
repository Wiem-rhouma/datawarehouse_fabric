SELECT *,
    CURRENT_TIMESTAMP() AS _ingested_at,
    'AdventureWorks2019.Production.Product' AS _source
FROM {{ source('bronze', 'product') }}
WHERE ProductID IS NOT NULL
    AND ListPrice >= 0
    AND StandardCost >= 0
QUALIFY ROW_NUMBER() OVER (PARTITION BY ProductID ORDER BY ProductID) = 1