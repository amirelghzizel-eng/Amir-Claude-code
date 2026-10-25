"""Étapes 1-3 : appairage, sauvegarde complète en JSON, test de capture d'écran."""
import json

from lgcommon import BACKUP_DIR, KEYS, connect, read_settings, run, screenshot, timestamp, try_request


async def main():
    client = await connect()
    data = {"date": timestamp(), "tv": "192.168.1.164"}
    for name, uri in {
        "software_info": "com.webos.service.update/getCurrentSWInformation",
        "system_info": "system/getSystemInfo",
        "launch_points": "com.webos.applicationManager/listLaunchPoints",
        "apps_all": "com.webos.applicationManager/listApps",
        "inputs": "tv/getExternalInputList",
        "volume": "audio/getVolume",
        "sound_output": "com.webos.service.apiadapter/audio/getSoundOutput",
    }.items():
        res, err = await try_request(client, uri)
        data[name] = res if res is not None else {"_erreur": err}
    data["settings"], data["unreadable"] = {}, {}
    for category, keys in KEYS.items():
        values, errors = await read_settings(client, category, keys)
        data["settings"][category] = values
        data["unreadable"][category] = errors
        print(f"{category:8} : {len(values)} lus, {len(errors)} illisibles")
    out = BACKUP_DIR / f"backup-{data['date']}.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    (BACKUP_DIR / "backup-latest.json").write_text(out.read_text())
    sw = data["software_info"]
    print(f"webOS : {sw.get('product_name', '?')} {sw.get('major_ver', '?')}.{sw.get('minor_ver', '?')}")
    print(f"Sauvegarde : {out}")
    await screenshot(client, "test")
    await client.disconnect()

run(main())
