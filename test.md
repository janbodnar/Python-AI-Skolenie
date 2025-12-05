# Priklady


## Blocking 

```python
import requests
from bs4 import BeautifulSoup

def fetch_title(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else "No title found"
        return title
    except requests.RequestException as e:
        return f"Error fetching {url}: {str(e)}"

websites = [
    "https://www.sme.sk",
    "https://www.pravda.sk",
    "https://dennikn.sk",
    "https://www.pluska.sk",
    "https://www.hnonline.sk",
    "https://www.cas.sk",
    "https://www.aktuality.sk",
    "https://www.topky.sk",
    "https://www.noviny.sk",
    "https://www.teraz.sk",
    "https://www.zoznam.sk",
    "https://www.azet.sk",
    "https://www.trend.sk",
    "https://noveslovo.sk",
    "https://korzar.sme.sk",
    "https://www.sita.sk",
    "https://www.ujszo.com",
    "https://spectator.sme.sk",
    "https://www.dobrenoviny.sk",
    "https://sport.aktuality.sk",
    "https://www.atlas.sk",
    "https://www.ta3.com",
    "https://www.parlamentnelisty.sk"
]

for site in websites:
    title = fetch_title(site)
    print(f"Title of {site}: {title}")
```



## Non blocking

```python
import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def fetch_title(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()  # Raise an error for bad status codes
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')
            title = soup.title.string.strip() if soup.title else "No title found"
            return title
    except aiohttp.ClientError as e:
        return f"Error fetching {url}: {str(e)}"

async def main():
    websites = [
        "https://www.sme.sk",
        "https://www.pravda.sk",
        "https://dennikn.sk",
        "https://www.pluska.sk",
        "https://www.hnonline.sk",
        "https://www.cas.sk",
        "https://www.aktuality.sk",
        "https://www.topky.sk",
        "https://www.noviny.sk",
        "https://www.teraz.sk",
        "https://www.zoznam.sk",
        "https://www.azet.sk",
        "https://www.trend.sk",
        "https://noveslovo.sk",
        "https://korzar.sme.sk",
        "https://www.sita.sk",
        "https://www.ujszo.com",
        "https://spectator.sme.sk",
        "https://www.dobrenoviny.sk",
        "https://sport.aktuality.sk",
        "https://www.atlas.sk",
        "https://www.ta3.com",
        "https://www.parlamentnelisty.sk"
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_title(session, site) for site in websites]
        titles = await asyncio.gather(*tasks)
        
        for site, title in zip(websites, titles):
            print(f"Title of {site}: {title}")

if __name__ == "__main__":
    asyncio.run(main())
```



## Generate test data

```python

import faker
fake = faker.Faker()

file_name = "test_data.csv"

with open(file_name, "w", encoding="utf-8") as f:

    # Write the header
    f.write("id;first_name;last_name;address;email;dob\n")

    for i in range(1, 100_001):

        _id = i
        first_name = fake.first_name()
        last_name = fake.last_name()
        address = fake.address().replace("\n", ",")
        email = fake.email()
        dob = fake.date_of_birth(minimum_age=18, maximum_age=90) 

        row = f"{_id};{first_name};{last_name};{address};{email};{dob}\n"
        f.write(row)
    
print(f"Generated {file_name} with 100,000 rows.")
```

## Analyze data by AI

```python
from openai import OpenAI
import os
import pandas as pd


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

# Read the data from users2.xlsx
df = pd.read_excel('users2.xlsx')
data_str = df.to_string()

query = f"Generate a report from the data provided.\n\nData:\n{data_str}"

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": query,
        }
    ],
    model='amazon/nova-2-lite-v1:free',
    max_completion_tokens=8000
)

# Get the response
response = chat_completion.choices[0].message.content

with open('report.md', 'w', encoding='utf-8') as f:
    f.write(response)
```


## Analyze data

```python
import pandas as pd

# Read the Excel file
df = pd.read_excel('users2.xlsx')

# Extract the salary column
salary = df['salary']

# Calculate statistics
mean_salary = salary.mean()
min_salary = salary.min()
max_salary = salary.max()
sum_salary = salary.sum()

# Print the results
print(f"Mean salary: {mean_salary}")
print(f"Minimum salary: {min_salary}")
print(f"Maximum salary: {max_salary}")
print(f"Sum of salaries: {sum_salary}")
```


