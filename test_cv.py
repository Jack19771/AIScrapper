from cv_generator import CVGenerator, UserProfile, JobRequirements

# Dane użytkownika
user = UserProfile(
    name="Anna Nowak",
    email="anna.nowak@email.com", 
    phone="+48 500 123 456",
    location="Warszawa",
    linkedin="linkedin.com/in/annanowak",
    current_position="Senior Python Developer",
    years_experience=6,
    skills=["Python", "Django", "PostgreSQL", "Docker", "AWS", "scikit-learn", "TensorFlow", "REST API"],
    education="M.Sc. Data Science, Warsaw University of Technology"
)

# Dane z API (ALGOTEQUE)
job = JobRequirements(
    title="Senior Solutions Architect",
    company="ALGOTEQUE SERVICES",
    required_skills=["Python", "ML", "AI", "scikit-learn", "PyTorch", "TensorFlow", "FastAPI", "PySpark"],
    nice_to_have=["Docker", "Kubernetes", "AWS"],
    experience_level="Senior",
    key_requirements=["5+ lat Python/ML", "NLP experience", "Big Data - PySpark"],
    technologies=["Python", "scikit-learn", "TensorFlow", "PyTorch", "FastAPI", "PySpark"]
)

# Generuj CV
generator = CVGenerator()
cv = generator.generate_cv(user, job)
print(cv)