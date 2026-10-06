# 1. Le besoin

> Passer de l'assistant qu'on tient par la main à une équipe qui mène un projet seule, en sécurité, et qui rend des
> comptes.

[← Sommaire](../README.md) · [2. La réflexion →](02-reflexion.md)

---

## Le point de départ

Quatre familles de travaux reviennent sans cesse : **développer** des applications web, **modéliser** des données et
des systèmes (Merise, UML), **réécrire et mettre en forme des cours**, **auditer la sécurité** d'un code ou d'une
configuration. Les assistants conversationnels aident tâche par tâche, mais ils demandent d'être pilotés en permanence :
copier, coller, relancer, vérifier, recommencer. Le temps humain part dans la coordination, pas dans les décisions.

L'idée de Maestro : **confier un cahier des charges le soir, retrouver le matin un livrable testé**, avec le compte
rendu de ce qui a été fait, de ce qui a coincé et de ce qui reste — sans avoir été réveillé pour rien.

## Les exigences fonctionnelles

| # | Exigence | Comment on saura qu'elle est tenue |
|---|---|---|
| F1 | Mener un projet de bout en bout : découpage, production, vérification, recette, compte rendu | un cahier des charges devient une application qui démarre pour de vrai, sans intervention |
| F2 | Couvrir quatre métiers : développement, modélisation, cours, cybersécurité défensive | chaque métier a son chef, ses ouvriers et ses compétences |
| F3 | Travailler sans surveillance, la nuit comprise | file de nuit, reprise après coupure, arrêt propre avant maintenance |
| F4 | Rendre compte à chaque niveau | statuts normalisés, journal, rapports, tableau de bord, notification quand rien n'avance sans l'humain |
| F5 | Se piloter de n'importe où | terminal à distance, tableau de bord web, réseau privé |
| F6 | Livrer dans Git, sous contrôle humain | une branche par run, une *pull request*, la fusion reste humaine |
| F7 | Apprendre de ses erreurs | une rétrospective écrit les leçons dans les compétences et la mémoire du projet |

## Les exigences de qualité

| Qualité | Formulation retenue |
|---|---|
| **Sécurité** | réduire le plus possible le risque d'attaque ; aucun secret en clair ni exposé ; rien de ce qu'écrit un agent ne s'exécute sur la machine hôte |
| **Sobriété** | consommer le moins de tokens possible sans perdre en qualité ; mesurer avant d'optimiser |
| **Fiabilité** | aucune boucle infinie ; la panne d'un fournisseur de modèles n'arrête pas le travail |
| **Traçabilité** | chaque décision est écrite : plan, journal, rapports, commits |
| **Testabilité** | chaque outil se teste sans modèle ; chaque permission d'agent est vérifiée automatiquement |
| **Lisibilité** | à tout moment, l'humain voit en un coup d'œil où en est chaque projet |

## Les contraintes

- **Un matériel modeste.** Un ordinateur portable d'entrée de gamme (Core i3, 8 Go de mémoire), dédié, allumé en
  permanence. Tout doit tenir dedans : agents, recette Docker, tableau de bord.
- **Un seul humain.** Il décide, arbitre et fusionne. Il ne doit être sollicité que lorsque rien n'avance sans lui.
- **Des modèles hétérogènes.** Des modèles ouverts, rapides mais inégaux, soumis à des limites de débit et à des
  plafonds d'usage ; un modèle plus solide dont l'usage est compté. Aucun ne doit devenir un point de panne unique.
- **Des outils avec leurs limites.** Un appel d'outil de l'orchestrateur ne peut pas durer plus d'une heure ; un
  agent n'a qu'un nombre fini d'étapes ; un modèle peut répondre à côté du format demandé.
- **Un cadre éthique pour la cybersécurité.** Défensif uniquement : son propre code, des laboratoires, des CTF.
  Rien d'actif sans périmètre écrit au préalable.
- **Pas de code confidentiel.** Les projets confiés sont des projets personnels ou d'apprentissage.

## Hors périmètre

- Remplacer le jugement humain : la fusion, les arbitrages et les secrets restent à l'humain.
- Naviguer sur le web : les agents n'ont pas d'outil de lecture de pages (c'est autant de surface d'injection en moins).
- Tester des cibles tierces.
- Le multi-utilisateur : Maestro sert une seule personne.

## Le critère de réussite

> *Un cahier des charges donné le soir ; le matin, une application qui démarre dans Docker, des tests verts, un audit
> de sécurité passé, une pull request à relire — et un compte rendu honnête de ce qui a coincé.*

Atteint entre la nuit du 4 au 5 octobre 2026 (sept tâches sur sept, puis la même application refaite deux fois plus
vite) et le matin du 5 (première recette Docker réelle) : voir [Les résultats](09-resultats.md).

---

[← Sommaire](../README.md) · [2. La réflexion →](02-reflexion.md)
