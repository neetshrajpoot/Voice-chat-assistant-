import os
from pathlib import Path
from difflib import get_close_matches
import shutil

START_MENU_DIRS = [
    Path(os.environ.get("PROGRAMDATA", "")) /
    "Microsoft/Windows/Start Menu/Programs",

    Path(os.environ.get("APPDATA", "")) /
    "Microsoft/Windows/Start Menu/Programs",
]


# Safe Windows apps that can be opened directly.
WINDOWS_APPS = {
    "camera": "microsoft.windows.camera:",
    "windows camera": "microsoft.windows.camera:",

    "calculator": "calculator:",
    "windows calculator": "calculator:",

    "photos": "ms-photos:",
    "windows photos": "ms-photos:",

    "gallery": "ms-photos:",

    "settings": "ms-settings:",
}


# Apps/tools that must NEVER be opened.
BLOCKED_APPS = {
    "cmd",
    "cmd.exe",
    "command prompt",

    "powershell",
    "powershell.exe",
    "windows powershell",

    "pwsh",
    "pwsh.exe",

    "windows terminal",
    "terminal",

    "command line",

    "registry editor",
    "regedit",
    "regedit.exe",
}


def normalize_name(name: str) -> str:
    """Normalize application names."""

    name = name.lower().strip()

    for suffix in [".lnk", ".url", ".exe"]:
        if name.endswith(suffix):
            name = name[:-len(suffix)]

    # Remove punctuation at the end.
    name = name.rstrip(" .,!?")

    return " ".join(name.split())


def is_blocked(name: str) -> bool:
    """Check whether an application is blocked."""

    normalized = normalize_name(name)

    if normalized in BLOCKED_APPS:
        return True

    for blocked in BLOCKED_APPS:
        if blocked in normalized:
            return True

    return False


def scan_installed_apps():
    """
    Scan Windows Start Menu shortcuts.

    The assistant opens the shortcut itself instead of
    executing arbitrary executable paths.
    """

    apps = {}

    for start_menu in START_MENU_DIRS:

        if not start_menu.exists():
            continue

        try:
            files = start_menu.rglob("*")
        except Exception:
            continue

        for file in files:

            if not file.is_file():
                continue

            if file.suffix.lower() not in {".lnk", ".url"}:
                continue

            app_name = normalize_name(file.stem)

            if not app_name:
                continue

            if is_blocked(app_name):
                continue

            if app_name not in apps:
                apps[app_name] = file

    return apps


APP_INDEX = scan_installed_apps()


def refresh_apps():
    """Refresh installed application index."""

    global APP_INDEX

    APP_INDEX = scan_installed_apps()

    return len(APP_INDEX)


def find_application(application: str):
    requested = normalize_name(application)

    if not requested:
        return None, None

    if is_blocked(requested):
        return None, "BLOCKED"

    # Explicit aliases for Visual Studio Code.
    vscode_names = {
        "vs code",
        "vscode",
        "visual studio code",
        "code editor",
    }

    if requested in vscode_names:
        # First, check Start Menu shortcuts.
        for name, target in APP_INDEX.items():
            if name in {
                "visual studio code",
                "visual studio code user setup",
                "visual studio code insiders",
            }:
                return "Visual Studio Code", target

        # Check common installation locations.
        local_app_data = Path(
            os.environ.get("LOCALAPPDATA", "")
        )

        program_files = Path(
            os.environ.get("PROGRAMFILES", r"C:\Program Files")
        )

        vscode_paths = [
            local_app_data / "Programs/Microsoft VS Code/Code.exe",
            program_files / "Microsoft VS Code/Code.exe",
        ]

        for path in vscode_paths:
            if path.is_file():
                return "Visual Studio Code", path

        # Check whether the VS Code launcher is available.
        code_launcher = shutil.which("code")

        if code_launcher:
            return "Visual Studio Code", Path(code_launcher)

        return None, None

    # Safe Windows applications.
    if requested in WINDOWS_APPS:
        return requested, WINDOWS_APPS[requested]

    # Exact Start Menu match.
    if requested in APP_INDEX:
        return requested, APP_INDEX[requested]

    # Partial match: allow only reasonably specific names.
    partial_matches = [
        name for name in APP_INDEX
        if len(requested) >= 4
        and (requested in name or name in requested)
    ]

    if partial_matches:
        best = min(partial_matches, key=len)
        return best, APP_INDEX[best]

    # Conservative fuzzy matching.
    matches = get_close_matches(
        requested,
        list(APP_INDEX.keys()),
        n=1,
        cutoff=0.75,
    )

    if matches:
        best = matches[0]
        return best, APP_INDEX[best]

    return None, None


def open_application(application: str) -> str:
    """
    Safely open an application.

    Supports:
    - Start Menu applications
    - Safe Windows app URI mappings

    Does NOT execute arbitrary commands.
    """

    requested = normalize_name(application)

    if not requested:
        return "Please tell me which application you want to open."

    # --------------------------------
    # Security block
    # --------------------------------

    if is_blocked(requested):

        return (
            f"I can't open '{application}'. "
            "Command-line and terminal applications "
            "are blocked."
        )

    app_name, target = find_application(requested)

    if target == "BLOCKED":

        return (
            f"I can't open '{application}'. "
            "This application is blocked for security."
        )

    if target is None:

        return (
            f"I couldn't find '{application}' "
            "in the Windows Start Menu."
        )

    try:

        # Windows URI application
        if isinstance(target, str):

            os.startfile(target)

        # Start Menu shortcut
        else:

            os.startfile(str(target))

        return f"Opening {app_name}."

    except Exception as error:

        print(f"Application launch error: {error}")

        return (
            f"I found {app_name}, "
            "but Windows could not open it."
        )