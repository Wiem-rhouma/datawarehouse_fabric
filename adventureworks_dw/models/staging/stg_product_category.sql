SELECT *,
    CURRENT_TIMESTAMP() AS _ingested_at,
    'AdventureWorks2019.Production.ProductCategory' AS _source
FROM {{ source('bronze', 'product_category') }}
WHERE ProductCategoryID IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY ProductCategoryID ORDER BY ProductCategoryID) = 1