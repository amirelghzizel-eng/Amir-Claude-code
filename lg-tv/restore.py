"""Étape 6 : remet les réglages de la sauvegarde (par défaut backup-latest.json).

Usage : python3 restore.py [--dry-run] [--yes] [fichier.json]
"""
import json
import sys

from lgcommon import BACKUP_DIR, ask, connect, read_settings, run, write_setting


def diff(saved, current):
    """Liste (catégorie, clé, actuel, sauvegardé) des réglages qui diffèrent."""
    return [
        (cat, key, current.get(cat, {}).get(key), val)
        for cat, values in saved.items()
        for key, val in values.items()
        if current.get(cat, {}).get(key) != val
    ]


async def restore(client, saved, dry_run=False, assume_yes=False):
    current = {}
    for cat, values in saved.items():
        current[cat], _ = await read_settings(client, cat, list(values))
    changes = diff(saved, current)
    if not changes:
        print("Rien à restaurer : tout est identique à la sauvegarde.")
        return []
    for cat, key, now, old in changes:
        print(f"  {cat}/{key} : {now!r} -> {old!r}")
    if dry_run or not (assume_yes or ask(f"Restaurer ces {len(changes)} réglages ?")):
        return changes
    failed = []
    # pictureMode d'abord : les autres réglages image dépendent du mode.
    for cat, key, _, old in sorted(changes, key=lambda c: c[1] != "pictureMode"):
        _, err = await write_setting(client, cat, key, old)
        print(f"  {cat}/{key} = {old!r} : {'OK' if not err else 'ÉCHEC ' + err}")
        if err:
            failed.append((cat, key))
    if failed:
        print("À remettre à la main via les menus :", ", ".join(f"{c}/{k}" for c, k in failed))
    return changes


async def main(args):
    path = next((a for a in args if not a.startswith("--")), BACKUP_DIR / "backup-latest.json")
    saved = json.loads(open(path, encoding="utf-8").read())["settings"]
    client = await connect()
    await restore(client, saved, "--dry-run" in args, "--yes" in args)
    await client.disconnect()

if __name__ == "__main__":
    run(main(sys.argv[1:]))
