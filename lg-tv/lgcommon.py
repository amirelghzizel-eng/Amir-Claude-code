"""Fonctions communes : connexion SSAP, lecture/écriture des réglages."""
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

from aiowebostv import WebOsClient

TV_IP = "192.168.1.164"
BACKUP_DIR = Path.home() / "Documents" / "LG-backup"
KEY_FILE = BACKUP_DIR / "client_key.json"
SETTINGS_URI = "com.webos.service.settings/getSystemSettings"
SET_SETTINGS_URI = "com.webos.service.settings/setSystemSettings"

# webOS exige la liste des clés à lire : on interroge large, clé par clé,
# et on garde celles que la télé accepte.
KEYS = {
    "picture": [
        "pictureMode", "backlight", "contrast", "brightness", "color", "tint",
        "sharpness", "hSharpness", "vSharpness", "colorTemperature",
        "dynamicContrast", "dynamicColor", "colorGamut", "superResolution",
        "gamma", "blackLevel", "noiseReduction", "mpegNoiseReduction",
        "realCinema", "motionEyeCare", "truMotionMode", "localDimming",
        "energySaving", "eyeComfortMode", "smoothGradation", "adjustingLuminance",
        "whiteBalanceColorTemperature", "whiteBalanceMethod", "colorManagementColorSystem",
    ],
    "sound": [
        "soundMode", "soundOutput", "balance", "autoVolume", "virtualSurround",
        "clearVoice", "bass", "treble", "avSync", "eqSelect",
    ],
    "option": [
        "country", "localeInfo", "audioGuidance", "screenRemoteAutoLaunch",
        "liveMenuLaunch", "storeMode", "homeAutoLaunch", "quickStartMode",
        "standByLight", "smartServiceCountryCode3",
    ],
    "other": ["simplinkEnable", "liveTVHomeAutoLaunch", "homePromotion"],
    "network": ["deviceName", "wolwowlOnOff"],
    "time": ["autoClock", "timeZone"],
}


def load_key():
    try:
        return json.loads(KEY_FILE.read_text())["client_key"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return None


async def connect():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    client = WebOsClient(TV_IP, client_key=load_key(), connect_timeout=10)
    if not load_key():
        print(">>> Accepte la demande d'appairage sur la télé (60 s)...")
    await client.connect()
    if client.client_key != load_key():
        KEY_FILE.write_text(json.dumps({"client_key": client.client_key}))
        KEY_FILE.chmod(0o600)
        print(f"Clé d'appairage enregistrée dans {KEY_FILE}")
    return client


async def try_request(client, uri, payload=None):
    """Renvoie (payload, None) ou (None, message d'erreur)."""
    try:
        return await client.request(uri, payload), None
    except Exception as err:  # noqa: BLE001 - on veut tout rapporter
        return None, f"{type(err).__name__}: {err}"


async def read_settings(client, category, keys):
    values, errors = {}, {}
    for key in keys:
        res, err = await try_request(client, SETTINGS_URI, {"category": category, "keys": [key]})
        if res and key in res.get("settings", {}):
            values[key] = res["settings"][key]
        else:
            errors[key] = err or "clé absente de la réponse"
    return values, errors


async def write_setting(client, category, key, value):
    return await try_request(client, SET_SETTINGS_URI, {"category": category, "settings": {key: value}})


def ask(question):
    return input(f"{question} [o/N] ").strip().lower() in ("o", "oui", "y", "yes")


def timestamp():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


async def screenshot(client, label):
    """Tente ssap://tv/executeOneShot. Renvoie le chemin du fichier ou None."""
    res, err = await try_request(client, "tv/executeOneShot", {"path": "/tmp/capture.jpg", "method": "DISPLAY", "format": "JPG"})
    if not res or "imageUri" not in res:
        print(f"Capture d'écran impossible ({err or res}). Vérifie à l'œil sur la télé.")
        return None
    import urllib.request
    out = BACKUP_DIR / f"capture-{label}-{timestamp()}.jpg"
    try:
        urllib.request.urlretrieve(res["imageUri"], out)
    except Exception as e:  # noqa: BLE001
        print(f"Capture créée sur la télé mais non téléchargeable : {e}")
        return None
    print(f"Capture : {out}")
    return out


def run(coro):
    try:
        asyncio.run(coro)
    except KeyboardInterrupt:
        sys.exit(1)
