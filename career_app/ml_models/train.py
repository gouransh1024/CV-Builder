"""
Train and serialize a machine learning model for career guidance recommendations.

Uses a scikit-learn TF-IDF + LogisticRegression pipeline trained on rich skill
and responsibility profiles across tech, data, design, finance, marketing,
healthcare, operations, and management domains.
"""

import os
from pathlib import Path
from typing import Optional, Union
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

TRAINING_DATA = [
    # Software & Web Development
    ("python django flask fastapi rest api postgresql docker backend microservices git redis celery sql", "Backend Engineer"),
    ("python backend web development databases sql api redis rabbitmq scalable architecture", "Backend Engineer"),
    ("fastapi django postgresql microservices restful apis server-side development python", "Backend Engineer"),

    ("python java c++ go backend algorithms distributed systems databases grpc aws api linux", "Software Engineer"),
    ("software development coding data structures algorithms object oriented programming design patterns git", "Software Engineer"),
    ("c++ java multithreading system design performance debugging unit testing linux", "Software Engineer"),

    ("javascript typescript react nextjs redux html css tailwind responsive ui frontend web design accessibility", "Frontend Developer"),
    ("frontend react vue web development javascript css html responsive design component libraries", "Frontend Developer"),
    ("typescript react state management web applications ui ux responsive frontend development", "Frontend Developer"),

    ("react nodejs fullstack javascript typescript express postgresql mongodb docker git rest graphql", "Full Stack Developer"),
    ("full stack web development javascript node express react mongo sql frontend backend", "Full Stack Developer"),
    ("mern stack web application development apis node react database integration deployment", "Full Stack Developer"),

    ("java spring boot hibernate maven microservices enterprise backend sql rest kafka docker", "Java Developer"),
    ("java enterprise spring framework jpa rest apis backend development sql microservices", "Java Developer"),

    ("c# net core aspnet entity framework azure sql server rest api microservices csharp", ".NET Developer"),
    ("csharp dotnet core asp net web api visual studio entity framework sql", ".NET Developer"),

    ("swift ios uikit swiftui xcode coredata cocoa mobile apple app store app development", "iOS Developer"),
    ("ios mobile app development swift swiftui xcode mobile interfaces apple devices", "iOS Developer"),

    ("kotlin android jetpack compose android studio java mobile sdk gradle material design", "Android Developer"),
    ("android app development kotlin java mobile sdk material design play store", "Android Developer"),

    ("flutter dart cross-platform mobile mobile app development widgets firebase android ios", "Flutter Developer"),
    ("cross platform mobile development flutter dart mobile apps state management firebase", "Flutter Developer"),

    # Data & AI / Machine Learning
    ("python pandas numpy scikit-learn machine learning deep learning tensorflow pytorch nlp computer vision data science", "Data Scientist"),
    ("machine learning data science predictive modeling statistics python pandas scikit learn ai algorithms", "Data Scientist"),
    ("data science mathematical modeling deep learning python data exploration hypothesis testing", "Data Scientist"),

    ("python sql powerbi tableau excel data analysis reporting statistics business intelligence dashboards metrics", "Data Analyst"),
    ("data analysis sql queries excel dashboards visualizations reporting data insights business metrics", "Data Analyst"),
    ("business data analysis tableau powerbi statistical analysis reporting quantitative research sql", "Data Analyst"),

    ("python spark hadoop kafka airflow dbt snowflake bigquery data warehouse etl sql data pipeline", "Data Engineer"),
    ("data engineering etl pipelines big data spark airflow sql data lake snowflake streaming", "Data Engineer"),
    ("data warehouse pipeline architecture kafka dbt python sql distributed data processing", "Data Engineer"),

    ("python pytorch tensorflow mlops huggingface transformers llm machine learning deployment docker model serving", "ML Engineer"),
    ("machine learning engineering model training deployment mlops kubeflow fastapi inference pipelines", "ML Engineer"),

    ("business intelligence sql powerbi tableau dax data modeling dashboards reporting kpi etl", "BI Analyst"),
    ("bi dashboards kpi tracking powerbi tableau data modeling reporting analytics", "BI Analyst"),

    # Cloud, DevOps & Infrastructure
    ("docker kubernetes aws terraform ansible ci cd jenkins linux bash devops helm prometheus grafana", "DevOps Engineer"),
    ("devops continuous integration delivery docker containerization kubernetes cloud deployment bash", "DevOps Engineer"),
    ("ci cd pipelines automation infrastructure as code terraform aws kubernetes monitoring", "DevOps Engineer"),

    ("aws cloud infrastructure architecture lambda s3 ec2 iam cloudformation cost optimization terraform", "Cloud Architect"),
    ("cloud computing architecture azure aws gcp cloud migration enterprise infrastructure security", "Cloud Architect"),

    ("cybersecurity penetration testing ethical hacking network security siem firewall wireshark vulnerability assessment nist", "Security Analyst"),
    ("infosec cybersecurity risk assessment vulnerability scanning incident response network defense compliance", "Security Analyst"),

    ("linux bash administration networking dns tcp ip monitoring automation ansible server maintenance", "Systems Administrator"),
    ("system administration linux unix server management shell scripting networking trouble shooting", "Systems Administrator"),

    ("database administration oracle postgresql mysql sql performance tuning backups indexing replication high availability", "Database Administrator"),
    ("dba database administration sql performance tuning backup recovery disaster planning mysql postgresql", "Database Administrator"),

    # Quality Assurance & Testing
    ("selenium automation cypress pytest jest testing test cases quality assurance sdet bug tracking junit", "QA Automation Engineer"),
    ("test automation selenium webdriver cypress end-to-end testing quality assurance api testing", "QA Automation Engineer"),

    ("manual testing test plans bug reporting regression smoke acceptance jira test cases quality assurance", "QA Manual Tester"),
    ("quality assurance manual test cases exploratory testing user acceptance testing jira bug tracking", "QA Manual Tester"),

    # Design & Product
    ("figma ui ux wireframes prototyping user research usability testing design system visual design interaction", "UI/UX Designer"),
    ("user experience user interface design wireframing prototyping figma user research design thinking", "UI/UX Designer"),

    ("photoshop illustrator indesign graphic design branding typography logo vector visual assets creative", "Graphic Designer"),
    ("visual design creative branding logo graphic illustration marketing materials photoshop", "Graphic Designer"),

    ("product roadmap user stories agile scrum backlog stakeholder management analytics market research strategy", "Product Manager"),
    ("product management feature prioritization product strategy user discovery metrics roadmap agile", "Product Manager"),

    ("scrum agile sprint planning kanban jira servant leadership coaching retrospectives team velocity", "Scrum Master"),
    ("agile methodology scrum master sprint execution facilitation kanban coaching team workflows", "Scrum Master"),

    # Marketing & Growth
    ("seo sem google analytics content marketing social media copywriting meta ads campaign email marketing roas", "Marketing Specialist"),
    ("digital marketing seo campaigns content strategy growth marketing brand awareness analytics", "Marketing Specialist"),

    ("content writing copywriting technical writing blogging articles storytelling seo editing proofreading documentation", "Content Writer"),
    ("creative writing blog articles copywriting social media copy content creation editorial", "Content Writer"),

    ("technical documentation api reference user guides markdown swagger technical writing software docs manuals", "Technical Writer"),
    ("technical author documentation api docs software guides manuals clear technical explanations", "Technical Writer"),

    ("sales b2b business development negotiation lead generation crm client relationships pipeline revenue prospecting", "Sales Representative"),
    ("b2b sales account management client acquisition deal closing customer outreach revenue growth", "Sales Representative"),

    # Finance, Accounting & Business
    ("financial modeling valuation excel forecasting dcf financial statements accounting budgeting variance analysis", "Financial Analyst"),
    ("financial analysis forecasting corporate finance budgeting excel financial modeling reporting", "Financial Analyst"),

    ("accounting bookkeeping general ledger reconciliation tax preparation audit gaap balance sheet quickbooks", "Accountant"),
    ("financial accounting bookkeeping balance sheet cash flow profit loss tax compliance ledger", "Accountant"),

    ("business analysis requirements gathering process mapping bpmn stakeholder interviews gap analysis user stories jira", "Business Analyst"),
    ("business process improvement requirements documentation workflow analysis stakeholder engagement", "Business Analyst"),

    ("operations supply chain logistics inventory procurement vendor management process improvement workflow lean", "Operations Manager"),
    ("operational management logistics supply chain efficiency resource planning vendor coordination", "Operations Manager"),

    # Human Resources & Education
    ("talent acquisition recruitment interviewing onboarding applicant tracking hr policies employee relations benefits", "HR Manager"),
    ("human resources recruiting talent management hr operations employee engagement onboarding", "HR Manager"),

    ("instructional design curriculum training pedagogy e-learning workshops coaching assessment education", "Corporate Trainer"),
    ("employee training professional development workshops coaching adult learning presentation skills", "Corporate Trainer"),

    # Healthcare & Law
    ("clinical healthcare administration medical records hipaa patient care health informatics compliance billing", "Healthcare Administrator"),
    ("healthcare management clinical operations hospital administration compliance patient records", "Healthcare Administrator"),

    ("legal compliance contracts regulatory governance risk policy due diligence legal research documentation", "Compliance Officer"),
    ("regulatory compliance corporate governance risk management legal policies ethics auditing", "Compliance Officer"),
]


