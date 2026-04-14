/**
 * Chatbot frontend – Gamers GADGETS
 * Sends user messages to /api/chatbot/message via AJAX
 * and renders rich responses (text, product cards, link chips).
 */
(function () {
    'use strict';

    /* ── Quick suggestion chips ── */
    const SUGGESTIONS = [
        { label: '🎹 Show keyboards',   text: 'show me keyboards' },
        { label: '🖥️ Best monitors',    text: 'best monitors' },
        { label: '🎮 Gamepads',         text: 'show me gamepads' },
        { label: '🖱️ Gaming mice',      text: 'show me gaming mouse' },
        { label: '🚚 Delivery info',    text: 'delivery information' },
        { label: '🛡️ Warranty',         text: 'warranty policy' },
        { label: '💳 Payment methods',  text: 'what payment methods do you accept' },
        { label: '📞 Contact us',       text: 'contact information' },
    ];

    /* ── DOM refs ── */
    const toggle  = document.getElementById('chatbot-toggle');
    const panel   = document.getElementById('chatbot-panel');
    const closeBtn= document.getElementById('chatbot-close');
    const messages= document.getElementById('chatbot-messages');
    const input   = document.getElementById('chatbot-input');
    const sendBtn = document.getElementById('chatbot-send');
    const sugsBox = document.getElementById('chatbot-suggestions');

    if (!toggle || !panel) return;  // widget not injected

    let isOpen = false;

    /* ── Open / Close ── */
    function openPanel() {
        isOpen = true;
        panel.classList.add('open');
        input.focus();
        if (messages.children.length === 0) {
            botGreet();
        }
    }

    function closePanel() {
        isOpen = false;
        panel.classList.remove('open');
    }

    toggle.addEventListener('click', () => isOpen ? closePanel() : openPanel());
    closeBtn.addEventListener('click', closePanel);

    /* ── Suggestion chips ── */
    SUGGESTIONS.forEach(s => {
        const btn = document.createElement('button');
        btn.className = 'suggestion-chip';
        btn.textContent = s.label;
        btn.addEventListener('click', () => {
            input.value = s.text;
            sendMessage();
        });
        sugsBox.appendChild(btn);
    });

    /* ── Send on Enter ── */
    input.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    sendBtn.addEventListener('click', sendMessage);

    /* ── Greeting (local, no AJAX) ── */
    function botGreet() {
        appendBotBubble(
            '👋 Hi! I\'m your **Gamers GADGETS** assistant.\n\n' +
            'I can help you:\n• Find products (keyboards, mice, monitors…)\n' +
            '• Answer delivery, refund & warranty questions\n' +
            '• Guide you around the store\n\nWhat can I help you with?',
            [], []
        );
    }

    /* ── Main send function ── */
    function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        appendUserBubble(text);
        input.value = '';
        const typing = appendTyping();

        fetch('/api/chatbot/message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text }),
        })
        .then(r => r.json())
        .then(data => {
            typing.remove();
            appendBotBubble(data.text || '🤔 No response.', data.links || [], data.products || []);
        })
        .catch(() => {
            typing.remove();
            appendBotBubble('⚠️ Sorry, I couldn\'t reach the server. Please try again.', [], []);
        });
    }

    /* ── Render helpers ── */

    function appendUserBubble(text) {
        const wrap = document.createElement('div');
        wrap.className = 'chat-msg user';
        wrap.innerHTML = `<div class="chat-bubble">${escHtml(text)}</div>`;
        messages.appendChild(wrap);
        scrollBottom();
    }

    function appendBotBubble(mdText, links, products) {
        const wrap = document.createElement('div');
        wrap.className = 'chat-msg bot';

        const avatar = document.createElement('div');
        avatar.className = 'bot-mini-avatar';
        avatar.textContent = '🤖';

        const right = document.createElement('div');
        right.style.maxWidth = '88%';

        // Main text bubble
        const bubble = document.createElement('div');
        bubble.className = 'chat-bubble';
        bubble.innerHTML = renderMarkdown(mdText);
        right.appendChild(bubble);

        // Product cards
        if (products && products.length) {
            const pc = document.createElement('div');
            pc.className = 'chat-products';
            products.forEach(p => {
                const card = document.createElement('a');
                card.className = 'chat-product-card';
                card.href = p.url;
                card.target = '_blank';
                card.innerHTML = `
                    <img class="chat-product-img" src="${escHtml(p.image) || ''}"
                         onerror="this.src='https://via.placeholder.com/46?text=img'"
                         alt="${escHtml(p.name)}">
                    <div class="chat-product-info">
                        <div class="chat-product-name">${escHtml(p.name)}</div>
                        <div class="chat-product-price">${escHtml(p.price)}</div>
                    </div>
                    <span style="font-size:.8rem;color:#999;">›</span>
                `;
                pc.appendChild(card);
            });
            right.appendChild(pc);
        }

        // Link chips
        if (links && links.length) {
            const lc = document.createElement('div');
            lc.className = 'chat-links';
            links.forEach(l => {
                const a = document.createElement('a');
                a.className = 'chat-link-chip';
                a.href = l.url;
                a.textContent = l.label;
                lc.appendChild(a);
            });
            right.appendChild(lc);
        }

        wrap.appendChild(avatar);
        wrap.appendChild(right);
        messages.appendChild(wrap);
        scrollBottom();
    }

    function appendTyping() {
        const wrap = document.createElement('div');
        wrap.className = 'chat-msg bot typing-indicator';
        wrap.innerHTML = `
            <div class="bot-mini-avatar">🤖</div>
            <div class="chat-bubble">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>`;
        messages.appendChild(wrap);
        scrollBottom();
        return wrap;
    }

    function scrollBottom() {
        messages.scrollTop = messages.scrollHeight;
    }

    /* Basic **bold** markdown → <strong> */
    function renderMarkdown(text) {
        return escHtml(text)
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
    }

    function escHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }
})();
