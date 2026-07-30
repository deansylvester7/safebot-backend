from urllib import response
from weakref import ref

from flask import Flask, request, jsonify, send_file, redirect
from pinecone import Pinecone
from dotenv import load_dotenv
from flask_cors import CORS
import os
load_dotenv()

SECTION_STARTS = [
    (5, "Abrasive Blasting Program"),
    (8, "Access to Medical Records Program"),
    (11, "Aerial Lifts Program"),
    (16, "Arsenic Awareness Program"),
    (19, "Asbestos Awareness Program"),
    (27, "Assured Grounding Conductors"),
    (29, "Behavior Based Safety Program"),
    (39, "Benzene Exposure Control Program"),
    (51, "Bloodborne Pathogens Program"),
    (69, "Business Continuity Program"),
    (71, "Cadmium Program"),
    (75, "Cold Weather Safety Program"),
    (84, "Compressed Air Safety Program"),
    (87, "Concrete and Masonry Program"),
    (96, "Confined Space Safety Program"),
    (126, "Cranes Program (US)"),
    (134, "Demolition and Blasting"),
    (153, "Disciplinary Program"),
    (156, "Driving Safety Program"),
    (161, "Electrical Safety Program"),
    (164, "Emergency Action Plan"),
    (173, "Hazard Analysis (JSA)"),
    (183, "Excavations and Trenching"),
    (215, "Fall Protection Program"),
    (221, "Fatigue Management"),
    (223, "Fire Protection"),
    (227, "First Aid"),
    (235, "Fit for Duty"),
    (237, "Forklifts & Powered Industrial Trucks"),
    (249, "Waste Management"),
    (251, "GFCI Program"),
    (253, "Hand and Power Tools"),
    (259, "Hazard Communication"),
    (268, "Heat Illness Prevention"),
    (277, "Heavy Equipment"),
    (283, "Hexavalent Chromium"),
    (288, "Housekeeping"),
    (291, "Slips, Trips & Falls"),
    (296, "Hydrogen Sulfide"),
    (302, "Illumination"),
    (303, "Incident Investigation"),
    (320, "Injury / Illness Recordkeeping"),
    (323, "Ionizing Radiation"),
    (328, "Ladder Safety"),
    (332, "Lead Awareness"),
    (337, "Lockout / Tagout"),
    (346, "Machine Guarding"),
    (350, "Manual Lifting"),
    (352, "Material Handling & Storage"),
    (354, "Mobile Equipment"),
    (356, "Noise & Hearing Conservation"),
    (360, "Drug & Alcohol Policy"),
    (364, "Pandemic Preparedness"),
    (371, "Personal Protective Equipment (PPE)"),
    (378, "Preventative Maintenance"),
    (380, "Respiratory Protection"),
    (388, "Rigging"),
    (391, "Risk Assessment"),
    (399, "Scaffolds"),
    (405, "Short Service Employee"),
    (407, "Stop Work Authority"),
    (409, "Subcontractor Management"),
    (420, "Traffic Control"),
    (453, "Welding, Cutting & Hot Work"),
    (463, "Working Alone"),
    (468, "Silica Exposure"),
    (474, "Commercial Fleet Safety"),
    (489, "Overhead & Gantry Cranes"),
    (499, "Fleet Safety"),
]
HANDBOOK_SECTION_STARTS = [
    (4, "Welcome"),
    (5, "T&T Industrial Commitments"),
    (5, "Equal Opportunity Employment and No-Harassment Policy"),
    (7, "Workplace Violence Policy"),
    (8, "Anti-Retaliation Commitment"),
    (8, "General Safety Policy"),
    (8, "Drug and Alcohol-Free Workplace and Testing Policy"),
    (12, "Smoke Free Workplace"),
    (12, "Problem Resolution & Reporting Policy"),
    (13, "Americans with Disabilities Act (ADA)"),
    (14, "Religious Accommodation"),
    
    (14, "Employment"),
    (14, "New Hires and Introductory Periods"),
    (15, "Employment Authorization Verification"),
    (15, "Reporting Changes to Personal Information"),
    (15, "Employment of Relatives and Friends"),
    (16, "Job Descriptions"),
    (16, "Posting of Openings"),
    (16, "Training Program"),

    (16, "Workplace Guidelines & General Policies"),
    (16, "Standards of Conduct"),
    (17, "Attendance Policy"),
    (18, "Personal Appearance"),
    (18, "Suggestion Policy"),
    (19, "Nonsolicitation/Nondistribution Policy"),
    (19, "Employer Sponsored Social Events"),
    (19, "Bulletin Boards"),
    (19, "Access to Personnel and Medical Records Files"),
    (20, "Third Party Disclosures"),

    (20, "Wage and Hour Policies"),
    (20, "Recording Time"),
    (20, "Direct Deposit"),
    (21, "Paycheck Deductions"),
    (21, "Pay Period"),
    (21, "Overtime"),
    (21, "Job Abandonment"),
    (21, "Meal and Rest Periods"),
    (22, "Accommodations for Nursing Mothers"),

    (22, "Employee Benefits"),
    (23, "COBRA"),
    (23, "Retirement Plan"),
    (24, "Tuition Reimbursement"),
    (24, "Leadership Development"),
    (24, "Life Insurance"),
    (24, "Short-Term Disability"),
    (24, "Critical Illness Coverage"),
    (25, "Accidental Coverage"),
    (25, "Workers' Compensation Insurance Policy"),
    (25, "Unemployment Compensation Insurance Policy"),
    (25, "Paid Time Off (PTO)"),
    (27, "Holidays"),
    (28, "Sick Pay"),
    (28, "Vacation Policy"),
    (28, "Bereavement Leave"),
    (28, "Voting Leave"),
    (29, "Jury Duty Leave"),
    (29, "Military Leave (USERRA)"),
    (29, "Personal Leave of Absence"),
    (30, "Family and Medical Leave Act (FMLA)"),

    (33, "Job Performance"),
    (33, "Performance Improvement"),
    (33, "Pay Raises"),
    (34, "Promotions"),
    (34, "Performance Bonus"),
    (34, "Transfers"),
    (34, "Disciplinary Process"),
    (34, "Criminal Activity/Arrests"),
    (35, "Workforce Reductions (Layoffs)"),

    (36, "Conflicts of Interest"),
    (36, "Outside Employment"),

    (37, "Customer Relations"),
    (37, "Customer, Client, and Visitor Relations"),
    (37, "Products and Services Knowledge"),

    (37, "Trade Secrets and Inventions"),
    (37, "Confidentiality and Nondisclosure of Trade Secrets"),
    (38, "Inventions"),

    (38, "Finance Policies"),
    (38, "Business Expenses Policy"),
    (38, "Travel Expenses"),
    (41, "Use of Employer Credit Cards"),

    (41, "Computer, Vehicle, and Equipment Use"),
    (41, "Authorization for Use of Personal Vehicle"),
    (41, "Use of Employer Vehicles"),
    (42, "GPS Monitoring of Employer Vehicles"),
    (42, "Personal Cell Phone/Mobile Device Use"),
    (43, "Use of Company Technology"),
    (44, "Computer Security and Copying of Software"),
    (44, "Security"),
    (44, "Social Media Policy"),
    (45, "Workplace Privacy and Right to Inspect"),
    (46, "Off-Duty Use of Employer Property or Premises"),

    (46, "Termination of Employment"),
    (46, "Resignation Policy"),
    (47, "Post-Employment References"),
    (47, "Exit Interview"),

    (47, "Closing Statement"),
    (48, "Acknowledgment of Receipt and Review"),
]

