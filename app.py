import streamlit as st
import joblib
import pandas as pd
import sqlite3
import numpy as np
from datetime import datetime

# Load the trained model and vectorizer
model = joblib.load('career_recommendation_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

# Configure page
st.set_page_config(
    page_title="CareerAI Pro - Your AI Career Guide",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        height: 3em;
    }
    .success-box {
        padding: 1em;
        border-radius: 5px;
        border-left: 5px solid #4CAF50;
        background-color: white;
    }
    .job-title {
        color: #2196F3;
        font-size: 1.5em;
    }
    </style>
    """, unsafe_allow_html=True)

def get_db_connection():
    return sqlite3.connect("career_guidance.db")

def predict_job(description):
    description_vectorized = vectorizer.transform([description])
    prediction = model.predict(description_vectorized)
    # Get prediction probabilities
    probs = model.predict_proba(description_vectorized)
    top_3_indices = np.argsort(probs[0])[-3:][::-1]
    top_3_probs = probs[0][top_3_indices]
    top_3_jobs = [str(model.classes_[i]) for i in top_3_indices]
    return top_3_jobs, top_3_probs

def get_job_details(job_title):
    conn = get_db_connection()
    query = """
    SELECT p.title, p.description, p.min_salary, p.max_salary, 
           p.location, p.company_name, p.skills_desc, p.formatted_experience_level,
           p.remote_allowed, p.formatted_work_type, p.views, p.applies,
           ROUND(AVG(p.min_salary), 2) as avg_min_salary,
           ROUND(AVG(p.max_salary), 2) as avg_max_salary
    FROM postings p
    WHERE p.title LIKE ?
    GROUP BY p.title
    LIMIT 5
    """
    try:
        job_details = pd.read_sql_query(query, conn, params=('%' + str(job_title) + '%',))
        return job_details if not job_details.empty else None
    finally:
        conn.close()

def get_market_insights():
    conn = get_db_connection()
    query = """
    SELECT 
        formatted_experience_level, 
        ROUND(AVG(med_salary), 2) as avg_salary,
        COUNT(*) as job_count,
        ROUND(AVG(views), 2) as avg_views,
        ROUND(AVG(applies), 2) as avg_applies
    FROM postings
    WHERE formatted_experience_level IS NOT NULL
    GROUP BY formatted_experience_level
    """
    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()

# Sidebar with user profile
with st.sidebar:
    st.title("🎯 CareerAI Pro")
    st.subheader("Your AI Career Navigator")
    
    # User session management
    if 'user_name' not in st.session_state:
        user_name = st.text_input("Enter your name")
        if user_name:
            st.session_state.user_name = user_name
            st.success(f"Welcome, {user_name}!")
    else:
        st.write(f"👋 Welcome back, {st.session_state.user_name}!")
    
    st.markdown("---")
    page = st.radio("Navigation", 
                    ["🏠 Home", "🚀 Career Explorer", 
                     "📊 Market Insights", "📚 Learning Path"])

# Main content
if page == "🏠 Home":
    st.title("Welcome to CareerAI Pro")
    st.subheader("Your Intelligent Career Development Partner")
    
    # Current time-based greeting
    current_hour = datetime.now().hour
    greeting = "Good morning" if 5 <= current_hour < 12 else "Good afternoon" if 12 <= current_hour < 18 else "Good evening"
    if 'user_name' in st.session_state:
        st.write(f"{greeting}, {st.session_state.user_name}! 👋")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("### 🌟 Why Choose CareerAI Pro?\n"
                "- 🤖 Advanced AI-powered job matching\n"
                "- 📊 Real-time market analytics\n"
                "- 🎯 Personalized career roadmap\n"
                "- 📈 Industry trend analysis\n"
                "- 💡 Skill gap identification")
    
    with col2:
        st.success("### 🚀 Features\n"
                  "1. Multi-path career recommendations\n"
                  "2. Salary insights and predictions\n"
                  "3. Customized learning roadmap\n"
                  "4. Industry demand analysis\n"
                  "5. Interview preparation guide")

elif page == "🚀 Career Explorer":
    st.title("Career Explorer")
    st.write("Discover your ideal career path with AI-powered recommendations")
    
    user_description = st.text_area(
        "📝 Tell us about your skills, experience, and interests:",
        height=150,
        placeholder="Example: I am a Python developer with 2 years of experience in web development..."
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        experience_level = st.selectbox(
            "Experience Level",
            ["Entry Level", "Mid Level", "Senior Level"]
        )
    with col2:
        preferred_location = st.text_input("Preferred Location")
    with col3:
        work_type = st.selectbox(
            "Preferred Work Type",
            ["Full-time", "Part-time", "Remote", "Hybrid"]
        )
    
    if st.button("🔍 Analyze My Profile"):
        if user_description:
            try:
                with st.spinner("🤖 AI is analyzing your profile..."):
                    predicted_jobs, probabilities = predict_job(user_description)
                
                st.success("### 🎯 Career Recommendations")
                
                for job, prob in zip(predicted_jobs, probabilities):
                    match_percentage = int(prob * 100)
                    job_details = get_job_details(job)
                    
                    if job_details is not None:
                        for _, job_data in job_details.iterrows():
                            with st.expander(f"🌟 {job_data['title']} (Match: {match_percentage}%)", expanded=True):
                                # Job Overview
                                st.markdown("#### 📋 Job Overview")
                                cols = st.columns(4)
                                with cols[0]:
                                    st.metric("Company", job_data['company_name'])
                                with cols[1]:
                                    st.metric("Location", job_data['location'])
                                with cols[2]:
                                    st.metric("Experience", job_data['formatted_experience_level'])
                                with cols[3]:
                                    st.metric("Work Type", job_data['formatted_work_type'])
                                
                                # Salary Information
                                if pd.notna(job_data['min_salary']) and pd.notna(job_data['max_salary']):
                                    st.markdown("#### 💰 Compensation")
                                    salary_cols = st.columns(2)
                                    with salary_cols[0]:
                                        st.metric("Minimum Salary", f"${float(job_data['min_salary']):,.2f}")
                                    with salary_cols[1]:
                                        st.metric("Maximum Salary", f"${float(job_data['max_salary']):,.2f}")
                                
                                # Job Description
                                st.markdown("#### 📝 Description")
                                st.write(job_data['description'])
                                
                                # Required Skills
                                if pd.notna(job_data['skills_desc']):
                                    st.markdown("#### 🎯 Required Skills")
                                    skills = job_data['skills_desc'].split(',')
                                    skill_cols = st.columns(3)
                                    for i, skill in enumerate(skills):
                                        skill_cols[i % 3].markdown(f"- {skill.strip()}")
                
                # Career Development Recommendations
                st.write("### 📚 Career Development Plan")
                tabs = st.tabs(["Learning Path", "Certifications", "Interview Prep"])
                
                with tabs[0]:
                    st.write("#### Recommended Courses")
                    for platform, courses in {
                        "Coursera": ["Advanced Python Programming", "Data Structures & Algorithms"],
                        "Udemy": ["Full Stack Development", "Cloud Computing Essentials"],
                        "LinkedIn": ["Project Management", "Agile Methodologies"]
                    }.items():
                        st.write(f"**{platform}:**")
                        for course in courses:
                            st.write(f"- {course}")
                
                with tabs[1]:
                    st.write("#### Recommended Certifications")
                    cert_cols = st.columns(2)
                    with cert_cols[0]:
                        st.write("**Technical Certifications:**")
                        st.write("- AWS Certified Developer")
                        st.write("- Google Cloud Professional")
                    with cert_cols[1]:
                        st.write("**Professional Certifications:**")
                        st.write("- PMP Certification")
                        st.write("- Scrum Master")
                
                with tabs[2]:
                    st.write("#### Interview Preparation")
                    st.write("**Key Topics to Prepare:**")
                    prep_cols = st.columns(2)
                    with prep_cols[0]:
                        st.write("Technical Skills:")
                        st.write("- System Design")
                        st.write("- Coding Problems")
                        st.write("- Database Concepts")
                    with prep_cols[1]:
                        st.write("Soft Skills:")
                        st.write("- Leadership Examples")
                        st.write("- Problem-solving Scenarios")
                        st.write("- Team Collaboration")
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.write("Please try again with different input.")
        else:
            st.warning("⚠️ Please enter your skills and experience to get recommendations.")

elif page == "📊 Market Insights":
    st.title("Market Insights")
    st.write("Explore current job market trends and analytics")
    
    market_data = get_market_insights()
    if not market_data.empty:
        # Market Overview
        st.subheader("📈 Market Overview")
        metric_cols = st.columns(3)
        with metric_cols[0]:
            total_jobs = market_data['job_count'].sum()
            st.metric("Total Job Openings", f"{total_jobs:,}")
        with metric_cols[1]:
            avg_salary = market_data['avg_salary'].mean()
            st.metric("Average Salary", f"${avg_salary:,.2f}")
        with metric_cols[2]:
            total_applications = (market_data['avg_applies'] * market_data['job_count']).sum()
            st.metric("Total Applications", f"{int(total_applications):,}")
        
        # Detailed Analysis
        st.subheader("📊 Detailed Analysis")
        
        # Experience Level Analysis
        st.write("#### Experience Level Breakdown")
        st.dataframe(market_data.style.highlight_max(axis=0))
        
        # Job Distribution Chart
        st.write("#### Job Distribution by Experience Level")
        st.bar_chart(market_data.set_index('formatted_experience_level')['job_count'])
        
        # Competition Analysis
        st.write("#### Competition Analysis")
        market_data['applications_per_job'] = market_data['avg_applies'] / market_data['job_count']
        st.line_chart(market_data.set_index('formatted_experience_level')['applications_per_job'])

elif page == "📚 Learning Path":
    st.title("Learning Path Generator")
    st.write("Create your personalized learning journey")
    
    col1, col2 = st.columns(2)
    with col1:
        target_role = st.selectbox(
            "Select Your Target Role",
            ["Software Engineer", "Data Scientist", "Product Manager",
             "UX Designer", "Marketing Specialist", "Cloud Architect"]
        )
    with col2:
        current_level = st.select_slider(
            "Your Current Experience Level",
            options=["Beginner", "Intermediate", "Advanced"]
        )
    
    if st.button("🎯 Generate My Learning Path"):
        st.write(f"### 🚀 Customized Learning Path for {target_role}")
        
        # Learning Phases
        phases = {
            "Phase 1: Foundation": {
                "Core Skills": ["Programming Fundamentals", "Data Structures", "Algorithms"],
                "Tools": ["Git", "IDE Setup", "Command Line"],
                "Duration": "3-4 months"
            },
            "Phase 2: Specialization": {
                "Technical Skills": ["Machine Learning", "Deep Learning", "Big Data"],
                "Frameworks": ["TensorFlow", "PyTorch", "Scikit-learn"],
                "Duration": "4-6 months"
            },
            "Phase 3: Advanced": {
                "Architecture": ["System Design", "Design Patterns", "Best Practices"],
                "DevOps": ["CI/CD", "Docker", "Kubernetes"],
                "Duration": "3-4 months"
            },
            "Phase 4: Professional": {
                "Soft Skills": ["Communication", "Leadership", "Project Management"],
                "Business": ["Agile", "Scrum", "Product Thinking"],
                "Duration": "2-3 months"
            }
        }
        
        for phase, details in phases.items():
            with st.expander(phase, expanded=True):
                cols = st.columns(3)
                with cols[0]:
                    st.write("**Skills to Learn:**")
                    for skill in details["Core Skills" if "Core Skills" in details else "Technical Skills"]:
                        st.write(f"- {skill}")
                with cols[1]:
                    st.write("**Tools/Frameworks:**")
                    for tool in details["Tools" if "Tools" in details else "Frameworks"]:
                        st.write(f"- {tool}")
                with cols[2]:
                    st.write("**Duration:**", details["Duration"])
                
                # Progress Bar
                progress = st.progress(0)
                if current_level == "Beginner":
                    progress.progress(33)
                elif current_level == "Intermediate":
                    progress.progress(66)
                else:
                    progress.progress(100)

# Footer
st.markdown("---")
st.markdown("### 💡 Career Success Tips")
tip_cols = st.columns(3)
with tip_cols[0]:
    st.info("**Profile Building**\n"
            "- Keep skills updated\n"
            "- Highlight achievements\n"
            "- Use industry keywords\n"
            "- Showcase projects")
with tip_cols[1]:
    st.success("**Interview Preparation**\n"
               "- Research companies\n"
               "- Practice coding challenges\n"
               "- Prepare STAR examples\n"
               "- Mock interviews")
with tip_cols[2]:
    st.warning("**Continuous Learning**\n"
               "- Follow tech blogs\n"
               "- Join communities\n"
               "- Build side projects\n"
               "- Attend workshops")
