"""Scènes 2D (kit plan) du bit « Tiers, couches et MVC » (courses-software-architecture/tiers-layers-mvc).

Exemple propre au bit : un site de réservation de places de cinéma (règles : dix places au plus par réservation,
une place n'est vendue qu'une fois).

Dessin, une sorte = un dessin :
- une machine = un plateau (layer) gris `n`, qui porte ce qui tourne dessus ;
- une couche de code = une barre `v` (pervenche) dans le programme ;
- une pièce du patron MVC = une boîte `g` (vert) ;
- la base de données = une boîte `b` (bleu) ;
- ce qu'on veut faire remarquer passe en `y` (jaune) le temps d'un temps.
Kit plan : x vers la droite, y vers le bas, unités de 28 px ; un enfant (in) est relatif au centre du parent.
Largeur visée ≈ 33 unités (au-delà, illisible au plateau).
"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools" / "scenes"))
from paths import outputs
from scene_kit import L, scene, send, wait, write


def ent(id, kind, at, size=None, tone=None, parent=None, **kw):
    d = {"id": id, "kind": kind, "at": list(at)}
    if tone: d["tone"] = tone
    if size: d["size"] = list(size) + [1]
    if parent: d["in"] = parent
    d.update({k: v for k, v in kw.items() if v is not None})
    return d


BAR = 1.9

# ---------- 1. trois questions : trois colonnes
COLS = {"t": -11.5, "c": 0.0, "m": 11.5}
CW, CH = 10.0, 13.0
q_ents = [
    ent("q-t", "layer", (COLS["t"], 0), (CW, CH), "n", title="tiers", sub="où le code tourne",
        detail="Un **tiers** est un niveau de **machines** : le poste, le serveur web, le serveur de base de données. Il se voit sur un plan du réseau."),
    ent("q-t1", "node", (0, -3.6), (CW - 1.6, BAR), "n", parent="q-t", title="navigateur"),
    ent("q-t2", "node", (0, 0), (CW - 1.6, BAR), "n", parent="q-t", title="serveur web"),
    ent("q-t3", "node", (0, 3.6), (CW - 1.6, BAR), "b", parent="q-t", title="base de données"),
    ent("q-c", "layer", (COLS["c"], 0), (CW, CH), "n", title="couches", sub="comment le code est rangé",
        detail="Une **couche** est un rangement du **code** d'un programme : des dossiers, des modules. Elle se voit dans le code, pas sur le réseau."),
    ent("q-c1", "node", (0, -3.6), (CW - 1.6, BAR), "v", parent="q-c", title="présentation"),
    ent("q-c2", "node", (0, 0), (CW - 1.6, BAR), "v", parent="q-c", title="métier"),
    ent("q-c3", "node", (0, 3.6), (CW - 1.6, BAR), "v", parent="q-c", title="accès aux données"),
    ent("q-m", "layer", (COLS["m"], 0), (CW, CH), "n", title="MVC", sub="comment un écran se construit",
        detail="**MVC** est un **patron de présentation** : une façon d'organiser le code qui reçoit un clic et construit l'écran qui répond."),
    ent("q-m1", "node", (0, -3.6), (CW - 1.6, BAR), "g", parent="q-m", title="vue"),
    ent("q-m2", "node", (0, 0), (CW - 1.6, BAR), "g", parent="q-m", title="contrôleur"),
    ent("q-m3", "node", (0, 3.6), (CW - 1.6, BAR), "g", parent="q-m", title="modèle"),
]
step_q = {
    "id": "trois-questions", "label": "Trois mots", "title": "Tiers, couches, MVC : trois questions",
    "body": ["Trois mots qu'on mélange souvent, et qui répondent à trois questions différentes."],
    "show": ["q-t", "q-t1", "q-t2", "q-t3"], "links": [L("q-t1", "q-t2"), L("q-t2", "q-t3")],
    "script": [
        wait(800),
        scene(say="**Tiers** : sur quelles machines tourne l'application ?", set=[{"id": "q-t", "tone": "y"}]),
        wait(900),
        scene(say="**Couches** : comment le code d'un programme est-il rangé ?", show=["q-c", "q-c1", "q-c2", "q-c3"],
              set=[{"id": "q-t", "tone": "n"}]),
        wait(900),
        scene(say="**MVC** : comment le code qui construit un écran est-il découpé ?", show=["q-m", "q-m1", "q-m2", "q-m3"]),
        wait(900),
        scene(say="Le premier se voit **sur le réseau**, les deux autres **dans le code**.",
              set=[{"id": "q-t", "tone": "n"}, {"id": "q-c", "tone": "y"}, {"id": "q-m", "tone": "y"}]),
        wait(3000),
    ],
}

# ---------- 2 et 3. les couches dans le serveur web (même dessin pour les deux sections)
SRV_W, SRV_H = 15.0, 12.0
l_ents = [
    ent("nav", "node", (-10.5, -5.5), (8.0, BAR), "n", title="navigateur", sub="sur le poste du spectateur",
        detail="Le **navigateur** du spectateur : une machine à lui, le premier tiers."),
    ent("srv", "layer", (5.0, 0), (SRV_W, SRV_H), "n", title="serveur web", sub="un seul programme",
        detail="Le **serveur web** fait tourner **un seul programme**, le site de réservation, rangé en trois couches."),
    ent("pres", "node", (0, -3.4), (SRV_W - 1.6, BAR), "v", parent="srv", title="présentation",
        sub="reçoit la demande, renvoie la page",
        detail="La **couche présentation** : le code qui reçoit les demandes du navigateur et prépare la réponse (une page, ou des données)."),
    ent("metier", "node", (0, 0.2), (SRV_W - 1.6, BAR), "v", parent="srv", title="métier",
        sub="dix places au plus ; une place, un spectateur",
        detail="La **couche métier** (on dit aussi **domaine**) : les règles du cinéma. Elle ne sait rien du HTML ni du SQL."),
    ent("data", "node", (0, 3.8), (SRV_W - 1.6, BAR), "v", parent="srv", title="accès aux données",
        sub="lit et écrit dans la base",
        detail="La **couche d'accès aux données** : le seul code qui parle à la base, en SQL ou par un outil qui l'écrit pour lui."),
    ent("db", "node", (-10.5, 5.5), (8.0, BAR), "b", title="base de données", sub="sur sa machine",
        detail="La **base de données**, sur une autre machine : le troisième tiers."),
]
L_LINKS = [L("nav", "pres"), L("data", "db")]
step_l = {
    "id": "couches", "label": "Couches", "title": "Trois couches dans un seul programme",
    "body": ["Une demande « réserver 3 places » traverse les couches du programme, de haut en bas, puis revient."],
    "show": ["nav", "srv", "pres", "metier", "data", "db"], "links": L_LINKS,
    "hud": [{"label": "tiers", "value": 3}, {"label": "couches", "value": 3}],
    "script": [
        wait(900),
        send(["nav", "pres", "metier", "data", "db"], label="réserver 3 places", reply="confirmée",
             explain=["Le navigateur envoie la demande au serveur web : la **présentation** la reçoit.",
                      "Elle la passe au **métier**, qui vérifie la règle : 3 places, c'est moins de 10.",
                      "Le métier demande à l'**accès aux données** d'enregistrer la réservation.",
                      "Seule cette couche parle à la **base**.",
                      "La réponse remonte dans l'autre sens, jusqu'au navigateur."]),
        wait(700),
        scene(say="Chaque couche n'appelle que **celle du dessous** : le métier ne touche jamais au SQL.",
              set=[{"id": "metier", "tone": "y"}]),
        wait(1500),
        scene(say="Trois couches, mais **un seul programme**, sur une seule machine du serveur.",
              set=[{"id": "metier", "tone": "v"}, {"id": "srv", "tone": "y"}]),
        wait(3000),
    ],
}
step_p = {
    "id": "deux-presentations", "label": "Deux « présentation »", "title": "Le tiers présentation n'est pas la couche présentation",
    "body": ["Le même schéma, avec un piège de vocabulaire : le mot « présentation » désigne deux choses."],
    "show": ["nav", "srv", "pres", "metier", "data", "db"], "links": L_LINKS,
    "hud": [{"label": "tiers", "value": 3}, {"label": "couches", "value": 3}],
    "script": [
        wait(900),
        scene(say="Le **tiers présentation**, c'est une **machine** : le poste et son navigateur.",
              set=[{"id": "nav", "tone": "y", "label": "tiers présentation"}]),
        wait(1500),
        scene(say="La **couche présentation**, c'est du **code**, et il tourne sur le **serveur**.",
              set=[{"id": "pres", "tone": "y", "label": "couche présentation"}]),
        wait(1500),
        scene(say="Même mot, deux réponses : **où** ça tourne, ou **comment** c'est rangé.",
              set=[{"id": "srv", "tone": "y"}]),
        wait(3000),
    ],
}

# ---------- 4. MVC : un clic, un écran
m_ents = [
    ent("vue", "node", (-11, 0), (8.0, 2.4), "g", title="vue", sub="la page « Réserver »",
        detail="La **vue** affiche : le formulaire, puis la page de confirmation. Elle ne décide rien."),
    ent("ctrl", "node", (0, -5.5), (9.0, 2.4), "g", title="contrôleur", sub="reçoit et orchestre",
        detail="Le **contrôleur** reçoit l'action (le clic), demande au modèle, puis choisit la vue à afficher. Il **orchestre**, il ne porte pas les règles."),
    ent("modele", "node", (11, 0), (8.0, 2.4), "g", title="modèle", sub="les règles et les données",
        detail="Le **modèle** porte les **règles métier** (dix places au plus) et les données. C'est le domaine, ou la porte vers lui."),
    ent("mdb", "node", (11, 6.0), (8.0, BAR), "b", title="base de données"),
]
step_m = {
    "id": "mvc", "label": "MVC", "title": "MVC : un clic, un écran",
    "body": ["Le spectateur clique sur « Réserver 3 places ». Trois pièces se partagent le travail."],
    "show": ["vue", "ctrl", "modele", "mdb"],
    "links": [L("vue", "ctrl"), L("ctrl", "modele"), L("modele", "mdb"), L("ctrl", "vue", dashed=True)],
    "script": [
        wait(900),
        send(["vue", "ctrl"], label="clic : 3 places",
             explain=["La vue transmet le clic au **contrôleur**."]),
        send(["ctrl", "modele", "mdb"], label="réserver 3 places", reply="d'accord",
             explain=["Le contrôleur demande au **modèle** de réserver.",
                      "Le modèle applique la règle (moins de dix places) et enregistre.",
                      "Il répond au contrôleur : c'est fait."]),
        send(["ctrl", "vue"], label="page confirmée",
             explain=["Le contrôleur **choisit la vue** à afficher : la confirmation."]),
        wait(600),
        scene(say="La règle des dix places vit dans le **modèle**, pas dans le contrôleur.",
              set=[{"id": "modele", "tone": "y"}]),
        wait(3000),
    ],
}

# ---------- 5. où vit MVC : rendu serveur ou appli dans le navigateur
LX, RX = -9.0, 9.0
BW = 15.0
w_ents = [
    ent("s-nav", "layer", (LX, -6.0), (BW, 4.4), "n", title="navigateur", sub="rendu serveur",
        detail="Avec le **rendu serveur**, le navigateur reçoit une page HTML toute faite et l'affiche."),
    ent("s-html", "node", (0, 0.4), (BW - 2, BAR), "n", parent="s-nav", title="affiche la page reçue"),
    ent("s-srv", "layer", (LX, 3.2), (BW, 7.4), "n", title="serveur web",
        detail="Le contrôleur, le modèle et la vue (un **gabarit** de page) tournent tous sur le serveur."),
    ent("s-c", "node", (0, -2.2), (BW - 2, BAR), "g", parent="s-srv", title="contrôleur"),
    ent("s-v", "node", (-3.3, 1.0), (BW / 2 - 1.8, BAR), "g", parent="s-srv", title="vue", sub="gabarit"),
    ent("s-m", "node", (3.3, 1.0), (BW / 2 - 1.8, BAR), "g", parent="s-srv", title="modèle"),
    ent("a-nav", "layer", (RX, -6.0), (BW, 4.4), "n", title="navigateur", sub="appli dans le navigateur",
        detail="Avec une **application dans le navigateur** (on dit *SPA*), l'écran se construit sur le poste : vue, contrôleur et l'**état** de l'écran."),
    ent("a-vc", "node", (0, 0.4), (BW - 2, BAR), "g", parent="a-nav", title="vue, contrôleur, état de l'écran"),
    ent("a-srv", "layer", (RX, 3.2), (BW, 7.4), "n", title="serveur web",
        detail="Le serveur n'envoie plus de pages : il expose une **API** qui répond en données. Les règles métier restent ici."),
    ent("a-api", "node", (0, -2.2), (BW - 2, BAR), "v", parent="a-srv", title="API", sub="répond en données"),
    ent("a-dom", "node", (0, 1.0), (BW - 2, BAR), "v", parent="a-srv", title="métier", sub="les règles qui comptent"),
]
step_w = {
    "id": "ou-vit-mvc", "label": "Serveur ou navigateur", "title": "Où vit MVC : sur le serveur ou dans le navigateur",
    "body": ["Deux façons de construire le même écran de réservation."],
    "show": ["s-nav", "s-html", "s-srv", "s-c", "s-v", "s-m"],
    "links": [L("s-html", "s-c"), L("s-c", "s-m"), L("s-c", "s-v")],
    "script": [
        wait(800),
        scene(say="À gauche, le **rendu serveur** : contrôleur, modèle et vue sont sur le serveur.",
              set=[{"id": "s-srv", "tone": "y"}]),
        send(["s-c", "s-v", "s-html"], label="page HTML",
             explain=["Le contrôleur fait remplir le gabarit par la vue.", "La page part, toute faite, vers le navigateur."]),
        wait(600),
        scene(say="À droite, une **application dans le navigateur** : la vue et son contrôleur tournent sur le poste.",
              show=["a-nav", "a-vc", "a-srv", "a-api", "a-dom"], set=[{"id": "s-srv", "tone": "n"}],
              link=[L("a-vc", "a-api"), L("a-api", "a-dom")]),
        send(["a-vc", "a-api", "a-dom"], label="réserver", reply="données",
             explain=["L'appli du navigateur appelle l'**API** du serveur.", "L'API confie la demande au **métier**.",
                      "Le serveur répond en données ; l'appli met l'écran à jour."]),
        wait(600),
        scene(say="Dans les deux cas, les **règles qui comptent** restent sur le serveur : le poste ne décide pas.",
              set=[{"id": "a-dom", "tone": "y"}, {"id": "s-m", "tone": "y"}]),
        wait(3200),
    ],
}

lesson = {
    "format": "bl-scenes/0.3", "id": "tiers-layers-mvc", "title": "Tiers, couches et MVC", "lang": "fr", "kit": "plan",
    "legend": [{"tone": "n", "label": "machine"}, {"tone": "v", "label": "couche de code"},
               {"tone": "g", "label": "pièce de MVC"}, {"tone": "b", "label": "base de données"}],
    "entities": q_ents + l_ents + m_ents + w_ents,
    "steps": [step_q, step_l, step_p, step_m, step_w],
}
write(lesson, *outputs(HERE, "tiers-layers-mvc.scene.json", "tiers-layers-mvc"))
