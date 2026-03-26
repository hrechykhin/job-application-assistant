"""Seed the database with a demo user and sample application data.

Usage:
    cd backend
    python seed_demo.py

    # or via Docker:
    docker compose exec backend python seed_demo.py
"""

import sys
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import engine
from app.models.application import Application, ApplicationStatus
from app.models.job import Job
from app.models.user import User

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "Demo1234!"
DEMO_NAME = "Demo User"

SAMPLE_JOBS = [
    {
        "title": "Senior Python Engineer",
        "company_name": "Spotify",
        "location": "Stockholm, SE",
        "job_url": "https://example.com/job/1",
        "description": "We are looking for a Senior Python Engineer to join our backend platform team. You will design and maintain high-throughput data pipelines, work with asyncio-based services, and collaborate with cross-functional teams across Europe.",
    },
    {
        "title": "Backend Engineer – Payments",
        "company_name": "N26",
        "location": "Berlin, DE",
        "job_url": "https://example.com/job/2",
        "description": "N26 is hiring a Backend Engineer to join our Payments tribe. You will build and scale our payment processing infrastructure using Python, FastAPI, and PostgreSQL. Strong understanding of financial systems and PCI-DSS compliance is a plus.",
    },
    {
        "title": "Full Stack Developer",
        "company_name": "Booking.com",
        "location": "Amsterdam, NL",
        "job_url": "https://example.com/job/3",
        "description": "Join Booking.com as a Full Stack Developer. You will work on customer-facing features using React and TypeScript on the frontend and Python microservices on the backend. Comfort with A/B testing and data-driven development is key.",
    },
    {
        "title": "Python Developer",
        "company_name": "Zalando",
        "location": "Berlin, DE",
        "job_url": "https://example.com/job/4",
        "description": "Zalando is seeking a Python Developer to help build our catalog and search platform. You will write clean, tested Python code, contribute to our internal tooling, and work in an autonomous, product-focused team.",
    },
    {
        "title": "Software Engineer – Backend",
        "company_name": "Revolut",
        "location": "London, UK",
        "job_url": "https://example.com/job/5",
        "description": "Revolut is looking for a Backend Software Engineer to work on our core banking infrastructure. You will build high-availability services in Python, work with event-driven architecture, and own features end-to-end.",
    },
    {
        "title": "API Engineer",
        "company_name": "Adyen",
        "location": "Amsterdam, NL",
        "job_url": "https://example.com/job/6",
        "description": "Adyen is hiring an API Engineer to design and maintain our public-facing payment APIs. You will work closely with merchants and partners, maintain OpenAPI specifications, and ensure developer experience is world-class.",
    },
    {
        "title": "Backend Developer",
        "company_name": "Delivery Hero",
        "location": "Berlin, DE",
        "job_url": "https://example.com/job/7",
        "description": "Delivery Hero is looking for a Backend Developer to join our logistics team. You will build scalable order dispatching services, work with Kafka and PostgreSQL, and improve reliability across our delivery network.",
    },
    {
        "title": "Senior Engineer",
        "company_name": "Wise",
        "location": "Tallinn, EE",
        "job_url": "https://example.com/job/8",
        "description": "Wise is hiring a Senior Engineer for our international transfer infrastructure. You will contribute to reducing transfer costs and improving speed for millions of customers using Python and event-driven microservices.",
    },
    {
        "title": "Software Engineer",
        "company_name": "SumUp",
        "location": "Berlin, DE",
        "job_url": "https://example.com/job/9",
        "description": "SumUp is looking for a Software Engineer to help merchants grow their business. You will build payment and merchant management features using Go and Python in a distributed team across Europe.",
    },
    {
        "title": "Python Engineer",
        "company_name": "GetYourGuide",
        "location": "Berlin, DE",
        "job_url": "https://example.com/job/10",
        "description": "GetYourGuide is seeking a Python Engineer to work on our experiences marketplace. You will build and maintain backend services, improve search and recommendations, and collaborate with product and data teams.",
    },
    {
        "title": "Backend Developer",
        "company_name": "Personio",
        "location": "Munich, DE",
        "job_url": "https://example.com/job/11",
        "description": "Personio is hiring a Backend Developer to help build the next generation of HR software in Europe. You will work with Python, PostgreSQL, and REST APIs in a fast-growing B2B SaaS company.",
    },
    {
        "title": "Platform Engineer",
        "company_name": "HelloFresh",
        "location": "Berlin, DE",
        "job_url": "https://example.com/job/12",
        "description": "HelloFresh is looking for a Platform Engineer to improve developer tooling and internal infrastructure. You will work on CI/CD pipelines, Kubernetes, and internal developer platforms used by 300+ engineers.",
    },
]

