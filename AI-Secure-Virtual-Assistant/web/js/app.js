/* =========================================================
   AI CHAT ASSISTANT
   Frontend Controller
   ========================================================= */


/* =========================================================
   ELEMENTS
   ========================================================= */

const chat = document.getElementById("chat");
const chatArea = document.getElementById("chatArea");

const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");

const newChatButton = document.getElementById("newChatButton");
const clearButton = document.getElementById("clearButton");

const chatHistory = document.getElementById("chatHistory");
const welcomeScreen = document.getElementById("welcomeScreen");

const thinking = document.getElementById("thinking");

const mobileMenuButton =
    document.getElementById("mobileMenuButton");

const sidebar =
    document.getElementById("sidebar");

const signInButton =
    document.getElementById("signInButton");

const authModal =
    document.getElementById("authModal");

const closeAuthModal =
    document.getElementById("closeAuthModal");

const settingsButton =
    document.getElementById("settingsButton");

const profileButton =
    document.getElementById("profileButton");

const attachmentButton =
    document.getElementById("attachmentButton");

const micButton =
    document.getElementById("micButton");


/* =========================================================
   STATE
   ========================================================= */

let currentChatId = null;
let chats = [];
let isSending = false;


/* =========================================================
   VOICE STATE
   ========================================================= */

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

let recognition = null;
let isListening = false;

/*
   Live conversation mode.

   false = normal mic mode
   true  = continuous conversation
*/

let liveConversation = false;

/*
   Prevent microphone from starting
   while AI is speaking.
*/

let assistantSpeaking = false;


/* =========================================================
   PYTHON VOICE ENGINE
   ========================================================= */

let pythonVoiceActive = false;
let pythonVoicePolling = null;
let lastVoiceEventId = 0;


/* =========================================================
   VOICE BUTTON STATE
   ========================================================= */

function setVoiceUI(active) {

    pythonVoiceActive = active;

    if (!micButton) return;

    micButton.classList.toggle(
        "listening",
        active
    );

    micButton.textContent = active ? "◉" : "🎙";

    micButton.title = active
        ? "Stop voice assistant"
        : "Start voice assistant";

    micButton.setAttribute(
        "aria-label",
        active
            ? "Stop voice assistant"
            : "Start voice assistant"
    );
}


/* =========================================================
   CHECK PYTHON VOICE STATUS
   ========================================================= */

async function pollVoiceStatus() {

    if (!pythonVoiceActive) return;

    try {

        const response = await fetch("/voice/status");

        if (!response.ok) return;

        const data = await response.json();

        if (
            data.event_id &&
            data.event_id > lastVoiceEventId
        ) {

            lastVoiceEventId = data.event_id;

            if (data.command) {
                addMessage("user", data.command);
            }

            if (data.response) {
                addMessage("assistant", data.response);
            }
        }

        if (data.running === false) {
            setVoiceUI(false);
        }

    } catch (error) {

        console.error(
            "Voice status error:",
            error
        );
    }
}


/* =========================================================
   START PYTHON VOICE
   ========================================================= */

async function startPythonVoice() {

    if (pythonVoiceActive) return;

    try {

        const response = await fetch(
            "/voice/start",
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error("Could not start voice engine");
        }

        lastVoiceEventId = 0;

        setVoiceUI(true);

        if (!pythonVoicePolling) {

            pythonVoicePolling = setInterval(
                pollVoiceStatus,
                500
            );
        }

        pollVoiceStatus();

    } catch (error) {

        console.error(
            "Python voice error:",
            error
        );

        setVoiceUI(false);
    }
}


/* =========================================================
   STOP PYTHON VOICE
   ========================================================= */

async function stopPythonVoice() {

    try {

        await fetch(
            "/voice/stop",
            {
                method: "POST"
            }
        );

    } catch (error) {

        console.error(error);
    }

    setVoiceUI(false);

    if (pythonVoicePolling) {

        clearInterval(pythonVoicePolling);

        pythonVoicePolling = null;
    }
}


/* =========================================================
   MIC BUTTON
   ========================================================= */

