from pathlib import Path
from threading import Event, Lock, Thread, current_thread

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.assistant import process_command
from app.intent import detect_intent
from app.voice import listen_once


app = FastAPI(
    title="AI Chat Assistant",
    version="1.0.0",
)

BASE_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = BASE_DIR / "web"

app.mount(
    "/css",
    StaticFiles(directory=WEB_DIR / "css"),
    name="css",
)

app.mount(
    "/js",
    StaticFiles(directory=WEB_DIR / "js"),
    name="js",
)


class CommandRequest(BaseModel):
    command: str


voice_lock = Lock()

voice_state = {
    "running": False,
    "event_id": 0,
    "command": "",
    "response": "",
}

voice_thread = None
voice_stop_event = None


def publish_voice_result(result, session_event):
    with voice_lock:
        if session_event.is_set():
            return

        voice_state["event_id"] += 1
        voice_state["command"] = result["command"]
        voice_state["response"] = result["response"]


def voice_worker(session_event):
    global voice_thread, voice_stop_event

    this_thread = current_thread()

    try:
        while not session_event.is_set():
            print("\n🎙️ Voice worker: waiting for a command...")

            result = listen_once(
                stop_event=session_event,
                on_result=lambda result: publish_voice_result(
                    result,
                    session_event,
                ),
            )

            if session_event.is_set():
                break

            if result is None:
                continue

            print("✅ Command completed. Listening again...")

    except Exception as error:
        print(
            f"❌ Voice worker error: "
            f"{type(error).__name__}: {error}"
        )

    finally:
        with voice_lock:
            if voice_thread is this_thread:
                voice_state["running"] = False
                voice_thread = None
                voice_stop_event = None

        print("🛑 Voice worker stopped.")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(WEB_DIR / "index.html")


@app.post("/assistant")
def assistant(request: CommandRequest):
    response = process_command(request.command)

    return {
        "command": request.command,
        "response": response,
    }


@app.post("/intent")
def analyze_intent(request: CommandRequest):
    return detect_intent(request.command)


@app.post("/voice/start")
def start_voice():
    global voice_thread, voice_stop_event

    with voice_lock:
        if voice_thread is not None and voice_thread.is_alive():
            if voice_stop_event is not None and voice_stop_event.is_set():
                return {
                    "success": False,
                    "message": "Voice assistant is stopping. Please wait a moment and try again.",
                }

            return {
                "success": True,
                "message": "Voice assistant is already running.",
            }

        session_event = Event()
        voice_stop_event = session_event

        voice_state["running"] = True
        voice_state["event_id"] = 0
        voice_state["command"] = ""
        voice_state["response"] = ""

        voice_thread = Thread(
            target=voice_worker,
            args=(session_event,),
            daemon=True,
            name="AI-Voice-Worker",
        )

        voice_thread.start()

    return {
        "success": True,
        "message": "Voice assistant started.",
    }


@app.post("/voice/stop")
def stop_voice():
    with voice_lock:
        if voice_stop_event is not None:
            voice_stop_event.set()

    return {
        "success": True,
        "message": "Voice assistant is stopping.",
    }


@app.get("/voice/status")
def voice_status():
    with voice_lock:
        return dict(voice_state)