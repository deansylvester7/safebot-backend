from flask import Flask, request, jsonify, send_file
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

def get_section_title(page):
    title = "T&T Industrial HSE Manual"

    for start_page, section in SECTION_STARTS:
        if page >= start_page:
            title = section
        else:
            break

    return title

app = Flask(__name__)
print("APP VERSION WITH MANUAL ROUTE LOADED")
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

    print("PDF PATH:", pdf_path)
    print("FILE EXISTS:", os.path.exists(pdf_path))

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
                "You are a construction safety assistant. "
                "Only answer using the safety manual. "
                "Use previous conversation context when relevant. "
                "If the answer is not found, respond exactly: "
                "'Not found in safety manual. Contact supervisor.'\n\n"
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
                        pages = list(ref.pages)

                        page = min(pages) if pages else 1

                        source = {
                            "title": get_section_title(page),
                            "pages": pages
                        }

                        if source not in sources:
                            sources.append(source)

                    except Exception as e:
                        print("Citation error:", e)

        log_entry = {
            "question": question,
            "answer": response.message.content
        }

        with open("logs.txt", "a", encoding="utf-8") as f:
            f.write(str(log_entry) + "\n")

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


if __name__ == "__main__":
    print(app.url_map)
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )