import sqlite3
import random
import datetime
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DB_FILE = 'comprehensive_wellness_v3.db'

# --- 1. Database & Massive Knowledge Seeding ---
# (This part is unchanged from the previous version)
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS user_profile (id INTEGER PRIMARY KEY, name TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS chat_history (id INTEGER PRIMARY KEY, sender TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    cursor.execute('CREATE TABLE IF NOT EXISTS knowledge_base (keywords TEXT, response TEXT, source TEXT)')
    
    cursor.execute('SELECT count(*) FROM knowledge_base')
    if cursor.fetchone()[0] == 0:
        data = [
            # --- ANXIETY & STRESS ---
            ('anxiety', 'Try "Box Breathing": Inhale for 4 seconds, Hold for 4, Exhale for 4, Hold for 4. It hacks your vagus nerve to calm you down.', 'Navy SEAL Technique'),
            ('anxiety', 'The "3-3-3 Rule": Name 3 things you see, 3 sounds you hear, and move 3 parts of your body. It pulls you out of your head.', 'Trauma Center'),
            ('stress', 'Academic stress is real. Remember: Your grades describe your performance, not your worth as a human being.', 'Campus Psychology'),
            ('panic', 'Hold an ice cube in your hand. The intense sensation forces your brain to focus on the cold rather than the panic spiral.', 'Therapy Aid'),
            # --- DEPRESSION & ISOLATION ---
            ('depression', 'Depression lies to you. It says "nothing matters." Try "Behavioral Activation": Do one small task (like washing a cup) even if you don\'t feel like it.', 'CBT Principles'),
            ('lonely', 'Isolation feeds depression. Try the "15-minute rule": Go to a public place (library, cafe) for just 15 minutes. You don\'t have to talk to anyone, just be near people.', 'Social Health'),
            ('sad', 'It is okay to have a "rot day" where you do nothing, but set a time limit. Tomorrow, we try again.', 'Self-Compassion'),
            # --- EATING DISORDERS ---
            ('eating', 'Your body is the instrument of your life, not just an ornament. If you are obsessing over food, please reach out to NEDA or a counselor.', 'NEDA'),
            ('body image', 'Social media is a highlight reel, not reality. Unfollow accounts that make you feel bad about your body.', 'Digital Wellness'),
            ('starving', 'Your brain needs glucose to study. Starving yourself actually lowers your grades by brain fog. Please nourish yourself.', 'Nutritional Science'),
            # --- ADDICTION ---
            ('addiction', 'Cravings usually last only 20 minutes. Can you "surf the urge"? Distract yourself for 20 minutes and the intensity will likely drop.', 'Recovery Logic'),
            ('drinking', 'Using substances to cope with stress creates a feedback loop. The relief is temporary, but the anxiety comes back double. Consider a "Sober October" challenge.', 'Health Services'),
            # --- PTSD & TRAUMA ---
            ('ptsd', 'If you are having a flashback: Stomp your feet on the ground. Say "I am [Name], I am in [Room], and the year is [Year]." Anchor yourself in the present.', 'Grounding Tech'),
            ('trauma', 'Trauma is not just in your head; it lives in the body. Yoga or progressive muscle relaxation can help release that stored tension.', 'The Body Keeps the Score'),
            # --- PSYCHOTIC DISORDERS ---
            ('voices', 'If you are hearing things others don\'t, it is vital to check in with a doctor. It’s a medical condition like asthma, and medication can help quiet the noise.', 'Medical Guide'),
            ('delusion', 'If reality feels slippery right now, stick to a strict routine. Wake up, eat, and sleep at the same time. Routine is a safety anchor.', 'Psychiatry'),
            # --- ACADEMIC & FINANCIAL PRESSURE ---
            ('grades', 'One bad grade is a detour, not a dead end. Have you visited the professor\'s office hours to discuss extra credit?', 'Academic Advisor'),
            ('money', 'Financial worry is exhausting. Have you checked the Student Union for food pantries or emergency grants?', 'Financial Aid Office'),
            ('focus', 'Poor focus often comes from "Multitasking." The brain cannot multitask. Try the Pomodoro timer: 25 mins work, 5 mins phone.', 'Study Hacks'),
            # --- PERSONALITY DISORDERS ---
            ('bpd', 'Emotion regulation tip: "Opposite Action." If you feel like isolating (fear), go to a public place. If you feel like yelling (anger), speak softly.', 'DBT Skills'),
            ('mood swings', 'Track your moods. Is there a trigger? Hunger? Sleep? Often "HALT" (Hungry, Angry, Lonely, Tired) causes the swing.', 'Self-Awareness'),
            # --- SUICIDE / CRISIS (Generic Fallbacks) ---
            ('suicide', 'I hear that you are in deep pain. Please, stay with us. Call 988 (USA) or your local emergency number immediately. You are valuable.', 'CRISIS ALERT'),
            ('kill', 'Please pause. Your pain is valid, but it is temporary. Suicide is permanent. Text "HOME" to 741741 to chat with a human right now.', 'CRISIS ALERT')
        ]
        cursor.executemany('INSERT INTO knowledge_base (keywords, response, source) VALUES (?, ?, ?)', data)
        conn.commit()
    conn.close()

# --- Database Helpers ---
def save_history(sender, message):
    conn = sqlite3.connect(DB_FILE)
    conn.execute('INSERT INTO chat_history (sender, message) VALUES (?, ?)', (sender, message))
    conn.commit()
    conn.close()

def get_history(limit=10):
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute('SELECT sender, message FROM chat_history ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return rows[::-1]

def update_name(name):
    conn = sqlite3.connect(DB_FILE)
    conn.execute('DELETE FROM user_profile') 
    conn.execute('INSERT INTO user_profile (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()

def get_name():
    conn = sqlite3.connect(DB_FILE)
    res = conn.execute('SELECT name FROM user_profile LIMIT 1').fetchone()
    conn.close()
    return res[0] if res else None

def get_smart_response(text):
    conn = sqlite3.connect(DB_FILE)
    for crisis_word in ['suicide', 'kill', 'die', 'end it']:
        if crisis_word in text:
            row = conn.execute("SELECT response, source FROM knowledge_base WHERE keywords = ?", ('suicide',)).fetchone()
            conn.close()
            return f"<b style='color:red'>{row[0]}</b> <br><br>Source: {row[1]}"

    cursor = conn.execute("SELECT response, source FROM knowledge_base WHERE ? LIKE '%' || keywords || '%'", (text,))
    rows = cursor.fetchall()
    conn.close()
    
    if rows:
        selected = random.choice(rows)
        return f"{selected[0]} <br><br><small>Source: {selected[1]}</small>"
    return None

init_db()

# --- Frontend with 3D Glassmorphism Styling ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compassionate AI</title>
    <style>
        /* 3D Background and Body Setup */
        body {
            font-family: 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            /* Using a high-quality abstract 3D image from Unsplash representing brain/network connection */
            background-image: url('https://images.unsplash.com/photo-1620121692029-d088224ddc74?q=80&w=2832&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            /* Darkens the background slightly so the chat pops */
            background-blend-mode: overlay;
            background-color: rgba(0, 0, 0, 0.3);
            display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0;
        }

        /* Glassmorphism Chat Container */
        #chat-container {
            width: 450px; height: 720px;
            /* Semi-transparent white background */
            background: rgba(255, 255, 255, 0.75);
            /* The blur effect for the frosted glass look */
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 25px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            display: flex; flex-direction: column; overflow: hidden;
        }

        #header {
            background: linear-gradient(135deg, #1565c0, #42a5f5);
            color: white; padding: 25px; text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        #header h2 { margin: 0; font-size: 1.5em; font-weight: 600; }
        #header small { opacity: 0.85; font-size: 0.9em; }

        #chat-box {
            flex: 1; padding: 25px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px;
            /* Transparent so the glass effect shows through */
            background: transparent;
            scrollbar-width: thin; scrollbar-color: rgba(0,0,0,0.2) transparent;
        }
        /* Cleaner scrollbar for Chrome/Safari */
        #chat-box::-webkit-scrollbar { width: 8px; }
        #chat-box::-webkit-scrollbar-track { background: transparent; }
        #chat-box::-webkit-scrollbar-thumb { background-color: rgba(0,0,0,0.2); border-radius: 4px; }

        .message {
            padding: 15px 20px; border-radius: 20px; max-width: 85%; font-size: 15px; line-height: 1.5;
            box-shadow: 0 3px 10px rgba(0,0,0,0.05);
            animation: fadeIn 0.3s ease-in-out;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        .user { align-self: flex-end; background: #1565c0; color: white; border-bottom-right-radius: 5px; }
        .bot { align-self: flex-start; background: rgba(255,255,255,0.9); color: #333; border-bottom-left-radius: 5px; }
        .bot small { color: #666; font-style: italic; }

        #input-area {
            padding: 20px; background: rgba(255,255,255,0.5); border-top: 1px solid rgba(255,255,255,0.5); display: flex; gap: 10px;
        }
        input {
            flex: 1; padding: 15px; border: none; background: rgba(255,255,255,0.8); border-radius: 30px; outline: none;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.05); font-size: 14px;
        }
        button {
            background: linear-gradient(135deg, #1565c0, #42a5f5);
            color: white; border: none; padding: 12px 25px; border-radius: 30px; cursor: pointer; font-weight: bold;
            transition: transform 0.1s; box-shadow: 0 4px 15px rgba(21, 101, 192, 0.3);
        }
        button:hover { transform: scale(1.05); }
        button:active { transform: scale(0.95); }
    </style>
</head>
<body>
<div id="chat-container">
    <div id="header">
        <h2>Wellness Companion</h2>
        <small>Your Safe Space</small>
    </div>
    <div id="chat-box"></div>
    <div id="input-area">
        <input type="text" id="user-input" placeholder="Share your thoughts here..." onkeypress="handleKeyPress(event)">
        <button onclick="sendMessage()">Send</button>
    </div>
</div>
<script>
    window.onload = async function() {
        const chatBox = document.getElementById('chat-box');
        // Add a temporary loading message
        chatBox.innerHTML = '<div class="message bot">Connecting to secure memory...</div>';
        try {
            const res = await fetch('/start');
            const data = await res.json();
            chatBox.innerHTML = ''; // Clear loading
            const name = data.name || "Friend";
            chatBox.innerHTML += `<div class="message bot">Hello, ${name}. I'm here for you.<br>We can talk about anxiety, PTSD, grades, or anything heavy on your mind.</div>`;
            data.history.forEach(msg => {
                chatBox.innerHTML += `<div class="message ${msg[0]}">${msg[1]}</div>`;
            });
        } catch(e) {
             chatBox.innerHTML = '<div class="message bot">I am having trouble connecting right now.</div>';
        }
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    function handleKeyPress(event) { if (event.key === 'Enter') sendMessage(); }

    async function sendMessage() {
        const input = document.getElementById('user-input');
        const chatBox = document.getElementById('chat-box');
        const text = input.value.trim();
        if (!text) return;

        chatBox.innerHTML += `<div class="message user">${text}</div>`;
        input.value = '';
        chatBox.scrollTop = chatBox.scrollHeight;

        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        chatBox.innerHTML += `<div class="message bot">${data.response}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    }
</script>
</body>
</html>
"""

# --- Backend Logic ---
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/start', methods=['GET'])
def start():
    return jsonify({"name": get_name(), "history": get_history()})

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get("message", "").lower()
    save_history('user', request.json.get("message"))

    # 1. Learning Name
    if "my name is" in user_msg:
        name = user_msg.split("is")[-1].strip().capitalize()
        update_name(name)
        reply = f"Thank you, {name}. I will keep that in mind."
    
    # 2. Database Knowledge Check
    elif get_smart_response(user_msg):
        reply = get_smart_response(user_msg)
    
    # 3. Conversational Fallback
    else:
        name = get_name() or "friend"
        reply = f"I'm listening, {name}. I can help with things like 'panic' attacks, 'body image', 'addiction', or 'focus' issues. Take your time."

    save_history('bot', reply)
    return jsonify({"response": reply})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
