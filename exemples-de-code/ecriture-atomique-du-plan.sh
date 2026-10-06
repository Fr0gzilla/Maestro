#!/usr/bin/env bash
# ecriture-atomique-du-plan.sh — extrait adapté de l'outil « plan » de Maestro.
#
# Le plan est LE fichier d'état d'un projet : un plan corrompu, c'est un run perdu, en pleine nuit. Aucun agent ne
# l'édite ; toute modification passe par une réécriture complète, faite ainsi :
#   - le nouveau contenu est écrit dans un fichier temporaire du MÊME dossier (même système de fichiers : le
#     renommage final est atomique) ;
#   - il est refusé s'il a perdu son en-tête ou des tâches (une commande interrompue, un programme awk raté) ;
#   - puis mv le substitue d'un coup : un lecteur voit l'ancien plan ou le nouveau, jamais un plan à moitié écrit.
# Les champs sont contrôlés avant d'entrer dans le tableau, et les identifiants de tâche sont ancrés.
#
# démonstration, dans un dossier temporaire : bash ecriture-atomique-du-plan.sh demo
set -euo pipefail
ETAT="${MAESTRO_ETAT:-.maestro}"
PLAN="$ETAT/plan.md"
LIGNE_TACHE='^\| *T[0-9]+ *\|'

die() { echo "plan: $*" >&2; exit 2; }

# les champs vont dans un tableau Markdown et dans des programmes awk : ni barre, ni antislash, ni saut de ligne
sans_separateur() { case "$*" in *"|"*|*"\\"*|*$'\n'*|*$'\r'*) die "caractère interdit dans un champ (| \\ saut de ligne)";; esac; }

# un identifiant de tâche est ancré : T001 ou T0420 — jamais « T001/../.. »
id_valide() { case "$1" in T[0-9][0-9][0-9]|T[0-9][0-9][0-9][0-9]) ;; *) die "identifiant invalide : $1 (attendu Tnnn)";; esac; }

# lit le nouveau plan sur l'entrée standard et le substitue à l'ancien, ou refuse
reecrire() {
  local tmp avant apres
  tmp=$(mktemp "$PLAN.XXXXXX") || die "fichier temporaire impossible dans $ETAT"
  cat > "$tmp"
  avant=$(grep -cE "$LIGNE_TACHE" "$PLAN" || true)
  apres=$(grep -cE "$LIGNE_TACHE" "$tmp" || true)
  if ! grep -q '^| ID |' "$tmp" || [ "$apres" -lt "$avant" ]; then
    rm -f "$tmp"; die "réécriture refusée : le plan serait tronqué ($avant -> $apres tâches)"
  fi
  chmod 644 "$tmp"
  mv "$tmp" "$PLAN"
}

# exemple d'usage : changer le statut d'une tâche (colonne 6 du tableau | ID | Groupe | Tâche | Après | Statut | Rapport |)
mettre_statut() {
  local id="$1" statut="$2"
  id_valide "$id"; sans_separateur "$statut"
  grep -qE "^\| *$id *\|" "$PLAN" || die "tâche inconnue : $id"
  awk -F'|' -v OFS='|' -v id="$id" -v st=" $statut " '$2 ~ "^ *" id " *$" { $6 = st } { print }' "$PLAN" | reecrire
}

if [ "${1:-}" = demo ]; then
  cd "$(mktemp -d)"; mkdir -p "$ETAT"
  cat > "$PLAN" <<'PLAN'
# Plan — démonstration
| ID | Groupe | Tâche | Après | Statut | Rapport |
|---|---|---|---|---|---|
| T001 | modele | MCD et MLD | - | FAIT | modele-T001.md |
| T002 | dev | Socle et pages | T001 | EN COURS | - |
PLAN
  mettre_statut T002 "FAIT"                           && echo "T002 → FAIT : accepté"
  grep '^| T002' "$PLAN"
  ( printf '| ID |\n' | reecrire ) 2>&1               || echo "(le plan est resté intact : $(grep -cE "$LIGNE_TACHE" "$PLAN") tâches)"
  ( mettre_statut 'T001/../..' FAIT ) 2>&1            || true
  ( mettre_statut T001 'FAIT | injecté' ) 2>&1        || true
fi
