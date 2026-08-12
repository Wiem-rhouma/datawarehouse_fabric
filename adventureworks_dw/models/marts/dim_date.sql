-- Dimension générée (pas issue d'une source), couverture 2011-01-01 à 2014-12-31
WITH RECURSIVE date_spine AS (
    SELECT CAST('2011-01-01' AS DATE) AS FullDate
    UNION ALL
    SELECT DATEADD(day, 1, FullDate)
    FROM date_spine
    WHERE FullDate < '2014-12-31'
)
SELECT
    FullDate,
    CAST(FORMAT(FullDate, 'yyyyMMdd') AS INT) AS DateKey,
    YEAR(FullDate) AS Year,
    DATEPART(quarter, FullDate) AS Quarter,
    MONTH(FullDate) AS Month,
    FORMAT(FullDate, 'MMMM') AS MonthName,
    DATEPART(weekday, FullDate) AS DayOfWeek,
    FORMAT(FullDate, 'dddd') AS DayName
FROM date_spine
OPTION (MAXRECURSION 0)