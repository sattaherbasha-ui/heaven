import sqlite3
import random
import datetime
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DB_FILE = 'comprehensive_wellness_v5.db'

# --- 1. Database & Massive Knowledge Seeding ---
# (Logic remains identical to preserve your data structure)
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS user_profile (id INTEGER PRIMARY KEY, name TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS chat_history (id INTEGER PRIMARY KEY, sender TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    cursor.execute('CREATE TABLE IF NOT EXISTS knowledge_base (keywords TEXT, response TEXT, source TEXT)')
    
    cursor.execute('SELECT count(*) FROM knowledge_base')
    if cursor.fetchone()[0] == 0:
        data = [
            ('anxiety', 'Try "Box Breathing": Inhale for 4 seconds, Hold for 4, Exhale for 4, Hold for 4. It hacks your vagus nerve to calm you down.', 'Navy SEAL Technique'),
            ('anxiety', 'The "3-3-3 Rule": Name 3 things you see, 3 sounds you hear, and move 3 parts of your body. It pulls you out of your head.', 'Trauma Center'),
            ('stress', 'Academic stress is real. Remember: Your grades describe your performance, not your worth as a human being.', 'Campus Psychology'),
            ('panic', 'Hold an ice cube in your hand. The intense sensation forces your brain to focus on the cold rather than the panic spiral.', 'Therapy Aid'),
            ('depression', 'Depression lies to you. It says "nothing matters." Try "Behavioral Activation": Do one small task (like washing a cup) even if you don\'t feel like it.', 'CBT Principles'),
            ('lonely', 'Isolation feeds depression. Try the "15-minute rule": Go to a public place (library, cafe) for just 15 minutes. You don\'t have to talk to anyone, just be near people.', 'Social Health'),
            ('sad', 'It is okay to have a "rot day" where you do nothing, but set a time limit. Tomorrow, we try again.', 'Self-Compassion'),
            ('eating', 'Your body is the instrument of your life, not just an ornament. If you are obsessing over food, please reach out to NEDA or a counselor.', 'NEDA'),
            ('body image', 'Social media is a highlight reel, not reality. Unfollow accounts that make you feel bad about your body.', 'Digital Wellness'),
            ('starving', 'Your brain needs glucose to study. Starving yourself actually lowers your grades by brain fog. Please nourish yourself.', 'Nutritional Science'),
            ('addiction', 'Cravings usually last only 20 minutes. Can you "surf the urge"? Distract yourself for 20 minutes and the intensity will likely drop.', 'Recovery Logic'),
            ('drinking', 'Using substances to cope with stress creates a feedback loop. The relief is temporary, but the anxiety comes back double. Consider a "Sober October" challenge.', 'Health Services'),
            ('ptsd', 'If you are having a flashback: Stomp your feet on the ground. Say "I am [Name], I am in [Room], and the year is [Year]." Anchor yourself in the present.', 'Grounding Tech'),
            ('trauma', 'Trauma is not just in your head; it lives in the body. Yoga or progressive muscle relaxation can help release that stored tension.', 'The Body Keeps the Score'),
            ('voices', 'If you are hearing things others don\'t, it is vital to check in with a doctor. It’s a medical condition like asthma, and medication can help quiet the noise.', 'Medical Guide'),
            ('delusion', 'If reality feels slippery right now, stick to a strict routine. Wake up, eat, and sleep at the same time. Routine is a safety anchor.', 'Psychiatry'),
            ('grades', 'One bad grade is a detour, not a dead end. Have you visited the professor\'s office hours to discuss extra credit?', 'Academic Advisor'),
            ('money', 'Financial worry is exhausting. Have you checked the Student Union for food pantries or emergency grants?', 'Financial Aid Office'),
            ('focus', 'Poor focus often comes from "Multitasking." The brain cannot multitask. Try the Pomodoro timer: 25 mins work, 5 mins phone.', 'Study Hacks'),
            ('bpd', 'Emotion regulation tip: "Opposite Action." If you feel like isolating (fear), go to a public place. If you feel like yelling (anger), speak softly.', 'DBT Skills'),
            ('mood swings', 'Track your moods. Is there a trigger? Hunger? Sleep? Often "HALT" (Hungry, Angry, Lonely, Tired) causes the swing.', 'Self-Awareness'),
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
    # Safety Check
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

# --- Frontend with TECH DOT PATTERN ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compassionate AI</title>
    <style>
        /* 1. MAIN BODY BACKGROUND (Outer 3D Space) */
        body {
            font-family: 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background-image: url('https://images.unsplash.com/photo-1664575198308-3959904fa430?q=80&w=2940&auto=format&fit=crop');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-color: #1a1a2e; /* Fallback color */
            display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0;
        }

        /* 2. CHAT CONTAINER GLASS STRUCTURE */
        #chat-container {
            width: 450px; height: 720px;
            /* Frosted Glass Effect */
            background: rgba(255, 255, 255, 0.15); /* Very transparent base */
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 25px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.5); /* Deep shadow for 3D lift */
            display: flex; flex-direction: column; overflow: hidden;
        }

        /* 3. HEADER */
        #header {
            background: rgba(21, 101, 192, 0.9); /* Semi-transparent blue */
            color: white; padding: 20px; text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        #header h2 { margin: 0; font-size: 1.4em; font-weight: 600; letter-spacing: 0.5px; }
        #header small { opacity: 0.8; font-size: 0.85em; display: block; margin-top: 5px;}

        /* 4. CHAT AREA BACKGROUND (The new styling request) */
        #chat-box {
            flex: 1; padding: 25px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px;
            
            /* -- NEW PATTERN STYLING -- */
            /* A subtle radial dot pattern to give it a 'tech' feel */
            background-color: rgba(245, 247, 250, 0.7); /* Light overlay */
            background-image: radial-gradient(#2980b9 0.5px, transparent 0.5px), radial-gradient(#2980b9 0.5px, transparent 0.5px);
            background-size: 20px 20px;
            background-position: 0 0, 10px 10px;
            
            scrollbar-width: thin; scrollbar-color: rgba(41, 128, 185, 0.3) transparent;
        }

        /* 5. MESSAGES */
        .message {
            padding: 15px 20px; border-radius: 20px; max-width: 80%; font-size: 15px; line-height: 1.5;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            position: relative;
            animation: popIn 0.3s ease-out;
        }
        @keyframes popIn { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }

        /* User Bubble: Deep Gradient Blue */
        .user { 
            align-self: flex-end; 
            background: linear-gradient(135deg, #1565c0, #0d47a1); 
            color: white; 
            border-bottom-right-radius: 4px; 
        }

        /* Bot Bubble: Clean White */
        .bot { 
            align-self: flex-start; 
            background: white; 
            color: #333; 
            border-bottom-left-radius: 4px; 
            border: 1px solid rgba(0,0,0,0.05);
        }
        .bot small { color: #666; font-size: 0.75em; display: block; margin-top: 8px; border-top: 1px solid #eee; padding-top: 5px; }
        .bot b[style='color:red'] { color: #d32f2f !important; }

        /* 6. INPUT AREA */
        #input-area {
            padding: 20px; 
            background: rgba(255, 255, 255, 0.8); /* Frosted bottom bar */
            backdrop-filter: blur(10px);
            border-top: 1px solid rgba(255,255,255,0.5); 
            display: flex; gap: 10px;
        }
        input {
            flex: 1; padding: 12px 20px; border: 1px solid #ddd; background: white; border-radius: 25px; outline: none;
            transition: 0.3s;
        }
        input:focus { border-color: #1565c0; box-shadow: 0 0 0 3px rgba(21, 101, 192, 0.1); }
        
        button {
            background: #1565c0; color: white; border: none; padding: 12px 25px; border-radius: 25px; cursor: pointer; font-weight: bold;
            transition: 0.2s; box-shadow: 0 4px 10px rgba(21, 101, 192, 0.3);
        }
        button:hover { background: #0d47a1; transform: translateY(-2px); }
    </style>
</head>
<body>
<div id="chat-container">
    <div id="header">
        <h2>Wellness AI</h2>
        <small>Always here to listen</small>
    </div>
    <div id="chat-box"></div>
    <div id="input-area">
        <input type="text" id="user-input" placeholder="Type a message..." onkeypress="handleKeyPress(event)">
        <button onclick="sendMessage()">Send</button>
    </div>
</div>
<script>
    window.onload = async function() {
        const chatBox = document.getElementById('chat-box');
        chatBox.innerHTML = '<div class="message bot" style="background:transparent; box-shadow:none;"><i>Initializing...</i></div>';
        try {
            const res = await fetch('/start');
            const data = await res.json();
            chatBox.innerHTML = ''; 
            const name = data.name || "Friend";
            chatBox.innerHTML += `<div class="message bot">Hello, ${name}. I am your safe space.<br><br>Feel free to talk about anxiety, pressure, grades, or whatever is on your mind.</div>`;
            data.history.forEach(msg => {
                chatBox.innerHTML += `<div class="message ${msg[0]}">${msg[1]}</div>`;
            });
        } catch(e) {
             chatBox.innerHTML = '<div class="message bot">Connection Offline.</div>';
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
        chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });

        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        chatBox.innerHTML += `<div class="message bot">${data.response}</div>`;
        chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
    }
</script>
</body>
</html>
"""

# --- Backend Logic (Unchanged) ---
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

    if "my name is" in user_msg:
        name = user_msg.split("is")[-1].strip().capitalize()
        update_name(name)
        reply = f"Nice to meet you, {name}."
    elif get_smart_response(user_msg):
        reply = get_smart_response(user_msg)
    else:
        name = get_name() or "friend"
        reply = f"I'm listening, {name}. Tell me more about how you are feeling."

    save_history('bot', reply)
    return jsonify({"response": reply})

if __name__ == '__main__':
    app.run(port=5000, debug=True)