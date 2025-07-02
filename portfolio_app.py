import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import re

# Page configuration
st.set_page_config(
    page_title="Anshuman Mohapatra | Software engineer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme and professional styling
st.markdown("""
<style>
    /* Global styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Hero section */
    .hero-section {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 3rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(45deg, #ffffff, #e0e0e0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        margin-bottom: 1rem;
        opacity: 0.9;
    }
    
    .hero-description {
        font-size: 1.1rem;
        max-width: 800px;
        margin: 0 auto 2rem;
        line-height: 1.6;
        opacity: 0.85;
    }
    
    /* Skill badges */
    .skill-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        border-radius: 25px;
        font-size: 0.9rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Section headers */
    .section-header {
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        color: #1e3c72;
        border-bottom: 3px solid #2a5298;
        padding-bottom: 0.5rem;
    }
    
    /* Project cards */
    .project-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .project-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .project-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #1e3c72;
        margin-bottom: 0.5rem;
    }
    
    .project-date {
        color: #6c757d;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    .project-description {
        line-height: 1.6;
        margin-bottom: 1rem;
        color: #495057;
    }
    
    .tech-stack {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .tech-tag {
        background: #2a5298;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    /* Contact section */
    .contact-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-top: 2rem;
    }
    
    .contact-button {
        background: rgba(255, 255, 255, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.5);
        color: white;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        text-decoration: none;
        display: inline-block;
        margin: 0.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .contact-button:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.8);
        transform: translateY(-2px);
    }
    
    /* Stats cards */
    .stats-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #2a5298;
    }
    
    .stats-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3c72;
        margin-bottom: 0.5rem;
    }
    
    .stats-label {
        color: #6c757d;
        font-weight: 500;
    }
    
    /* Timeline */
    .timeline-item {
        border-left: 3px solid #2a5298;
        padding-left: 1.5rem;
        margin-bottom: 2rem;
        position: relative;
    }
    
    .timeline-item::before {
        content: '';
        position: absolute;
        left: -8px;
        top: 0;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #2a5298;
    }
    
</style>
""", unsafe_allow_html=True)

def parse_project_date(date_str):
    # Try to extract the latest date from the string
    # Handles formats like 'Jun 19-22, 2025', 'Jun 11-14, 2025', 'Feb 03-12, 2025', 'Oct 01, 2024 - Dec 31, 2024', 'Jun 26, 2025'
    date_str = date_str.strip()
    # Handle range with dash
    if '-' in date_str:
        parts = re.split(r'-|–', date_str)
        last_part = parts[-1].strip()
        # If last part is just a day, get the month and year from the first part
        if ',' in last_part:
            # e.g. 'Jun 19-22, 2025' -> '22, 2025'
            month = date_str.split()[0]
            day_year = last_part.split(',')
            day = re.sub(r'[^0-9]', '', day_year[0])
            year = re.sub(r'[^0-9]', '', day_year[1]) if len(day_year) > 1 else re.sub(r'[^0-9]', '', last_part)
            return datetime.strptime(f"{month} {day} {year}", "%b %d %Y")
        elif len(parts) == 2 and ',' in parts[1]:
            # e.g. 'Oct 01, 2024 - Dec 31, 2024'
            return datetime.strptime(parts[1].strip(), "%b %d, %Y")
        else:
            # e.g. 'Jun 11-14, 2025' -> '14, 2025'
            month = date_str.split()[0]
            day_year = last_part.split(',')
            day = re.sub(r'[^0-9]', '', day_year[0])
            year = re.sub(r'[^0-9]', '', day_year[1]) if len(day_year) > 1 else re.sub(r'[^0-9]', '', last_part)
            return datetime.strptime(f"{month} {day} {year}", "%b %d %Y")
    else:
        # e.g. 'Jun 26, 2025'
        try:
            return datetime.strptime(date_str, "%b %d, %Y")
        except:
            try:
                return datetime.strptime(date_str, "%b %d, %Y")
            except:
                return datetime.min

def main():
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Anshuman Mohapatra</h1>
        <p class="hero-subtitle">Software engineer</p>
        <p class="hero-description">
            Passionate B.Tech Computer Science student specializing in cloud-native development, DevSecOps pipelines, 
            and microservices architecture. Experienced in building production-grade applications with modern CI/CD practices 
            and container orchestration on AWS and Kubernetes.
        </p>
        <div style="margin-top: 2rem;">
            <span class="skill-badge">Python</span>
            <span class="skill-badge">AWS</span>
            <span class="skill-badge">Kubernetes</span>
            <span class="skill-badge">Docker</span>
            <span class="skill-badge">Jenkins</span>
            <span class="skill-badge">Flask</span>
            <span class="skill-badge">DevSecOps</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 About", "💼 Projects", "🛠️ Skills", "📞 Contact"])
    
    with tab1:
        show_about_section()
    
    with tab2:
        show_projects_section()
    
    with tab3:
        show_skills_section()
    
    with tab4:
        show_contact_section()

def show_about_section():
    st.markdown('<h2 class="section-header">About Me</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🚀 Career Journey
        
        I'm a passionate B.Tech Computer Science student at ITER, SOA University, graduating in 2026. My journey began with curiosity about how applications work behind the scenes, leading me deep into the DevOps and cloud infrastructure domain.
        
        ### 💡 What Makes Me Different
        
        While many developers focus solely on writing code, I bring a unique perspective that spans the entire software lifecycle. My experience with containerization, CI/CD pipelines, and cloud deployment means I write more scalable, deployment-friendly code from the start.
        
        ### 🎯 Current Focus
        
        - **DevSecOps Pipelines**: Building secure, automated deployment workflows
        - **Cloud-Native Development**: Microservices architecture on AWS and Kubernetes  
        - **Full-Stack Applications**: End-to-end development with modern frameworks
        - **Content Creation**: Sharing knowledge through technical videos
        
        ### 🌟 Future Vision
        
        I aim to become a developer who bridges the gap between development and operations, leading teams that understand both great code and production-ready deployment practices.
        """)
    
    with col2:
        # Stats
        st.markdown("""
        <div class="stats-card">
            <div class="stats-number">15+</div>
            <div class="stats-label">Projects Completed</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="stats-card">
            <div class="stats-number">350+</div>
            <div class="stats-label">GitHub Contributions</div>
        </div>
        """, unsafe_allow_html=True)

def show_projects_section():
    st.markdown('<h2 class="section-header">Featured Projects</h2>', unsafe_allow_html=True)
    
    # Project data
    projects = [
        {
            "title": "Infra-Code-To-Prod-k8s",
            "date": "Jun 11-14, 2025",
            "description": "Comprehensive CI/CD pipeline using Terraform, Jenkins, SonarQube, JFrog Artifactory, Docker, and AWS EKS. Automates the entire software delivery process from code commit to production deployment.",
            "tech_stack": ["Terraform", "AWS EC2", "AWS EKS", "Jenkins", "SonarQube", "JFrog Artifactory", "Docker", "Kubernetes (AWS EKS)", "Trivy"],
            "link": "https://github.com/Anshuman-git-code/Infra-Code-To-Prod-k8s.git"
        },
        {
            "title": "Registration App Jenkins Maven Deploy",
            "date": "Jun 06-09, 2025",
            "description": "Complete CI/CD pipeline using Jenkins and Docker on AWS infrastructure. Automates the build, test, and deployment process for applications using containerization.",
            "tech_stack": ["Jenkins", "Maven", "Docker", "AWS EC2", "Amazon Linux", "Tomcat"],
            "link": "https://github.com/Anshuman-git-code/registration-app-Jenkins_Maven_Deploy.git"
        },
        {
            "title": "Jenkins Kubernetes Orchestrator",
            "date": "Jun 02-05, 2025",
            "description": "End-to-end CI/CD pipeline implementation using Jenkins, SonarQube, Docker, and Kubernetes (EKS) with GitOps methodology via ArgoCD. Features automated build, test, security scanning, and deployment of a Java web application with infrastructure as code principles.",
            "tech_stack": ["Docker", "Jenkins", "Maven", "Trivy", "Kubernetes (EKS)", "SonarQube", "ArgoCD", "Tomcat"],
            "link": "https://github.com/Anshuman-git-code/Jenkins-Kubernetes-Orchestrator.git"
        },
        {
            "title": "Automated Voting App Deployment with Argo CD",
            "date": "May 20-29, 2025",
            "description": "Led the deployment of scalable applications on AWS EC2 using Kubernetes and Argo CD for streamlined management and continuous integration. Orchestrated deployments via Kubernetes dashboard, ensuring efficient resource utilisation and seamless scaling.",
            "tech_stack": ["AWS EC2", "Kubernetes", "Kind", "Argo CD", "GitOps", "CI/CD"],
            "link": "https://github.com/Anshuman-git-code/k8s-kind-voting-app-on-Kubernetes-With-ArgoCD.git"
        },
        {
            "title": "Full Stack Chat Application Deployment",
            "date": "Apr 27-30, 2025",
            "description": "Improved scalability and automation with CI/CD pipelines using GitHub Actions, Kubernetes manifests for cloud deployment on platforms like AWS.",
            "tech_stack": ["DevOps", "Cloud", "CI/CD", "Kubernetes"],
            "link": "https://github.com/Anshuman-git-code/full-stack_chatApp.git"
        },
        {
            "title": "Multi-Stage Dockerized Web Scraper",
            "date": "Apr 18-21, 2025",
            "description": "A multi-stage Dockerized web scraper built with Puppeteer (Node.js) and Flask (Python). Scrapes dynamic websites and serves extracted content via a lightweight REST API. Demonstrates DevOps practices like multi-stage builds and container optimization.",
            "tech_stack": ["Docker", "Node.js", "Puppeteer", "Python", "Flask", "Alpine Linux"],
            "link": "https://github.com/Anshuman-git-code/multi-stage-puppeteer-flask-scraper.git"
        },
        {
            "title": "Real-time Cryptocurrency Data Integration",
            "date": "Feb 03-12, 2025",
            "description": "Fetches live data for the top 50 cryptos using CoinGecko API, analyzes trends, and updates a Google Sheets dashboard every 5 minutes. Tracks top 5 cryptos, avg price & 24h gainers/losers.",
            "tech_stack": ["Python", "REST API", "Pandas", "CoinGecko API", "Data Automation"],
            "link": "https://github.com/Anshuman-git-code/crypto-data-fetching.git"
        },
        {
            "title": "Flask Blog Application",
            "date": "Oct 01, 2024 - Dec 31, 2024",
            "description": "A simple Flask-based web application that allows users to create accounts, post blogs, and view other users' blogs and profiles. Features registration, login, and an interactive feed.",
            "tech_stack": ["Python", "Flask", "SQLAlchemy", "Flask-WTF", "Flask-Bcrypt", "Jinja2"],
            "link": "https://github.com/Anshuman-git-code/Your_Blog.git"
        },
        {
            "title": "E-Commerce Three-Tier Application EKS Deployment",
            "date": "Jun 26, 2025",
            "description": "Complete end-to-end deployment of a microservices-based E-Commerce application on Amazon EKS. Showcases enterprise-grade cloud-native architecture with 11 interconnected services, comprehensive microservices orchestration, and production-ready infrastructure automation.",
            "tech_stack": ["AWS EKS", "kubectl", "MongoDB", "MySQL", "Redis", "RabbitMQ", "Kubernetes", "Microservices"],
            "link": "https://github.com/Anshuman-git-code/E-Commerce-Three-Tier-Application-Deploy-on-AWS-EKS.git"
        },
        {
            "title": "Netflix Clone Deploy",
            "date": "Jun 19-22, 2025",
            "description": "Complete DevOps pipeline for Netflix Clone with TypeScript. Features enterprise-grade automation from code commit to production with comprehensive CI/CD integration, security scanning, and Kubernetes orchestration.",
            "tech_stack": ["AWS EC2", "Jenkins", "Docker", "SonarQube", "Trivy", "Kubernetes", "Prometheus", "Grafana"],
            "link": "https://github.com/Anshuman-git-code/Netflix-Clone-Deploy.git"
        },
        {
            "title": "Reddit Clone Deployment",
            "date": "Jun 15-18, 2025",
            "description": "End-to-end DevOps pipeline for Reddit Clone using modern cloud-native tools and GitOps practices. Demonstrates enterprise-grade automation with comprehensive monitoring and security.",
            "tech_stack": ["AWS EKS", "Terraform", "Jenkins", "Docker", "ArgoCD", "Prometheus", "Grafana"],
            "link": "https://github.com/Anshuman-git-code/Redit-Clone-Deployment.git"
        },
        {
            "title": "Kubernetes Containerized Code Execution Platform",
            "date": "Mar 3 - Apr 16, 2025",
            "description": "Secure, containerized code execution platform built with Kubernetes. Allows users to execute code in multiple programming languages (Python, JavaScript, C, C++) through a web interface with robust security measures.",
            "tech_stack": ["Python", "Flask", "Docker", "Kubernetes", "Nginx"],
            "link": "https://github.com/Anshuman-git-code/Execution-Containerized-k8s.git"
        },
        {
            "title": "AI-Powered Chatbot",
            "date": "Feb 14-27, 2025",
            "description": "Flask-based chatbot using Langchain, Hugging Face models, and FAISS for efficient retrieval. Leverages vector embeddings for intelligent responses, ideal for QA systems and AI-driven chat applications.",
            "tech_stack": ["Python", "Flask", "Langchain", "Hugging Face", "FAISS", "LLMs"],
            "link": "https://github.com/Anshuman-git-code/Langchain_Flask_Bot.git"
        },
        {
            "title": "Wanderlust MERN Application Kubernetes Deployment",
            "date": "May 30 - Jun 1, 2025",
            "description": "Deployed microservices travel platform on Kubernetes using kubeadm with master-worker architecture. Implemented namespace isolation, persistent storage, and proper service discovery.",
            "tech_stack": ["Kubernetes", "Docker", "MongoDB", "Redis", "Node.js", "AWS EC2"],
            "link": "https://github.com/Anshuman-git-code/wanderlust-MERN-k8s-deployment.git"
        }
    ]
    
    # Sort projects by parsed date descending (most recent first)
    projects = sorted(projects, key=lambda p: parse_project_date(p['date']), reverse=True)
    
    # Display projects
    for project in projects:
        st.markdown(f"""
        <div class="project-card">
            <div class="project-title">{project['title']}</div>
            <div class="project-date">📅 {project['date']}</div>
            <div class="project-description">{project['description']}</div>
            <div class="tech-stack">
                {''.join([f'<span class="tech-tag">{tech}</span>' for tech in project['tech_stack']])}
            </div>
            <a href="{project['link']}" target="_blank" style="color: #2a5298; font-weight: 600; text-decoration: none;">
                🔗 View Project
            </a>
        </div>
        """, unsafe_allow_html=True)

def show_skills_section():
    st.markdown('<h2 class="section-header">Technical Skills</h2>', unsafe_allow_html=True)
    
    # Skill categories
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔧 DevOps & Cloud
        """)
        devops_skills = ["AWS (EC2, EKS, ALB)", "Docker", "Kubernetes", "Jenkins", "Terraform", 
                        "ArgoCD", "Prometheus", "Grafana", "GitOps", "CI/CD Pipelines"]
        
        for skill in devops_skills:
            st.markdown(f"• **{skill}**")
        
        st.markdown("""
        ### 🔒 Security & Quality
        """)
        security_skills = ["SonarQube", "Trivy", "OWASP Security Scanning", "DevSecOps", 
                          "Container Security", "Multi-stage Docker Builds"]
        
        for skill in security_skills:
            st.markdown(f"• **{skill}**")
    
    with col2:
        st.markdown("""
        ### 💻 Programming & Frameworks
        """)
        programming_skills = ["Python", "JavaScript", "TypeScript", "Java", "Flask", "Node.js", "HTML/CSS"]
        
        for skill in programming_skills:
            st.markdown(f"• **{skill}**")
        
        st.markdown("""
        ### 🗄️ Databases & Tools
        """)
        database_skills = ["MongoDB", "MySQL", "Redis", "SQLAlchemy", "Git", "GitHub Actions", 
                          "Helm Charts", "Nginx", "Load Balancing"]
        
        for skill in database_skills:
            st.markdown(f"• **{skill}**")
    
    # Skill proficiency visualization
    st.markdown("### 📊 Skill Proficiency")
    
    skills_data = {
        'Skill': ['AWS', 'Kubernetes', 'Docker', 'Python', 'Jenkins', 'DevOps', 'Flask'],
        'Proficiency': [85, 80, 90, 85, 75, 88, 80]
    }
    
    fig = px.bar(
        skills_data, 
        x='Proficiency', 
        y='Skill', 
        orientation='h',
        color='Proficiency',
        color_continuous_scale='blues',
        title="Technical Skill Proficiency (%)"
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Proficiency Level (%)",
        yaxis_title="Skills"
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # GitHub contribution timeline (moved from Achievements section)
    st.markdown("### 📈 GitHub Activity Timeline")
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    contributions = [45, 52, 67, 89, 76, 85]
    fig2 = go.Figure(data=go.Scatter(
        x=months, 
        y=contributions,
        mode='lines+markers',
        line=dict(color='#2a5298', width=3),
        marker=dict(size=8, color='#1e3c72')
    ))
    fig2.update_layout(
        title="GitHub Contributions (2025)",
        xaxis_title="Month",
        yaxis_title="Contributions",
        height=300
    )
    st.plotly_chart(fig2, use_container_width=True)

def show_contact_section():
    st.markdown('<h2 class="section-header">Let\'s Connect</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="contact-section">
        <h3>Ready to build something amazing together?</h3>
        <p>I'm always excited to discuss new opportunities, collaborate on interesting projects, or share insights about DevOps and cloud technologies.</p>
        
        <div style="margin-top: 2rem;">
            <a href="mailto:anshuman.mohapatra04@gmail.com" class="contact-button">📧 Email Me</a>
            <a href="https://github.com/Anshuman-git-code" class="contact-button" target="_blank">🔗 GitHub</a>
            <a href="tel:+917978294262" class="contact-button">📱 Call Me</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Contact details
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📍 Location
        **Cuttack, Odisha, India**  
        CDA, Sector - 7  
        Pin: 753014
        """)
    
    with col2:
        st.markdown("""
        ### 📞 Contact Info
        **Phone:** +91-7978294262  
        **Email:** anshuman.mohapatra04@gmail.com  
        **Languages:** English, Odia, Hindi
        """)
    
    with col3:
        st.markdown("""
        ### 🎓 Education
        **B.Tech Computer Science**  
        ITER, SOA University  
        Expected Graduation: 2026  
        """)
    
    # Education timeline
    st.markdown("### 🎓 Education Journey")
    
    education_timeline = [
        {
            "year": "2022 - 2026",
            "institution": "Institute of Technical Education and Research, Bhubaneshwar",
            "degree": "B.Tech - Computer Science & Engineering"
        },
        {
            "year": "2022",
            "institution": "St. Xavier's High School, Cuttack", 
            "degree": "12th Grade - CBSE"
        },
        {
            "year": "2020",
            "institution": "DAV Public School, Cuttack",
            "degree": "10th Grade - CBSE"
        }
    ]
    
    for edu in education_timeline:
        st.markdown(f"""
        <div class="timeline-item">
            <h4 style="color: #1e3c72; margin-bottom: 0.5rem;">{edu['degree']}</h4>
            <p style="color: #6c757d; margin-bottom: 0.5rem;"><strong>{edu['year']}</strong> | {edu['institution']}</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()