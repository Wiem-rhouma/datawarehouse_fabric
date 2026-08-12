-- OrganizationNode exclue explicitement : type SqlHierarchyId incompatible Delta Lake
SELECT
    BusinessEntityID, NationalIDNumber, LoginID, OrganizationLevel,
    JobTitle, BirthDate, MaritalStatus, Gender, HireDate,
    SalariedFlag, VacationHours, SickLeaveHours, CurrentFlag,
    rowguid, ModifiedDate,
    CURRENT_TIMESTAMP() AS _ingested_at,
    'AdventureWorks2019.HumanResources.Employee' AS _source
FROM {{ source('bronze', 'employee') }}
WHERE BusinessEntityID IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY BusinessEntityID ORDER BY BusinessEntityID) = 1