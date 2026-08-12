SELECT *,
    CURRENT_TIMESTAMP() AS _ingested_at,
    'AdventureWorks2019.Production.ProductSubcategory' AS _source
FROM {{ source('bronze', 'product_subcategory') }}
WHERE ProductSubcategoryID IS NOT NULL
    AND ProductCategoryID IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY ProductSubcategoryID ORDER BY ProductSubcategoryID) = 1