
function makeChoice(choice, btnEl) {
    const buttons = document.querySelectorAll('#scenario-options .scenario-btn');
    buttons.forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = '0.5';
        btn.style.transform = 'none';
    });
    btnEl.style.opacity = '1';
    btnEl.classList.add('selected');

    
    btnEl.innerHTML += ' <span style="font-size:0.8rem; color:#666;">Processing...</span>';

    
    fetch('/scenario/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ choice: choice })
    })
    .then(res => res.json())
    .then(data => {
        showScenarioResult(data, 'scenario-result', 'result-emoji', 'result-message', 'reward-xp', 'reward-coins', 'result-explanation');
    })
    .catch(err => {
        console.error('Scenario submit error:', err);
        // Show fallback result for demo even if API fails
        const fallback = getFallbackResult(choice);
        showScenarioResult(fallback, 'scenario-result', 'result-emoji', 'result-message', 'reward-xp', 'reward-coins', 'result-explanation');
    });
}


function getFallbackResult(choice) {
    const fallbacks = {
        save:      { xp: 150, coins: 50, message: '🎯 Smart move! Saving builds your financial safety net.' },
        invest:    { xp: 200, coins: 75, message: '📈 Excellent! Investing grows your wealth over time.' },
        emergency: { xp: 120, coins: 40, message: '🛡️ Wise choice! An emergency fund protects against surprises.' },
        lifestyle: { xp: 30,  coins: 10, message: '⚠️ Spending all on lifestyle leaves no buffer. Balance is key!' }
    };
    return fallbacks[choice] || { xp: 50, coins: 20, message: '👍 Good attempt! Keep learning.' };
}


function showScenarioResult(data, resultId, emojiId, msgId, xpId, coinsId, explainId) {
    const resultEl = document.getElementById(resultId);
    const emojiEl  = document.getElementById(emojiId);
    const msgEl    = document.getElementById(msgId);
    const xpEl     = document.getElementById(xpId);
    const coinsEl  = document.getElementById(coinsId);
    const explainEl= document.getElementById(explainId);

    if (!resultEl) return;


    emojiEl.textContent  = data.xp >= 150 ? '🎉' : data.xp >= 100 ? '👍' : '⚠️';
    msgEl.textContent    = data.xp >= 150 ? 'Great Financial Decision!' : data.xp >= 100 ? 'Good Thinking!' : 'Room to Improve!';
    xpEl.textContent     = `⚡ +${data.xp} XP`;
    coinsEl.textContent  = `🪙 +${data.coins} Coins`;
    explainEl.textContent = data.message;

    resultEl.classList.remove('hidden');
    resultEl.style.animation = 'fadeInUp 0.4s ease';

    setTimeout(() => resultEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 100);

}

function nextScenario() {
    const sc1 = document.getElementById('scenario-main');
    const sc2 = document.getElementById('scenario-2');
    if (sc1 && sc2) {
        sc1.style.animation = 'fadeInUp 0.3s ease reverse';
        setTimeout(() => {
            sc1.classList.add('hidden');
            sc2.classList.remove('hidden');
            sc2.style.animation = 'fadeInUp 0.4s ease';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }, 280);
    }
}

