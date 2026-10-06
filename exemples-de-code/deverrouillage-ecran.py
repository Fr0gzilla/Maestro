#!/usr/bin/env python3
"""deverrouillage-ecran.py — extrait adapté de l'écran de contrôle de Maestro : le code qui ouvre un terminal.

L'écran du PC dédié affiche en permanence une animation ; le code de l'opérateur, puis Entrée, ouvre un terminal.
Ce code n'est jamais conservé en clair :
  - seule son empreinte est écrite — scrypt (n = 2^14, r = 8, p = 1) avec un sel aléatoire de 16 octets ; PBKDF2-SHA256
    à 600 000 tours si scrypt manque, et l'algorithme est noté avec l'empreinte : la vérification ne se rabat jamais
    sur plus faible que ce qui a été enregistré ;
  - la comparaison se fait en temps constant (hmac.compare_digest) ;
  - cinq codes faux de suite imposent une attente d'une minute, doublée à chaque nouvelle série, une heure au plus ;
  - chaque tentative est journalisée ; les fichiers sont en mode 600, dans un dossier de l'hôte.
Le code se choisit sur la machine elle-même, saisi deux fois sans écho : il ne passe jamais par une conversation.

démonstration, dans un dossier temporaire : python3 deverrouillage-ecran.py
"""
import hashlib, hmac, json, os, sys, tempfile, time
from datetime import datetime

HOTE = os.environ.get("MAESTRO_HOTE", os.path.expanduser("~/.maestro"))


def fichiers():
    return (os.path.join(HOTE, "ecran.code"), os.path.join(HOTE, "ecran.etat"), os.path.join(HOTE, "ecran.log"))


def ecrire_prive(chemin, texte):
    os.makedirs(os.path.dirname(chemin), mode=0o700, exist_ok=True)
    tmp = chemin + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f: f.write(texte)
    os.replace(tmp, chemin)


def empreinte(code, sel, algo="scrypt"):
    """None si l'algorithme enregistré n'est pas disponible ici : la vérification échoue alors, sans se rabattre"""
    if algo == "scrypt":
        return hashlib.scrypt(code.encode("utf-8"), salt=sel, n=2 ** 14, r=8, p=1, dklen=32) if hasattr(hashlib, "scrypt") else None
    if algo == "pbkdf2":
        return hashlib.pbkdf2_hmac("sha256", code.encode("utf-8"), sel, 600_000)
    return None


def noter(quoi):
    try:
        os.makedirs(HOTE, mode=0o700, exist_ok=True)
        fd = os.open(fichiers()[2], os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(fd, "a", encoding="utf-8") as f: f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {quoi}\n")
    except OSError:
        pass


def enregistrer_code(code):
    """dans le vrai outil, le code est saisi deux fois sans écho (getpass) ; ici, passé en argument pour la démonstration"""
    if len(code) < 6: raise ValueError("6 caractères au moins")
    sel, algo = os.urandom(16), ("scrypt" if hasattr(hashlib, "scrypt") else "pbkdf2")
    ecrire_prive(fichiers()[0], json.dumps({"algo": algo, "sel": sel.hex(), "empreinte": empreinte(code, sel, algo).hex()}))
    noter("code changé")


def code_juste(code):
    try:
        c = json.load(open(fichiers()[0], encoding="utf-8"))
        e = empreinte(code, bytes.fromhex(c["sel"]), c.get("algo", "scrypt"))
        return e is not None and hmac.compare_digest(e, bytes.fromhex(c["empreinte"]))
    except (OSError, ValueError, KeyError, TypeError):
        return False


def tentative(code):
    """« ok », « non », ou « attente:<secondes> » — l'attente est vérifiée AVANT le code : pendant une attente, même
    le bon code est refusé, sinon l'attente ne ralentirait pas une recherche exhaustive"""
    try: e = json.load(open(fichiers()[1], encoding="utf-8"))
    except (OSError, ValueError): e = {}
    maintenant = time.time()
    if e.get("jusqu_a", 0) > maintenant: return f"attente:{int(e['jusqu_a'] - maintenant) + 1}"
    if code_juste(code):
        ecrire_prive(fichiers()[1], json.dumps({"echecs": 0, "series": 0, "jusqu_a": 0})); noter("terminal ouvert")
        return "ok"
    e["echecs"] = int(e.get("echecs", 0)) + 1
    if e["echecs"] >= 5:
        e["series"] = int(e.get("series", 0)) + 1; e["echecs"] = 0
        e["jusqu_a"] = maintenant + min(3600, 60 * 2 ** (e["series"] - 1))
        noter(f"5 codes faux de suite : attente de {int(e['jusqu_a'] - maintenant)} s")
    else:
        noter("code faux")
    ecrire_prive(fichiers()[1], json.dumps(e))
    return "non"


if __name__ == "__main__":
    HOTE = tempfile.mkdtemp(prefix="ecran-demo-")
    enregistrer_code("un-code-de-demonstration")
    print("enregistré :", open(fichiers()[0]).read()[:72] + "…")
    for i in range(1, 6): print(f"code faux n° {i} :", tentative("123456"))
    print("bon code, pendant l'attente :", tentative("un-code-de-demonstration"))
    ecrire_prive(fichiers()[1], json.dumps({**json.load(open(fichiers()[1])), "jusqu_a": 0}))   # on simule la fin de l'attente
    print("bon code, après l'attente :", tentative("un-code-de-demonstration"))
    print("journal :"); sys.stdout.write("".join("  " + l for l in open(fichiers()[2])))
