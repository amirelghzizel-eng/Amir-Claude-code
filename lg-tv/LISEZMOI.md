# LG 43LH570U (webOS 3) — boîte à outils SSAP

À lancer **sur le Mac** (même Wi-Fi que la télé) :

```bash
mkdir -p ~/Documents/LG-backup && cp *.py ~/Documents/LG-backup/ && cd ~/Documents/LG-backup
python3 -m venv .venv && source .venv/bin/activate && pip install aiowebostv
python3 backup.py          # appairage (accepte sur la télé) + sauvegarde JSON + test capture
python3 test_restore.py    # test hors-ligne de la restauration
python3 restore.py --dry-run   # montre ce qui serait remis, sans rien écrire
```

La clé d'appairage est dans `~/Documents/LG-backup/client_key.json` (droits 600).

## Couleurs — un réglage par commande (chacune demande confirmation et propose d'annuler)

Lis d'abord les valeurs exactes dans `backup-latest.json` (format variable selon le firmware).

```bash
python3 apply.py picture pictureMode cinema      # ou expert1
python3 apply.py picture energySaving off
python3 apply.py picture dynamicColor off
python3 apply.py picture colorTemperature <val>  # voir ci-dessous
```

Si la télé répond « 401 / insufficient permissions », webOS 3 interdit l'écriture via SSAP : passe par les menus.

**Menus (télécommande : bouton ⚙ Réglages → ⋮ Tous les réglages)**
1. Image → Mode image → **Cinéma** (ou Expert (pièce lumineuse)).
2. Image → Économie d'énergie → **Arrêt**.
3. Image → Mode image → Réglages avancés → Couleur → **Température de couleur : Chaud 2** (ou W50 sur le curseur).
4. Même menu Couleur → **Couleur dynamique : Arrêt** ; Gamme de couleur : **Standard** (si présent).
5. Contraste dynamique : Arrêt (évite les virages de teinte).

## Pubs et télémétrie

Via SSAP, webOS 3 n'expose pas de réglage officiel pour ça (seules des clés non documentées
comme `homePromotion` peuvent exister ; `backup.py` indique si elles sont lisibles). Menus :

1. Réglages → Tous les réglages → Général → À propos de ce téléviseur → **Accords utilisateur** :
   décoche « Publicités ciblées / Viewing Information / Voice Information » (garde l'accord de base
   si tu veux conserver les applis).
2. Général → **LG Live Plus** (ou « Live Plus ») → **Arrêt** (reconnaissance de contenu ACR).
3. Général → **Promotion de l'accueil** / « Home Promotion » → **Arrêt** (bannières de l'accueil).
4. Général → Paramètres de la page d'accueil (si présent) → désactive « Contenu recommandé ».
5. Option facultative : Général → Lancement auto de l'accueil → Arrêt.

## Restauration

```bash
python3 restore.py                 # compare, liste, demande confirmation, réécrit
python3 restore.py backup-XXXX.json
```
Les réglages refusés par la télé sont listés pour être remis à la main.
