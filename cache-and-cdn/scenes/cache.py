"""Scènes (Feuilleté, bl-scenes/0.3) du bit « Répondre plus vite : cache et CDN ».

Exemple propre au bit : un site de recettes de cuisine, dont la recette de la tarte aux pommes est lue des milliers de fois.

Dessin, une sorte = un dessin :
- un programme (l'application du site) = un bloc bleu `b` ;
- la base de données = un `store` bleu `b` ; le cache = un `store` jaune `y` (une copie rapide) ;
- un serveur du CDN = un bloc vert `g` (une copie près des lecteurs) ;
- ce qui est périmé passe en rose `r`.
"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools" / "scenes"))
from paths import outputs
from scene_kit import G, L, scene, send, wait, write, hud, traffic

S = [1.8, 1.8, 1.0]
ents = [
    {"id": "users", "kind": "actor", "at": G(0, 12.0), "label": "les lecteurs",
     "detail": "Des milliers de lecteurs ouvrent la même recette."},
    {"id": "app", "kind": "node", "at": G(0, 3.0), "size": S, "tone": "b", "title": "application du site",
     "detail": "L'**application** construit chaque page à partir des données de la base."},
    {"id": "db", "kind": "store", "at": G(0, -7.0), "tone": "b", "title": "base de données",
     "detail": "La **base de données** garde les recettes. Lire sur disque et assembler une recette prend du temps."},
    {"id": "cache", "kind": "store", "at": G(9.0, -2.0), "tone": "y", "title": "cache",
     "detail": "Un **cache** garde en mémoire une copie des réponses déjà calculées (Redis, Memcached…). Lire en mémoire est bien plus rapide."},
    {"id": "paris", "kind": "actor", "at": G(-9.0, 12.0), "label": "lectrice à Paris"},
    {"id": "mtl", "kind": "actor", "at": G(9.0, 12.0), "label": "lecteur à Montréal"},
    {"id": "edge-p", "kind": "node", "at": G(-9.0, 3.0), "size": S, "tone": "g", "title": "CDN", "sub": "serveur proche",
     "detail": "Un **CDN** (*Content Delivery Network*) a des serveurs dans le monde entier. Chacun garde une copie des fichiers, près des lecteurs."},
    {"id": "edge-m", "kind": "node", "at": G(9.0, 3.0), "size": S, "tone": "g"},
    {"id": "origin", "kind": "node", "at": G(0, -6.0), "size": S, "tone": "b", "title": "serveur d'origine", "sub": "à Paris",
     "detail": "Le **serveur d'origine** : celui du site, qui a la version de référence de chaque fichier."},
]
steps = []

# ---------- 1. sans cache
steps.append({
    "id": "sans-cache", "label": "Sans cache", "title": "Sans cache : la même recette, calculée mille fois",
    "body": ["Chaque lecteur déclenche le même travail."],
    "show": ["users", "app", "db"], "links": [L("users", "app"), L("app", "db")],
    "flows": [traffic(["users", "app", "db"], gap=320)],
    "hud": [hud("lectures base", "1 000/s"), hud("réponse", "120 ms")],
    "script": [
        wait(1800),
        scene(say="Mille lecteurs par seconde ouvrent la **même** recette de tarte aux pommes.",
              set=[{"id": "app", "label": "tarte aux pommes ×1 000"}]),
        wait(1500),
        scene(say="Pour chacun, l'application **relit** la base et refait la même page.",
              set=[{"id": "db", "label": "occupée à 90 %", "tone": "y"}], hud=[hud("lectures base", "1 000/s", "y")]),
        wait(1500),
        scene(say="Le résultat est **identique** à chaque fois : tout ce travail est refait pour rien.",
              set=[{"id": "db", "tone": "r"}], hud=[hud("réponse", "800 ms", "r")]),
        wait(3000),
    ],
})

# ---------- 2. le cache
steps.append({
    "id": "cache", "label": "Le cache", "title": "Le cache : garder une copie de la réponse",
    "body": ["Une copie en mémoire, demandée avant la base."],
    "show": ["users", "app", "db", "cache"], "links": [L("users", "app"), L("app", "db"), L("app", "cache")],
    "hud": [hud("lectures base", 0), hud("réponse", "—")],
    "script": [
        wait(900),
        send(["app", "cache"], label="tarte ?", reply="absente"),
        scene(say="L'application demande d'abord au **cache**. Il ne l'a pas encore : c'est un **défaut de cache** (*miss*).",
              set=[{"id": "cache", "label": "vide"}]),
        send(["app", "db"], label="tarte ?", reply="recette"),
        scene(say="Elle lit la base une fois, puis **range** la réponse dans le cache.",
              set=[{"id": "cache", "label": "tarte aux pommes"}], hud=[hud("lectures base", 1), hud("réponse", "120 ms")]),
        send(["app", "cache"], label="tarte ?", reply="recette"),
        scene(say="Les lecteurs suivants sont servis **depuis la mémoire** : c'est un **succès de cache** (*hit*).",
              hud=[hud("réponse", "5 ms", "g")]),
        wait(1300),
        scene(say="Sur mille lectures, la base n'en voit plus qu'**une**.",
              set=[{"id": "db", "label": "au repos", "tone": "g"}, {"id": "cache", "label": "999 succès sur 1 000"}]),
        wait(3000),
    ],
})

# ---------- 3. périmé
steps.append({
    "id": "perime", "label": "Périmé", "title": "La copie périmée : durée de vie et invalidation",
    "body": ["La recette change. Le cache, lui, ne le sait pas."],
    "show": ["users", "app", "db", "cache"], "links": [L("users", "app"), L("app", "db"), L("app", "cache")],
    "hud": [hud("base", "200 g sucre"), hud("cache", "250 g sucre")],
    "script": [
        wait(900),
        scene(say="L'autrice corrige la recette dans la base : **200 g** de sucre au lieu de 250.",
              set=[{"id": "db", "label": "200 g de sucre", "tone": "g"}]),
        wait(1200),
        send(["app", "cache"], label="tarte ?", reply="250 g"),
        scene(say="Le cache sert toujours l'ancienne version : sa copie est **périmée**.",
              set=[{"id": "cache", "label": "250 g, périmé", "tone": "r"}], hud=[hud("cache", "250 g sucre", "r")]),
        wait(1300),
        scene(say="Première parade : une **durée de vie** (*TTL*). Passé dix minutes, la copie est jetée et relue.",
              set=[{"id": "cache", "label": "expire dans 10 min", "tone": "y"}]),
        wait(1400),
        scene(say="Seconde parade : **invalider** la copie au moment où la recette change.",
              set=[{"id": "app", "label": "efface « tarte »"}, {"id": "cache", "label": "vide", "tone": "y"}], hud=[hud("cache", "—")]),
        send(["app", "db"], label="tarte ?", reply="200 g"),
        scene(say="La lecture suivante relit la base et range la **bonne** version.",
              set=[{"id": "cache", "label": "200 g", "tone": "y"}, {"id": "app", "label": None}], hud=[hud("cache", "200 g sucre", "g")]),
        wait(3000),
    ],
})

# ---------- 4. CDN
steps.append({
    "id": "cdn", "label": "CDN", "title": "Le CDN : des copies près des lecteurs",
    "body": ["Le site est à Paris. Ses lecteurs, partout."],
    "show": ["paris", "mtl", "origin"], "links": [L("paris", "origin"), L("mtl", "origin")],
    "hud": [hud("Montréal", "—")],
    "script": [
        wait(900),
        send(["mtl", "origin"], label="photo-tarte.jpg", reply="photo"),
        scene(say="Depuis Montréal, chaque fichier traverse l'**Atlantique**, aller et retour.",
              set=[{"id": "mtl", "label": "lecteur à Montréal : 180 ms"}], hud=[hud("Montréal", "180 ms", "y")]),
        wait(1200),
        scene(say="Un **CDN** place des serveurs près des lecteurs, qui gardent des copies des fichiers.",
              show=["edge-p", "edge-m"], unlink=[L("paris", "origin"), L("mtl", "origin")],
              link=[L("paris", "edge-p"), L("mtl", "edge-m"), L("edge-p", "origin"), L("edge-m", "origin")]),
        send(["mtl", "edge-m", "origin"], label="photo-tarte.jpg", reply="photo"),
        scene(say="La première demande va jusqu'à l'**origine** ; le serveur de Montréal garde la copie.",
              set=[{"id": "edge-m", "label": "copie gardée"}]),
        send(["mtl", "edge-m"], label="photo-tarte.jpg", reply="photo"),
        scene(say="Les suivantes sont servies **sur place** : plus rapide, et l'origine ne voit presque plus rien passer.",
              set=[{"id": "mtl", "label": "lecteur à Montréal : 15 ms"}, {"id": "origin", "label": "au calme", "tone": "g"}], hud=[hud("Montréal", "15 ms", "g")]),
        wait(3000),
    ],
})

lesson = {
    "format": "bl-scenes/0.3", "id": "cache-and-cdn", "title": "Cache et CDN", "lang": "fr", "kit": "feuillete",
    "legend": [{"kind": "req", "label": "requête"}, {"kind": "res", "label": "réponse"}],
    "entities": ents, "steps": steps,
}
write(lesson, *outputs(HERE, "cache.scene.json", "cache"))
