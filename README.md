# Suicide Analysis Project (EN)

Analytical review [of suicide statistics](https://www.kaggle.com/datasets/utkarshx27/suicide-attempts-in-shandong-china) in Shandong, China (2009-2011).

The aim is to practice skills of data cleaning, statistical hypothesis testing, regression modeling and data visualization.

Compared to the agrarian society, the industrialized and information societies record high rates of mental disorders and suicides. The analysis of Shandong's data will help come to understanding of the factors affecting human suicidal behavior.

![Shandong](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/5cd5847d-c302-49ee-847b-ca991f723b70)
<p align="center"> Map of Shandong 2020 [<a style = " white-space:nowrap; " href="https://www.mdpi.com/2073-445X/10/6/639">Meng et al, 2021</a>] </p>

Questions:
- What demographic risk groups can be identified?
- What are the predictors of method and outcome of suicide attempts, as well as hospitalization?
- What are the differences between urban and rural observations?
- What recommendations can be made based on the available data?
- What additional information is needed for a more in-depth study?

Conclusions:
1. ...
2. ...
3. ...
4. ...
5. ...

---

## Stage 1. Data Cleaning
The suicide_china_original [[1]](suicide_china_original.csv) was already in acceptable condition. Simple cleanup procedures with SQL Server have thus been performed:
- Checking for duplicate columns;
- Check for duplicate observations;
- Checking for NaN-values (with the method of [hkravitz](https://stackoverflow.com/a/37406536));
- Renaming columns with names that match SQL syntax;
- Conversion of values to lowercase letters;
- Removal of extra spaces;
- Conversion of binary values to 1 and 0;
- Transfer of cleaned data to a new table to preserve the integrity of the original dataset.
```SQL
--Equality check for column1 & Person_ID--
SELECT *, CASE WHEN entries = of_them_equal THEN 1 ELSE 0 END AS col_equality_check
FROM (
SELECT COUNT(*) AS entries,
COUNT(CASE WHEN column1 = Person_ID THEN 1 ELSE 0 END) AS of_them_equal
FROM suicide_china_original ) Src;

--Duplicate check--
SELECT Person_ID, Hospitalised, Died, Urban, [Year], [Month], Sex, Age, Education, Occupation, Method, COUNT(*) as Amount
FROM suicide_china_original
GROUP BY Person_ID, Hospitalised, Died, Urban, [Year], [Month], Sex, Age, Education, Occupation, Method
HAVING COUNT(*) > 1;

--NaN check--
SET NOCOUNT ON
DECLARE @Schema NVARCHAR(100) = 'dbo'
DECLARE @Table NVARCHAR(100) = 'suicide_china_original'
DECLARE @sql NVARCHAR(MAX) =''
IF OBJECT_ID ('tempdb..#Nulls') IS NOT NULL DROP TABLE #Nulls

CREATE TABLE #Nulls (TableName sysname, ColumnName sysname, ColumnPosition int, NullCount int, NonNullCount int)

SELECT @sql += 'SELECT
'''+TABLE_NAME+''' AS TableName,
'''+COLUMN_NAME+''' AS ColumnName,
'''+CONVERT(VARCHAR(5),ORDINAL_POSITION)+''' AS ColumnPosition,
SUM(CASE WHEN '+COLUMN_NAME+' IS NULL THEN 1 ELSE 0 END) CountNulls,
COUNT(' +COLUMN_NAME+') CountnonNulls
FROM '+QUOTENAME(TABLE_SCHEMA)+'.'+QUOTENAME(TABLE_NAME)+';'+ CHAR(10)

FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = @Schema
AND TABLE_NAME = @Table

INSERT INTO #Nulls 
EXEC sp_executesql @sql

SELECT * 
FROM #Nulls

DROP TABLE #Nulls;

--Formatting and cleaning--
SELECT
Person_ID,
(CASE WHEN Hospitalised = 'yes' THEN 1 ELSE 0 END) AS Hospitalised,
(CASE WHEN Died = 'yes' THEN 1 ELSE 0 END) AS Died,
(CASE WHEN Urban = 'yes' THEN 1 
WHEN Urban = 'no' THEN 0 ELSE NULL END) AS Urban,
[Year] AS Yr,
[Month] AS Mth,
Sex,
Age,
LOWER(TRIM(Education)) AS Education,
Occupation,
LOWER(TRIM(method)) AS Method

INTO suicide_china

FROM suicide_china_original;
```

The month and age fields were difficult to read due to the large number of unique values. For the sake of readability, they have been combined into quarters and age intervals, respectively:
- Creating a column of annual quarters based on the months column;
- Creating a column of age intervals based on the age column.
```SQL
--Quarters--
ALTER TABLE suicide_china
ADD Quart nvarchar(10);

UPDATE suicide_china
SET Quart = Qrt
FROM suicide_china
INNER JOIN (

SELECT Person_ID,
CASE 
WHEN Mth BETWEEN 1 AND 3 THEN 'Q1'
WHEN Mth BETWEEN 4 AND 6 THEN 'Q2'
WHEN Mth BETWEEN 7 AND 9 THEN 'Q3'
WHEN Mth BETWEEN 10 AND 12 THEN 'Q4'
END AS Qrt
FROM suicide_china

) AS Src
ON suicide_china.Person_ID = Src.Person_ID;

--Age Intervals--
ALTER TABLE suicide_china
ADD Age_Interval nvarchar(10);

UPDATE suicide_china
SET Age_Interval = Age_Int
FROM suicide_china
INNER JOIN (

SELECT Person_ID,
CASE
WHEN Age BETWEEN 0 AND 4 THEN '0-4'
WHEN Age BETWEEN 5 AND 9 THEN '5-9'
WHEN Age BETWEEN 10 AND 14 THEN '10-14'
WHEN Age BETWEEN 15 AND 19 THEN '15-19'
WHEN Age BETWEEN 20 AND 24 THEN '20-24'
WHEN Age BETWEEN 25 AND 29 THEN '25-29'
WHEN Age BETWEEN 30 AND 34 THEN '30-34'
WHEN Age BETWEEN 35 AND 39 THEN '35-39'
WHEN Age BETWEEN 40 AND 44 THEN '40-44'
WHEN Age BETWEEN 45 AND 49 THEN '45-49'
WHEN Age BETWEEN 50 AND 54 THEN '50-54'
WHEN Age BETWEEN 55 AND 59 THEN '55-59'
WHEN Age BETWEEN 60 AND 64 THEN '60-64'
WHEN Age BETWEEN 65 AND 69 THEN '65-69'
WHEN Age BETWEEN 70 AND 74 THEN '70-74'
WHEN Age BETWEEN 75 AND 79 THEN '75-79'
WHEN Age BETWEEN 80 AND 84 THEN '80-84'
WHEN Age BETWEEN 85 AND 89 THEN '85-89'
WHEN Age BETWEEN 90 AND 94 THEN '90-94'
WHEN Age BETWEEN 95 AND 99 THEN '95-99'
WHEN Age BETWEEN 100 AND 104 THEN '100-104'
WHEN Age BETWEEN 105 AND 109 THEN '105-109'
WHEN AGE BETWEEN 110 AND 114 THEN '110-114'
END AS Age_Int
FROM suicide_china

) AS ints
ON suicide_china.Person_ID = ints.Person_ID;
```

Full SQL-document [[2]](https://github.com/Makar-Data/China_suicide_analysis-RU/blob/main/1.%20%D0%A7%D0%B8%D1%81%D1%82%D0%BA%D0%B0%20%D0%B8%20%D0%BF%D1%80%D0%B5%D0%BE%D0%B1%D1%80%D0%B0%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5/Data_clean.sql) is listed in the repository.

As a result of data cleaning, an analysis-ready suicide_china [[3]](suicide_china.rpt) table was created.

---
