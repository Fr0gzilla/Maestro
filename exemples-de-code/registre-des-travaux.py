#!/usr/bin/env python3
"""registre-des-travaux.py — extrait adapté de l'outil « travaux » de Maestro.

Le registre des travaux longs (une campagne de mesure, un essai de nuit…) qui alimente les encadrés « en cours » du
terminal Maestro et de l'écran du PC. Un travail s'y inscrit lui-même, met à jour son avancement et sa fin estimée,
puis s'en retire ; une entrée dont le processus est mort disparaît d'elle-même à la lecture — un travail planté ne
reste jamais affiché « en cours ».

Choix notables : un fichier JSON par travail, écrit de façon atomique (fichier temporaire puis os.replace), en mode
600, dans un dossier de l'hôte jamais monté chez les agents ; des identifiants contraints par une expression ancrée.

usage : registre-des-travaux.py debut <id> "<quoi>" [--debut HH:MM|epoch] [--fin HH:MM|epoch] [--avancement x/y] [--pid n]
        registre-des-travaux.py maj <id> [--quoi "…"] [--fin HH:MM|epoch] [--avancement x/y]
        registre-des-travaux.py fin <id>
        registre-des-travaux.py liste            les travaux vivants, un objet JSON par ligne (les morts sont retirés)
--pid : le processus du travail (par défaut, celui qui appelle) ; --debut : maintenant par défaut.
codes : 0 ok · 2 usage · 5 travail inconnu
"""
import json, os, re, sys, time
from datetime import datetime, timedelta

DOSSIER = os.path.join(os.environ.get("MAESTRO_HOTE", os.path.expanduser("~/.maestro")), "travaux")


def usage(code=2):
    print(__doc__.split("\n\n", 2)[2].rstrip(), file=sys.stderr)
    sys.exit(code)


def instant(v):
    """HH:MM (aujourd'hui, ou demain si l'heure est passée) ou secondes depuis l'époque"""
    if re.fullmatch(r"\d{9,11}", v): return int(v)
    m = re.fullmatch(r"([01]?\d|2[0-3]):([0-5]\d)", v)
    if not m: usage()
    t = datetime.now().replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0, microsecond=0)
    if t.timestamp() < time.time() - 60: t += timedelta(days=1)
    return int(t.timestamp())


def chemin(ident):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,40}", ident): usage()      # ni « / », ni « .. », ni majuscules
    return os.path.join(DOSSIER, ident + ".json")


def ecrire(ident, entree):
    os.makedirs(DOSSIER, mode=0o700, exist_ok=True)
    tmp = chemin(ident) + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f: json.dump(entree, f, ensure_ascii=False)
    os.replace(tmp, chemin(ident))                                         # atomique : jamais d'entrée à moitié écrite


def vivant(pid):
    try:
        os.kill(int(pid), 0); return int(pid) > 1
    except (OSError, ValueError, TypeError):
        return False


def options(args):
    o, i = {}, 0
    while i < len(args):
        if args[i] not in ("--debut", "--fin", "--avancement", "--pid", "--quoi") or i + 1 >= len(args): usage()
        o[args[i][2:]] = args[i + 1]; i += 2
    if "avancement" in o and not re.fullmatch(r"\d+/\d+", o["avancement"]): usage()
    if "pid" in o and not o["pid"].isdigit(): usage()
    return o


def main(a):
    if not a: usage()
    cmd = a[0]
    if cmd == "debut" and len(a) >= 3:
        o = options(a[3:])
        e = {"id": a[1], "quoi": a[2][:120], "debut": instant(o["debut"]) if "debut" in o else int(time.time()),
             "pid": int(o.get("pid") or os.getppid())}
        if "fin" in o: e["fin"] = instant(o["fin"])
        if "avancement" in o: e["avancement"] = o["avancement"]
        ecrire(a[1], e)
    elif cmd == "maj" and len(a) >= 2:
        try: e = json.load(open(chemin(a[1]), encoding="utf-8"))
        except (OSError, ValueError): sys.exit(5)
        o = options(a[2:])
        if "quoi" in o: e["quoi"] = o["quoi"][:120]
        if "fin" in o: e["fin"] = instant(o["fin"])
        if "avancement" in o: e["avancement"] = o["avancement"]
        ecrire(a[1], e)
    elif cmd == "fin" and len(a) == 2:
        try: os.remove(chemin(a[1]))
        except OSError: pass
    elif cmd == "liste" and len(a) == 1:
        try: noms = sorted(os.listdir(DOSSIER))
        except OSError: noms = []
        for n in noms:
            if not n.endswith(".json"): continue
            p = os.path.join(DOSSIER, n)
            try: e = json.load(open(p, encoding="utf-8"))
            except (OSError, ValueError): continue
            if vivant(e.get("pid")): print(json.dumps(e, ensure_ascii=False))
            else:                                                          # processus mort : l'entrée disparaît
                try: os.remove(p)
                except OSError: pass
    else: usage()


if __name__ == "__main__":
    main(sys.argv[1:])
