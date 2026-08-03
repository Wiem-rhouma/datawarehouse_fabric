SELECT
    TerritoryID,
    Name AS TerritoryName,
    CountryRegionCode,
    "Group" AS TerritoryGroup
FROM {{ ref('stg_sales_territory') }}