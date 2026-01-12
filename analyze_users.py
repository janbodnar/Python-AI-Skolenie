import pandas as pd
from collections import Counter

df = pd.read_csv('data/user_data4.csv')

min_salary = df['salary'].min()
max_salary = df['salary'].max()
avg_salary = df['salary'].mean()
median_salary = df['salary'].median()

occupation_counts = df['occupation'].value_counts()
top_3_occupations = occupation_counts.head(3)

df['email_domain'] = df['email'].str.split('@').str[1]
domain_counts = df['email_domain'].value_counts()

with open('user_analysis.md', 'w') as f:
    f.write('# User Data Analysis Report\n\n')
    
    f.write('## Salary Analysis\n\n')
    f.write(f'**Minimum Salary:** {min_salary}\n\n')
    f.write(f'**Maximum Salary:** {max_salary}\n\n')
    f.write(f'**Average Salary:** {avg_salary:.2f}\n\n')
    f.write(f'**Median Salary:** {median_salary}\n\n')
    
    f.write('## Additional Insights\n\n')
    
    f.write('### Top 3 Most Common Occupations\n\n')
    for idx, (occupation, count) in enumerate(top_3_occupations.items(), 1):
        f.write(f'{idx}. {occupation}: {count} user(s)\n')
    f.write('\n')
    
    f.write('### Count of Users by Email Domain\n\n')
    for domain, count in domain_counts.items():
        f.write(f'- {domain}: {count} user(s)\n')

print('Analysis complete! Report saved to user_analysis.md')
