// ==================================================
// DOM
// ==================================================

const chatForm =
    document.getElementById("chatForm");

const messageInput =
    document.getElementById("messageInput");

const sendButton =
    document.getElementById("sendButton");

const messages =
    document.getElementById("messages");

const welcomeScreen =
    document.getElementById("welcomeScreen");

const chatArea =
    document.getElementById("chatArea");

const newChatButton =
    document.getElementById("newChatButton");


// ==================================================
// Session
// ==================================================

function createSessionId() {

    if (
        window.crypto
        && crypto.randomUUID
    ) {
        return crypto.randomUUID();
    }

    return (
        "session-"
        + Date.now()
        + "-"
        + Math.random()
            .toString(36)
            .slice(2)
    );
}


let sessionId =
    localStorage.getItem(
        "aster-row-session"
    );


if (!sessionId) {

    sessionId =
        createSessionId();

    localStorage.setItem(
        "aster-row-session",
        sessionId
    );
}


// ==================================================
// Utilities
// ==================================================

function escapeHtml(text) {

    const div =
        document.createElement(
            "div"
        );

    div.textContent =
        text ?? "";

    return div.innerHTML;
}


function scrollToBottom() {

    requestAnimationFrame(
        () => {

            chatArea.scrollTo({
                top:
                    chatArea.scrollHeight,

                behavior:
                    "smooth"
            });

        }
    );
}


function hideWelcome() {

    if (
        welcomeScreen.style.display
        !== "none"
    ) {

        welcomeScreen.style.display =
            "none";
    }
}


// ==================================================
// Messages
// ==================================================

function addUserMessage(text) {

    hideWelcome();

    const row =
        document.createElement(
            "div"
        );

    row.className =
        "message-row user";

    row.innerHTML = `
        <div class="message">

            <div class="message-author">
                YOU
            </div>

            <div class="message-bubble">
                ${escapeHtml(text)}
            </div>

        </div>
    `;

    messages.appendChild(
        row
    );

    scrollToBottom();
}


function addAssistantMessage(
    data
) {

    hideWelcome();

    const row =
        document.createElement(
            "div"
        );

    row.className =
        "message-row assistant";


    // ------------------------------
    // Sources
    // ------------------------------

    let sourcesHtml = "";

    if (
        Array.isArray(data.sources)
        && data.sources.length > 0
    ) {

        const sourceItems =
            data.sources
                .map(
                    source => `
                        <div class="source-item">

                            <span class="source-dot">
                                •
                            </span>

                            <span>
                                ${escapeHtml(
                                    source.filename
                                )}
                                —
                                ${escapeHtml(
                                    source.heading
                                )}
                            </span>

                        </div>
                    `
                )
                .join("");


        sourcesHtml = `
            <div class="sources-card">

                <div class="sources-title">
                    SOURCES
                </div>

                ${sourceItems}

            </div>
        `;
    }


    // ------------------------------
    // Handoff
    // ------------------------------

    let handoffHtml = "";

    if (data.handoff) {

        handoffHtml = `
            <div class="handoff-card">

                <div class="handoff-icon">
                    ◌
                </div>

                <div>

                    <strong>
                        Human assistance recommended
                    </strong>

                    <p>
                        ${
                            escapeHtml(
                                data.handoff_reason
                                ||
                                "This request may require additional support."
                            )
                        }
                    </p>

                </div>

            </div>
        `;
    }


    // ------------------------------
    // Main
    // ------------------------------

    row.innerHTML = `
        <div class="message">

            <div class="message-author">
                ASTER & ROW
            </div>

            <div class="message-bubble">
                ${escapeHtml(data.answer)}
            </div>

            ${sourcesHtml}

            ${handoffHtml}

        </div>
    `;

    messages.appendChild(
        row
    );

    scrollToBottom();
}


// ==================================================
// Typing indicator
// ==================================================

function showTyping() {

    const row =
        document.createElement(
            "div"
        );

    row.className =
        "message-row assistant";

    row.id =
        "typingIndicator";

    row.innerHTML = `
        <div class="message">

            <div class="message-author">
                ASTER & ROW
            </div>

            <div
                class="
                    message-bubble
                    typing-bubble
                "
            >
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>

        </div>
    `;

    messages.appendChild(
        row
    );

    scrollToBottom();
}


function removeTyping() {

    const indicator =
        document.getElementById(
            "typingIndicator"
        );

    if (indicator) {
        indicator.remove();
    }
}


// ==================================================
// API
// ==================================================

async function sendMessage(
    message
) {

    addUserMessage(
        message
    );

    showTyping();

    sendButton.disabled =
        true;

    messageInput.disabled =
        true;


    try {

        const response =
            await fetch(
                "/api/chat",
                {
                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            message:
                                message,

                            session_id:
                                sessionId
                        })
                }
            );


        const data =
            await response.json();


        removeTyping();


        if (!response.ok) {

            throw new Error(
                data.detail
                ||
                "Unable to process request."
            );
        }


        addAssistantMessage(
            data
        );

    }

    catch (error) {

        removeTyping();

        addAssistantMessage({
            answer:
                (
                    "Something went wrong while "
                    + "contacting the support agent. "
                    + "Please try again."
                ),

            sources: [],

            handoff: false
        });

        console.error(
            error
        );
    }

    finally {

        sendButton.disabled =
            false;

        messageInput.disabled =
            false;

        messageInput.focus();
    }
}


// ==================================================
// Form
// ==================================================

chatForm.addEventListener(
    "submit",
    event => {

        event.preventDefault();

        const message =
            messageInput
                .value
                .trim();

        if (!message) {
            return;
        }

        messageInput.value =
            "";

        resetTextareaHeight();

        sendMessage(
            message
        );
    }
);


// Enter sends.
// Shift+Enter creates newline.

messageInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter"
            && !event.shiftKey
        ) {

            event.preventDefault();

            chatForm.requestSubmit();
        }
    }
);


// ==================================================
// Auto resize textarea
// ==================================================

function resetTextareaHeight() {

    messageInput.style.height =
        "auto";
}


messageInput.addEventListener(
    "input",
    () => {

        resetTextareaHeight();

        messageInput.style.height =
            Math.min(
                messageInput.scrollHeight,
                130
            )
            + "px";
    }
);


// ==================================================
// Suggested prompts
// ==================================================

document
    .querySelectorAll(
        ".suggestion"
    )
    .forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    const message =
                        button.dataset.message;

                    if (message) {

                        sendMessage(
                            message
                        );
                    }
                }
            );

        }
    );


// ==================================================
// New chat
// ==================================================

newChatButton.addEventListener(
    "click",
    () => {

        sessionId =
            createSessionId();

        localStorage.setItem(
            "aster-row-session",
            sessionId
        );

        messages.innerHTML =
            "";

        welcomeScreen.style.display =
            "";

        messageInput.value =
            "";

        messageInput.focus();
    }
);


// ==================================================
// Initial focus
// ==================================================

messageInput.focus();