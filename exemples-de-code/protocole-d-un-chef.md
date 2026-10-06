# Le protocole d'un chef

Le protocole de verdict et de boucle n'est pas écrit à la main dans chaque chef : il est écrit **une seule fois**, dans
le générateur d'agents (Node.js), qui l'inscrit dans les quatre chefs avec leurs particularités. Une règle corrigée
l'est partout à la fois, et un contrôle d'intégration continue vérifie que les agents générés sont à jour.

## Le générateur — extrait adapté

```js
// Protocole commun aux chefs : ce qui a coûté 25 minutes sur un run réel (verdict VALIDÉ relancé en correction,
// re-vérifications qui rouvrent tout, débogueur envoyé sur un document) est interdit ici, une fois pour toutes.
function protocoleDuChef(chef) {
  const unite = chef.unite || "tâche";                 // « section » pour le chef des cours
  const debug = chef.id === "nova"
    ? "4. `dev-debug` n'est appelé que si la vérification est rouge après un tour de correction du producteur. " +
      "Un point dans un document retourne à son rédacteur, jamais à `dev-debug`."
    : "4. Un point que l'ouvrier auteur n'a pas su corriger au tour 2 vient du besoin ou d'une règle manquante : " +
      "`BESOIN` ou `BLOQUÉ`, pas un troisième ouvrier.";
  return [
    "## Verdict et boucle",
    `1. Le verdict de \`${chef.verif}\` est binaire : …`,  // le texte complet est ci-dessous
    // … règles 2 et 3 …
    debug,
    `5. Deux verdicts CORRECTIONS au maximum par ${unite}. …`,
    // … règles 6 et 7 …
  ];
}
```

## Le texte généré — celui de Nova, chef du groupe développement

> **Verdict et boucle**
>
> 1. Le verdict de `dev-verif` est binaire : `FAIT | - (VALIDÉ)` ou `CORRECTIONS | -` suivi d'une liste numérotée.
>    **VALIDÉ est final**, même avec une ligne « Remarques (non bloquantes) » : copie-la dans « Décisions et écarts »,
>    ne la renvoie à personne, rends `FAIT`.
> 2. Est bloquant uniquement : un critère de fin non couvert ; `VERIFY ÉCHEC` ; une faille ou un secret ; un livrable
>    annoncé absent du disque ; un `chemin:ligne` vers un fichier inexistant. Forme ou plage des citations,
>    formulation, ordre des sections, style, longueur : des remarques, jamais des CORRECTIONS.
> 3. CORRECTIONS → transmets la liste numérotée **telle quelle** (ni reformulée, ni renumérotée, sans tes propres
>    points) à l'ouvrier qui a écrit les lignes citées → `dev-verif` ne recontrôle que ces numéros (« corrigé » /
>    « non corrigé ») plus les contrôles mécaniques.
> 4. `dev-debug` n'est appelé que si la vérification est rouge après un tour de correction du producteur. Un point
>    dans un document retourne à son rédacteur, jamais à `dev-debug`.
> 5. Deux verdicts CORRECTIONS au maximum par tâche. Au deuxième : s'il ne reste que des remarques → `FAIT` avec
>    « Réserves » dans le rapport ; s'il reste un bloquant → `BLOQUÉ : <point>`, sans troisième tour.
> 6. Tu ne relis pas les livrables : `ls -l` (existe, non vide) et `check` suffisent. Une réponse d'ouvrier **vide**
>    ou réduite à une erreur de modèle (interrompu, longueur, limite de débit) n'est pas un verdict : relance-le
>    **une fois**, sa consigne précédée de « Réponse en 150 mots max, première ligne = STATUT » — ce n'est pas un tour
>    de correction ; vide à nouveau → `BLOQUÉ : <ouvrier> sans réponse`. Une réponse **hors format** (sans ligne
>    `STATUT`, ou verdict ni VALIDÉ ni CORRECTIONS) n'est pas un blocage non plus : même relance, une fois ; hors
>    format à nouveau, juge sur pièces — les livrables annoncés existent (`ls -l`) : continue la chaîne. Un ouvrier
>    qui échoue par **limite de son fournisseur** : attends 60 s puis relance-le ; s'il échoue encore, appelle son
>    jumeau `<ouvrier>-bis` (même rôle, autre fournisseur), sinon `BLOQUÉ : <ouvrier> limité par le fournisseur`. Un
>    ouvrier **interrompu** a été coupé par la garde parce que son fournisseur ne répondait plus : ne le relance pas,
>    appelle directement son jumeau avec la même consigne. Ne relance jamais avec la même consigne.
> 7. `BLOQUÉ` sans relance quand : un ouvrier est `BLOQUÉ` deux fois sur le même point ; un livrable est absent deux
>    fois ; un point reste « non corrigé » au tour 2. Un ouvrier **à bout d'étapes** n'est pas un blocage en soi : si
>    les livrables qu'il annonce existent, continue la chaîne (`dev-verif` dira ce qui manque) ; s'ils manquent,
>    relance-le une fois sur la part restante seulement, puis `BLOQUÉ`. Un livrable amont manquant est un `BESOIN`,
>    pas un `BLOQUÉ`.
>
> **Sobriété du chef** — chaque étape relit tout ton contexte : un appel d'ouvrier par étape, les contrôles groupés en
> un seul appel (`ls -l a b && check all`), pas de liste de tâches (le plan est sur disque), pas de relecture des
> livrables.

## Chaque règle a une origine mesurée

| Règle | L'incident qui l'a fait naître |
|---|---|
| VALIDÉ est final | un verdict validé « avec remarques » renvoyé en correction : 25 minutes sur 46 perdues en re-vérifications |
| Ce qui est bloquant, et rien d'autre | trois tours de correction pour des numéros de ligne dans des citations |
| La liste transmise telle quelle, re-vérification des seuls numéros | des re-vérifications qui rouvraient tout le livrable |
| Le débogueur seulement sur une vérification rouge | un débogueur envoyé sur un document Markdown |
| Deux tours au plus | la boucle infinie, et une tâche de 3 h 15 qui a relu 22,9 M tokens |
| Réponse vide : une relance courte | un juge en boucle de raisonnement jusqu'au plafond du fournisseur, sans un mot de verdict |
| Réponse hors format : jugement sur pièces | deux tâches bloquées alors que le travail était fait |
| Limite de débit : attendre, puis le jumeau | une limite sur le modèle des juges qui bloquait toutes les tâches |
| Interrompu par la garde : directement le jumeau | un ouvrier figé 34 minutes sur une panne muette de son fournisseur |
| À bout d'étapes, livrables présents : continuer | une tâche bloquée alors que ses dix fichiers existaient |
| Sobriété du chef | des étapes de chef qui relisaient tout pour une liste de tâches inutile (− 27 % de tokens chez les chefs après la règle) |
