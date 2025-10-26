import os
import gradio as gr
import pandas as pd
from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

csv_files = {
    "career_data": "https://huggingface.co/spaces/morooj234/morooj1/resolve/main/data/career_data.csv",
    "job_roles": "https://huggingface.co/spaces/morooj234/morooj1/resolve/main/data/job_roles.csv",
    "learning_paths": "https://huggingface.co/spaces/morooj234/morooj1/resolve/main/data/learning_paths.csv",
    "motivations": "https://huggingface.co/spaces/morooj234/morooj1/resolve/main/data/motivations.csv"
}

dataframes = []
for name, url in csv_files.items():
    try:
        df = pd.read_csv(url)
        dataframes.append(df)
        print(f"✅ Loaded {name} ({len(df)} rows)")
    except Exception as e:
        print(f"❌ Error loading {name}: {e}")

merged_df = pd.concat(dataframes, ignore_index=True)

def analyze_career(mbti, interests, skills, summary):
    try:
        context = merged_df.sample(3).to_dict(orient="records")
        prompt = f"""
You are CareerMind AI — a friendly and professional AI career counselor.
Analyze this user's profile and provide:
1️⃣ Personality Overview
2️⃣ 3 Recommended Career Paths (with short justification)
3️⃣ A 6-week learning roadmap
4️⃣ A motivational message

MBTI: {mbti or "Unknown"}
Interests: {interests}
Skills: {skills}
Summary: {summary}

Here is some context data to help you:
{context}
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.7,
            max_tokens=700
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def chat_with_ai(message, history):
    try:
        prompt = f"You are CareerMind AI, a smart career coach. The user said: {message}"
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.8,
            max_tokens=400
        )
        answer = response.choices[0].message.content
        history.append((message, answer))
        return history, ""
    except Exception as e:
        history.append(("System", f"⚠️ Error: {str(e)}"))
        return history, ""

custom_css = """
body {background: linear-gradient(180deg,#121111 0%,#2a1f1c 100%); color:#EDEAE6; font-family:'Poppins',sans-serif;}
h1 {color:#EADFD7; text-align:center;}
p {color:#CBBBAF; text-align:center;}
button {background:#A47963; color:white; border-radius:10px; font-weight:600;}
button:hover {background:#5A352A;}
footer{display:none;}
"""

with gr.Blocks(css=custom_css, title="CareerMind AI") as demo:
    gr.HTML("<h1>🧠 CareerMind AI</h1>")
    gr.HTML("<p>Smart career counselor for students and graduates — powered by AI 💼</p>")

    with gr.Tab("💬 Chat with CareerMind AI"):
        chatbot = gr.Chatbot(height=400)
        msg = gr.Textbox(label="Your Message", placeholder="Ask about your career path...")
        clear = gr.Button("🧹 Clear Chat")
        msg.submit(chat_with_ai, [msg, chatbot], [chatbot, msg])
        clear.click(lambda: None, None, chatbot, queue=False)

    with gr.Tab("📊 Career Analysis Form"):
        mbti = gr.Textbox(label="Your MBTI Type (optional)")
        interests = gr.Textbox(label="Your Interests")
        skills = gr.Textbox(label="Your Skills (e.g., Excel, Python, Figma)")
        summary = gr.Textbox(label="Your Goals or Background")
        analyze_btn = gr.Button("🔍 Analyze My Career Path")
        output = gr.Textbox(label="CareerMind AI Result", lines=16)
        analyze_btn.click(analyze_career, [mbti, interests, skills, summary], output)

demo.launch()