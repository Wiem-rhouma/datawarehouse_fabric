SELECT *,
    CURRENT_TIMESTAMP() AS _ingested_at,
    'AdventureWorks2019.Purchasing.Vendor' AS _source
FROM {{ source('bronze', 'vendor') }}
WHERE BusinessEntityID IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY BusinessEntityID ORDER BY BusinessEntityID) = 1