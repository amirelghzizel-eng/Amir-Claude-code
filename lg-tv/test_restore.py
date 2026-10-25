"""Test hors-ligne de restore.py avec une fausse télé (aucune connexion réseau)."""
import asyncio

import restore


class FakeTV:
    def __init__(self, state, refuse=()):
        self.state, self.refuse = state, set(refuse)

    async def request(self, uri, payload=None):
        cat = payload["category"]
        if uri.endswith("getSystemSettings"):
            return {"returnValue": True, "settings": {k: self.state[cat][k] for k in payload["keys"] if k in self.state[cat]}}
        for k, v in payload["settings"].items():
            if k in self.refuse:
                raise PermissionError("401 insufficient permissions")
            self.state[cat][k] = v
        return {"returnValue": True}


saved = {"picture": {"pictureMode": "vivid", "colorTemperature": 0, "energySaving": "auto"}, "sound": {"soundMode": "standard"}}
tv = FakeTV({"picture": {"pictureMode": "cinema", "colorTemperature": 40, "energySaving": "off"}, "sound": {"soundMode": "standard"}}, refuse={"energySaving"})
assert len(asyncio.run(restore.restore(tv, saved, dry_run=True))) == 3
assert tv.state["picture"]["pictureMode"] == "cinema", "dry-run ne doit rien écrire"
asyncio.run(restore.restore(tv, saved, assume_yes=True))
assert tv.state["picture"] == {"pictureMode": "vivid", "colorTemperature": 0, "energySaving": "off"}
assert asyncio.run(restore.restore(FakeTV({"picture": dict(saved["picture"]), "sound": dict(saved["sound"])}), saved)) == []
print("test_restore : OK")
