#!/usr/bin/env python3
"""modele-de-cout.py — le coût d'une session d'agent, et pourquoi Maestro découpe le travail.

À chaque étape, un modèle relit tout son contexte : la consigne, les fichiers lus, les commandes et leurs sorties, et
son propre raisonnement, qui reste dans le contexte. Si ce contexte part de c0 tokens et grossit de g tokens par
étape, une session de n étapes relit :

    relu(n) = Σ (c0 + k·g), k = 0 … n-1  =  n·c0 + g·n(n-1)/2  ≈  n·c0 + g·n²/2

Le terme en n² domine dès quelques étapes : à travail égal, deux sessions de 8 étapes coûtent nettement moins qu'une
de 16. D'où, dans Maestro, des lots découpés par le chef (un module de tests par appel), des limites d'étapes imposées
et des sessions courtes. Le découpage a pourtant un optimum : chaque session de plus coûte un appel et une relecture
au chef, et repaie c0.

Valeurs par défaut : les médianes mesurées sur l'ouvrier qui écrit les tests (c0 ≈ 8 500 tokens, g ≈ 2 500).

usage : python3 modele-de-cout.py                     les exemples du chapitre « L'économie de tokens »
        python3 modele-de-cout.py 8500 11200 13900 …  estime c0 et g à partir des contextes mesurés, étape par étape
"""
import sys


def relu(n, c0, g):
    """tokens relus par une session de n étapes (somme exacte)"""
    return n * c0 + g * n * (n - 1) // 2


def decoupe(n, lots, c0, g):
    """le même travail de n étapes, découpé en `lots` sessions aussi égales que possible"""
    base, reste = divmod(n, lots)
    return sum(relu(base + (1 if i < reste else 0), c0, g) for i in range(lots))


def estimer(contextes):
    """c0 et g par moindres carrés, à partir de la taille du contexte mesurée à chaque étape (k = 0, 1, 2…)"""
    n = len(contextes)
    if n < 2: raise ValueError("il faut au moins deux étapes mesurées")
    mk, my = (n - 1) / 2, sum(contextes) / n
    g = sum((k - mk) * (y - my) for k, y in enumerate(contextes)) / sum((k - mk) ** 2 for k in range(n))
    return my - g * mk, g


def milliers(x):
    return f"{x:,.0f}".replace(",", " ")


def main(args):
    if args:
        c0, g = estimer([float(a) for a in args])
        print(f"c0 ≈ {milliers(c0)} tokens · g ≈ {milliers(g)} tokens par étape")
        print(f"une session de {len(args)} étapes relit ≈ {milliers(relu(len(args), c0, g))} tokens")
        return
    c0, g, n = 8_500, 2_500, 16
    ref = relu(n, c0, g)
    print(f"c0 = {milliers(c0)} · g = {milliers(g)} · le même travail de {n} étapes\n")
    print(f"{'découpage':<30}{'tokens relus':>14}{'écart':>9}")
    for lots in (1, 2, 4):
        r = decoupe(n, lots, c0, g)
        ecart = "" if lots == 1 else f"{(r - ref) / ref:+.0%}".replace("-", "− ")
        print(f"{f'{lots} session(s) de {n // lots} étapes':<30}{milliers(r):>14}{ecart:>9}")


if __name__ == "__main__":
    main(sys.argv[1:])