if (micButton) {

    micButton.addEventListener(
        "click",
        async () => {

            if (pythonVoiceActive) {
                await stopPythonVoice();
            } else {
                await startPythonVoice();
            }

        }
    );
} 


/* =========================================================
   AI VOICE OUTPUT
   ========================================================= */

let speechEnabled = true;


function speakResponse(text) {

    if (!speechEnabled) {
        return;
    }


    if (
        !("speechSynthesis" in window)
    ) {

        console.warn(
            "Speech synthesis is not supported."
        );


        assistantSpeaking = false;


        if (liveConversation) {

            startLiveListening();

        }


        return;
    }


    /*
       AI is now speaking.
       Microphone must remain OFF.
    */

    assistantSpeaking = true;


    window.speechSynthesis.cancel();


    /*
       Clean Markdown formatting ONLY
       for speech.

       Normal characters are preserved.
    */

    const cleanText = text

        /*
           Markdown table separator rows

           Example:
           |----------|----------|
        */

        .replace(
            /^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$/gm,
            ""
        )


        /*
           Remove pipes only from
           Markdown table rows.
        */

        .replace(
            /^\s*\|.*\|\s*$/gm,
            (line) => {

                return line
                    .replace(
                        /^\s*\|/,
                        ""
                    )
                    .replace(
                        /\|\s*$/,
                        ""
                    )
                    .replace(
                        /\|/g,
                        " "
                    );
            }
        )


        /*
           Bold Markdown
        */

        .replace(
            /\*\*(.*?)\*\*/g,
            "$1"
        )


        /*
           Italic Markdown
        */

        .replace(
            /(?<!\w)\*(.*?)\*(?!\w)/g,
            "$1"
        )


        /*
           Inline code
        */

        .replace(
            /`([^`]+)`/g,
            "$1"
        )


        /*
           Markdown headings
        */

        .replace(
            /^\s*#{1,6}\s+/gm,
            ""
        )


        /*
           Markdown links
        */

        .replace(
            /\[([^\]]+)\]\([^)]+\)/g,
            "$1"
        )


        /*
           Markdown bullet points
        */

        .replace(
            /^\s*[-*+]\s+/gm,
            ""
        )


        /*
           Numbered lists
        */

        .replace(
            /^\s*\d+\.\s+/gm,
            ""
        )


        /*
           Markdown horizontal rules
        */

        .replace(
            /^\s*(?:-{3,}|\*{3,}|_{3,})\s*$/gm,
            ""
        )


        /*
           Remove extra whitespace
        */

        .replace(
            /\s+/g,
            " "
        )


        .trim();


    /*
       Nothing left to speak.
    */

    if (!cleanText) {

        assistantSpeaking = false;


        if (liveConversation) {

            startLiveListening();

        }


        return;
    }


    const utterance =
        new SpeechSynthesisUtterance(
            cleanText
        );


    utterance.lang =
        "en-IN";


    utterance.rate =
        1.0;


    utterance.pitch =
        1.0;


    utterance.volume =
        1.0;


    /*
       AI finished speaking.
       Automatically start listening again.
    */

    utterance.onend = () => {

        assistantSpeaking = false;


        if (liveConversation) {

            setTimeout(
                () => {

                    startLiveListening();

                },
                200
            );
        }
    };


    /*
       If TTS fails, return to listening mode.
    */

    utterance.onerror = () => {

        assistantSpeaking = false;


        if (liveConversation) {

            startLiveListening();

        }
    };


    window.speechSynthesis.speak(
        utterance
    );
}


/* =========================================================
   CHAT ID
   ========================================================= */

function generateChatId() {

    return Date.now().toString();

}


/* =========================================================
   CREATE NEW CHAT
   ========================================================= */

function createNewChat() {

    currentChatId =
        generateChatId();


    chat.innerHTML =
        "";


    welcomeScreen.style.display =
        "block";


    thinking.classList.remove(
        "visible"
    );


    messageInput.value =
        "";


    messageInput.style.height =
        "auto";


    renderHistory();


    messageInput.focus();


    closeMobileSidebar();

}


/* =========================================================
   ADD MESSAGE
   ========================================================= */

function addMessage(
    role,
    content
) {

    welcomeScreen.style.display =
        "none";


    const message =
        document.createElement(
            "div"
        );


    message.className =
        `message ${role}`;


    const avatar =
        document.createElement(
            "div"
        );


    avatar.className =
        "message-avatar";


    avatar.textContent =
        role === "assistant"
            ? "AI"
            : "N";


    const messageContent =
        document.createElement(
            "div"
        );


    messageContent.className =
        "message-content";


    messageContent.textContent =
        content;


    message.appendChild(
        avatar
    );


    message.appendChild(
        messageContent
    );


    chat.appendChild(
        message
    );


    scrollToBottom();


    return message;
}


/* =========================================================
   THINKING
   ========================================================= */

function showThinking() {

    thinking.classList.add(
        "visible"
    );


    scrollToBottom();

}


function hideThinking() {

    thinking.classList.remove(
        "visible"
    );

}


/* =========================================================
   SCROLL
   ========================================================= */

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


/* =========================================================
   SEND MESSAGE
   ========================================================= */

async function sendMessage(
    customMessage = null
) {

    if (isSending) {
        return;
    }


    const message =
        customMessage !== null
            ? customMessage.trim()
            : messageInput.value.trim();


    if (!message) {
        return;
    }


    isSending = true;


    sendButton.disabled =
        true;


    /* USER MESSAGE */

    addMessage(
        "user",
        message
    );


    /* CLEAR INPUT */

    messageInput.value =
        "";


    messageInput.style.height =
        "auto";


    /* CREATE CHAT */

    if (!currentChatId) {

        currentChatId =
            generateChatId();


        addChatToHistory(
            message
        );
    }


    /* THINKING */

    showThinking();


    try {

        const response =
            await fetch(
                "/assistant",
                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({
                            command:
                                message
                        })
                }
            );


        if (!response.ok) {

            throw new Error(
                `Server returned ${response.status}`
            );
        }


        const data =
            await response.json();


        hideThinking();


        const assistantResponse =
            data.response;


        /* AI MESSAGE */

        addMessage(
            "assistant",
            assistantResponse
        );


        /* SPEAK AI RESPONSE */

        speakResponse(
            assistantResponse
        );


        /* UPDATE SIDEBAR */

        updateCurrentChatTitle(
            message
        );


    } catch (error) {

        console.error(
            "Assistant error:",
            error
        );


        hideThinking();


        const errorMessage =
            "Sorry, I couldn't connect to the assistant. Please make sure the server is running.";


        addMessage(
            "assistant",
            errorMessage
        );


        /*
           In live mode, let the user
           speak again after an error.
        */

        if (liveConversation) {

            assistantSpeaking =
                false;


            setTimeout(
                () => {

                    startLiveListening();

                },
                300
            );
        }


    } finally {

        isSending =
            false;


        sendButton.disabled =
            false;


        messageInput.focus();

    }
}


/* =========================================================
   CHAT HISTORY
   ========================================================= */

function addChatToHistory(
    message
) {

    const chatItem = {

        id:
            currentChatId,

        title:
            createChatTitle(
                message
            )
    };


    chats.unshift(
        chatItem
    );


    if (chats.length > 20) {

        chats =
            chats.slice(
                0,
                20
            );
    }


    renderHistory();
}


/* =========================================================
   CHAT TITLE
   ========================================================= */

function createChatTitle(
    message
) {

    let title =
        message.trim();


    if (title.length > 35) {

        title =
            title.substring(
                0,
                35
            ) + "...";
    }


    return title;
}


/* =========================================================
   UPDATE CURRENT CHAT TITLE
   ========================================================= */

function updateCurrentChatTitle(
    message
) {

    const current =
        chats.find(
            item =>
                item.id ===
                currentChatId
        );


    if (!current) {
        return;
    }


    current.title =
        createChatTitle(
            message
        );


    renderHistory();
}


/* =========================================================
   RENDER HISTORY
   ========================================================= */

function renderHistory() {

    chatHistory.innerHTML =
        "";


    chats.forEach(
        item => {

            const button =
                document.createElement(
                    "button"
                );


            button.className =
                "history-item";


            if (
                item.id ===
                currentChatId
            ) {

                button.classList.add(
                    "active"
                );
            }


            button.textContent =
                item.title;


            button.addEventListener(
                "click",
                () => {

                    currentChatId =
                        item.id;


                    renderHistory();

                }
            );


            chatHistory.appendChild(
                button
            );
        }
    );
}


/* =========================================================
   CLEAR CHAT
   ========================================================= */

function clearChat() {

    chat.innerHTML =
        "";


    welcomeScreen.style.display =
        "block";


    thinking.classList.remove(
        "visible"
    );


    messageInput.value =
        "";


    messageInput.style.height =
        "auto";


    currentChatId =
        null;


    renderHistory();


    messageInput.focus();
}


/* =========================================================
   NEW CHAT
   ========================================================= */

newChatButton.addEventListener(
    "click",
    createNewChat
);


/* =========================================================
   CLEAR
   ========================================================= */

clearButton.addEventListener(
    "click",
    clearChat
);


/* =========================================================
   SEND BUTTON
   ========================================================= */

sendButton.addEventListener(
    "click",
    () => {

        sendMessage();

    }
);


/* =========================================================
   ENTER TO SEND
   ========================================================= */

messageInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();
        }
    }
);


/* =========================================================
   TEXTAREA RESIZE
   ========================================================= */

messageInput.addEventListener(
    "input",
    () => {

        messageInput.style.height =
            "auto";


        messageInput.style.height =
            Math.min(
                messageInput.scrollHeight,
                150
            ) + "px";
    }
);


/* =========================================================
   SUGGESTIONS
   ========================================================= */

document
    .querySelectorAll(
        ".suggestion-card"
    )
    .forEach(
        card => {

            card.addEventListener(
                "click",
                () => {

                    const prompt =
                        card.dataset.prompt;


                    if (!prompt) {
                        return;
                    }


                    messageInput.value =
                        prompt;


                    messageInput.style.height =
                        "auto";


                    sendMessage();
                }
            );
        }
    );


/* =========================================================
   MOBILE SIDEBAR
   ========================================================= */

mobileMenuButton.addEventListener(
    "click",
    () => {

        sidebar.classList.toggle(
            "open"
        );
    }
);


function closeMobileSidebar() {

    sidebar.classList.remove(
        "open"
    );
}


/* =========================================================
   SIGN IN MODAL
   ========================================================= */

signInButton.addEventListener(
    "click",
    () => {

        authModal.classList.add(
            "active"
        );
    }
);


closeAuthModal.addEventListener(
    "click",
    () => {

        authModal.classList.remove(
            "active"
        );
    }
);


authModal.addEventListener(
    "click",
    event => {

        if (
            event.target ===
            authModal
        ) {

            authModal.classList.remove(
                "active"
            );
        }
    }
);


/* =========================================================
   SETTINGS
   ========================================================= */

settingsButton.addEventListener(
    "click",
    () => {

        console.log(
            "Settings panel will be added later."
        );
    }
);


/* =========================================================
   PROFILE
   ========================================================= */

profileButton.addEventListener(
    "click",
    () => {

        console.log(
            "Profile menu will be added later."
        );
    }
);


/* =========================================================
   ATTACHMENT
   ========================================================= */

attachmentButton.addEventListener(
    "click",
    () => {

        console.log(
            "Attachment system will be added later."
        );
    }
);


/* =========================================================
   GOOGLE / GITHUB
   ========================================================= */

const googleLogin =
    document.getElementById(
        "googleLogin"
    );


const githubLogin =
    document.getElementById(
        "githubLogin"
    );


if (googleLogin) {

    googleLogin.addEventListener(
        "click",
        () => {

            console.log(
                "Google OAuth will be connected later."
            );
        }
    );
}


if (githubLogin) {

    githubLogin.addEventListener(
        "click",
        () => {

            console.log(
                "GitHub OAuth will be connected later."
            );
        }
    );
}


/* =========================================================
   INITIALIZE
   ========================================================= */

createNewChat();


console.log(
    "AI Chat Assistant frontend initialized."
);