_now = datetime.now(UTC)

# (status, notes, interview_at, deadline)
APP_CONFIG: list[tuple] = [
    (
        ApplicationStatus.SAVED,
        "Great culture, strong Python team. Check benefits package before applying.",
        None,
        _now + timedelta(days=10),
    ),
    (
        ApplicationStatus.SAVED,
        "Remote-friendly policy — confirm if hybrid is required.",
        None,
        None,
    ),
    (ApplicationStatus.SAVED, None, None, None),
    (
        ApplicationStatus.APPLIED,
        "Applied via LinkedIn. Recruiter viewed profile next day.",
        None,
        None,
    ),
    (
        ApplicationStatus.APPLIED,
        "Referral from a contact on the payments team.",
        None,
        None,
    ),
    (ApplicationStatus.APPLIED, None, None, None),
    (
        ApplicationStatus.INTERVIEW,
        "Technical screen done — went well. Waiting for system design round invite.",
        None,
        None,
    ),
    (
        ApplicationStatus.INTERVIEW,
        "Second interview scheduled. Prepare system design: distributed rate limiter.",
        _now + timedelta(days=5),
        None,
    ),
    (
        ApplicationStatus.OFFER,
        "Offer received: €95k base + equity. Waiting for written contract. Deadline to respond: end of week.",
        None,
        None,
    ),
    (
        ApplicationStatus.REJECTED,
        "Rejected after coding test. Feedback: strong on algorithms, weaker on system design.",
        None,
        None,
    ),
    (ApplicationStatus.SAVED, "Interesting product — look at their tech blog first.", None, None),
    (ApplicationStatus.APPLIED, None, None, None),
]


def seed() -> None:
    with Session(engine) as session:
        existing = session.query(User).filter_by(email=DEMO_EMAIL).first()
        if existing:
            print(f"Demo user '{DEMO_EMAIL}' already exists — skipping.")
            sys.exit(0)

        user = User(
            email=DEMO_EMAIL,
            hashed_password=hash_password(DEMO_PASSWORD),
            full_name=DEMO_NAME,
            is_active=True,
        )
        session.add(user)
        session.flush()

        jobs = []
        for job_data in SAMPLE_JOBS:
            job = Job(user_id=user.id, **job_data)
            session.add(job)
            jobs.append(job)
        session.flush()

        for i, (status, notes, interview_at, deadline) in enumerate(APP_CONFIG):
            app = Application(
                user_id=user.id,
                job_id=jobs[i].id,
                status=status,
                notes=notes,
                interview_at=interview_at,
                deadline=deadline,
                applied_at=(_now - timedelta(days=14 - i)) if status != ApplicationStatus.SAVED else None,
            )
            session.add(app)

        session.commit()

    status_counts: dict[str, int] = {}
    for status, *_ in APP_CONFIG:
        status_counts[status] = status_counts.get(status, 0) + 1

    print(f"Demo data created successfully.")
    print(f"  User:  {DEMO_EMAIL} / {DEMO_PASSWORD}")
    print(f"  Jobs:  {len(SAMPLE_JOBS)}")
    print(f"  Applications: {len(APP_CONFIG)}")
    for s, count in sorted(status_counts.items()):
        print(f"    {s}: {count}")


if __name__ == "__main__":
    seed()
