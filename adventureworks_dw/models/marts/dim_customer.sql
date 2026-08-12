SELECT
    CustomerID,
    PersonID,
    StoreID,
    TerritoryID,
    CASE WHEN StoreID IS NOT NULL THEN 'Entreprise' ELSE 'Particulier' END AS CustomerType
FROM {{ ref('stg_customer') }}