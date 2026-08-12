SELECT
    pod.PurchaseOrderDetailID,
    pod.PurchaseOrderID,
    poh.OrderDate,
    poh.VendorID,
    poh.EmployeeID,
    pod.ProductID,
    pod.OrderQty,
    pod.UnitPrice,
    pod.LineTotal,
    poh.ShipDate,
    DATEDIFF(day, poh.OrderDate, poh.ShipDate) AS ReceptionDelayDays
FROM {{ ref('stg_purchase_order_detail') }} pod
INNER JOIN {{ ref('stg_purchase_order_header') }} poh
    ON pod.PurchaseOrderID = poh.PurchaseOrderID