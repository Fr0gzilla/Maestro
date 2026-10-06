# Extraits de code

Des pièces choisies du code de Maestro, **adaptées pour la publication** : les noms d'outils, de dossiers et de
variables sont simplifiés, les chemins de la machine retirés. La logique est celle du système en service, et chaque
extrait s'exécute seul — les démonstrations travaillent dans un dossier temporaire.

| Fichier | Langage | Ce qu'il montre |
|---|---|---|
| [`controle-des-processus.sh`](controle-des-processus.sh) | Bash | ne jamais croire un numéro de processus lu dans un fichier : « -1 » passé à `kill` viserait tous les processus du compte |
| [`ecriture-atomique-du-plan.sh`](ecriture-atomique-du-plan.sh) | Bash | un fichier d'état qui ne se corrompt pas : écriture atomique, refus d'un plan tronqué, champs et identifiants contrôlés |
| [`registre-des-travaux.py`](registre-des-travaux.py) | Python | le registre des travaux longs affichés par les interfaces ; une entrée dont le processus est mort disparaît seule |
| [`deverrouillage-ecran.py`](deverrouillage-ecran.py) | Python | le code de l'écran de contrôle : empreinte scrypt, comparaison en temps constant, attente croissante, journal |
| [`modele-de-cout.py`](modele-de-cout.py) | Python | le coût quadratique d'une session d'agent, et pourquoi découper le travail |
| [`protocole-d-un-chef.md`](protocole-d-un-chef.md) | JavaScript et texte généré | le protocole de verdict écrit une fois et généré dans les quatre chefs, avec l'incident à l'origine de chaque règle |

## Les essayer

```bash
bash ecriture-atomique-du-plan.sh demo        # une mise à jour acceptée, trois tentatives refusées
python3 deverrouillage-ecran.py               # cinq codes faux, l'attente, puis l'ouverture
python3 modele-de-cout.py                     # 16 étapes en 1, 2 ou 4 sessions
python3 modele-de-cout.py 8500 11200 13900    # estimer c0 et g à partir de contextes mesurés
```

Ces extraits illustrent la revue ; ils ne constituent pas le code complet de Maestro, qui reste privé.
