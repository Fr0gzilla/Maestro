# 8. Les interfaces

> Un système qui travaille seul doit se lire en un coup d'œil. Trois surfaces, une même identité : le terminal
> Maestro pour converser, l'écran du PC pour veiller, le tableau de bord pour consulter — et Frogzilla pour donner le
> ton.

[← 7. L'exploitation](07-exploitation.md) · [Sommaire](../README.md) · [9. Les résultats →](09-resultats.md)

---

## Le terminal Maestro

<p align="center">
  <img src="../assets/maestro-accueil.png" alt="L'accueil du terminal Maestro : logo, Frogzilla, un encadré par travail en cours" width="760">
</p>

Le point d'entrée de l'opérateur : une interface de conversation écrite en Python, **sans aucune dépendance**, qui
fait de Claude Code un moteur invisible (flux d'événements en continu, session propre à l'interface). Rien ne
s'interpose entre l'opérateur et l'orchestrateur, mais tout est mis en forme.

- **L'accueil** : le logo en relief (dégradé champagne → bronze, reflet animé), « by Fr0gzilla », et **un encadré par
  travail en cours** — son nom, son avancement, son heure de lancement ou de départ prévu, sa fin estimée et une
  barre de progression. Les travaux longs s'inscrivent eux-mêmes dans un registre ([extrait](../exemples-de-code/registre-des-travaux.py)).
- **Un projet ouvert** : sa carte (pastille d'état, barre de progression, heure du dernier événement), puis le plan
  tâche par tâche sur `/statut`.
- **Les réponses en flux**, avec un rendu Markdown dans le terminal : titres, tableaux alignés, blocs de code, listes.
  Les actions de l'orchestrateur sont repliées (`/détail` les montre).
- **Les événements du run annoncés d'eux-mêmes**, par lecture du journal du projet.
- **Des commandes locales à zéro token** : `/statut`, `/journal`, `/tokens`, `/pause`, `/nuit`, `/projet`,
  `/travaux`, `/theme` — aucune ne réveille un modèle.
- **Un thème clair ou sombre**, détecté en interrogeant le terminal sur sa couleur de fond.
- **Des garde-fous** : l'interface refuse de lancer un run dans un projet où un run automatique tourne déjà.

<p align="center">
  <img src="../assets/maestro-projet.png" alt="Un projet ouvert dans le terminal Maestro : sa carte et son plan de onze tâches, toutes faites" width="760"><br>
  <sub>Le projet du tableau de bord, onze tâches sur onze : chaque ligne est une tâche du plan, avec son groupe</sub>
</p>

## L'écran du PC dédié

<p align="center">
  <img src="../assets/ecran-du-pc.png" alt="L'écran de contrôle du PC dédié : le logo, Frogzilla, la date, l'état du serveur et les travaux en cours" width="820">
</p>

Le portable qui héberge Maestro affiche **en permanence** une animation : le logo et son reflet, Frogzilla, la date et
l'heure, l'état du serveur des agents, les travaux en cours — et une fête quand une tâche est validée. **Le code de
l'opérateur, puis Entrée, ouvre un terminal.**

- **Un kiosque** : un compositeur Wayland qui n'affiche qu'une application, un terminal léger sans aucun raccourci qui
  ouvre, lance ou colle quoi que ce soit, la police JetBrains Mono.
- **Une session automatique** sur la première console, qui ne lance que l'écran : s'il s'arrête, la session se ferme
  et repart — jamais de terminal sans le code.
- **Un code jamais stocké en clair** (empreinte scrypt), des essais limités et journalisés, un retour à l'écran après
  quinze minutes sans frappe ([extrait](../exemples-de-code/deverrouillage-ecran.py)).
- **Un écran qui dure** : le contenu se décale de quelques pixels toutes les dix minutes, pour ne marquer aucune dalle.

## Le tableau de bord web

<p align="center">
  <img src="../assets/tableau-de-bord.png" alt="Le tableau de bord web : le plan d'un projet, le graphe de ses dépendances et ses onze tâches" width="760">
</p>

Le premier vrai projet confié à Maestro a été **son propre tableau de bord** : un cahier des charges de 128 lignes,
un plan de onze tâches, mené par les agents puis audité par le groupe cybersécurité et recetté dans Docker. La couche
d'interface a été reprise à la main en cours de route, après relecture page par page : les agents avaient livré une
version fonctionnelle mais inégale (styles manquants, une page en erreur), et la règle reste qu'un livrable n'est
accepté que s'il est réellement utilisable.

- **Ce qu'il montre** : la liste des projets et leur état, le plan de chaque projet avec le **graphe de ses
  dépendances**, les runs en cours, le journal filtrable, les consignes, les rapports, l'audit, la recette, l'usage des
  modèles et les alertes du serveur — et un **dialogue avec Maestro** par une file de messages.
- **Comment il est fait** : PHP sans framework ; rendu **côté serveur, sans bibliothèque** — le Markdown est échappé
  d'abord, puis seule une liste fermée de balises est rétablie, et seuls les liens `http`, `https` et `mailto` passent ;
  le graphe des dépendances est dessiné en SVG ; une politique de sécurité de contenu stricte, sans script en ligne.
- **Comment il tourne** : un conteneur en lecture seule, sans aucune capacité Linux, sous un utilisateur non
  privilégié ; les projets montés en lecture seule ; un accès par mot de passe, limité en nombre d'essais, sur le
  réseau privé uniquement.
- **Ce qui a été vérifié** : 28 tests d'interface, des pages relues à 1 280 et à 400 pixels de large, en thème sombre et
  clair ; un rendu Markdown passé au fuzzing (6 millions de cas, aucune faille XSS).

## Frogzilla

<p align="center">
  <img src="../assets/frogzilla-humeurs.png" alt="Frogzilla dans ses six humeurs : repos, dirige, dort, alarme, salue, fête" width="820">
</p>

La mascotte de Maestro, en art pixel dans le terminal comme sur l'écran du PC. Son humeur suit l'état du système, ce
qui permet de le lire de loin :

| Humeur | Quand |
|---|---|
| **repos** | des tâches attendent, aucun chef ne travaille |
| **dirige** | un chef est au travail |
| **dort** | le serveur des agents est arrêté |
| **alarme** | une tâche est bloquée et attend un arbitrage |
| **salue** | le plan est terminé |
| **fête** | une tâche vient d'être validée |

Une mini-Frogzilla sert aussi d'indicateur d'attente pendant que Maestro réfléchit. Le dessin est isolé derrière une
petite interface (une image par instant et par humeur) : la mascotte peut être remplacée sans toucher au reste.

---

[← 7. L'exploitation](07-exploitation.md) · [Sommaire](../README.md) · [9. Les résultats →](09-resultats.md)
