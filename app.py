from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import db, User, Progress
import os

app = Flask(__name__)
app.secret_key = 'hackathon-dev-secret-key'  



basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'finance_app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='demo').first():
        demo_user = User(
            username='demo',
            email='demo@finliteracy.app',
            password='demo123',  
            xp=1240,
            coins=850,
            level=3,
            streak_days=5
        )
        db.session.add(demo_user)
        db.session.flush()
        demo_progress = Progress(
            user_id=demo_user.id,
            scenarios_completed=7,
            financial_score=72.5,
            budgeting_level=2,
            saving_level=1,
            debt_level=0,
            investing_level=0,
            independence_level=0,
            badges_earned='first_save,budget_master,streak_3'
        )
        db.session.add(demo_progress)
        db.session.commit()
        print("✅ Demo user seeded: username=demo, password=demo123")


def get_current_user():
    """Fetch logged-in user from session."""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None



@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route.
    TODO: Add JWT-based auth for production.
    TODO: Add rate limiting to prevent brute force.
    """
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password. Try demo / demo123'

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    """
    Main dashboard - shows XP, coins, level, daily challenge.
    TODO: Fetch real daily challenges from a challenges table.
    TODO: Add streak tracking logic.
    """
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    progress = user.progress or Progress(user_id=user.id, scenarios_completed=0, financial_score=50.0)

    xp_for_next = user.level * 500
    xp_percent = min(int((user.xp % xp_for_next) / xp_for_next * 100), 100)

    return render_template('dashboard.html',
        user=user,
        progress=progress,
        xp_percent=xp_percent,
        xp_for_next=xp_for_next
    )


@app.route('/scenario')
def scenario():
    """
    Financial scenario simulation page.
    TODO: Load scenarios dynamically from DB.
    TODO: Track which scenarios each user has already completed.
    """
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    return render_template('scenario.html', user=user)


@app.route('/scenario/submit', methods=['POST'])
def scenario_submit():
    """
    Handle scenario choice submission.
    Awards XP and coins based on the choice made.
    TODO: Persist results to DB and update user progress.
    TODO: Add more complex scoring based on scenario difficulty.
    """
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()
    choice = data.get('choice')

    rewards = {
        'save': {'xp': 150, 'coins': 50, 'score_delta': 10,
                 'message': '🎯 Smart move! Saving builds your financial safety net.'},
        'invest': {'xp': 200, 'coins': 75, 'score_delta': 15,
                   'message': '📈 Excellent! Investing grows your wealth over time.'},
        'emergency': {'xp': 120, 'coins': 40, 'score_delta': 8,
                      'message': '🛡️ Wise choice! An emergency fund protects against surprises.'},
        'lifestyle': {'xp': 30, 'coins': 10, 'score_delta': -5,
                      'message': '⚠️ Spending all on lifestyle leaves no buffer. Balance is key!'}
    }

    reward = rewards.get(choice, {'xp': 50, 'coins': 20, 'score_delta': 0, 'message': 'Good attempt!'})

    
    return jsonify({
        'xp': reward['xp'],
        'coins': reward['coins'],
        'message': reward['message'],
        'new_xp': user.xp + reward['xp'],
        'new_coins': user.coins + reward['coins']
    })


@app.route('/learning')
def learning():
    """
    Learning path page.
    TODO: Load user's actual progress per topic.
    TODO: Add quiz/assessment at end of each level.
    """
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    progress = user.progress or Progress(user_id=user.id)
    return render_template('learning_path.html', user=user, progress=progress)


@app.route('/mentor')
def mentor():
    """
    AI Mentor chat page.
    TODO: Integrate OpenAI / Gemini API for real financial Q&A.
    TODO: Add conversation history persistence.
    TODO: Add personalized advice based on user's financial score.
    """
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    return render_template('ai_mentor.html', user=user)


@app.route('/mentor/chat', methods=['POST'])
def mentor_chat():
    """
    AI Mentor chat endpoint.
    Currently returns dummy responses.
    TODO: Replace dummy_response with actual AI API call:
        import openai
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content
    """
    data = request.get_json()
    user_message = data.get('message', '').lower()

    dummy_responses = {
        'budget': "A great budgeting rule is the 50/30/20 rule: 50% needs, 30% wants, 20% savings. Start tracking your expenses this week! 📊",
        'save': "Try automating your savings! Set up an auto-transfer on salary day so you save before you spend. Even ₹500/month adds up! 💰",
        'invest': "For beginners, index mutual funds are a great start. They're diversified and low-cost. SIPs let you invest as little as ₹100/month! 📈",
        'debt': "Tackle high-interest debt first (avalanche method). Pay minimums on all, then attack the highest interest rate debt aggressively. 🎯",
        'emergency': "Aim for 3-6 months of expenses in an emergency fund. Keep it in a liquid savings account, not investments. 🛡️",
        'credit': "Pay your full credit card balance every month to avoid interest. Your credit score improves with on-time payments! 💳",
    }

    reply = "That's a great financial question! As your AI mentor, I'd suggest starting with the basics: track your income and expenses for one month to understand your spending patterns. Would you like tips on budgeting, saving, or investing? 🤖💡"

    for keyword, response in dummy_responses.items():
        if keyword in user_message:
            reply = response
            break


    return jsonify({'reply': reply})


@app.route('/api/user/stats')
def user_stats():
    """API endpoint for user stats - useful for future mobile app integration."""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify(user.to_dict())


if __name__ == '__main__':
    print("🚀 FinLiteracy App running at http://localhost:5000")
    print("   Demo login: username=demo  password=demo123")
    app.run(debug=True, port=5000)
