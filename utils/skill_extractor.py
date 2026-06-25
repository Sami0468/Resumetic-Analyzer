import re

TECHNICAL_SKILLS = {
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "ruby", "go", "golang",
    "rust", "kotlin", "swift", "php", "scala", "r", "matlab", "perl", "bash", "shell",
    # Web
    "html", "css", "html5", "css3", "react", "reactjs", "react.js", "angular", "angularjs",
    "vue", "vuejs", "vue.js", "node", "nodejs", "node.js", "express", "expressjs", "next.js",
    "nextjs", "nuxt", "svelte", "jquery", "bootstrap", "tailwind", "sass", "less",
    # Backend / APIs
    "flask", "django", "fastapi", "spring", "springboot", "asp.net", "laravel", "rails",
    "graphql", "rest", "restful", "api", "microservices", "grpc",
    # Databases
    "sql", "mysql", "postgresql", "postgres", "sqlite", "mongodb", "redis", "cassandra",
    "dynamodb", "firebase", "elasticsearch", "oracle", "mssql",
    # Cloud / DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "terraform",
    "ansible", "jenkins", "ci/cd", "github actions", "gitlab ci", "linux", "nginx",
    "apache", "heroku", "vercel", "netlify",
    # Data / AI / ML
    "machine learning", "deep learning", "data science", "nlp", "natural language processing",
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "pandas", "numpy",
    "matplotlib", "seaborn", "opencv", "computer vision", "ai", "artificial intelligence",
    # Tools
    "git", "github", "gitlab", "bitbucket", "jira", "confluence", "trello", "slack",
    "figma", "photoshop", "illustrator", "xd", "postman", "swagger",
    # Other
    "blockchain", "solidity", "web3", "unity", "unreal", "android", "ios", "flutter",
    "react native", "xamarin", "selenium", "pytest", "junit", "cypress", "agile", "scrum",
}

SOFT_SKILLS = {
    "communication", "leadership", "teamwork", "team player", "problem solving",
    "problem-solving", "critical thinking", "time management", "adaptability", "creativity",
    "collaboration", "attention to detail", "multitasking", "decision making",
    "conflict resolution", "emotional intelligence", "presentation", "negotiation",
    "customer service", "mentoring", "coaching", "project management", "analytical",
    "organized", "self-motivated", "fast learner", "quick learner",
}

def tokenize(text):
    return re.findall(r'[a-zA-Z0-9#.+/\-]+', text.lower())

def extract_skills(text):
    text_lower = text.lower()
    tokens = tokenize(text)
    token_set = set(tokens)

    found_tech = set()
    found_soft = set()

    # Multi-word skill matching
    for skill in TECHNICAL_SKILLS:
        if ' ' in skill:
            if skill in text_lower:
                found_tech.add(skill.title())
        else:
            if skill in token_set:
                found_tech.add(skill.upper() if len(skill) <= 4 else skill.title())

    for skill in SOFT_SKILLS:
        if ' ' in skill or '-' in skill:
            if skill in text_lower:
                found_soft.add(skill.title())
        else:
            if skill in token_set:
                found_soft.add(skill.title())

    return {
        "technical": sorted(list(found_tech)),
        "soft": sorted(list(found_soft)),
        "all": sorted(list(found_tech | found_soft))
    }

def extract_jd_skills(jd_text):
    result = extract_skills(jd_text)
    return result["all"]