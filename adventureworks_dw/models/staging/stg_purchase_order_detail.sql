SELECT *,
    CURRENT_TIMESTAMP() AS _ingested_at,
    'AdventureWorks2019.Purchasing.PurchaseOrderDetail' AS _source
FROM {{ source('bronze', 'purchase_order_detail') }}
WHERE OrderQty > 0
    AND UnitPrice >= 0
QUALIFY ROW_NUMBER() OVER (PARTITION BY PurchaseOrderDetailID ORDER BY PurchaseOrderDetailID) = 1