function makeChoice2(choice, btnEl) {
    const buttons = document.querySelectorAll('#scenario-2-options .scenario-btn');
    buttons.forEach(btn => { btn.disabled = true; btn.style.opacity = '0.5'; });
    btnEl.style.opacity = '1';
    btnEl.classList.add('selected');

    const results = {
        credit:    { xp: 20,  coins: 5,  emoji: '⚠️', title: 'Risky Move', msg: 'Credit card interest can spiral quickly. Use credit only when you have a payoff plan!' },
        emergency2:{ xp: 180, coins: 70, emoji: '🎉', title: 'Perfect Response!', msg: 'Using your emergency fund is exactly right. That\'s what it\'s built for!' },
        borrow:    { xp: 80,  coins: 30, emoji: '👍', title: 'Decent Choice', msg: 'Borrowing from family is okay but make a solid repayment plan. Treat it like a real loan.' },
        delay:     { xp: 100, coins: 35, emoji: '✅', title: 'Smart Planning', msg: 'Delaying non-urgent repairs while saving shows financial discipline!' }
    };

    const r = results[choice] || results['delay'];

    const resultEl = document.getElementById('scenario-2-result');
    document.getElementById('result-2-emoji').textContent   = r.emoji;
    document.getElementById('result-2-message').textContent = r.title;
    document.getElementById('reward-2-xp').textContent      = `⚡ +${r.xp} XP`;
    document.getElementById('reward-2-coins').textContent   = `🪙 +${r.coins} Coins`;
    document.getElementById('result-2-explanation').textContent = r.msg;

    resultEl.classList.remove('hidden');
    resultEl.style.animation = 'fadeInUp 0.4s ease';
    setTimeout(() => resultEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 100);
}


function sendMessage() {
    const input  = document.getElementById('chat-input');
    const messages = document.getElementById('chat-messages');
    const typing   = document.getElementById('typing');

    const text = input.value.trim();
    if (!text) return;

    appendMessage(messages, text, 'user');
    input.value = '';

    if (typing) typing.classList.remove('hidden');

    
    scrollChat(messages);

    fetch('/mentor/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
    })
    .then(res => res.json())
    .then(data => {
        if (typing) typing.classList.add('hidden');
        appendMessage(messages, data.reply, 'bot');
        scrollChat(messages);
    })
    .catch(err => {
        console.error('Mentor chat error:', err);
        if (typing) typing.classList.add('hidden');
        appendMessage(messages, "Sorry, I'm having trouble connecting right now. Please try again! 🤖", 'bot');
        scrollChat(messages);
    });
}

function appendMessage(container, text, role) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message message-${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'bot' ? '🤖' : '👤';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = `<p>${escapeHtml(text)}</p>`;

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    msgDiv.style.animation = 'fadeInUp 0.3s ease';

    container.appendChild(msgDiv);
}

function scrollChat(container) {
    setTimeout(() => {
        container.scrollTop = container.scrollHeight;
    }, 50);
}

function handleEnter(event) {
    if (event.key === 'Enter') sendMessage();
}

function escapeHtml(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}


function startCountdown() {
    const timerEl = document.querySelector('.challenge-reward span:last-child');
    if (!timerEl) return;

    
    const now = new Date();
    const midnight = new Date();
    midnight.setHours(24, 0, 0, 0);
    let remaining = Math.floor((midnight - now) / 1000);

    function updateTimer() {
        if (remaining <= 0) {
            timerEl.textContent = '⏰ Resetting...';
            return;
        }
        const h = String(Math.floor(remaining / 3600)).padStart(2, '0');
        const m = String(Math.floor((remaining % 3600) / 60)).padStart(2, '0');
        const s = String(remaining % 60).padStart(2, '0');
        timerEl.textContent = `⏰ ${h}:${m}:${s} left`;
        remaining--;
    }

    updateTimer();
    setInterval(updateTimer, 1000);
}




document.addEventListener('DOMContentLoaded', function () {
    
    const xpFill = document.querySelector('.xp-fill');
    if (xpFill) {
        const target = xpFill.style.width;
        xpFill.style.width = '0%';
        setTimeout(() => { xpFill.style.width = target; }, 200);
    }

    
    const chartBars = document.querySelectorAll('.chart-bar-fill');
    chartBars.forEach(bar => {
        const target = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => { bar.style.width = target; }, 400);
    });

    const bigFill = document.querySelector('.big-progress-fill');
    if (bigFill) {
        const target = bigFill.style.width;
        bigFill.style.width = '0%';
        setTimeout(() => { bigFill.style.width = target; }, 300);
    }

    
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) scrollChat(chatMessages);

    console.log('🚀 FinLiteracy loaded successfully!');
});
