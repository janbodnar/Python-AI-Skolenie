
-- Create a better users table with more realistic fields
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    occupation TEXT NOT NULL,
    salary REAL NOT NULL,
    created_at TEXT NOT NULL
);

-- Insert 20 users with realistic data
INSERT INTO users (first_name, last_name, email, occupation, salary, created_at) VALUES
('Jana', 'Nováková', 'jana.novakova@gmail.com', 'Software Engineer', 3200.00, '2026-01-01'),
('Peter', 'Kováč', 'peter.kovac@example.com', 'Data Analyst', 2800.00, '2026-01-02'),
('Lucia', 'Horváthová', 'lucia.horvathova@example.com', 'Project Manager', 3500.00, '2026-01-03'),
('Martin', 'Tóth', 'martin.toth@example.com', 'UX Designer', 3000.00, '2026-01-04'),
('Simona', 'Varga', 'simona.varga@example.com', 'QA Engineer', 2700.00, '2026-01-05'),
('Marek', 'Polák', 'marek.polak@example.com', 'DevOps Engineer', 3400.00, '2026-01-06'),
('Zuzana', 'Bartošová', 'zuzana.bartosova@example.com', 'HR Specialist', 2500.00, '2026-01-07'),
('Tomáš', 'Urban', 'tomas.urban@example.com', 'Business Analyst', 2900.00, '2026-01-08'),
('Barbora', 'Králová', 'barbora.kralova@simplemail.com', 'Marketing Manager', 3300.00, '2026-01-09'),
('Jozef', 'Šimek', 'jozef.simek@example.com', 'System Administrator', 3100.00, '2026-01-10'),
('Michaela', 'Dudová', 'michaela.dudova@example.com', 'Content Writer', 2200.00, '2026-01-11'),
('Richard', 'Bielik', 'richard.bielik@example.com', 'Product Owner', 3600.00, '2026-01-12'),
('Katarína', 'Farkašová', 'katarina.farkasova@gmail.com', 'Accountant', 2600.00, '2026-01-13'),
('Andrej', 'Gregor', 'andrej.gregor@example.com', 'Network Engineer', 3200.00, '2026-01-14'),
('Veronika', 'Kučerová', 'veronika.kucerova@gmail.com', 'Graphic Designer', 2400.00, '2026-01-15'),
('Patrik', 'Holub', 'patrik.holub@gmail.com', 'Mobile Developer', 3300.00, '2026-01-16'),
('Eva', 'Švecová', 'eva.svecova@example.com', 'Recruiter', 2300.00, '2026-01-17'),
('Roman', 'Marek', 'roman.marek@simplemail.com', 'Database Administrator', 3400.00, '2026-01-18'),
('Monika', 'Blažeková', 'monika.blazekova@example.com', 'Scrum Master', 3100.00, '2026-01-19'),
('Filip', 'Klein', 'filip.klein@example.com', 'Web Developer', 3000.00, '2026-01-20');
