import threading
import speech_recognition as sr

from app.assistant import process_command
from app.tts import speak


recognizer = sr.Recognizer()

recognizer.dynamic_energy_threshold = True
recognizer.energy_threshold = 250
recognizer.dynamic_energy_adjustment_damping = 0.15
recognizer.dynamic_energy_ratio = 1.2
recognizer.pause_threshold = 0.8
recognizer.non_speaking_duration = 0.5


def listen_once(stop_event=None, on_result=None):
    """
    Listen for one voice command, process it, and return its result.
    The main voice worker can call this function repeatedly.
    """

    if stop_event is None:
        stop_event = threading.Event()

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            print(f"🎙️ Microphone calibrated. Energy threshold: {recognizer.energy_threshold}")
            
            print("\n🎙️ Listening... Speak now!")

            while not stop_event.is_set():
                try:
                    audio = recognizer.listen(
                        source,
                        timeout=5,
                        phrase_time_limit=8,
                    )
                    break

                except sr.WaitTimeoutError:
                    print("⏳ No speech detected. Still listening...")
                    continue

            else:
                return None

        if stop_event.is_set():
            return None

        print("🌐 Recognizing speech...")

        try:
            command = recognizer.recognize_google(
                audio,
                language="en-IN",
            ).strip()

        except sr.UnknownValueError:
            print("❌ Speech wasn't clear. Listening again...")
            return None

        except sr.RequestError as error:
            print(f"❌ Speech recognition service error: {error}")
            return None

        if not command:
            print("No command detected. Listening again...")
            return None

        if stop_event.is_set():
            return None

        print(f"🗣️ You said: {command}")
        print("⚙️ Processing command...")

        response = process_command(command)

        print(f"🤖 Assistant: {response}")

        result = {
            "command": command,
            "response": response,
        }

        if on_result:
            on_result(result)

        if not stop_event.is_set():
            try:
                speak(response)
            except Exception as error:
                print(f"❌ Voice output error: {error}")

        return result

    except Exception as error:
        print(
            f"❌ Voice engine error: "
            f"{type(error).__name__}: {error}"
        )
        return None