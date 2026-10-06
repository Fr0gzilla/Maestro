#!/usr/bin/env bash
# controle-des-processus.sh — extrait adapté de l'outil « processus » de Maestro.
#
# Le problème : l'hôte doit parfois attendre la fin d'un chef, ou l'arrêter. Le numéro de processus est lu dans un
# fichier .pid. Si un agent pouvait écrire ce fichier, il y mettrait « -1 » : passé à kill, ce numéro vise TOUS les
# processus du compte (l'orchestrateur, les superviseurs, le tableau de bord…).
#
# Deux lignes de défense :
#   1. les .pid qui font foi sont tenus dans un dossier de l'hôte, jamais monté chez les agents ;
#   2. ce contrôle, avant tout usage : un entier supérieur à 1, un processus vivant du compte, dont la ligne de
#      commande contient le motif attendu et, si un dossier est donné, dont le dossier courant est celui-là (Linux).
#      Il écarte aussi un numéro recyclé par un autre programme après la fin du chef.
#
# usage  : controle-des-processus.sh <fichier .pid> <motif> [dossier]
# sortie : le numéro et le code 0 s'il est valide et vivant ; code 1 sinon ; code 2 pour une erreur d'usage
# exemple : pid=$(controle-des-processus.sh "$etat/T004.pid" "--agent" "$PWD") && kill -TERM "$pid"
set -uo pipefail
f="${1:-}"; motif="${2:-}"; dossier="${3:-}"
[ -n "$f" ] && [ -n "$motif" ] || { sed -n '2,17p' "$0" >&2; exit 2; }

# 32 octets au plus, première ligne seulement : un fichier géant ou multiligne ne passe pas
pid=$(head -c 32 "$f" 2>/dev/null | head -n 1) || exit 1

# un entier décimal sans zéro initial : ni vide, ni signe (« -1 »), ni « 0 » (qui vise le groupe de processus),
# ni « 0x… » ou « 017 » (lus autrement selon l'outil)
case "$pid" in ''|0*|*[!0-9]*) exit 1 ;; esac
[ "${#pid}" -le 9 ] && [ "$pid" -gt 1 ] || exit 1        # 1, c'est init : jamais

kill -0 "$pid" 2>/dev/null || exit 1                      # vivant, et appartenant à ce compte

# la ligne de commande doit être celle du programme attendu (sinon : numéro recyclé, ou fichier altéré)
if [ -r "/proc/$pid/cmdline" ]; then ligne=$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null)
else ligne=$(ps -ww -o args= -p "$pid" 2>/dev/null) || exit 1; fi    # sans /proc (macOS) : ps
case "$ligne" in *"$motif"*) ;; *) exit 1 ;; esac

# et, sous Linux, son dossier courant doit être celui du projet
if [ -n "$dossier" ] && [ -e "/proc/$pid/cwd" ]; then
  [ "$(readlink "/proc/$pid/cwd" 2>/dev/null)" = "$(cd "$dossier" 2>/dev/null && pwd -P)" ] || exit 1
fi
echo "$pid"
