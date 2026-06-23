from flask import Flask, request, jsonify, send_file
from pinecone import Pinecone
from dotenv import load_dotenv
from flask_cors import CORS
import os

load_dotenv()

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

        for msg in history:
            pinecone_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

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
                        file_name = ref.file.name
                        pages = list(ref.pages)

                        source = {
                            "title": file_name,
                            "pages": pages
                        }

                        if source not in sources:
                            sources.append(source)

                    except Exception:
                        pass

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