"""Scènes 2D (kit plan) du bit « Les protocoles entre programmes : de TCP à gRPC ».

Exemple propre au bit : un transporteur de colis (appli de suivi, services internes, position du livreur en direct).

Dessin, une sorte = un dessin :
- un programme (client, service, navigateur) = une boîte pervenche `v` ;
- une couche de protocole (OSI) = une barre ; celles dont parle le bit en vert `g`, les autres en neutre `n` ;
- un paquet ou un message perdu = rose `r` ; un contrat (fichier .proto, schéma) = jaune `y`.
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


B = 1.9

# ---------- 1. OSI comme repère
OSI = [("o7", "7 · application", "HTTP, gRPC, WebSocket, SMTP"), ("o6", "6 · présentation", "format, chiffrement"),
       ("o5", "5 · session", "ouverture, reprise"), ("o4", "4 · transport", "TCP, UDP"),
       ("o3", "3 · réseau", "IP : l'adresse de la machine"), ("o2", "2 · liaison", "Ethernet, Wi-Fi"),
       ("o1", "1 · physique", "câble, ondes")]
o_ents = [ent("osi", "layer", (0, 0), (20, 20.5), "n", title="modèle OSI", sub="sept couches, un repère",
              detail="Le **modèle OSI** range les protocoles réseau en sept couches. C'est un **repère** : les protocoles réels ne s'y rangent pas toujours exactement.")]
for i, (oid, name, sub) in enumerate(OSI):
    o_ents.append(ent(oid, "node", (0, -6.0 + i * 2.25), (18, 1.9), "n", parent="osi", title=name, sub=sub))
step_o = {
    "id": "osi", "label": "OSI", "title": "Le modèle OSI, un repère pour ranger les protocoles",
    "body": ["Chaque protocole s'appuie sur celui du dessous, comme une lettre dans une enveloppe, dans un sac postal."],
    "show": [e["id"] for e in o_ents], "links": [],
    "script": [
        wait(900),
        scene(say="En bas, le **câble** ou les ondes, puis le réseau local.", set=[{"id": "o1", "tone": "y"}, {"id": "o2", "tone": "y"}]),
        wait(1000),
        scene(say="**IP** amène les paquets jusqu'à la bonne **machine**, grâce à son adresse.",
              set=[{"id": "o1", "tone": "n"}, {"id": "o2", "tone": "n"}, {"id": "o3", "tone": "y"}]),
        wait(1000),
        scene(say="**TCP** ou **UDP** les amènent jusqu'au bon **programme**, grâce à un numéro de port.",
              set=[{"id": "o3", "tone": "n"}, {"id": "o4", "tone": "g"}]),
        wait(1000),
        scene(say="Tout en haut, le protocole d'**application** : ce que les programmes se disent.",
              set=[{"id": "o7", "tone": "g"}]),
        wait(1000),
        scene(say="Ce contenu parle de ces deux couches : **transport** et **application**.", set=[{"id": "osi", "tone": "g"}]),
        wait(3000),
    ],
}

# ---------- 2. TCP ou UDP
t_ents = [
    ent("t-a", "node", (-12, -4.5), (6, 2.4), "v", title="expéditeur", sub="TCP"),
    ent("t-b", "node", (12, -4.5), (6, 2.4), "v", title="destinataire", sub="TCP",
        detail="Avec **TCP**, le destinataire accuse réception ; ce qui manque est renvoyé, et tout arrive dans l'ordre."),
    ent("u-a", "node", (-12, 4.5), (6, 2.4), "v", title="expéditeur", sub="UDP"),
    ent("u-b", "node", (12, 4.5), (6, 2.4), "v", title="destinataire", sub="UDP",
        detail="Avec **UDP**, les paquets partent sans accusé de réception : ce qui se perd est perdu, rien ne ralentit."),
]
step_t = {
    "id": "tcp-udp", "label": "TCP, UDP", "title": "TCP ou UDP : livraison garantie, ou livraison rapide",
    "body": ["Quatre paquets partent. Le troisième se perd en route."],
    "show": [e["id"] for e in t_ents], "links": [L("t-a", "t-b"), L("u-a", "u-b")],
    "hud": [{"label": "TCP reçus", "value": "0 / 4"}, {"label": "UDP reçus", "value": "0 / 4"}],
    "script": [
        wait(800),
        send(["t-a", "t-b"], label="1, 2", reply="reçu 1, 2"),
        send(["t-a", "t-b"], label="3", reply="3 manque"),
        scene(say="TCP : le destinataire signale qu'il manque le **3**. L'expéditeur le **renvoie**.",
              set=[{"id": "t-b", "label": "attend le 3"}], hud=[hud("TCP reçus", "2 / 4", "y")]),
        send(["t-a", "t-b"], label="3, 4", reply="reçu 3, 4"),
        scene(say="Tout arrive, **dans l'ordre**, un peu plus tard.",
              set=[{"id": "t-b", "label": None, "tone": "g"}], hud=[hud("TCP reçus", "4 / 4", "g")]),
        wait(600),
        send(["u-a", "u-b"], label="1, 2, 4"),
        scene(say="UDP : le 3 est **perdu**, personne ne le redemande. Mais rien n'a attendu.",
              set=[{"id": "u-b", "label": "le 3 manque", "tone": "y"}], hud=[hud("UDP reçus", "3 / 4", "y")]),
        wait(3000),
    ],
}

# ---------- 3. REST
r_ents = [
    ent("r-app", "node", (-11, 0), (8, 3.0), "v", title="appli de suivi",
        detail="L'appli du client parle à l'API du transporteur en **HTTP**."),
    ent("r-api", "layer", (7, 0), (17, 13), "v", title="API REST", sub="des ressources, des verbes HTTP",
        detail="**REST** organise une API HTTP autour de **ressources** (des colis) désignées par une adresse, et des **verbes** HTTP pour agir dessus."),
    ent("r-1", "node", (0, -3.9), (15, 1.9), "n", parent="r-api", title="GET /colis/42", sub="lire un colis"),
    ent("r-2", "node", (0, -1.3), (15, 1.9), "n", parent="r-api", title="POST /colis", sub="créer un colis"),
    ent("r-3", "node", (0, 1.3), (15, 1.9), "n", parent="r-api", title="PATCH /colis/42", sub="modifier l'adresse"),
    ent("r-4", "node", (0, 3.9), (15, 1.9), "n", parent="r-api", title="DELETE /colis/42", sub="annuler l'envoi"),
]
step_r = {
    "id": "rest", "label": "REST", "title": "REST : des ressources et des verbes, sur HTTP",
    "body": ["Une seule ressource, le colis 42, et quatre façons d'agir dessus."],
    "show": [e["id"] for e in r_ents], "links": [L("r-app", "r-1"), L("r-app", "r-2"), L("r-app", "r-3"), L("r-app", "r-4")],
    "script": [
        wait(800),
        send(["r-app", "r-1"], label="GET /colis/42", reply='{"etat": "en route"}',
             explain=["L'appli **lit** le colis : le verbe GET, l'adresse du colis.", "L'API répond en JSON, avec le code 200."]),
        scene(say="L'adresse désigne **quoi** (le colis 42), le verbe dit **ce qu'on fait**.", set=[{"id": "r-1", "tone": "g"}]),
        wait(800),
        send(["r-app", "r-3"], label="PATCH adresse", reply="200"),
        scene(say="Même adresse, autre verbe : on **modifie** l'adresse de livraison.", set=[{"id": "r-1", "tone": "n"}, {"id": "r-3", "tone": "g"}]),
        wait(800),
        scene(say="Simple, lisible, compris partout : c'est la forme la plus courante des API web.", set=[{"id": "r-api", "tone": "g"}]),
        wait(3000),
    ],
}

# ---------- 4. GraphQL
g_ents = [
    ent("g-app", "node", (-12, 0), (7, 3.0), "v", title="appli mobile", sub="un écran : colis, expéditeur, étapes"),
    ent("g-c", "node", (2, -5.5), (9, 2.2), "n", title="/colis/42"),
    ent("g-e", "node", (2, 0), (9, 2.2), "n", title="/expediteurs/7"),
    ent("g-s", "node", (2, 5.5), (9, 2.2), "n", title="/colis/42/etapes"),
    ent("g-gql", "node", (12, 0), (8, 3.0), "g", title="API GraphQL", sub="une seule adresse",
        detail="**GraphQL** : le client envoie une requête qui décrit **exactement les champs** qu'il veut ; le serveur répond avec ces champs, en une fois."),
]
step_g = {
    "id": "graphql", "label": "GraphQL", "title": "GraphQL : le client demande exactement ce qu'il affiche",
    "body": ["Un écran de l'appli mobile affiche le colis, son expéditeur et ses trois dernières étapes."],
    "show": ["g-app", "g-c", "g-e", "g-s"], "links": [L("g-app", "g-c"), L("g-app", "g-e"), L("g-app", "g-s")],
    "hud": [{"label": "requêtes", "value": "0"}],
    "script": [
        wait(800),
        send(["g-app", "g-c"], label="GET", reply="colis complet"),
        send(["g-app", "g-e"], label="GET", reply="expéditeur complet"),
        send(["g-app", "g-s"], label="GET", reply="toutes les étapes"),
        scene(say="En REST : **trois requêtes**, et des réponses plus grosses que ce que l'écran affiche.",
              hud=[hud("requêtes", "3", "y")]),
        wait(900),
        scene(say="Avec **GraphQL**, une seule adresse.", show=["g-gql"], hide=["g-c", "g-e", "g-s"],
              link=[L("g-app", "g-gql")], hud=[hud("requêtes", "0", None)]),
        send(["g-app", "g-gql"], label="colis { état, étapes }", reply="ces champs-là",
             explain=["L'appli décrit **les champs** dont l'écran a besoin.", "Le serveur répond avec eux, et rien d'autre."]),
        scene(say="**Une requête**, la réponse taillée pour l'écran. En échange, un serveur plus complexe à écrire et à protéger.",
              hud=[hud("requêtes", "1", "g")]),
        wait(3000),
    ],
}

# ---------- 5. gRPC
p_ents = [
    ent("p-a", "node", (-11, 0), (8, 3.0), "v", title="service Tournées",
        detail="Deux **services internes** du transporteur, qui s'appellent des milliers de fois par seconde."),
    ent("p-b", "node", (11, 0), (8, 3.0), "v", title="service Position"),
    ent("p-proto", "node", (0, -6.0), (11, 2.6), "y", title="position.proto", sub="le contrat, écrit une fois",
        detail="Le fichier **.proto** décrit les appels et les messages. Un outil en **génère le code** des deux côtés, dans leurs langages."),
]
step_p = {
    "id": "grpc", "label": "gRPC", "title": "gRPC : un contrat strict et des messages compacts, entre services",
    "body": ["Deux services internes qui se parlent des milliers de fois par seconde."],
    "show": ["p-a", "p-b"], "links": [L("p-a", "p-b")],
    "script": [
        wait(800),
        scene(say="D'abord un **contrat** : le fichier .proto décrit les appels et les messages.",
              show=["p-proto"], link=[L("p-proto", "p-a", dashed=True), L("p-proto", "p-b", dashed=True)]),
        wait(900),
        scene(say="Un outil en **génère le code** des deux côtés : on appelle le service distant comme une fonction.",
              set=[{"id": "p-a", "label": "code généré"}, {"id": "p-b", "label": "code généré"}]),
        send(["p-a", "p-b"], label="Position(livreur 12)", reply="48.85, 2.35",
             explain=["Tournées appelle Position : le message part en **binaire**, compact, sur HTTP/2.", "La réponse revient dans le format du contrat."]),
        scene(say="Rapide et typé, mais peu lisible à l'œil et mal compris des navigateurs : on le garde **entre services**.",
              set=[{"id": "p-proto", "tone": "g"}]),
        wait(3000),
    ],
}

# ---------- 6. le serveur qui parle le premier
s_ents = [
    ent("s-nav", "node", (-11, 0), (8, 3.0), "v", title="page de suivi", sub="la position du livreur"),
    ent("s-srv", "node", (11, 0), (8, 3.0), "v", title="serveur"),
]
step_s = {
    "id": "temps-reel", "label": "Temps réel", "title": "Polling, SSE, WebSocket : quand le serveur a quelque chose à dire",
    "body": ["La page de suivi doit montrer le livreur qui avance. En HTTP, c'est toujours le client qui demande."],
    "show": ["s-nav", "s-srv"], "links": [L("s-nav", "s-srv")],
    "hud": [{"label": "technique", "value": "—"}, {"label": "pour rien", "value": "—"}],
    "script": [
        wait(800),
        scene(say="**Polling** : la page redemande toutes les cinq secondes.", hud=[hud("technique", "polling")]),
        send(["s-nav", "s-srv"], label="du neuf ?", reply="non"),
        send(["s-nav", "s-srv"], label="du neuf ?", reply="non"),
        send(["s-nav", "s-srv"], label="du neuf ?", reply="il a bougé"),
        scene(say="Simple, mais la plupart des réponses disent « rien de neuf ».", hud=[hud("pour rien", "2 sur 3", "y")]),
        wait(700),
        scene(say="**SSE** : une connexion reste ouverte, le **serveur envoie** quand il a du neuf.",
              hud=[hud("technique", "SSE"), hud("pour rien", "0", "g")]),
        send(["s-srv", "s-nav"], label="position"),
        send(["s-srv", "s-nav"], label="position"),
        scene(say="**WebSocket** : une connexion dans les **deux sens**, pour écrire aussi au livreur.",
              hud=[hud("technique", "WebSocket")]),
        send(["s-nav", "s-srv"], label="sonnez au 2e"),
        send(["s-srv", "s-nav"], label="bien reçu"),
        wait(3000),
    ],
}

lesson = {
    "format": "bl-scenes/0.3", "id": "communication-protocols", "title": "Les protocoles entre programmes", "lang": "fr", "kit": "plan",
    "legend": [{"tone": "v", "label": "programme"}, {"tone": "g", "label": "ce dont on parle"}, {"tone": "y", "label": "contrat, attention"}],
    "entities": o_ents + t_ents + r_ents + g_ents + p_ents + s_ents,
    "steps": [step_o, step_t, step_r, step_g, step_p, step_s],
}
write(lesson, *outputs(HERE, "protocols.scene.json", "protocols"))