def get_handbook_section_title(page):
    title = "Employee Handbook"

    for start_page, section in HANDBOOK_SECTION_STARTS:
        if page >= start_page:
            title = section
        else:
            break

    return title

def get_section_title(page):
    for i, (start_page, title) in enumerate(SECTION_STARTS):
        next_start = (
            SECTION_STARTS[i + 1][0]
            if i + 1 < len(SECTION_STARTS)
            else float("inf")
        )

        # Normal case
        if start_page <= page < next_start:
            return title

        # Pinecone sometimes cites the page immediately before a section.
        if page == start_page - 1:
            return title

    return "T&T Industrial HSE Manual"



app = Flask(__name__)
print("APP VERSION 7.16.26 WITH EMPLOYEE HANDBOOK")
CORS(app)

pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

ASSISTANT_NAME = "safebot"

@app.route("/")
def home():
    return {
        "status": "online",
        "assistant": ASSISTANT_NAME
    }


@app.route("/test")
def test():
    return "test route works"


@app.route("/manual")
def manual():
    pdf_path = os.path.join(
        os.path.dirname(__file__),
        "manuals",
        "TT_HSE_Manual.pdf"
    )

    return send_file(
        pdf_path,
        mimetype="application/pdf"
    )


@app.route("/handbook")
def handbook():
    pdf_path = os.path.join(
        os.path.dirname(__file__),
        "manuals",
        "Employee_Handbook.pdf"
    )

    return send_file(
        pdf_path,
        mimetype="application/pdf"
    )


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question")
    history = data.get("history", [])

    if not question:
        return jsonify({
            "error": "No question provided"
        }), 400

    try:
        pinecone_messages = []

        # Include conversation history
        for msg in history:
            pinecone_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Current question
        pinecone_messages.append({
            "role": "user",
            "content": (
                "You are T&T Industrial's AI assistant. "
                "Answer questions only using the documents in your knowledge base, "
                "including the Health, Safety, and Environmental (HSE) Manual and the Employee Handbook. "
                "Use previous conversation context when relevant. "
                "If the answer is not found in the available company documents, respond exactly: "
                "'Not found in company documentation. Contact your supervisor or Human Resources.'\n\n"
                f"Question: {question}"
            )
        })

        response = pc.assistant.chat(
            assistant_name=ASSISTANT_NAME,
            messages=pinecone_messages
        )

        sources = []

        if hasattr(response, "citations"):
            for citation in response.citations:
                for ref in citation.references:
                    try:
                        pages = sorted(list(ref.pages))

                        if pages:
                            page = pages[len(pages) // 2]
                        else:
                            page = 1

                        filename = getattr(ref.file, "name", "")
                        print(ref)
                        print("FILE:", ref.file)
                        print("PAGES:", pages)
                        print("SECTION:", get_section_title(page))
                        if filename == "Employee_Handbook.pdf":
                            source = {
                                "document": "Employee Handbook",
                                "title": get_handbook_section_title(page),
                                "page": page,
                            }

                        else:
                            source = {
                                "document": "HSE Manual",
                                "title": get_section_title(page),
                                "page": page,
                            }

                        if source not in sources:
                            sources.append(source)

                    except Exception as e:
                        print("Citation error:", e)

        print("FINAL SOURCES:", sources)

        log_entry = {
            "question": question,
            "answer": response.message.content
        }

        with open("logs.txt", "a", encoding="utf-8") as f:
            f.write(str(log_entry) + "\n")

        print("FINAL SOURCES:", sources)

        return jsonify({
            "answer": response.message.content,
            "sources": sources,
            "status": "success"
        })

    except Exception as e:
        print(e)

        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500
        
@app.route("/manual-viewer")
def manual_viewer():
    return redirect("/static/pdfjs/web/viewer.html?file=/manual")
@app.route("/handbook-viewer")
def handbook_viewer():
    return redirect("/static/pdfjs/web/viewer.html?file=/handbook")

if __name__ == "__main__":
    print(app.url_map)
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
