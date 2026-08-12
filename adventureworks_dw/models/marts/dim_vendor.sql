SELECT
    BusinessEntityID AS VendorID,
    Name AS VendorName,
    CreditRating,
    ActiveFlag
FROM {{ ref('stg_vendor') }}