## Users data

```SQL
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    occupation TEXT,
    salary REAL
);

-- Individual INSERT statements for 100 rows
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (1, 'Liam', 'Miller', 'Software Engineer', 95000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (2, 'Olivia', 'Davis', 'Data Scientist', 110000.50);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (3, 'Noah', 'Wilson', 'UX Designer', 82000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (4, 'Emma', 'Moore', 'Product Manager', 130000.75);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (5, 'Oliver', 'Taylor', 'Marketing Specialist', 65000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (6, 'Ava', 'Anderson', 'Financial Analyst', 90000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (7, 'Elijah', 'Thomas', 'Systems Administrator', 75000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (8, 'Charlotte', 'Jackson', 'HR Manager', 78000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (9, 'William', 'White', 'Sales Representative', 60000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (10, 'Sophia', 'Harris', 'Project Coordinator', 72000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (11, 'James', 'Martin', 'Civil Engineer', 88000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (12, 'Amelia', 'Garcia', 'Chemist', 70000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (13, 'Benjamin', 'Rodriguez', 'Network Technician', 62000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (14, 'Isabella', 'Lee', 'Copywriter', 55000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (15, 'Lucas', 'Perez', 'Mechanical Engineer', 92000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (16, 'Mia', 'Hall', 'Registered Nurse', 71000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (17, 'Henry', 'Allen', 'Electrician', 58000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (18, 'Evelyn', 'Young', 'Librarian', 45000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (19, 'Alexander', 'King', 'Pilot', 150000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (20, 'Harper', 'Scott', 'Interior Designer', 68000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (21, 'Ethan', 'Baker', 'Web Developer', 85000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (22, 'Abigail', 'Green', 'Physical Therapist', 77000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (23, 'Daniel', 'Adams', 'Geologist', 74000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (24, 'Emily', 'Nelson', 'Art Director', 98000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (25, 'Jacob', 'Carter', 'Lawyer', 120000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (26, 'Madison', 'Mitchell', 'Teacher', 52000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (27, 'Michael', 'Roberts', 'Biologist', 76000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (28, 'Luna', 'Campbell', 'Veterinarian', 80000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (29, 'Logan', 'Parker', 'Construction Manager', 94000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (30, 'Avery', 'Evans', 'Journalist', 59000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (31, 'Sebastian', 'Edwards', 'Chef', 48000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (32, 'Chloe', 'Collins', 'Paralegal', 51000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (33, 'Jack', 'Stewart', 'Police Officer', 63000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (34, 'Grace', 'Sanchez', 'Pharmacist', 105000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (35, 'Jackson', 'Morris', 'Insurance Agent', 54000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (36, 'Scarlett', 'Rogers', 'Statistician', 97000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (37, 'Aiden', 'Reed', 'Firefighter', 61000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (38, 'Zoey', 'Cook', 'Speech Pathologist', 79000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (39, 'Gabriel', 'Morgan', 'Auditor', 83000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (40, 'Lily', 'Bell', 'Realtor', 73000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (41, 'Samuel', 'Murphy', 'Dentist', 140000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (42, 'Layla', 'Bailey', 'Massage Therapist', 40000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (43, 'Carter', 'Rivera', 'Plumber', 57000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (44, 'Zoe', 'Cooper', 'Market Researcher', 69000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (45, 'David', 'Richardson', 'Aerospace Engineer', 115000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (46, 'Nora', 'Cox', 'Medical Assistant', 47000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (47, 'Joseph', 'Howard', 'HR Specialist', 66000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (48, 'Stella', 'Ward', 'Curator', 53000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (49, 'Matthew', 'Torres', 'Electrician', 64000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (50, 'Hannah', 'Peterson', 'Dietitian', 67000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (51, 'Ryan', 'Gray', 'IT Support Specialist', 50000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (52, 'Eliana', 'Ramirez', 'Forensic Scientist', 81000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (53, 'Leo', 'James', 'Actuary', 108000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (54, 'Penelope', 'Watson', 'Event Planner', 49000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (55, 'Jaxon', 'Brooks', 'Architect', 102000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (56, 'Victoria', 'Kelly', 'Occupational Therapist', 75500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (57, 'Adam', 'Sanders', 'Financial Advisor', 93000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (58, 'Hazel', 'Price', 'Marketing Manager', 96000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (59, 'Julian', 'Bennett', 'Professor', 112000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (60, 'Aurora', 'Wood', 'Social Worker', 56000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (61, 'Theodore', 'Barnes', 'Data Analyst', 78500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (62, 'Skylar', 'Ross', 'Graphic Designer', 60500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (63, 'Caleb', 'Henderson', 'Drilling Engineer', 125000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (64, 'Violet', 'Coleman', 'Speech Therapist', 70500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (65, 'Asher', 'Jenkins', 'Machine Operator', 42000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (66, 'Savannah', 'Perry', 'Real Estate Appraiser', 69500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (67, 'Eli', 'Powell', 'Stockbroker', 135000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (68, 'Brooklyn', 'Long', 'Veterinary Technician', 46000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (69, 'Dominic', 'Patterson', 'Physical Trainer', 41000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (70, 'Emilia', 'Hughes', 'School Counselor', 64500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (71, 'Grayson', 'Flores', 'Automotive Technician', 53500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (72, 'Isabelle', 'Washington', 'Technical Writer', 77500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (73, 'Owen', 'Butler', 'Electrician', 61500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (74, 'Natalia', 'Simmons', 'Operations Manager', 101000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (75, 'Aaron', 'Foster', 'Laboratory Technician', 58500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (76, 'Eleanor', 'Gonzales', 'Urban Planner', 84000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (77, 'Connor', 'Bryant', 'Accountant', 79500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (78, 'Allison', 'Alexander', 'Museum Technician', 44000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (79, 'Landon', 'Russell', 'Chef', 52500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (80, 'Audrey', 'Griffin', 'Dental Hygienist', 65500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (81, 'Cole', 'Diaz', 'Welder', 45500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (82, 'Clara', 'Hayes', 'Marketing Coordinator', 59500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (83, 'Christian', 'Myers', 'Petroleum Engineer', 145000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (84, 'Samantha', 'Ford', 'Travel Agent', 43000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (85, 'Adrian', 'Hamilton', 'Forester', 62500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (86, 'Madeline', 'Graham', 'Photographer', 51500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (87, 'Hunter', 'Sullivan', 'Paramedic', 63500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (88, 'Gabriella', 'Wallace', 'Interior Designer', 74500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (89, 'Jeremiah', 'Woods', 'Aerospace Technician', 87000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (90, 'Alice', 'Cole', 'Librarian', 47500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (91, 'Elias', 'West', 'Financial Manager', 118000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (92, 'Serenity', 'Jordan', 'Copy Editor', 56500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (93, 'Robert', 'Owens', 'Electrician', 68500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (94, 'Kinsley', 'Fisher', 'Technical Support Analyst', 71500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (95, 'Jonah', 'Gomez', 'Civil Engineering Technician', 76500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (96, 'Kylie', 'Murray', 'Public Relations Specialist', 70000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (97, 'Josiah', 'Harrison', 'Web Designer', 89000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (98, 'Annabelle', 'Gibson', 'Museum Archivist', 49500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (99, 'Isaiah', 'Mcdaniel', 'Security Analyst', 99000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (100, 'Ruby', 'Chambers', 'School Administrator', 91000.00);
```


