import pandas as pd
from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

app = Flask(__name__)


jobs_data = pd.read_csv('python/jobs.csv')


def extract_numeric(value):
    match = re.search(r'\d+', str(value))  
    if match:
        return int(match.group())
    return 0  


def parse_range(input_str):
    if isinstance(input_str, int):
        return input_str, input_str  
    parts = re.findall(r'\d+', str(input_str))  
    if len(parts) == 2:
        return int(parts[0]), int(parts[1])
    elif len(parts) == 1:
        return int(parts[0]), int(parts[0])  
    else:
        return 0, 0  


def preprocess_data(df):
    df['salary'] = df['salary'].apply(lambda x: int(re.search(r'\d+', str(x)).group()))
    df['work_experience'] = df['year_work_experience'].apply(lambda x: int(re.search(r'\d+', str(x)).group()))
    df['work_hours_week'] = df['work_hours_week'].apply(lambda x: int(re.search(r'\d+', str(x)).group()))
    return df


jobs_data = preprocess_data(jobs_data)


skills_vectorizer = TfidfVectorizer(stop_words='english')
skills_matrix = skills_vectorizer.fit_transform(jobs_data['skills'])

@app.route('/recommend_jobs', methods=['POST'])
def recommend_jobs():
    user_input = request.get_json()
    
    print(f"User Input: {user_input}") 

    
    user_personality = user_input['personality']
    user_work_experience_min, user_work_experience_max = parse_range(user_input['work_experience'])
    user_work_hours_min, user_work_hours_max = parse_range(user_input['work_hours'])
    user_salary_min, user_salary_max = parse_range(user_input['salary'])
    user_skills = user_input['skills']  

    filtered_jobs = jobs_data[jobs_data['personality'] == user_personality]

    if filtered_jobs.empty:
        print("No jobs found matching the specified personality")  
        return jsonify([])  

    print(f"Filtered Jobs: {filtered_jobs}") 

    
    user_salary = (user_salary_min + user_salary_max) / 2
    user_work_experience = (user_work_experience_min + user_work_experience_max) / 2
    user_work_hours = (user_work_hours_min + user_work_hours_max) / 2

    user_skills_vector = skills_vectorizer.transform([user_skills]).toarray()

  
    similarities = []
    for idx, job in filtered_jobs.iterrows():
        job_salary = extract_numeric(job['salary'])
        job_experience = extract_numeric(job['work_experience'])
        job_hours = extract_numeric(job['work_hours_week'])
        job_skills_vector = skills_vectorizer.transform([job['skills']]).toarray()

       
        salary_similarity = 1 - (abs(job_salary - user_salary) / (user_salary_max - user_salary_min)) if user_salary_min != user_salary_max else 1
        experience_similarity = 1 - (abs(job_experience - user_work_experience) / (user_work_experience_max - user_work_experience_min)) if user_work_experience_min != user_work_experience_max else 1
        hours_similarity = 1 - (abs(job_hours - user_work_hours) / (user_work_hours_max - user_work_hours_min)) if user_work_hours_min != user_work_hours_max else 1
        skills_similarity = cosine_similarity(user_skills_vector, job_skills_vector).flatten()[0]

        
        average_similarity = (salary_similarity + experience_similarity + hours_similarity + skills_similarity) / 4
        similarities.append({
            'title': job['title'],
            'salary': job_salary,
            'personality': job['personality'],
            'work_experience': job_experience,
            'work_hours': job_hours,
            'skills': job['skills'],
            'accuracy_percentage': float(average_similarity * 100)  
        })

    print(f"Similarities Before Sorting: {similarities}")  

    
    recommended_jobs = sorted(similarities, key=lambda x: x['accuracy_percentage'], reverse=True)[:3]

    print(f"Recommended Jobs After Sorting: {recommended_jobs}")  

    return jsonify(recommended_jobs)

if __name__ == '__main__':
    app.run(debug=True)
