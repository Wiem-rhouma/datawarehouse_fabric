SELECT *,
    CURRENT_TIMESTAMP() AS _ingested_at,
    'AdventureWorks2019.Sales.Customer' AS _source
FROM {{ source('bronze', 'customer') }}
WHERE CustomerID IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY CustomerID ORDER BY CustomerID) = 1