## Generate SQLite data

```python

import sqlite3

# data

slovak_movie_reviews = {
    1: "Príbeh bol úplne pútavý a herecké výkony brilantné. Nemohol som sa odtrhnúť ani na sekundu!",
    2: "Tempo bolo mimoriadne pomalé a postavy nemali žiadnu hĺbku. Nudil som sa už v polovici.",
    3: "Hoci vizuálne efekty boli ohromujúce, dej pôsobil predvídateľne a bez inšpirácie.",
    4: "Toto je filmové dielo, ktoré mi dojalo srdce. Každá scéna bola dokonalosť!",
    5: "Dialógy boli trápne a humor úplne zlyhal. Určite to nestojí za ten humbug.",
    6: "Bol to priemerný film – nie dobrý, ale ani úplná katastrofa. Niektoré časti ma bavili.",
    7: "Chemia medzi hlavnými postavami bola elektrizujúca a soundtrack fenomenálny!",
    8: "Film začal skvele, ale v druhej polovici sa úplne rozpadol. Veľké sklamanie.",
    9: "Vizualne ohromujúci film, ktorý dokonale spája akciu a emócie. Určite odporúčam!",
    10: "Premisa bola zaujímavá, ale realizácia bola slabá. Nedokázalo ma to zaujať."
}

# Code to save to database
conn = sqlite3.connect('reviews.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY, review TEXT)''')
for id, review in slovak_movie_reviews.items():
    cursor.execute('INSERT INTO reviews (id, review) VALUES (?, ?)', (id, review))
conn.commit()
conn.close()
```


