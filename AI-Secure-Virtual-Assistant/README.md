# AI-Powered Secure Virtual Assistant

A Python-based virtual assistant with a web chat interface, voice
interaction, intent detection, and utility tools. The backend uses
FastAPI, and the frontend uses HTML, CSS, and JavaScript.

> **Project status:** Under development. Voice-session handling and
> microphone sensitivity are still being tested.

## Features

-   Web chat interface for sending commands and viewing responses.
-   FastAPI endpoints for chat, intent detection, and voice controls.
-   Intent detection for supported commands such as greetings,
    calculations, date/time questions, application launching, and
    web/YouTube requests.
-   Voice input through the Python voice module.
-   Text-to-speech output through the configured speech engine.
-   Application-launching, browser, and calculator tools.
-   Optional LLM integration, depending on local configuration.

## Technology Stack

-   Python
-   FastAPI and Uvicorn
-   HTML, CSS, JavaScript
-   SpeechRecognition (if configured)
-   pyttsx3 (if configured)
-   Groq API / LLM integration (if configured)
-   Python threading for voice-session management

## Project Structure

``` text
AI-Secure-Virtual-Assistant/
├── .env                      # Local configuration; do not commit
├── run_voice.py
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app and API routes
│   ├── assistant.py           # Main command-processing flow
│   ├── intent.py              # Intent detection
│   ├── llm.py                 # LLM integration
│   ├── memory.py              # Conversation memory
│   ├── voice.py               # Speech recognition / voice loop
│   ├── tts.py                 # Text-to-speech
│   ├── security.py             # Security-related helpers
│   ├── tool_manager.py        # Tool coordination
│   └── tools/
│       ├── __init__.py
│       ├── applications.py    # Supported desktop applications
│       ├── browser.py         # Browser actions
│       └── calculator.py      # Calculation utility
├── logs/
└── web/
    ├── index.html
    ├── css/style.css
    └── js/app.js
```

The exact files present may vary as development continues.

## Requirements

-   Python 3.10 or newer recommended.
-   A supported desktop operating system for application-launching
    features.
-   A working microphone for voice input.
-   Internet access for online speech recognition or API-backed LLM
    features.
-   Required Python packages installed in your virtual environment.

## Setup

### 1. Open the project

Open the project folder in VS Code and open a terminal in the project
root.

### 2. Create and activate a virtual environment

**Windows PowerShell:**

``` powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If your existing environment is named `.venv-1`, activate that instead:

``` powershell
.\.venv-1\Scripts\Activate.ps1
```

### 3. Install dependencies

If a `requirements.txt` file exists:

``` powershell
pip install -r requirements.txt
```

Otherwise, install the dependencies required by the project modules.
Common packages used by this project include:

``` powershell
pip install fastapi "uvicorn[standard]" pydantic SpeechRecognition pyttsx3
```

Install any additional dependencies required by `app/llm.py` and other
modules.

### 4. Configure environment variables

Create or update `.env` using the variable names expected by your own
configuration and LLM code. If your implementation uses Groq, it may
require a Groq API key. Use the exact variable name your code expects.

**Never commit real API keys, passwords, or tokens.** Add `.env` and
virtual environments to `.gitignore`.

Example `.gitignore` entries:

``` gitignore
.env
.env.*
!.env.example
.venv/
.venv-*/
__pycache__/
*.py[cod]
logs/
```

A sanitized `.env.example` may document variable names, but must not
contain real credentials.

## Run the Application

From the project root, activate the virtual environment and run:

``` powershell
uvicorn app.main:app --reload
```

Open these addresses in your browser:

-   **Web interface:** `http://127.0.0.1:8000`
-   **API documentation:** `http://127.0.0.1:8000/docs`

Stop the server with `Ctrl+C`.

## API Endpoints

  -----------------------------------------------------------------------
  Method                  Endpoint                Purpose
  ----------------------- ----------------------- -----------------------
  `GET`                   `/`                     Serves the web
                                                  interface

  `POST`                  `/assistant`            Processes a text
                                                  command

  `POST`                  `/intent`               Returns the detected
                                                  intent

  `POST`                  `/voice/start`          Starts the Python voice
                                                  worker

  `POST`                  `/voice/stop`           Requests the voice
                                                  worker to stop

  `GET`                   `/voice/status`         Returns voice status
                                                  and the latest
                                                  command/response
  -----------------------------------------------------------------------

### Example request

Send JSON to `/assistant`:

``` json
{
  "command": "What is Python?"
}
```

The response includes the submitted command and the assistant's
response.

## Voice Assistant

1.  Start the FastAPI server.
2.  Open the web interface.
3.  Press the microphone button to start the Python voice engine.
4.  Speak a supported command and wait for the response.
5.  Press the button again to request that voice mode stop.

**Voice controls are still under development.** If speech is not
recognized or an older command repeats after restarting voice mode,
check the server terminal and review `app/voice.py`, `app/main.py`, and
the polling logic in `web/js/app.js`.

Microphone permissions, audio-device selection, speech-recognition
connectivity, and text-to-speech availability can affect voice features.

## Security Notes

-   Never commit `.env`, API keys, passwords, tokens, or other secrets.
-   Rotate any API key that has been exposed.
-   Do not expose the development server publicly without suitable
    authentication, authorization, input validation, and deployment
    security.
-   Keep application-launching actions explicitly allow-listed; avoid
    executing arbitrary shell commands.
-   Do not describe the project as production-ready or security-audited
    until it has been reviewed and tested.

## Troubleshooting

### `uvicorn` is not recognized

Activate the correct virtual environment, then run:

``` powershell
python -m pip install "uvicorn[standard]"
python -m uvicorn app.main:app --reload
```

### Module not found

Confirm that the terminal is in the project root and the correct virtual
environment is active. Install the missing dependency into that
environment.

### Web page does not load

Check that the server started without errors and open
`http://127.0.0.1:8000`. Review terminal output if startup fails.

### Voice input or output does not work

Check microphone permissions and the selected audio device. Verify the
dependencies used by `app/voice.py` and `app/tts.py`, and inspect
terminal logs. Voice restart behavior is still being worked on.

## Contributing

This is a learning and development project. Improvements to intent
detection, accessibility, safe tool execution, voice reliability, tests,
and documentation are welcome.

## License

No license has been specified yet. Add a `LICENSE` file before
distributing the project under a particular open-source license.
