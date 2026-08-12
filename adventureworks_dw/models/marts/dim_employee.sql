SELECT
    BusinessEntityID AS EmployeeID,
    JobTitle,
    HireDate,
    Gender
FROM {{ ref('stg_employee') }}