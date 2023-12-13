# Suicide Analysis Project (EN)

Analytical review [of suicide statistics](https://www.kaggle.com/datasets/utkarshx27/suicide-attempts-in-shandong-china) in Shandong, China (2009-2011).

The aim is to practice skills of data cleaning, statistical hypothesis testing, regression modeling and data visualization.

Compared to the agrarian society, the industrialized and information societies record high rates of mental disorders and suicides. The analysis of Shandong's data will help come to understanding of the factors affecting human suicidal behavior.

![Shandong](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/5cd5847d-c302-49ee-847b-ca991f723b70)
<p align="center"> Map of Shandong 2020 [<a style = " white-space:nowrap; " href="https://www.mdpi.com/2073-445X/10/6/639">Meng et al, 2021</a>] </p>

Questions:
- What demographic risk groups can be identified?
- What are the predictors of method and outcome of suicide attempts, as well as hospitalization?
- What recommendations can be made based on the available data?
- What additional information is needed for a more in-depth study?

Conclusions:
1. Datest is most likely to be composed of low-income people. Within this group, illiterate individuals and adults with only primary education are particularly at risk of lethal outcomes;
2. Age and method of attempt are other predictors of the outcome. With increasing age, there is a change in the pattern of methods used in favor of more lethal tools;
3. Despite the lack of data on material well-being of the observed people, a high role of socio-economic factors in determining the lethality of suicide attempts has been hypothesized based on studies of other East Asian countries;
4. All people who made a failed suicide attempt were hospitalized. Of those who died, 16% were hospitalized. The dataset data does not allow for a detailed discussion of the role of hospitalization in keeping a person alive;
5. A worldwide trend for the maximum number of suicide attempts in late spring - early summer, and the minimum in the winter season is followed.

Information needed for a more in-depth study:
- Material well-being. Monthly income, annual income, approximate range of disposable income, or ability/inability to pay rent, make large purchases, etc.;
- Marital status. Whether the person has stable and healthy social ties. Data from other studies shows that information on divorce will also be useful;
- Demographic and socio-economic data of the Shandong population for comparison with the dataset. In this way it will be possible to establish factors of suicidality, not just the lethality of suicide attempts. Most likely such data is only available in Chinese.

Recommendations:

Approach A (Systematic). A system of suggestions to minimize the root factors of suicidality, the implementation of which is possible as part of the overall modernization of the province:
- Expand health insurance to include psychotherapy services;
- Increase enrollment in training areas for medical personnel specializing in mental health;
- Form a system of adult evening schools. Particularly for illiterate persons and people with primary education;
- Encourage mechanization of work on small farmlands.

Approach B (Economical). A set of interventions aimed at improving the situation and not requiring systematic change:
- Compile a demographic profile of a person predisposed to suicidal behavior for medical staff;
- Establish a hotline for calls in life crisis circumstances.

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

Full SQL-document [[2]](https://github.com/Makar-Data/China_suicide_analysis-EN/blob/main/1.%20Data%20Cleaning/Data_clean.sql) is listed in the repository.

As a result of data cleaning, an analysis-ready suicide_china [[3]](suicide_china.rpt) table was created.

---

## Stage 2. Exploratory Data Analysis
As an exercise, SQL Server tables were utilized whenever possible instead of Pandas crosstabs.

First, unique values of the dataset categorical columns were pulled.
![0 4](https://github.com/Makar-Data/China_suicide_analysis/assets/152608115/78d9ae79-9350-4e32-8abb-ba088969fa83)

Variations of 3 tables were used for the EDA:
1. A number and proportion of values by column [[4]](https://github.com/Makar-Data/China_suicide_analysis-EN/blob/main/2.%20EDA/2.Table1.sql):

![image](https://github.com/Makar-Data/China_suicide_analysis/assets/152608115/5d617278-80e7-4993-8d07-c319b93f6341)
```SQL
SELECT Sex, COUNT(*) AS Amount, ROUND(CAST(COUNT(*) AS FLOAT)*100/SUM(CAST(COUNT(*) AS FLOAT)) OVER(), 2) AS Perc
FROM suicide_china 
GROUP BY Sex
ORDER BY Perc DESC;
```

2. A number and proportion of values by two columns [[5]](https://github.com/Makar-Data/China_suicide_analysis-EN/blob/main/2.%20EDA/3.Table2.sql):

![image](https://github.com/Makar-Data/China_suicide_analysis/assets/152608115/e032fa95-efbc-455c-b301-49fde98fc8b2)
```SQL
SELECT Age_Interval,

CONCAT(
CAST(COUNT(CASE WHEN Sex = 'male' THEN 1 ELSE NULL END) AS VARCHAR(10)), 
' (', 
CAST((ROUND(CAST(COUNT(CASE WHEN Sex = 'male' THEN 1 ELSE NULL END) AS FLOAT)*100/SUM(CAST(COUNT(*) AS FLOAT)) OVER(), 2)) AS VARCHAR(10)), 
'%)') 
AS Males,

CONCAT(
CAST(COUNT(CASE WHEN Sex = 'female' THEN 1 ELSE NULL END) AS VARCHAR(10)), 
' (', 
CAST((ROUND(CAST(COUNT(CASE WHEN Sex = 'female' THEN 1 ELSE NULL END) AS FLOAT)*100/SUM(CAST(COUNT(*) AS FLOAT)) OVER(), 2)) AS VARCHAR(10)), 
'%)') 
AS Females,
COUNT(*) AS Total

FROM suicide_china
GROUP BY Age_Interval
ORDER BY Total DESC;
```

3. Proportion of outcomes by variables [[6]](https://github.com/Makar-Data/China_suicide_analysis-EN/blob/main/2.%20EDA/4.Table3.sql):

![image](https://github.com/Makar-Data/China_suicide_analysis/assets/152608115/e94c5474-f805-4f60-9cc5-0e65045b68a4)
```SQL
SELECT *, 
CONCAT(CAST(ROUND(CAST(Died AS FLOAT)/CAST(Total AS FLOAT), 2)*100 AS VARCHAR(10)), '%') AS Death_Rate

FROM (
	SELECT Method,
	COUNT(CASE WHEN Died = 1 THEN 1 ELSE NULL END)
	AS Died,
	COUNT(CASE WHEN Died = 0 THEN 1 ELSE NULL END)
	AS Survived,
	COUNT(*) AS Total
	
	FROM suicide_china
	GROUP BY Method
	) Src;
```

A combination of other variables were also used to construct data tables [[7]](https://github.com/Makar-Data/China_suicide_analysis-EN/tree/main/2.%20EDA/Images).

A number of barplots were made with Python and Pyodbc. Some of them are the following:

![6 1 Возрастное_распределение](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/76bf5fe8-fda1-4cb5-8294-91153ef98797)
![6 5 Распределение_профессий](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/2dd6b829-4a6f-4075-b5a4-194ea018ff4c)

Another barplot was constructed to represent the chronological distribution of observations. Various seasons were color-coded to detect seasonal trends. Maximum of observations appeared in summer months, while minimum in winter. This corresponds with world observations [<a style = " white-space:nowrap; " href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3315262/">Woo et al, 2012</a>].

![0 3](https://github.com/Makar-Data/China_suicide_analysis/assets/152608115/7973c6e6-1231-4e01-aea8-912edce9af13)
```Python
import pyodbc as db
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# SQL Server interaction
conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''
SELECT CONCAT(Yr, '-', Mth) AS YrMth,
Mth,
COUNT(*) AS Cases
FROM suicide_china
GROUP BY Yr, Mth
ORDER BY Yr, Mth;
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)

# Transformation dates into datetime format for ease of color-coding
df['YrMth'] = pd.to_datetime(df['YrMth'])
df['YrMth'] = df['YrMth'].dt.date.apply(lambda x: x.strftime('%Y-%m'))

# Color-coding
colors = {1: 'tab:blue', 2: 'tab:blue',
          3: 'tab:green', 4: 'tab:green', 5: 'tab:green',
          6: 'tab:red', 7: 'tab:red', 8: 'tab:red',
          9: 'tab:olive', 10: 'tab:olive', 11: 'tab:olive',
          12: 'tab:blue'}

legend = [Patch(facecolor='tab:blue', edgecolor='tab:blue', label='Winter'),
          Patch(facecolor='tab:green', edgecolor='tab:green', label='Spring'),
          Patch(facecolor='tab:red', edgecolor='tab:red', label='Summer'),
          Patch(facecolor='tab:olive', edgecolor='tab:olive', label='Autumn'),]

# Visualization
plt.style.use('seaborn')

plt.bar(x=df['YrMth'], height=df['Cases'], color=[colors[i] for i in df['Mth']])
plt.xticks(fontsize=10, rotation=90)

plt.title('Suicide attempts in Shandong over time')
plt.xlabel('Date')
plt.ylabel('Cases')

plt.legend(handles=legend, loc='upper left')
plt.tight_layout()
plt.show()
```

A population pyramid was made to represent the demographic base of the dataset. Additionally, the pyramid was divided according to the outcome of suicide attempts. A significant portion of code was taken from the [CoderzColumn](https://www.youtube.com/watch?v=yRFAslDEtgk&t=6s&ab_channel=CoderzColumn) guide.

![0 4 4](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/e46b235d-6ec3-4a19-8ab8-269f93202b48)
```Python
import pyodbc as db
import pandas as pd
import matplotlib.pyplot as plt

# SQL Server interaction
conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''  
SELECT Sex, Age, Died  
FROM suicide_china;  
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)

# Repeated age interval creation to preserve the intervals with no observations and their order
df['Age_Interval'] = pd.cut(df['Age'],
                            bins=[0, 4, 9, 14, 19, 24, 29, 34, 39, 44, 49,
                                  54, 59, 64, 69, 74, 79, 84, 89, 94, 99, 104],
                            labels=['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39',
                                    '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79',
                                    '80-84', '85-89', '90-94', '95-99', '100-104'])

# Matrix creation
crosstab = pd.crosstab(index=df['Age_Interval'], columns=[df['Sex'], df['Died']], dropna=False, normalize='all')
male_died = [number * 100 for number in crosstab['male'][1]]
female_died = [number * 100 for number in crosstab['female'][1]]
male_lived = [number * 100 for number in crosstab['male'][0]]
female_lived = [number * 100 for number in crosstab['female'][0]]

# Transformation of the matrix into the format, suitable for the pyramid's visualization code
age = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64',
       '65-69', '70-74', '75-79', '80-84', '85-89', '90-94', '95-99', '100-104']

pyramid_df = pd.DataFrame({'Age': age, 'Male_l': male_lived, 'Male_d': male_died,
                           'Female_d': female_died, 'Female_l': female_lived})

# Creation of columns with the data on relative position of barplot parts
pyramid_df['Female_Width'] = pyramid_df['Female_d'] + pyramid_df['Female_l']
pyramid_df['Male_Width'] = pyramid_df['Male_d'] + pyramid_df['Male_l']
pyramid_df['Male_d_Left'] = -pyramid_df['Male_d']
pyramid_df['Male_l_Left'] = -pyramid_df['Male_Width']

# Visualization initialization
plt.style.use('seaborn-v0_8')
fig = plt.figure(figsize=(15,10))

plt.barh(y=pyramid_df['Age'], width=pyramid_df['Female_d'],
         color='tab:red', label='Females Died', edgecolor='black')
plt.barh(y=pyramid_df['Age'], width=pyramid_df['Female_l'], left=pyramid_df['Female_d'],
         color='tab:orange', label='Females Survived', edgecolor='black')
plt.barh(y=pyramid_df['Age'], width=pyramid_df['Male_d'], left=pyramid_df['Male_d_Left'],
         color='tab:blue', label='Males Died', edgecolor='black')
plt.barh(y=pyramid_df['Age'], width=pyramid_df['Male_l'], left=pyramid_df['Male_l_Left'],
         color='tab:cyan', label='Males Survived', edgecolor='black')

# Creation of columns with the data on text position and format
pyramid_df['Male_d_Text'] = pyramid_df['Male_d_Left'] / 2
pyramid_df['Male_l_Text'] = (pyramid_df['Male_l_Left'] + pyramid_df['Male_d_Left']) / 2
pyramid_df['Female_d_Text'] = (pyramid_df['Female_Width'] + pyramid_df['Female_d']) / 2
pyramid_df['Female_l_Text'] = pyramid_df['Female_d'] / 2

for idx in range(len(pyramid_df)):
    alpha_ = 1 if pyramid_df['Male_d_Text'][idx] != 0.5 else 0
    alpha_ = 1 if pyramid_df['Male_l_Text'][idx] != 0 else 0
    alpha = 1 if pyramid_df['Female_d_Text'][idx] != 0 else 0
    alpha = 1 if pyramid_df['Female_l_Text'][idx] != 0 else 0
    plt.text(x=pyramid_df['Male_d_Text'][idx], y=idx,
             s='{}%'.format(round(pyramid_df['Male_d'][idx], 1)),
             fontsize=14, ha='center', va='center', alpha=alpha)
    plt.text(x=pyramid_df['Male_l_Text'][idx], y=idx,
             s='{}%'.format(round(pyramid_df['Male_l'][idx], 1)),
             fontsize=14, ha='center', va='center', alpha=alpha)
    plt.text(x=pyramid_df['Female_d_Text'][idx], y=idx,
             s='{}%'.format(round(pyramid_df['Female_l'][idx], 1)),
             fontsize=14, ha='center', va='center', alpha=alpha)
    plt.text(x=pyramid_df['Female_l_Text'][idx], y=idx,
             s='{}%'.format(round(pyramid_df['Female_d'][idx], 1)),
             fontsize=14, ha='center', va='center', alpha=alpha)

# Visualization finalization
plt.xlim(-6, 6)
plt.xticks(range(-6, 7), ['{}%'.format(i) for i in range(-6, 7)], fontsize=14)
plt.yticks(fontsize=14)

plt.title('Suicide attempts in Shandong (2009-2011)', pad=20, fontsize=25, fontweight='bold')
plt.xlabel('Percentage of suicide attempts', fontsize=20, )
plt.ylabel('Age', fontsize=20)

plt.legend(fontsize=20, shadow=True)
plt.tight_layout()
plt.show()
```

Ratio of education, occupation and method values were displayed on piecharts.

![Диаграмма образования](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/642ea2a1-bf99-4b4e-9551-36c8d6191ce4)
![Диаграмма профессий](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/a369e93f-9bd6-4926-81e8-ff0c36793aae)
![Одна диаграмма методов](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/a2efdfd9-f8eb-4c54-9eb3-17e261ac95f6)
```Python
import pyodbc as db
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# SQL Server interaction
conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''
SELECT Education, COUNT(*) AS Amount
FROM suicide_china
GROUP BY Education
ORDER BY Amount DESC;
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)

# Visualization
palette = sns.color_palette('hls', len(df))
plt.style.use('seaborn')

fig, ax = plt.subplots()
ax.pie(df['Amount'], autopct='%1.1f%%', pctdistance=0.8, colors=palette,
              wedgeprops={'edgecolor': 'black', 'linewidth': 0.3})

fig.suptitle('Education Ratio')

ax.legend(labels=df['Education'] + ' ' + '(' + df['Amount'].astype(str) + ')',
          loc=(0.9, 0))

plt.tight_layout()
plt.show()
```

Additionally, two pie charts of methods by the outcome of the suicide attempt were made.
![Две диаграммы методов](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/667f7595-9761-4fb2-a369-b9082e7b4eb4)
```Python
import pyodbc as db
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# SQL Server interaction
conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''
SELECT Method, Died, COUNT(*) AS Amount
FROM suicide_china
GROUP BY Method, Died
ORDER BY Amount DESC;
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)
df_died = df.loc[df['Died'] == 1]
df_lived = df.loc[df['Died'] == 0]

# Visualization
plt.style.use('seaborn')
palette = sns.color_palette('hls', len(df))
signified = df['Method'].unique()
signifiers = palette.as_hex()
unified_palette = {signified[i]: signifiers[i] for i in range(df['Method'].nunique())}
died_palette = [unified_palette[signified] for signified in df_died['Method'].unique()]
lived_palette = [unified_palette[signified] for signified in df_lived['Method'].unique()]

fig = plt.figure()
fig.suptitle('Methods by Outcome')

ax1 = fig.add_subplot(121)
ax1.set_title('Died')
ax1.pie(df_died['Amount'], autopct='%1.1f%%', pctdistance=0.8, colors=died_palette,
              wedgeprops={'edgecolor': 'black', 'linewidth': 0.3})
ax1.legend(labels=df_died['Method'] + ' ' + '(' + df_died['Amount'].astype(str) + ')',
           loc=(0,-0.2), ncol=2)

ax2 = fig.add_subplot(122)
ax2.set_title('Survived')
ax2.pie(df_lived['Amount'], autopct='%1.1f%%', pctdistance=0.8, colors=lived_palette,
              wedgeprops={'edgecolor': 'black', 'linewidth': 0.3})
ax2.legend(labels=df_lived['Method'] + ' ' + '(' + df_lived['Amount'].astype(str) + ')',
           loc=(0,-0.2), ncol=2)

plt.grid(visible=False)
plt.tight_layout()
plt.show()
```

A graph of discrete distribution of methods by age intervals was also created.

![0 5](https://github.com/Makar-Data/China_suicide_analysis/assets/152608115/619c7daf-796d-4aa8-a98f-7979ec0d6d6e)
```Python
import pyodbc as db
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# SQL Server interaction
conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''  
SELECT Person_ID, Method, Age_Interval 
FROM suicide_china
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)

# Transformation of the data into the format, suitable for the visualization code
needed = df.pivot(index='Person_ID', columns='Age_Interval', values='Method')
new_cols = [col for col in needed.columns if col != '100-104'] + ['100-104']
needed = needed[new_cols]
category_names = ['pesticide', 'hanging', 'other poison', 'poison unspec', 'unspecified', 'cutting', 'drowning', 'jumping', 'others']
questions = list(needed.columns.values)
raws = []

list_obj_cols = needed.columns[needed.dtypes == 'object'].tolist()
for obj_col in list_obj_cols:
    needed[obj_col] = needed[obj_col].astype(pd.api.types.CategoricalDtype(categories=category_names))

list_cat_cols = needed.columns[needed.dtypes == 'category'].tolist()
for cat_col in list_cat_cols:
    dc = needed[cat_col].value_counts().sort_index().reset_index().to_dict(orient='list')
    raws.append(dc['count'])

results = [[num / sum(brackets) * 100 for num in brackets] for brackets in raws]
number_results = {questions[i]: raws[i] for i in range(len(questions))}
percentage_results = {questions[i]: results[i] for i in range(len(questions))}

# Visualization
palette = sns.color_palette('hls', df['Method'].nunique())

def survey(number_results, percentage_results, category_names):
    labels = list(percentage_results.keys())
    data = np.array(list(percentage_results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = palette

    fig, ax = plt.subplots(figsize=(9.2, 5))
    fig.suptitle('Methods by Age')
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        ax.barh(labels, widths, left=starts, height=0.5,
                label=colname, color=color)
        xcenters = starts + widths / 2
        numbers = np.array(list(number_results.values()))[:, i]

        r, g, b = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        text_label = zip(xcenters, numbers)
        for y, (x, c) in enumerate(text_label):
            alpha = 1 if c != 0 else 0
            ax.text(x, y+0.06, str(int(c)),
                    ha='center', va='center', color=text_color, alpha=alpha, fontsize=8)
    ax.legend(ncol=5, bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')
    return fig, ax


survey(number_results, percentage_results, category_names)

plt.tight_layout()
plt.show()
```

EDA results:
- The chronological framework is 2009-2011. Each year consists of 12 months [[8]](https://github.com/Makar-Data/China_suicide_analysis-EN/blob/main/2.%20EDA/Images/4.Year_completeness.png);
- Dataset consists primarily of observations in rural areas (2213, 86.08%) [[9]](https://github.com/Makar-Data/China_suicide_analysis-EN/blob/main/2.%20EDA/Images/6.3.Area_distribution.png) with a correspondingly high proportion of farmers (2032, 79.04%) [[10]](https://github.com/Makar-Data/China_suicide_analysis-EN/blob/main/2.%20EDA/Images/6.5.Occupation_distribution.png);
- Observations were about evenly divided on the outcome of attempted suicide (1315, 51.15% - survived; 1256, 48.85% - died) [[11]](https://github.com/Makar-Data/China_suicide_analysis-EN/blob/main/2.%20EDA/Images/6.7.Outcome_distribution.png);
- Seasonal fluctuations of cases are visible. The maximum is recorded in summer and the minimum in winter;
- All survivors of the suicide attempt were hospitalized. Of those who subsequently died, only 238, 19% [[12]](https://github.com/Makar-Data/China_suicide_analysis-EN/blob/main/2.%20EDA/Images/3.3.Hospitalization_rate_by_outcomes.png). Attempt outcome is a major predictor of hospitalization;
- The lethality of suicide attempts increases steadily with increasing age;
- With increasing age, the pattern of methods used tends toward the more lethal;
- The most common methods are: pesticide use (1768, 68.77%), hanging (431, 16.76%), other poisons (146, 9.84%); the least: jumping (15, 0.58%), drowning (26, 1.01%), cutting (29, 1.13%);
- The most lethal methods are: drowning (26/26, 100%), hanging (419/431, 97%), jumping (12/15, 80%); the least: unspecified poision (3/104, 3%), unspecified method (3/48, 6%), other poisons (15/146, 10%) [[13]](https://github.com/Makar-Data/China_suicide_analysis-EN/blob/main/2.%20EDA/Images/3.1.Death_rate_by_methods.png);
- The most common methods for females are: other poisons (66% of observations apply to women), drowning (68%), pesticide (54%); males: unspecified method (63% of observations apply to men), hanging (61%), cutting (52%) [[14]](https://github.com/Makar-Data/China_suicide_analysis-EN/blob/main/2.%20EDA/Images/3.5.Sex_rate_by_methods.png);
- Although the survival rate after pesticide use is relatively high, the lethality of attempts in rural areas is slightly higher than in urban areas (52%, 41%) [[15]](https://github.com/Makar-Data/China_suicide_analysis-EN/blob/main/2.%20EDA/Images/1.3.Area_ratio.png).

---

## Stage 3. Statistical Hypothesis Testing

It was possible to roll out two kinds of hypothesis tests: (1) for two independent samples; (2) for categorical values.

Chi-test of categorical independence was used to determine the relationship of categorical values. A heat map of pvalue for the corresponding fields was compiled. The visualization algorithm was taken from [Shafqaat Ahmad](https://medium.com/analytics-vidhya/constructing-heat-map-for-chi-square-test-of-independence-6d78aa2b140f), ([github](https://github.com/shafqaatahmad/chisquare-test-heatmap/tree/main)).

![Chi_heatmap](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/b74fcc14-2085-4115-955b-27aea07c81ae)
```Python
import pyodbc as db
import pandas as pd
import numpy as np
from scipy import stats
import seaborn as sns
import matplotlib.pylab as plt

conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''
SELECT *
FROM suicide_china;
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)
df.index = df['Person_ID']
del df['Person_ID']
del df['Age']
del df['Mth']

col_names = df.columns

chi_matrix=pd.DataFrame(df,columns=col_names,index=col_names)

outercnt=0
innercnt=0
for icol in col_names:
    for jcol in col_names:
        mycrosstab=pd.crosstab(df[icol],df[jcol])
        stat, p, dof, expected=stats.chi2_contingency(mycrosstab)
        chi_matrix.iloc[outercnt,innercnt]=round(p,3)
        cntexpected=expected[expected<5].size
        perexpected=((expected.size-cntexpected)/expected.size)*100
        if perexpected < 20:
            chi_matrix.iloc[outercnt, innercnt] = 2
        if icol == jcol:
            chi_matrix.iloc[outercnt, innercnt] = 0.00
        innercnt = innercnt + 1
    outercnt = outercnt + 1
    innercnt = 0

plt.style.use('seaborn')
fig = sns.heatmap(chi_matrix.astype(np.float64), annot=True, linewidths=0.1, cmap='coolwarm_r',
            annot_kws={"fontsize": 8}, cbar_kws={'label': 'pvalue'})

fig.set_title('Chi2 Independence Test Pvalues')
plt.tight_layout()
plt.show()
```

The Mann-Whitney-U-test was used to identify differences in the distribution of ages of individuals with different outcomes of suicide attempts. To exclude the possibility of using Student's t-test, Shapiro-Wilk test and Kolmogorov-Smirnov test of fit of distributions to normal distribution were conducted. Diviation from normality was detected, which excluded the possibility of using parametric tests. The shapes of distributions were compared visually. Their inconsistency requires interpretation of the Mann-Whitney-U-test results to be read as reflecting the situation of stochastic dominance of the values of one distribution over the values of another.

A test was performed to determine if there was a statistically significant difference. The distributions are recorded on one graph with different colors.

![Возрасты по исходам (один)](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/656371d3-cb34-4c06-866a-5d1bfce21db9)
```Python
import numpy as np
import pyodbc as db
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# SQL Server interaction
conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''
SELECT Age, Died
FROM suicide_china;
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)

# Category division
df_died = df.loc[df['Died'] == 1]
df_lived = df.loc[df['Died'] == 0]
dfs = [df['Age'], df_died['Age'], df_lived['Age']]

# Goodness of fit test
print('Shapiro-Wilk Test:')
for dataframe in dfs:
    print(stats.shapiro(dataframe))

print('\nKolmogorov-Smirnov Test:')
for dataframe in dfs:
    dist = getattr(stats, 'norm')
    param = dist.fit(dataframe)
    result = stats.kstest(dataframe, 'norm', args=param)
    print(result)

# Mann-Whitney test
sample1 = df_died['Age']
sample2 = df_lived['Age']

results = stats.mannwhitneyu(sample1, sample2)
u = results[0]
mean = (len(sample1) * len(sample2)) / 2
std = np.sqrt((len(sample1) * len(sample2) * (len(sample1) + len(sample2) + 1)) / 12)
z = (u - mean) / std

print('\nMann-Whitney Test:')
print(results)
print('Z-critical:', z)

# Visualization
dfd = df_died.groupby(['Age'], as_index=False).agg('count')
dfd.rename(columns={'Died': 'Amount'}, inplace=True)
dfl = df_lived.groupby(['Age'], as_index=False).agg('count')
dfl.rename(columns={'Died': 'Amount'}, inplace=True)

plt.style.use('seaborn')

fig1 = plt.figure()

ax1 = fig1.add_subplot(121)
ax1.bar(dfd['Age'], dfd['Amount'], alpha=0.5)
ax1.set_xlabel('Age')
ax1.set_ylabel('Cases')
ax2 = fig1.add_subplot(122)
ax2.bar(dfl['Age'], dfl['Amount'], alpha=0.5)
ax2.set_xlabel('Age')
fig1.suptitle('Age Distribution')
plt.tight_layout()

fig2 = plt.figure()

ax3 = fig2.add_subplot()
ax3.bar(dfd['Age'], dfd['Amount'], alpha=0.5, color='tab:red', label='Died')
ax3.bar(dfl['Age'], dfl['Amount'], alpha=0.5, color='tab:blue', label='Survived')
ax3.set_ylabel('Cases')
fig2.suptitle('Age Distribution')
plt.legend()
plt.tight_layout()

fig3 = plt.figure()

ax4 = fig3.add_subplot()
ax4.boxplot([dfd['Age'], dfl['Age']])
plt.xticks([1, 2], ['Died', 'Survived'])
fig3.suptitle('Age Distribution')
plt.tight_layout()

plt.show()
```

---

## Stage 4. Modeling

Suicide outcome was used as the target value for the logistic regression model.

Predictors were selected based on a random forest. Predictors that passed the arbitrarily set importance threshold of 0.10 (Education = 0.27, Method = 0.24, Age_Interval = 0.24) were allowed to move to subsequent stages of the procedure. The OOB of the random forest was equal to 0.80.

The dataset was divided into three groups: training, validation, and test in the proportion of 70-15-15, respectively. For the training group intercept was equal to 2.81, coefficients: Age_Interval = 0.10, Education = -1.01, Method = -0.46.

Confusion matrix was made based on validation and test groups. In the latter case f1-score of accuracy was equal to 0.78. The matrix was visualized.

![Confusion_matrix](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/b393fdff-3700-4d68-af71-804650243045)
```Python
import numpy as np
import pyodbc as db
import pandas as pd
from sklearn import metrics
from sklearn import linear_model
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import seaborn as sns
import matplotlib.pylab as plt

# SQL Server interaction
conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''
SELECT Sex, Age_Interval, Quart, Urban, Education, Occupation, Method, Died
FROM suicide_china;
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)
label_encoder = preprocessing.LabelEncoder()
df = df.apply(label_encoder.fit_transform)

# X - features, y - target value (Died = 0/1)
all_X = df.iloc[:,:-1]
y = df.iloc[:,-1]

# Selection of the most important features via the random forest method
X_train_sel, X_test_sel, y_train_sel, y_test_sel = train_test_split(all_X, y, test_size=0.3, random_state=42)
rfc = RandomForestClassifier(random_state=0, criterion='gini', oob_score=True)
rfc.fit(X_train_sel, y_train_sel)

feature_names = df.columns[:-1]
assessed_X = []
for feature in zip(feature_names, rfc.feature_importances_):
    print(feature)
    assessed_X.append(feature)
print('OOB:', rfc.oob_score_)

predictors = [predictor for (predictor, score) in assessed_X if score > 0.1]
X = df[predictors]

# Modeling
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

print("\ntrain sample:", len(X_train))
print("val sample:", len(X_val))
print("test sample:", len(X_test))

log_model = linear_model.LogisticRegression(solver='lbfgs')
log_model.fit(X=X_train, y=y_train)
print('\nIntercept:', log_model.intercept_)
print('Predictors:', predictors)
print('Coefficient:', log_model.coef_)

val_prediction = log_model.predict(X_val)
print('\nValidation group matrix:')
print(metrics.confusion_matrix(y_true=y_val, y_pred=val_prediction))
print(metrics.classification_report(y_true=y_val, y_pred=val_prediction))

test_predition = log_model.predict(X_test)
confmatrix = metrics.confusion_matrix(y_true=y_test, y_pred=test_predition)
print('\nTest group matrix:')
print(confmatrix)
print(metrics.classification_report(y_true=y_test, y_pred=test_predition))

# Visualization of the confusion matrix
plt.style.use('seaborn')
class_names = [0, 1]

fig, ax = plt.subplots()

tick_marks = np.arange(len(class_names))
plt.xticks(tick_marks, class_names)
plt.yticks(tick_marks, class_names)
sns.heatmap(pd.DataFrame(confmatrix), annot=True, cmap='Blues', fmt='g')
ax.xaxis.set_label_position('top')
plt.title('Confusion matrix', y = 1.1)
plt.ylabel('Actual outcome')
plt.xlabel('Predicted outcome')

plt.tight_layout()
plt.show()
```

---

## Stage 5. Conclusion and discussion

Education was not identified in previous stages of analysis as the most important predictor of mortality, but is confirmed upon visual inspection.

![Образование_по_исходам](https://github.com/Makar-Data/China_suicide_analysis-RU/assets/152608115/95353b1b-e593-401b-afa6-03f41338e584)

The available data do not allow to draw a confident conclusion about the nature of this phenomenon. It is possible to put forward a number of hypotheses:

Hypothesis 1. Level of education is a proxy for person's area of residence. Refuted by the low importance of area variable in the regression model as well as the relatively low difference in suicide lethality between urban and rural areas. Although the influence of the area variable cannot be ruled out, it should not be considered decisive.

Hypothesis 2. Previous observations have shown an increase in the lethality of suicide attempts with increasing age. Therefore, it is possible to put forward a hypothesis that the combination of lower education and high age is a feature of the generation born during the years of industrialization and the Great Leap (1950s-1960s). Although the 60-90 age groups do have one of the lowest proportions of education above primary level, the relatively low importance of age in the regression argues against age as a determinant of mortality.

![1 5 Age_dist_by_education](https://github.com/Makar-Data/China_suicide_analysis-EN/assets/152608115/22becaf5-cb0f-4dac-85dc-1b3139c7459e)

Hypothesis 3. Illiteracy and primary education are predominantly recorded among people above 50-60 years of age. Representatives of these age groups were born in China during or before the reforms of the 1970s and 1980s. Perhaps the changed economic policies have marginalized people with low education who are then unable to compete in the labor market with the new generation of workers. In part, this hypothesis is supported by observations in the Republic of Korea and Japan, where educational attainment and employment status are cited as major factors in adult mental distress [<a style = " white-space:nowrap; " href="https://www.nature.com/articles/s41598-020-71789-y">Cheon et al, 2020</a>], [<a style = " white-space:nowrap; " href="https://www.sciencedirect.com/science/article/abs/pii/S0165032719319822">Nishi et al, 2020</a>]. Of the predictors identified by studies of other East Asian countries (among others, low household income, marital status, independent living, sleep duration, physical health status, lack of mental support systems, etc.), education is one of the only ones available in this dataset. In such a case, the level of education can be considered a proxy for the set of socioeconomic parameters that lead to low household income. The assertion about the high role of education and wealth in mortality is confirmed by other studies [<a style = " white-space:nowrap; " href="https://www.thelancet.com/journals/lanpub/article/PIIS2468-2667(23)00207-4/fulltext">Favril et al, 2023</a>].

A natural criticism would be the thesis that occupation is a more informative proxy for income. However, since the dataset consists only of people who have attempted suicide, it is appropriate to assume that the vast majority of observations are already ones of people with low income. Thus, under Hypothesis 3, education is a predictor of income not for the entire population of Shandong, but for the part of the population that is already in a less favorable socioeconomic position. Then, the column of occupations dominated by employment in agriculture does not give the opportunity to structure this social group as effectively as the values of education - because it already constitutes its main defining feature.
