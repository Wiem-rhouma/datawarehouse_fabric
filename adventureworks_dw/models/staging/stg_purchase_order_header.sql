SELECT *,
    CURRENT_TIMESTAMP() AS _ingested_at,
    'AdventureWorks2019.Purchasing.PurchaseOrderHeader' AS _source
FROM {{ source('bronze', 'purchase_order_header') }}
WHERE VendorID IS NOT NULL
    AND (ShipDate IS NULL OR ShipDate >= OrderDate)
QUALIFY ROW_NUMBER() OVER (PARTITION BY PurchaseOrderID ORDER BY PurchaseOrderID) = 1