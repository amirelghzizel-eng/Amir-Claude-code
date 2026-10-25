"""Étape 4 : applique UN réglage, après confirmation, puis vérifie et propose d'annuler.

Usage : python3 apply.py <catégorie> <clé> <valeur>
  ex.   python3 apply.py picture pictureMode cinema
"""
import json
import sys

from lgcommon import ask, connect, read_settings, run, screenshot, write_setting


def parse(value):
    try:
        return json.loads(value)  # nombres
    except json.JSONDecodeError:
        return value


async def main(category, key, value):
    client = await connect()
    before, err = await read_settings(client, category, [key])
    if key not in before:
        print(f"Impossible de lire {category}/{key} : {err.get(key)}")
        if not ask("Tenter l'écriture quand même ?"):
            return await client.disconnect()
    print(f"{category}/{key} : actuel = {before.get(key)!r} -> proposé = {value!r}")
    if not ask("Appliquer ce changement ?"):
        return await client.disconnect()
    res, err = await write_setting(client, category, key, value)
    if err:
        print(f"Refusé par la télé : {err}\n=> à faire via les menus.")
        return await client.disconnect()
    after, _ = await read_settings(client, category, [key])
    print(f"Relu après écriture : {after.get(key)!r}")
    await screenshot(client, f"{category}-{key}")
    if key in before and not ask("Le résultat te convient (sinon je remets l'ancienne valeur) ?"):
        await write_setting(client, category, key, before[key])
        print(f"Remis à {before[key]!r}")
    await client.disconnect()

if len(sys.argv) != 4:
    sys.exit(__doc__)
run(main(sys.argv[1], sys.argv[2], parse(sys.argv[3])))
