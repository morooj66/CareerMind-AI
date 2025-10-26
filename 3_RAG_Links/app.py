import gradio as gr
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

custom_css = """
body { background-color: #1b1918; color: #f3eeea; font-family: 'Poppins', sans-serif; }
h1 { text-align:center; color: #EADFD7; font-size: 1.9em; margin-bottom: 0.5em; }
textarea, input { background-color: #2b2522; color: #f8f6f4; border: 1px solid #A47963; border-radius: 10px; padding: 10px; }
button { background-color: #A47963; color: white; border: none; border-radius: 10px; padding: 10px 20px; font-weight: bold; transition: 0.3s; }
button:hover { background-color: #5A352A; }
.output-card { background-color: #2e2622; border-radius: 12px; padding: 15px; margin-top: 10px; }
a { color: #E4BFAF; text-decoration: none; font-weight: 600; }
a:hover { text-decoration: underline; color: #f1d2c4; }
"""

def web_rag_query(question):
    try:
        course_links = [
            "https://www.coursera.org/courses",
            "https://www.edx.org/",
            "https://www.udemy.com/",
            "https://www.futurelearn.com/",
            "https://www.linkedin.com/learning/"
        ]

        context = ""
        for link in course_links:
            try:
                html = requests.get(link, timeout=5)
                soup = BeautifulSoup(html.text, "html.parser")
                text = soup.get_text()
                context += f"\n\n[From {link}]:\n{text[:1200]}"
            except Exception:
                context += f"\n\n⚠️ Could not retrieve content from {link}"

        prompt = f"""
You are CourseFinder AI, a professional AI advisor that helps users find relevant online courses and certificates.
Context:
{context}
User Question:
{question}
Generate a structured response with:
- 2 to 3 course recommendations
- A short summary (1–2 sentences)
- Direct course link under each
Make it formatted and clear.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        answer = response.choices[0].message.content
        return "<div class='output-card'><h3>🎓 Course Recommendations</h3><p>" + answer.replace("\n", "<br>") + "</p></div>"

    except Exception as e:
        return f"<div class='output-card'>⚠️ Error: {str(e)}</div>"

with gr.Blocks(css=custom_css, title="CourseFinder AI") as demo:
    gr.HTML("<h1>🎓 CourseFinder AI</h1>")
    gr.Markdown("Ask about your goal and get tailored course recommendations from trusted platforms 🌐")

    question = gr.Textbox(
        label="Your Question",
        placeholder="Example: What's the best course for learning Python for data analysis?",
        lines=2
    )
    submit = gr.Button("🔍 Find Courses")
    output = gr.HTML(label="AI Recommendations")

    submit.click(web_rag_query, question, output)

demo.launch()
