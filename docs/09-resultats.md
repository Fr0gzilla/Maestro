# 9. Les résultats

> Ce qui a été livré, ce que les mesures disent, ce qui a échoué en route — et ce que chaque échec a changé.

[← 8. Les interfaces](08-interfaces.md) · [Sommaire](../README.md) · [Chronologie →](chronologie.md)

---

## En chiffres

| | |
|---|---:|
| Agents définis | **70** (1 orchestrateur, 4 chefs, 32 ouvriers, 32 jumeaux, 1 rétrospective) |
| Compétences métier | **49** |
| Outils déterministes « zéro token » | **une trentaine** |
| Tests de fumée, dont les attaques rejouées | **398** |
| Vérifications automatiques de permissions | **17 674** |
| Projets menés jusqu'au bout | **3** |
| `/projet` avant → après optimisation | **46 min → 3 min 12 s** |
| Même application, avant → après optimisation | **− 50 % de temps, − 46 % de tokens relus** |
| Redémarrage à froid, tous services revenus | **46 s** |

## Les projets livrés

### Une application web d'inscription et de connexion

PHP, MySQL, Docker. Le premier run complet, de nuit, depuis le seul cahier des charges : modélisation, socle,
pages, tests, Docker, audit de sécurité, correctifs, re-audit.

