import pandas as pd
import sys

INPUT_FILE = 'data/user_data4.csv'
OUTPUT_FILE = 'user_analysis.md'

try:
    df = pd.read_csv(INPUT_FILE)
except FileNotFoundError:
    print(f'Error: File {INPUT_FILE} not found.')
    sys.exit(1)
except pd.errors.EmptyDataError:
    print(f'Error: File {INPUT_FILE} is empty.')
    sys.exit(1)
except Exception as e:
    print(f'Error reading {INPUT_FILE}: {e}')
    sys.exit(1)

min_salary = df['salary'].min()
max_salary = df['salary'].max()
avg_salary = df['salary'].mean()
median_salary = df['salary'].median()

occupation_counts = df['occupation'].value_counts()
top_3_occupations = occupation_counts.head(3)

df['email_domain'] = df['email'].str.split('@').str[1]
domain_counts = df['email_domain'].value_counts()

try:
    with open(OUTPUT_FILE, 'w') as f:
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
    
    print(f'Analysis complete! Report saved to {OUTPUT_FILE}')
except IOError as e:
    print(f'Error writing to {OUTPUT_FILE}: {e}')
    sys.exit(1)
