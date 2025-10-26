import gradio as gr
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


sidebar_css = """
body {
  background: linear-gradient(180deg, #121111 0%, #2a1f1c 100%);
  font-family: 'Poppins', sans-serif;
  color: #EDEAE6;
}
.gradio-container {
  background-color: transparent;
}
h1 {
  color: #EADFD7;
  text-align: center;
  font-size: 1.9em;
  letter-spacing: 0.5px;
}
p {
  text-align: center;
  color: #CBBBAF;
  margin-bottom: 1.5em;
  font-size: 1.05em;
}
.sidebar {
  background-color: #1E1C1B;
  border-right: 2px solid #A47963;
  padding: 20px;
  border-radius: 18px;
  min-width: 220px;
}
.tab-button {
  display: block;
  background-color: #2a1f1c;
  color: #EADFD7;
  border: 1px solid #A47963;
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 15px;
  text-align: left;
  font-weight: 600;
  transition: 0.3s;
}
.tab-button:hover {
  background-color: #A47963;
  color: #FFF;
}
input, textarea {
  background-color: #2C2C2C;
  color: #F5F3EF;
  border: 1px solid #A47963;
  border-radius: 10px;
  padding: 10px;
}
button {
  background-color: #A47963;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 10px 20px;
  font-weight: 600;
  transition: 0.3s ease;
}
button:hover {
  background-color: #5A352A;
}
.message.user {
  background-color: #A47963;
  color: white;
  border-radius: 18px 18px 0 18px;
  padding: 10px 14px;
  margin: 5px;
  max-width: 80%;
}
.message.bot {
  background-color: #3A2C28;
  color: #FFF;
  border-radius: 18px 18px 18px 0;
  padding: 10px 14px;
  margin: 5px;
  max-width: 80%;
}
footer { display: none; }
"""

def analyze_career(mbti, interests, skills, summary):
    try:
        prompt = f"""
You are CareerMind AI, a friendly and insightful AI career counselor.
MBTI: {mbti if mbti else "Unknown"}
Interests: {interests}
Skills: {skills}
Summary: {summary}
Analyze their personality, infer MBTI if missing, and return:
1. Personality Overview
2. 3 Recommended Career Paths with justification
3. A 6-week learning roadmap
4. Motivational message
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def chat_with_ai(message, history):
    try:
        messages = [{"role": "system", "content": "You are CareerMind AI, a professional and warm career counselor."}]
        for user, bot in history:
            messages.append({"role": "user", "content": user})
            messages.append({"role": "assistant", "content": bot})
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.8
        )
        bot_message = response.choices[0].message.content
        history.append((message, bot_message))
        return history, ""
    except Exception as e:
        history.append((message, f"⚠️ Error: {str(e)}"))
        return history, ""

with gr.Blocks(css=sidebar_css, title="CareerMind AI – Personal Career Coach") as demo:
    gr.HTML("<h1>🧠 CareerMind AI</h1>")
    gr.HTML("<p>Your personal career coach — powered by AI & personality insights 💼</p>")

    with gr.Row():
        with gr.Column(scale=1, elem_classes=["sidebar"]):
            chat_tab = gr.Button("💬 Chat with CareerMind AI", elem_classes=["tab-button"])
            form_tab = gr.Button("📘 Career Analysis Form", elem_classes=["tab-button"])

        with gr.Column(scale=3):
            chat_section = gr.Group(visible=True)
            with chat_section:
                chatbot = gr.Chatbot(height=420, label="Chatbot")
                msg = gr.Textbox(label="Your message", placeholder="Ask about your personality, skills, or goals...")
                clear = gr.Button("🧹 Clear Chat")
                msg.submit(chat_with_ai, [msg, chatbot], [chatbot, msg])
                clear.click(lambda: None, None, chatbot, queue=False)

            form_section = gr.Group(visible=False)
            with form_section:
                mbti = gr.Textbox(label="Your MBTI Type (leave blank if unknown)")
                interests = gr.Textbox(label="Your Interests")
                skills = gr.Textbox(label="Your Skills (e.g., Excel, communication, coding)")
                summary = gr.Textbox(label="Personality Summary or Quick Answers")
                submit = gr.Button("🔍 Analyze My Career Path")
                output = gr.Textbox(label="CareerMind AI Analysis Result", lines=18)
                submit.click(analyze_career, [mbti, interests, skills, summary], output)

      
        chat_tab.click(lambda: (gr.update(visible=True), gr.update(visible=False)), None, [chat_section, form_section])
        form_tab.click(lambda: (gr.update(visible=False), gr.update(visible=True)), None, [chat_section, form_section])

demo.launch()
