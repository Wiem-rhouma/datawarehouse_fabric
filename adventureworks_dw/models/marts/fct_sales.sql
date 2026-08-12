SELECT
    sod.SalesOrderDetailID,
    sod.SalesOrderID,
    soh.OrderDate,
    soh.CustomerID,
    soh.SalesPersonID AS EmployeeID,
    soh.TerritoryID,
    sod.ProductID,
    sod.OrderQty,
    sod.UnitPrice,
    sod.UnitPriceDiscount,
    sod.LineTotal,
    soh.ShipDate,
    DATEDIFF(day, soh.OrderDate, soh.ShipDate) AS DeliveryDelayDays,
    CASE WHEN soh.SalesPersonID IS NULL THEN 'Online' ELSE 'Sales Rep' END AS SalesChannel
FROM {{ ref('stg_sales_order_detail') }} sod
INNER JOIN {{ ref('stg_sales_order_header') }} soh
    ON sod.SalesOrderID = soh.SalesOrderID