def train_and_save_model(output_path: Optional[Union[str, Path]] = None) -> Pipeline:
    """Train the career guidance NLP pipeline and save to disk."""
    if output_path is None:
        base_dir = Path(__file__).resolve().parent
        output_path = base_dir / "career_guidance_model.pkl"
    else:
        output_path = Path(output_path)

    X = [text for text, _ in TRAINING_DATA]
    y = [career for _, career in TRAINING_DATA]

    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=(1, 2),
                stop_words="english",
                min_df=1,
                sublinear_tf=True,
            ),
        ),
        (
            "classifier",
            LogisticRegression(
                C=2.0,
                max_iter=1000,
                random_state=42,
            ),
        ),
    ])

    pipeline.fit(X, y)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, output_path)
    print(f"[OK] Model successfully trained on {len(X)} profiles across {len(set(y))} unique careers.")
    print(f"[OK] Saved model to: {output_path} ({os.path.getsize(output_path)} bytes)")
    return pipeline


if __name__ == "__main__":
    model = train_and_save_model()
    test_cases = [
        "python pandas numpy machine learning statistics",
        "react typescript html css frontend responsive",
        "docker kubernetes aws ci cd terraform linux",
        "financial modeling excel forecasting valuation",
    ]
    print("\nTest Predictions:")
    for query in test_cases:
        probas = model.predict_proba([query])[0]
        top_indices = probas.argsort()[-3:][::-1]
        top_preds = [f"{model.classes_[i]} ({probas[i]*100:.1f}%)" for i in top_indices]
        print(f" - '{query}': {', '.join(top_preds)}")