- **Sept tâches sur sept**, de 18 h 55 à 2 h 31 (dont une heure d'interruptions et de relances).
- Quatre relances sur une même tâche, **chacune pour une cause différente, chacune corrigée à la racine** (limite
  d'étapes, dossier temporaire refusé, juge en boucle, citation mal lue par un contrôle).
- L'audit du groupe cybersécurité a trouvé 3 points moyens et 8 faibles ; l'orchestrateur a créé de lui-même une
  tâche de correctifs pour le groupe dev ; le re-audit a conclu à 0 critique, 0 haute, 0 moyenne.

### La même application, refaite après optimisation

Même cahier des charges, projet neuf, tous les correctifs de la nuit en place. Puis, le matin, la **première
recette Docker réelle** : l'application construite, démarrée et parcourue (inscription → connexion → tableau de bord
→ déconnexion) en **45 secondes**, dans la zone de recette.

| À cahier des charges identique | Premier run | Après optimisation | Écart |
|---|---:|---:|---:|
| Temps des tâches | 455 min | 226 min | **− 50 %** |
| Appels de modèle | 1 003 | 686 | **− 32 %** |
| Tokens relus (hors cache) | 2,6 M | 1,9 M | − 27 % |
| Tokens relus (en cache) | 29,2 M | 15,2 M | **− 48 %** |
| Tokens relus (total) | 31,8 M | 17,1 M | **− 46 %** |
| Tokens de raisonnement | 606 k | 384 k | − 37 % |
| Relances | 4 | **0** | |
| Arbitrages humains | 2 | **0** | |

Pendant ce second run, la maintenance de 4 h est passée en vrai, avec un redémarrage de la machine : le run s'est
arrêté proprement entre deux tâches et a repris seul après.

### Le tableau de bord de Maestro

Le premier vrai projet : le tableau de bord web de Maestro, construit par ses propres agents. **Onze tâches sur
onze**, audit de sécurité arbitré (2 correctifs, 2 points sans objet), **recette Docker OK**, en service depuis. Voir
[Les interfaces](08-interfaces.md#le-tableau-de-bord-web).

### En préparation : une application existante, reprise par les quatre groupes

Une application Flask existante, réécrite par les quatre groupes à partir d'un cahier des charges de 966 lignes tiré
du code d'origine : un plan de 17 tâches (modélisation, développement, audit, documentation de cours, recette). Le
premier projet à mobiliser **tous** les métiers de Maestro.

## Ce qui a échoué, et ce que chaque échec a changé

| Incident | Cause | Ce qui a changé |
|---|---|---|
| L'orchestrateur s'arrête seul en plein run | un appel d'outil ne peut pas dépasser une heure ; une tâche en a pris 75 min | les chefs tournent en arrière-plan, l'orchestrateur les attend par tranches de 50 min |
| Un juge répète la même ligne 1 274 fois | boucle de raisonnement jusqu'au plafond du fournisseur : 32 000 tokens, 10 minutes, aucun verdict | sortie de ce modèle plafonnée à 12 000 tokens ; une réponse vide est relancée une fois en version courte |
| Toutes les tâches bloquées en même temps | limite de débit sur le modèle des juges, alors que chaque tâche passe par un juge | jumeaux de secours pour tous les ouvriers, chez un autre fournisseur |
| Un ouvrier fait `git stash` | le plan et le journal du run disparaissent plusieurs minutes | l'état du dépôt est réservé à l'orchestrateur |
| Un ouvrier figé 34 minutes | panne muette d'un fournisseur : ni réponse, ni erreur | la garde interrompt toute requête muette depuis 12 min ; le chef appelle le jumeau |
| Une limite d'usage épuisée en une heure | tous les postes basculés sur le modèle des chefs pendant une panne | ce modèle est réservé aux chefs ; outil de bascule poste par poste |
| Un commit bloqué par le scan des secrets | un mot de passe factice dans un test (« MauvaisMotDePasse!9 ») | un faux positif se prouve selon des critères stricts, il ne se déclare pas |
| Une tâche de 3 h 15 | une boucle de corrections : 22,9 M tokens relus | budget par tâche (durée et tokens), puis bilan |
| Deux tâches bloquées, travail pourtant fait | réponse d'ouvrier hors format | relance courte, puis jugement sur pièces |
| Des mesures en retard de plusieurs minutes | la base des sessions lue sans son journal d'écriture | lecture seule normale partout ; les mesures douteuses ont été refaites |
| La garde batterie inactive toute une nuit | un fichier de minuterie vide après une réinstallation | l'installateur refuse une unité vide ; la maintenance vérifie ses propres minuteries |
| Des services installés en root | une erreur d'installation (commande lancée avec `sudo`) | l'installateur et chaque service refusent root |
| L'intégration continue rouge 19 h sans que personne le voie | un contrôle lisait des fichiers compilés | correction, et un outil qui lit l'état de l'intégration continue |

## Les leçons

1. **Une contrainte vaut mieux qu'une consigne.** Ce que la configuration impose est suivi ; ce qu'on demande à un
   modèle léger l'est rarement.
2. **Le coût d'un agent est quadratique en nombre d'étapes.** Des sessions courtes et des lots découpés valent plus
   que des prompts raccourcis.
3. **Le mécanique doit sortir des modèles.** Chaque script a remplacé des dizaines d'appels et supprimé une classe
   d'erreurs.
4. **Le format de sortie est un point de fragilité** : un protocole robuste tolère l'écart et juge sur pièces.
5. **Chaque modèle est un point de panne.** La disponibilité passe avant l'élégance : jumeaux, sondes, bascule.
6. **Les fichiers sont le meilleur bus entre agents** : ils se relisent, se versionnent, se vérifient, et rendent tout
   reprenable.
7. **Tout ce qu'écrit un agent est une donnée non fiable** — y compris la configuration d'un dépôt Git.
8. **La résilience s'éprouve, elle ne se suppose pas** : chaque reprise a été provoquée volontairement avant d'être
   considérée comme acquise.
9. **Les outils de mesure se trompent aussi** : une mesure surprenante se vérifie avant de décider.
10. **L'humain est la ressource la plus rare** : ne le solliciter que lorsque rien n'avance sans lui.

## La suite

- Publier les résultats de la campagne économie/puissance et ne garder que les réglages qui ne coûtent rien en qualité.
- Mener le projet à quatre groupes, et mesurer sur une vraie fonctionnalité les économies de la deuxième série.
- Exercer les chemins jamais empruntés : une recette en échec renvoyée au groupe dev, une coupure réseau de toute la
  machine, une batterie qui se vide pour de vrai.
- Isoler davantage : un conteneur par projet pour un projet non fiable.

---

[← 8. Les interfaces](08-interfaces.md) · [Sommaire](../README.md) · [Chronologie →](chronologie.md)
