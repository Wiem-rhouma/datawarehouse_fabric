SELECT
    p.ProductID,
    p.Name AS ProductName,
    p.ListPrice,
    p.StandardCost,
    sc.Name AS SubcategoryName,
    c.Name AS CategoryName
FROM {{ ref('stg_product') }} p
LEFT JOIN {{ ref('stg_product_subcategory') }} sc
    ON p.ProductSubcategoryID = sc.ProductSubcategoryID
LEFT JOIN {{ ref('stg_product_category') }} c
    ON sc.ProductCategoryID = c.ProductCategoryID