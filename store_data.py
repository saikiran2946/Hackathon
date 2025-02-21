import sqlite3
import pandas as pd

# Connect to SQLite Database (Creates if it doesn't exist)
conn = sqlite3.connect("career_guidance.db")
cursor = conn.cursor()

# Create Tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS postings (
    job_id INTEGER PRIMARY KEY,
    company_name TEXT,
    title TEXT,
    description TEXT,
    max_salary REAL,
    pay_period TEXT,
    location TEXT,
    company_id INTEGER,
    views INTEGER,
    med_salary REAL,
    min_salary REAL,
    formatted_work_type TEXT,
    applies INTEGER,
    original_listed_time TEXT,
    remote_allowed TEXT,
    job_posting_url TEXT,
    application_url TEXT,
    application_type TEXT,
    expiry TEXT,
    closed_time TEXT,
    formatted_experience_level TEXT,
    skills_desc TEXT,
    listed_time TEXT,
    posting_domain TEXT,
    sponsored TEXT,
    work_type TEXT,
    currency TEXT,
    compensation_type TEXT,
    normalized_salary REAL,
    zip_code TEXT,
    fips TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS job_skills (
    job_id INTEGER PRIMARY KEY,
    job_title TEXT,
    skill_abr TEXT,
    experience_required INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS salaries (
    job_id INTEGER PRIMARY KEY,
    job_title TEXT,
    max_salary REAL,
    min_salary REAL,
    currency TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS job_industries (
    job_id INTEGER PRIMARY KEY,
    industry_id INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS benefits (
    job_id INTEGER PRIMARY KEY,
    benefit_type TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS skills (
    skill_abr TEXT PRIMARY KEY,
    skill_name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS industries (
    industry_id INTEGER PRIMARY KEY,
    industry_name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    company_size TEXT,
    state TEXT,
    country TEXT,
    city TEXT,
    zip_code TEXT,
    address TEXT,
    url TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS company_industries (
    company_id INTEGER,
    industry TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS company_specialities (
    company_id INTEGER,
    speciality TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS employee_counts (
    company_id INTEGER PRIMARY KEY,
    employee_count INTEGER,
    follower_count INTEGER,
    time_recorded TEXT
)
""")

# Load Data from Preprocessed CSV Files
df_postings = pd.read_csv("cleaned_postings.csv")
df_job_skills = pd.read_csv("skill_data.csv")
df_salaries = pd.read_csv("salaries_data.csv")
df_job_industries = pd.read_csv("job_industries.csv")
df_benefits = pd.read_csv("benefits_data.csv")
df_skills = pd.read_csv("cleaned_skills.csv")
df_industries = pd.read_csv("cleaned_industries.csv")
df_companies = pd.read_csv("cleaned_companies.csv")
df_company_industries = pd.read_csv("cleaned_company_industries.csv")
df_company_specialities = pd.read_csv("cleaned_company_specialities.csv")
df_employee_counts = pd.read_csv("cleaned_employee_counts.csv")

# Insert Data into SQLite Tables
df_postings.to_sql("postings", conn, if_exists="replace", index=False)
df_job_skills.to_sql("job_skills", conn, if_exists="replace", index=False)
df_salaries.to_sql("salaries", conn, if_exists="replace", index=False)
df_job_industries.to_sql("job_industries", conn, if_exists="replace", index=False)
df_benefits.to_sql("benefits", conn, if_exists="replace", index=False)
df_skills.to_sql("skills", conn, if_exists="replace", index=False)
df_industries.to_sql("industries", conn, if_exists="replace", index=False)
df_companies.to_sql("companies", conn, if_exists="replace", index=False)
df_company_industries.to_sql("company_industries", conn, if_exists="replace", index=False)
df_company_specialities.to_sql("company_specialities", conn, if_exists="replace", index=False)
df_employee_counts.to_sql("employee_counts", conn, if_exists="replace", index=False)

# Commit and Close Connection
conn.commit()
conn.close()

print("✅ Data Successfully Stored in SQLite3 Database.")
import sqlite3

conn = sqlite3.connect("career_guidance.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(job_skills)")
columns = cursor.fetchall()

for col in columns:
    print(col)

conn.close()
