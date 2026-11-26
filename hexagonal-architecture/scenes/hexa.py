"""Scènes 2D (kit plan) du bit « Couches, hexagonale, onion, clean : vers qui pointent les dépendances ».

Exemple propre au bit : la prise de rendez-vous d'un cabinet vétérinaire (règle : pas deux rendez-vous sur le même
créneau ; un rappel par SMS la veille).
Section « ce que l'hexagonale n'est pas » : l'appli de VTC du docx de Boris (lake/bronze/local/2026-11-26-architecture-
scenarios-docx), redessinée, pas recopiée : un monolithe dessiné en hexagone.

Dessin, une sorte = un dessin :
- une couche de code = une barre pervenche `v` ;
- le domaine (les règles) = vert `g` ; un port (interface définie par le domaine) = jaune `y` ;
- un adaptateur (web, mobile, base, SMS) = neutre `n` ; une dépendance qui pose problème = rose `r`.
- Une flèche va de ce qui dépend vers ce dont il dépend (« A connaît B »).
Kit plan : x vers la droite, y vers le bas, unités de 28 px ; un enfant (in) est relatif au centre du parent.
"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools" / "scenes"))
from paths import outputs
from scene_kit import L, scene, send, wait, write, hud


def ent(id, kind, at, size=None, tone=None, parent=None, **kw):
    d = {"id": id, "kind": kind, "at": list(at)}
    if tone: d["tone"] = tone
    if size: d["size"] = list(size) + [1]
    if parent: d["in"] = parent
    d.update({k: v for k, v in kw.items() if v is not None})
    return d


# ---------- 1 et 2. couches (même dessin)
c_ents = [
    ent("c-pres", "node", (0, -6.0), (16, 2.6), "v", title="présentation", sub="pages web, appli mobile",
        detail="La couche **présentation** reçoit les demandes et affiche les réponses."),
    ent("c-dom", "node", (0, 0), (16, 2.6), "g", title="métier", sub="pas deux rendez-vous sur un créneau",
        detail="La couche **métier** porte les règles du cabinet."),
    ent("c-data", "node", (0, 6.0), (16, 2.6), "v", title="accès aux données", sub="Postgres, fournisseur de SMS",
        detail="La couche **accès aux données** parle à la base et, ici, au fournisseur de SMS."),
]
C_LINKS = [L("c-pres", "c-dom"), L("c-dom", "c-data")]
step_c = {
    "id": "couches", "label": "Couches", "title": "Une architecture en couches bien tenue",
    "body": ["Trois couches, et une règle : chacune ne connaît que celle du dessous."],
    "show": [e["id"] for e in c_ents], "links": C_LINKS,
    "script": [
        wait(900),
        send(["c-pres", "c-dom", "c-data"], label="rendez-vous mardi 10 h", reply="confirmé",
             explain=["La présentation transmet la demande au métier.", "Le métier vérifie le créneau, puis demande d'enregistrer.",
                      "La réponse remonte."]),
        scene(say="Les flèches disent **qui connaît qui** : toujours vers le bas.", set=[{"id": "c-dom", "label": "connaît la couche du dessous"}]),
        wait(1200),
        scene(say="Bien tenue, cette architecture est **correcte**, et suffit à beaucoup d'applications.",
              set=[{"id": "c-dom", "label": None, "tone": "g"}]),
        wait(3000),
    ],
}
step_p = {
    "id": "probleme", "label": "Le problème", "title": "Le problème : les règles dépendent de la base",
    "body": ["Le même schéma. Regardons la flèche du milieu."],
    "show": [e["id"] for e in c_ents], "links": C_LINKS,
    "hud": [{"label": "tester la règle", "value": "—"}, {"label": "changer de SMS", "value": "—"}],
    "script": [
        wait(900),
        scene(say="Le métier **connaît** l'accès aux données : il appelle du code écrit pour Postgres et pour un fournisseur de SMS précis.",
              set=[{"id": "c-data", "tone": "r"}]),
        wait(1300),
        scene(say="Pour tester la règle des créneaux, il faut donc une **vraie base**.",
              hud=[hud("tester la règle", "base requise", "r")]),
        wait(1200),
        scene(say="Et changer de fournisseur de SMS oblige à **retoucher le métier**.",
              hud=[hud("changer de SMS", "touche au métier", "r")]),
        wait(1200),
        scene(say="Les règles, le cœur de l'application, dépendent des détails techniques : c'est **ce sens-là** qu'on va inverser.",
              set=[{"id": "c-dom", "tone": "y"}]),
        wait(3000),
    ],
}

# ---------- 3. ports et adaptateurs
h_ents = [
    ent("h-core", "layer", (0, 0), (13, 11), "g", title="domaine", sub="les règles, sans technique",
        detail="Au centre, le **domaine** : les règles du cabinet. Il ne connaît ni le web, ni Postgres, ni le fournisseur de SMS."),
    ent("h-rule", "node", (0, -1.6), (11, 1.9), "g", parent="h-core", title="pas deux rendez-vous par créneau"),
    ent("h-p1", "node", (-2.8, 2.2), (5.2, 2.2), "y", parent="h-core", title="port", sub="ranger les rendez-vous",
        detail="Un **port** : une interface que le **domaine** définit, avec ses mots à lui (« ranger un rendez-vous »). Il ne dit pas comment."),
    ent("h-p2", "node", (2.8, 2.2), (5.2, 2.2), "y", parent="h-core", title="port", sub="prévenir le client"),
    ent("h-web", "node", (-14, -4.5), (8, 2.4), "n", title="adaptateur web", sub="le contrôleur des pages",
        detail="Un **adaptateur primaire** : il reçoit une demande de l'extérieur et appelle le domaine."),
    ent("h-mob", "node", (-14, 0), (8, 2.4), "n", title="adaptateur mobile", sub="l'API de l'appli"),
    ent("h-test", "node", (-14, 4.5), (8, 2.4), "n", title="les tests", sub="appellent le domaine directement"),
    ent("h-pg", "node", (14, -2.2), (8, 2.4), "n", title="adaptateur Postgres", sub="implémente « ranger »",
        detail="Un **adaptateur secondaire** : il **implémente** un port du domaine avec une technique précise."),
    ent("h-sms", "node", (14, 2.8), (8, 2.4), "n", title="adaptateur SMS", sub="implémente « prévenir »"),
]
step_h = {
    "id": "ports-adaptateurs", "label": "Ports et adaptateurs", "title": "Inverser la dépendance : ports et adaptateurs",
    "body": ["Le domaine au centre, la technique autour, et toutes les flèches vers le centre."],
    "show": ["h-core", "h-rule"], "links": [],
    "hud": [{"label": "tester la règle", "value": "—"}, {"label": "changer de SMS", "value": "—"}],
    "script": [
        wait(900),
        scene(say="Le domaine définit ce dont il a besoin, avec ses mots : ce sont ses **ports**.", show=["h-p1", "h-p2"]),
        wait(1000),
        scene(say="À droite, des **adaptateurs** implémentent ces ports : l'un pour Postgres, l'autre pour le SMS.",
              show=["h-pg", "h-sms"], link=[L("h-pg", "h-p1"), L("h-sms", "h-p2")]),
        wait(1100),
        scene(say="La flèche s'est **inversée** : c'est l'adaptateur qui connaît le domaine, plus l'inverse.",
              set=[{"id": "h-pg", "tone": "y"}]),
        wait(1100),
        scene(say="À gauche, d'autres adaptateurs appellent le domaine : le web, le mobile… et les **tests**.",
              show=["h-web", "h-mob", "h-test"], link=[L("h-web", "h-core"), L("h-mob", "h-core"), L("h-test", "h-core")],
              set=[{"id": "h-pg", "tone": "n"}]),
        wait(1000),
        scene(say="La règle se teste **sans base**, et changer de fournisseur de SMS, c'est **écrire un adaptateur**.",
              hud=[hud("tester la règle", "sans base", "g"), hud("changer de SMS", "un adaptateur", "g")]),
        wait(3200),
    ],
}

# ---------- 4. onion et clean
o_ents = [
    ent("o-out", "layer", (0, 0), (34, 17), "n", title="infrastructure et interfaces", sub="web, base, SMS, frameworks",
        detail="Le cercle extérieur : tout ce qui est technique et change souvent."),
    ent("o-app", "layer", (0, 1.4), (21, 11.5), "v", parent="o-out", title="cas d'usage", sub="prendre un rendez-vous, l'annuler",
        detail="Le cercle des **cas d'usage** (ou couche application) : il enchaîne les règles pour une action de l'utilisateur."),
    ent("o-dom", "layer", (0.6, 1.5), (9.6, 6), "g", parent="o-app", title="domaine", sub="les règles",
        detail="Au centre, le **domaine**, qui ne dépend de rien."),
    ent("o-x", "node", (-13.6, 2.0), (5.2, 2.0), "n", parent="o-out", title="contrôleur web"),
    ent("o-u", "node", (-7.75, 1.5), (5.0, 2.2), "v", parent="o-app", title="prendre un RDV"),
    ent("o-r", "node", (0, 1.0), (8.0, 2.0), "g", parent="o-dom", title="créneau libre ?"),
]
step_o = {
    "id": "onion-clean", "label": "Onion et clean", "title": "Onion et clean : la même règle, d'autres dessins",
    "body": ["Des cercles plutôt qu'un hexagone, et la même règle de dépendance."],
    "show": ["o-out"], "links": [],
    "script": [
        wait(900),
        scene(say="Le cercle extérieur : le web, la base, les frameworks, tout ce qui change souvent.", show=["o-x"], set=[{"id": "o-out", "tone": "y"}]),
        wait(1000),
        scene(say="Dedans, les **cas d'usage** : prendre un rendez-vous, l'annuler.", show=["o-app", "o-u"], link=[L("o-x", "o-u")], set=[{"id": "o-out", "tone": "n"}]),
        wait(1000),
        scene(say="Au centre, le **domaine**.", show=["o-dom", "o-r"], link=[L("o-u", "o-r")]),
        wait(1000),
        scene(say="La règle, partout : un cercle ne connaît que les cercles **plus au centre**. Onion, clean, hexagonale : même idée.",
              set=[{"id": "o-dom", "tone": "y"}]),
        wait(3200),
    ],
}

# ---------- 5. ce que l'hexagonale n'est pas
n_ents = [
    ent("n-web", "layer", (-11, 0), (13, 12), "n", title="adaptateur web",
        detail="MVC vit **dans** l'adaptateur web : l'hexagonale ne le remplace pas, elle dit où il se range."),
    ent("n-v", "node", (0, -2.4), (11, 1.9), "v", parent="n-web", title="vue"),
    ent("n-c", "node", (0, 0.4), (11, 1.9), "v", parent="n-web", title="contrôleur"),
    ent("n-m", "node", (0, 3.2), (11, 1.9), "g", parent="n-web", title="modèle → le domaine"),
    ent("n-mono", "layer", (8, 0), (15, 12), "g", title="appli de VTC", sub="un seul déploiement",
        detail="Une appli de VTC dessinée en hexagone : passagers, chauffeurs, trajets, factures, paiements, notifications au centre, des adaptateurs autour. **Un seul artefact** : c'est un monolithe."),
]
for i, name in enumerate(["passagers", "chauffeurs", "trajets", "factures", "paiements", "notifications"]):
    n_ents.append(ent(f"n-d{i}", "node", (-3.3 + (i % 2) * 6.6, -2.6 + (i // 2) * 2.7), (6.0, 1.9), "g", parent="n-mono", title=name))
step_n = {
    "id": "ce-quelle-nest-pas", "label": "Ce qu'elle n'est pas", "title": "Ce que l'hexagonale n'est pas",
    "body": ["Deux confusions fréquentes, côte à côte."],
    "show": ["n-web", "n-v", "n-c", "n-m"], "links": [L("n-c", "n-m")],
    "script": [
        wait(900),
        scene(say="MVC n'est pas en concurrence avec l'hexagonale : il vit **dans l'adaptateur web**.",
              set=[{"id": "n-web", "tone": "y"}]),
        wait(1300),
        scene(say="À droite, une appli de VTC dessinée en hexagone…",
              show=["n-mono"] + [f"n-d{i}" for i in range(6)], set=[{"id": "n-web", "tone": "n"}]),
        wait(1100),
        scene(say="…mais livrée d'un seul bloc : c'est un **monolithe**. Hexagonale ne veut pas dire micro-services.",
              set=[{"id": "n-mono", "tone": "y"}]),
        wait(3200),
    ],
}

lesson = {
    "format": "bl-scenes/0.3", "id": "hexagonal-architecture", "title": "Couches et hexagonale", "lang": "fr", "kit": "plan",
    "legend": [{"tone": "g", "label": "domaine"}, {"tone": "y", "label": "port"}, {"tone": "n", "label": "adaptateur"},
               {"tone": "v", "label": "couche, cercle"}],
    "entities": c_ents + h_ents + o_ents + n_ents,
    "steps": [step_c, step_p, step_h, step_o, step_n],
}
write(lesson, *outputs(HERE, "hexagonal.scene.json", "hexagonal"))
