import pyodbc as db
import pandas as pd
import matplotlib.pyplot as plt

conn = db.connect('Driver={SQL Server};'
                      'Server=Mai-PC\SQLEXPRESS;'
                      'Database=T;'
                      'Trusted_Connection=yes;')

query = '''
SELECT Method, COUNT(*) AS Amount
FROM suicide_china
GROUP BY Method
ORDER BY Amount DESC;
'''

sql_query = pd.read_sql_query(query, conn)
df = pd.DataFrame(sql_query)

# Визуализация
plt.style.use('seaborn')

fig, ax = plt.subplots()
bars = ax.bar(df['Method'], df['Amount'], alpha=0.8)

fig.suptitle('Methods Distribution')
ax.bar_label(bars)
ax.tick_params(axis='x', labelrotation=25)
ax.set_ylabel('Cases')

plt.tight_layout()
plt.show()