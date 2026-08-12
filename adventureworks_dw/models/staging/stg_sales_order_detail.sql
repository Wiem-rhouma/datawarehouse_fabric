SELECT *,
    CURRENT_TIMESTAMP() AS _ingested_at,
    'AdventureWorks2019.Sales.SalesOrderDetail' AS _source
FROM {{ source('bronze', 'sales_order_detail') }}
WHERE OrderQty > 0
    AND UnitPrice >= 0
QUALIFY ROW_NUMBER() OVER (PARTITION BY SalesOrderDetailID ORDER BY SalesOrderDetailID) = 1