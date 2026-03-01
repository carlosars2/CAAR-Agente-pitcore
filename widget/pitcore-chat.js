/**
 * Pitcore CAAR Chat Widget
 *
 * Embeddable chat widget for pitcore.online
 * Connects via WebSocket to the CAAR Agent API.
 *
 * Usage:
 *   <link rel="stylesheet" href="https://pitcore.online/agent/widget/pitcore-chat.css">
 *   <script src="https://pitcore.online/agent/widget/pitcore-chat.js"
 *           data-api="https://pitcore.online/agent/api"
 *           defer></script>
 */
(function () {
  "use strict";

  // --- Configuration ---
  var scriptTag = document.currentScript;
  var API_BASE = (scriptTag && scriptTag.getAttribute("data-api")) || "/agent/api";
  var WS_BASE = API_BASE.replace(/^http/, "ws");
  var CONVERSATION_KEY = "pitcore_caar_conv_id";

  // --- State ---
  var ws = null;
  var isOpen = false;
  var isSending = false;
  var conversationId = localStorage.getItem(CONVERSATION_KEY) || generateId();

  localStorage.setItem(CONVERSATION_KEY, conversationId);

  // --- Helpers ---
  function generateId() {
    return "caar_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2, 8);
  }

  function escapeHtml(text) {
    var div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function formatMessage(text) {
    // Bold: **text** → <strong>text</strong>
    var formatted = escapeHtml(text);
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    // Lists: lines starting with - or •
    formatted = formatted.replace(/^[\-•]\s+(.+)$/gm, "<li>$1</li>");
    if (formatted.indexOf("<li>") !== -1) {
      formatted = formatted.replace(/(<li>[\s\S]*?<\/li>)/g, "<ul>$1</ul>");
      // Clean up consecutive ul tags
      formatted = formatted.replace(/<\/ul>\s*<ul>/g, "");
    }
    return formatted;
  }

  // --- Build DOM ---
  function buildWidget() {
    var container = document.createElement("div");
    container.id = "pitcore-chat-widget";
    container.innerHTML =
      // Toggle button
      '<button id="pitcore-chat-toggle" aria-label="Abrir chat">' +
        '<svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.2L4 17.2V4h16v12z"/></svg>' +
      '</button>' +
      // Chat window
      '<div id="pitcore-chat-window">' +
        // Header
        '<div id="pitcore-chat-header">' +
          '<div class="avatar">C</div>' +
          '<div class="info">' +
            '<div class="name">CAAR — Pitcore & Systems</div>' +
            '<div class="status">Online</div>' +
          '</div>' +
          '<button class="close-btn" aria-label="Fechar chat">&times;</button>' +
        '</div>' +
        // Messages
        '<div id="pitcore-chat-messages"></div>' +
        // Input
        '<div id="pitcore-chat-input-area">' +
          '<textarea id="pitcore-chat-input" placeholder="Digite sua mensagem..." rows="1"></textarea>' +
          '<button id="pitcore-chat-send" aria-label="Enviar">' +
            '<svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>' +
          '</button>' +
        '</div>' +
        // Footer
        '<div id="pitcore-chat-footer">Powered by <a href="https://pitcore.online" target="_blank">Pitcore & Systems</a></div>' +
      '</div>';

    document.body.appendChild(container);

    // Bind events
    var toggle = document.getElementById("pitcore-chat-toggle");
    var window_ = document.getElementById("pitcore-chat-window");
    var closeBtn = container.querySelector(".close-btn");
    var input = document.getElementById("pitcore-chat-input");
    var sendBtn = document.getElementById("pitcore-chat-send");

    toggle.addEventListener("click", function () {
      isOpen = !isOpen;
      if (isOpen) {
        window_.classList.add("open");
        toggle.style.display = "none";
        input.focus();
        connectWebSocket();
        // Show greeting if first time
        var msgs = document.getElementById("pitcore-chat-messages");
        if (msgs.children.length === 0) {
          addMessage("assistant", "Ola! Sou a CAAR, consultora virtual da Pitcore & Systems. Como posso ajudar seu centro automotivo hoje?");
        }
      } else {
        window_.classList.remove("open");
        toggle.style.display = "flex";
      }
    });

    closeBtn.addEventListener("click", function () {
      isOpen = false;
      window_.classList.remove("open");
      toggle.style.display = "flex";
    });

    sendBtn.addEventListener("click", sendMessage);

    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    // Auto-resize textarea
    input.addEventListener("input", function () {
      this.style.height = "auto";
      this.style.height = Math.min(this.scrollHeight, 80) + "px";
    });
  }

  // --- WebSocket ---
  function connectWebSocket() {
    if (ws && ws.readyState <= 1) return; // Already connected/connecting

    var wsUrl = WS_BASE + "/chat/ws/" + conversationId;
    ws = new WebSocket(wsUrl);

    ws.onopen = function () {
      console.log("[CAAR] WebSocket connected");
    };

    ws.onmessage = function (event) {
      hideTyping();
      try {
        var data = JSON.parse(event.data);
        if (data.message) {
          addMessage("assistant", data.message);
        }
      } catch (e) {
        addMessage("assistant", event.data);
      }
      isSending = false;
      updateSendButton();
    };

    ws.onclose = function () {
      console.log("[CAAR] WebSocket closed");
      ws = null;
      // Reconnect if widget is still open
      if (isOpen) {
        setTimeout(connectWebSocket, 3000);
      }
    };

    ws.onerror = function () {
      console.warn("[CAAR] WebSocket error — falling back to REST");
      ws = null;
    };
  }

  // --- Send message ---
  function sendMessage() {
    var input = document.getElementById("pitcore-chat-input");
    var text = input.value.trim();
    if (!text || isSending) return;

    isSending = true;
    updateSendButton();

    addMessage("user", text);
    input.value = "";
    input.style.height = "auto";
    showTyping();

    // Try WebSocket first, fall back to REST
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ message: text }));
    } else {
      sendViaREST(text);
    }
  }

  function sendViaREST(text) {
    fetch(API_BASE + "/chat/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        conversation_id: conversationId,
        message: text,
        channel: "website",
      }),
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        hideTyping();
        addMessage("assistant", data.message);
      })
      .catch(function (err) {
        hideTyping();
        addMessage("assistant", "Desculpe, houve um erro. Tente novamente em alguns instantes.");
        console.error("[CAAR] REST error:", err);
      })
      .finally(function () {
        isSending = false;
        updateSendButton();
      });
  }

  // --- UI helpers ---
  function addMessage(role, text) {
    var container = document.getElementById("pitcore-chat-messages");
    var div = document.createElement("div");
    div.className = "pc-message " + role;
    div.innerHTML = formatMessage(text);
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  }

  function showTyping() {
    var container = document.getElementById("pitcore-chat-messages");
    var existing = container.querySelector(".pc-typing");
    if (existing) return;

    var div = document.createElement("div");
    div.className = "pc-typing";
    div.innerHTML = "<span></span><span></span><span></span>";
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  }

  function hideTyping() {
    var container = document.getElementById("pitcore-chat-messages");
    var typing = container.querySelector(".pc-typing");
    if (typing) typing.remove();
  }

  function updateSendButton() {
    var btn = document.getElementById("pitcore-chat-send");
    if (btn) btn.disabled = isSending;
  }

  // --- Init ---
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", buildWidget);
  } else {
    buildWidget();
  }
})();
