"""
Seed script — creates default admin user and initial knowledge base data.
Run once after first deployment: python scripts/seed_db.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, create_tables
from app.core.security import hash_password
from app.models.user import User
from app.models.faq import FAQ
from app.models.procedure import Procedure


def seed():
    create_tables()
    db = SessionLocal()

    try:
        # ── Default Admin ──
        admin = db.query(User).filter(User.email == "admin@dept.edu").first()
        if not admin:
            admin = User(
                name="Department Administrator",
                email="admin@dept.edu",
                hashed_password=hash_password("admin123"),
                role="admin",
                department="Computer Science & Engineering",
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("✅ Admin user created: admin@dept.edu / admin123")
        else:
            print("ℹ️  Admin user already exists")
            
        # ── Default Student ──
        student_email = "student@test.edu"
        student = db.query(User).filter(User.email == student_email).first()
        if not student:
            student = User(
                name="Test Student",
                email=student_email,
                student_id="ST-2026-1001",
                hashed_password=hash_password("student123"),
                role="student",
                department="Computer Science & Engineering",
            )
            db.add(student)
            db.commit()
            db.refresh(student)
            print(f"✅ Student user created: {student_email} / student123")
        else:
            print("ℹ️  Student user already exists")

        # ── Default FAQs ──
        if db.query(FAQ).count() == 0:
            faqs = [
                FAQ(question="What is the minimum CGPA requirement to graduate?",
                    answer="Students must maintain a minimum CGPA of 2.5 to be eligible for graduation. Students with CGPA below 2.0 will receive academic probation notice.",
                    category="Academic", is_active=True, created_by=admin.id),
                FAQ(question="How do I get my official transcript?",
                    answer="Submit Form TR-01 to the department office. Processing takes 5-7 working days. Rush processing (2 days) is available at additional fee. Bring your student ID when collecting.",
                    category="Administrative", is_active=True, created_by=admin.id),
                FAQ(question="What is the attendance policy?",
                    answer="Minimum 75% attendance is required to sit for final exams. Below 75% results in automatic NC (Not Complete) grade. Medical certificates must be submitted within 3 working days of the absence.",
                    category="Exams", is_active=True, created_by=admin.id),
                FAQ(question="When are tuition fees due?",
                    answer="Fees are due within the first 2 weeks of each semester. Late payment incurs a 2% monthly surcharge. Scholarship students must confirm renewal at the financial aid office annually.",
                    category="Fees", is_active=True, created_by=admin.id),
                FAQ(question="Can I take courses from other departments?",
                    answer="Yes, with academic advisor approval. Elective slots allow up to 2 courses from other departments per semester, subject to prerequisites and seat availability.",
                    category="Academic", is_active=True, created_by=admin.id),
                FAQ(question="How do I apply for a scholarship?",
                    answer="Scholarship applications open at the start of each academic year. Submit Form SC-01 with your CGPA certificate, income certificate, and recommendation letter to the scholarship committee.",
                    category="Fees", is_active=True, created_by=admin.id),
                FAQ(question="Who is the department head?",
                    answer="The department is currently headed by Prof. Dr. Kabir Hossain. Office hours are Sunday-Thursday 10am-12pm. Appointments can be booked through the department office.",
                    category="Administrative", is_active=True, created_by=admin.id),
                FAQ(question="How do I register for thesis?",
                    answer="Thesis registration requires completion of 120 credits. Submit the thesis registration form with your proposed supervisor's signature before the semester registration deadline.",
                    category="Academic", is_active=True, created_by=admin.id),
            ]
            db.add_all(faqs)
            db.commit()
            print(f"✅ {len(faqs)} FAQs created")
        else:
            print(f"ℹ️  FAQs already exist ({db.query(FAQ).count()} found)")

        # ── Default Procedures ──
        if db.query(Procedure).count() == 0:
            procedures = [
                Procedure(
                    title="Thesis Submission Process", category="Academic",
                    steps=[
                        "Get supervisor approval and signatures by November 30",
                        "Upload soft copy (PDF) to the student portal by December 15",
                        "Submit 3 spiral-bound hard copies to the department office by December 17",
                        "Pay thesis binding fee at the accounts section (keep receipt)",
                        "Submit payment receipt and supervisor approval form to the coordinator",
                        "Collect acknowledgment slip from the department office",
                    ],
                    is_active=True, created_by=admin.id
                ),
                Procedure(
                    title="Course Waiver Application", category="Administrative",
                    steps=[
                        "Obtain Form DW-01 from the department office or download from portal",
                        "Attach the syllabus/course outline from the equivalent course at your previous institution",
                        "Get your academic supervisor's signature on the form",
                        "Submit the complete package to the Academic Section before the add/drop deadline",
                        "The committee reviews within 7-10 working days",
                        "Collect the decision letter from the Academic Section",
                    ],
                    is_active=True, created_by=admin.id
                ),
                Procedure(
                    title="Official Transcript Request", category="Administrative",
                    steps=[
                        "Fill Form TR-01 available at the department office",
                        "Pay the transcript fee at the accounts section",
                        "Attach the payment receipt to the completed form",
                        "Submit the form and receipt to the department office",
                        "Collect your transcript after 5-7 working days (bring student ID)",
                    ],
                    is_active=True, created_by=admin.id
                ),
                Procedure(
                    title="Exam Re-evaluation Request", category="Exams",
                    steps=[
                        "Submit the re-evaluation application within 7 days of result publication",
                        "Fill Form RE-02 with course code, semester, and reason for re-evaluation",
                        "Pay the re-evaluation fee at the accounts section",
                        "Submit the form and receipt to the exam section",
                        "Results are published within 14 working days",
                    ],
                    is_active=True, created_by=admin.id
                ),
                Procedure(
                    title="Internship Registration", category="Academic",
                    steps=[
                        "Find a company and get a formal offer letter",
                        "Get supervisor approval (Form INT-01)",
                        "Register the internship in the student portal",
                        "Submit the offer letter and Form INT-01 to the academic section",
                        "Complete a minimum of 8 weeks of internship",
                        "Submit internship report within 2 weeks of completion",
                    ],
                    is_active=True, created_by=admin.id
                ),
            ]
            db.add_all(procedures)
            db.commit()
            print(f"✅ {len(procedures)} Procedures created")
        else:
            print(f"ℹ️  Procedures already exist ({db.query(Procedure).count()} found)")

        print("\n🎉 Database seeding complete!")
        print("\nDefault credentials:")
        print("  Admin: admin@dept.edu / admin123")
        print("\nChange these credentials in production!")

    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