Sentiment analysis from database data:

```python
from openai import OpenAI
import os
import sqlite3



client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

# Load reviews from database
conn = sqlite3.connect('reviews.db')
cursor = conn.cursor()
cursor.execute('SELECT id, review FROM reviews')
reviews = cursor.fetchall()
conn.close()


for key, value in reviews:

    content = 'Na škále od 0 do 1, napíš sentiment nasledujúceho filmu. Uveď len číslo. '
    content += value

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        temperature=0.7,
        top_p=0.9,
        model='amazon/nova-2-lite-v1:free',
        max_completion_tokens=1000
    )

    # print(chat_completion.choices[0].message.content)
    output = chat_completion.choices[0].message.content
    print(key, value, output)
```



## Sentiment analyza

```python
from openai import OpenAI

from pathlib import Path
import os
import time


# client = OpenAI(
#     base_url="https://api.deepseek.com",
#     api_key=os.environ.get("DEEPSEEK_API_KEY"),
# )

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

# movie_reviews = {
#     1: "The storyline was absolutely captivating, and the performances were brilliant. I couldn't look away for a second!",
#     2: "The pacing was excruciatingly slow, and the characters lacked depth. I was bored halfway through.",
#     3: "While the visuals were breathtaking, the plot felt predictable and uninspired.",
#     4: "This is a cinematic masterpiece that touched my heart. Every scene was perfection!",
#     5: "The dialogue was cringe-worthy, and the humor fell flat. Definitely not worth the hype.",
#     6: "It was an average film—not great, but not terrible either. I enjoyed some parts.",
#     7: "The chemistry between the leads was electric, and the soundtrack was phenomenal!",
#     8: "The movie started strong but completely fell apart in the second half. Such a disappointment.",
#     9: "A visually stunning film that combines action and emotion seamlessly. Highly recommend!",
#     10: "The premise was intriguing, but the execution left a lot to be desired. It just didn't click for me."
# }

slovak_movie_reviews = {
    1: "Príbeh bol úplne pútavý a herecké výkony brilantné. Nemohol som sa odtrhnúť ani na sekundu!",
    2: "Tempo bolo mimoriadne pomalé a postavy nemali žiadnu hĺbku. Nudil som sa už v polovici.",
    3: "Hoci vizuálne efekty boli ohromujúce, dej pôsobil predvídateľne a bez inšpirácie.",
    4: "Toto je filmové dielo, ktoré mi dojalo srdce. Každá scéna bola dokonalosť!",
    5: "Dialógy boli trápne a humor úplne zlyhal. Určite to nestojí za ten humbug.",
    6: "Bol to priemerný film – nie dobrý, ale ani úplná katastrofa. Niektoré časti ma bavili.",
    7: "Chemia medzi hlavnými postavami bola elektrizujúca a soundtrack fenomenálny!",
    8: "Film začal skvele, ale v druhej polovici sa úplne rozpadol. Veľké sklamanie.",
    9: "Vizualne ohromujúci film, ktorý dokonale spája akciu a emócie. Určite odporúčam!",
    10: "Premisa bola zaujímavá, ale realizácia bola slabá. Nedokázalo ma to zaujať."
}

for key, value in slovak_movie_reviews.items():

    # content = 'On a scale 0-1, figure out the sentiment of the the following movie review:'
    content = 'Na škále od 0 do 1, napíš sentiment nasledujúceho filmu. Uveď len číslo. '
    content += value

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        temperature=0.7,
        top_p=0.9,
        model='amazon/nova-2-lite-v1:free',
        max_completion_tokens=1000
    )

    # print(chat_completion.choices[0].message.content)
    output = chat_completion.choices[0].message.content
    print(key, value, output)
```
