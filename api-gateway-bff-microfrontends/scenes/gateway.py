"""Scènes 2D (kit plan) du bit « Passerelle d'API, BFF et micro-frontends ».

Exemple propre au bit : une agence de voyages en ligne (vols, hôtels, paiement, avis), un site web et une appli mobile.

Dessin, une sorte = un dessin :
- une application côté utilisateur (site, appli mobile, morceau de page) = une boîte pervenche `v` ;
- un service du back (déployé seul) = une boîte verte `g` ;
- un point d'entrée (passerelle, BFF) = une boîte jaune `y` ;
- un outil commun (annuaire, design system) = une boîte grise `n` ;
- ce qui casse passe en rose `r`.
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


SVC = [("vol", "vols"), ("hot", "hôtels"), ("pay", "paiement"), ("avi", "avis")]
SY = [-6.0, -2.0, 2.0, 6.0]
SW, SH = 8.0, 2.4

# ---------- 1. sans passerelle
a_ents = [
    ent("a-web", "node", (-12, -3), (8, 2.6), "v", title="site web",
        detail="Le **site web** de l'agence, dans le navigateur."),
    ent("a-mob", "node", (-12, 3), (8, 2.6), "v", title="appli mobile"),
]
for (sid, name), y in zip(SVC, SY):
    a_ents.append(ent(f"a-{sid}", "node", (10, y), (SW, SH), "g", title=name,
                      detail="Sur le schéma, quatre **services**, chacun déployé seul." if sid == "vol" else None))
step_a = {
    "id": "sans-passerelle", "label": "Sans passerelle", "title": "Sans passerelle : chaque appli parle à chaque service",
    "body": ["Deux applis, quatre services, et autant de chemins entre eux."],
    "show": [e["id"] for e in a_ents],
    "links": [L(c, f"a-{s}") for c in ("a-web", "a-mob") for s, _ in SVC],
    "hud": [{"label": "adresses", "value": 4}],
    "script": [
        wait(900),
        scene(say="Chaque appli connaît **l'adresse des quatre services**.", set=[{"id": "a-web", "tone": "y"}, {"id": "a-mob", "tone": "y"}]),
        send(["a-mob", "a-vol"], label="vols ?"),
        send(["a-mob", "a-hot"], label="hôtels ?"),
        scene(say="Chaque service vérifie lui-même **qui est connecté** : quatre fois le même code.",
              set=[{"id": "a-web", "tone": "v"}, {"id": "a-mob", "tone": "v"}] + [{"id": f"a-{s}", "label": "vérifie le jeton"} for s, _ in SVC]),
        wait(1300),
        scene(say="Le paiement change d'adresse : il faut **mettre à jour et republier** les deux applis.",
              set=[{"id": "a-pay", "tone": "r", "label": "nouvelle adresse"}, {"id": "a-mob", "tone": "r"}, {"id": "a-web", "tone": "r"}]),
        wait(3000),
    ],
}

# ---------- 2. la passerelle
b_ents = [
    ent("b-web", "node", (-13, -3), (7, 2.6), "v", title="site web"),
    ent("b-mob", "node", (-13, 3), (7, 2.6), "v", title="appli mobile"),
    ent("b-gw", "node", (-1.5, 0), (8, 6.0), "y", title="passerelle d'API", sub="une seule adresse",
        detail="La **passerelle d'API** (*API gateway*) : le seul point d'entrée. Elle reçoit tout, et route vers le bon service."),
]
for (sid, name), y in zip(SVC, SY):
    b_ents.append(ent(f"b-{sid}", "node", (11, y), (SW, SH), "g", title=name))
step_b = {
    "id": "passerelle", "label": "Passerelle", "title": "La passerelle d'API : une seule porte d'entrée",
    "body": ["Une porte unique devant les services."],
    "show": [e["id"] for e in b_ents],
    "links": [L("b-web", "b-gw"), L("b-mob", "b-gw")] + [L("b-gw", f"b-{s}") for s, _ in SVC],
    "hud": [{"label": "adresses", "value": 1}],
    "script": [
        wait(900),
        scene(say="Les applis ne connaissent plus qu'**une adresse** : celle de la passerelle.", set=[{"id": "b-gw", "label": "api.agence.fr"}]),
        send(["b-mob", "b-gw", "b-vol"], label="GET /vols",
             explain=["La requête arrive à la passerelle.", "Elle la **route** vers le service des vols, d'après le chemin."]),
        scene(say="Elle vérifie **une fois** qui est connecté, à la place de chaque service.",
              set=[{"id": "b-gw", "label": "vérifie le jeton"}]),
        send(["b-web", "b-gw", "b-hot"], label="GET /hotels"),
        scene(say="Elle peut aussi **limiter le débit** d'un client trop bavard, et tout journaliser.",
              set=[{"id": "b-gw", "label": "100 requêtes / min"}]),
        wait(1200),
        scene(say="Le paiement change d'adresse ? Seule la **passerelle** est mise à jour.",
              set=[{"id": "b-pay", "tone": "y", "label": "nouvelle adresse"}, {"id": "b-gw", "label": "route mise à jour"}]),
        wait(3000),
    ],
}

# ---------- 3. l'annuaire de services
c_ents = [
    ent("c-gw", "node", (-12, -2), (8, 3.0), "y", title="passerelle d'API"),
    ent("c-reg", "node", (-12, 5.5), (8, 3.0), "n", title="annuaire de services", sub="qui est où",
        detail="L'**annuaire de services** (*service registry*) tient la liste des copies en service et de leurs adresses."),
    ent("c-vol", "layer", (8, 0), (12, 13), "g", title="service des vols", sub="trois copies",
        detail="Le même service tourne en **trois copies**, sur des machines qui changent."),
]
CY = [-2.6, 1.0, 4.6]
ADDR = ["10.0.1.7", "10.0.2.3", "10.0.3.9"]
for i, (y, a) in enumerate(zip(CY, ADDR)):
    c_ents.append(ent(f"c-v{i}", "node", (0, y), (9, 2.4), "g", parent="c-vol", label=a))
step_c = {
    "id": "annuaire", "label": "Annuaire", "title": "L'annuaire de services : trouver des copies qui bougent",
    "body": ["Derrière la passerelle, les copies d'un service apparaissent et disparaissent."],
    "show": ["c-gw", "c-vol"] + [f"c-v{i}" for i in range(3)], "links": [],
    "hud": [{"label": "copies", "value": 3}],
    "script": [
        wait(900),
        scene(say="Trois copies du service des vols, chacune avec **son adresse**, qui change à chaque redémarrage.",
              set=[{"id": f"c-v{i}", "tone": "y"} for i in range(3)]),
        wait(900),
        scene(say="Au démarrage, chaque copie **s'inscrit** dans l'annuaire.", show=["c-reg"],
              set=[{"id": f"c-v{i}", "tone": "g"} for i in range(3)],
              link=[L("c-vol", "c-reg", dashed=True)]),
        wait(900),
        scene(say="La passerelle **demande** à l'annuaire où sont les vols.", link=[L("c-gw", "c-reg")]),
        send(["c-gw", "c-reg"], label="où sont les vols ?", reply="3 adresses"),
        scene(say="Puis elle envoie la requête à l'une des copies.", link=[L("c-gw", f"c-v{i}") for i in range(3)]),
        send(["c-gw", "c-v0"], label="GET /vols"),
        scene(say="Une copie tombe : l'annuaire la **retire** de la liste.",
              set=[{"id": "c-v1", "tone": "r", "label": "en panne"}], unlink=[L("c-gw", "c-v1")],
              hud=[hud("copies", 2)]),
        send(["c-gw", "c-v2"], label="GET /vols"),
        scene(say="Les requêtes vont aux **deux copies restantes**, sans rien changer dans la passerelle.", set=[{"id": "c-gw", "label": "rien à changer"}]),
        wait(3000),
    ],
}

# ---------- 4. le BFF
d_ents = [
    ent("d-web", "node", (-14, -4), (6.6, 2.6), "v", title="site web"),
    ent("d-mob", "node", (-14, 4), (6.6, 2.6), "v", title="appli mobile"),
    ent("d-bw", "node", (-3, -4), (7.4, 2.6), "y", title="BFF du site",
        detail="Un **BFF** (*Backend For Frontend*) : un petit back écrit **pour une seule interface**, qui assemble ce qu'elle affiche."),
    ent("d-bm", "node", (-3, 4), (7.4, 2.6), "y", title="BFF mobile"),
]
for (sid, name), y in zip([("vol", "vols"), ("hot", "hôtels"), ("avi", "avis")], [-5.0, 0.0, 5.0]):
    d_ents.append(ent(f"d-{sid}", "node", (11, y), (SW, SH), "g", title=name))
step_d = {
    "id": "bff", "label": "BFF", "title": "Le BFF : un back taillé pour chaque interface",
    "body": ["Le site et l'appli n'affichent pas la même chose."],
    "show": ["d-web", "d-mob", "d-vol", "d-hot", "d-avi"], "links": [],
    "script": [
        wait(900),
        scene(say="L'écran d'un voyage sur mobile montre le vol, l'hôtel et une note. Le site affiche **beaucoup plus**.",
              set=[{"id": "d-mob", "label": "un résumé"}, {"id": "d-web", "label": "page complète"}]),
        wait(1100),
        scene(say="Chaque interface reçoit **son BFF**, écrit par l'équipe qui fait cette interface.",
              show=["d-bw", "d-bm"], link=[L("d-web", "d-bw"), L("d-mob", "d-bm")] +
              [L(b, s) for b in ("d-bw", "d-bm") for s in ("d-vol", "d-hot", "d-avi")]),
        send(["d-mob", "d-bm"], label="écran voyage"),
        scene(say="Le BFF mobile appelle **les trois services**…", set=[{"id": "d-bm", "label": "assemble"}]),
        send(["d-bm", "d-vol"], label="vol"),
        send(["d-bm", "d-hot"], label="hôtel"),
        send(["d-bm", "d-avi"], label="note"),
        scene(say="…et renvoie **une seule réponse**, réduite à ce que l'écran affiche.", set=[{"id": "d-bm", "label": "3 Ko, un appel"}]),
        send(["d-bm", "d-mob"], label="résumé"),
        scene(say="Le site, lui, reçoit sa page complète par **son** BFF : chacun évolue sans gêner l'autre.",
              set=[{"id": "d-bw", "label": "page complète"}]),
        wait(3000),
    ],
}

# ---------- 5. micro-frontends
e_ents = [
    ent("e-page", "layer", (-3, -1), (22, 10), "v", title="une page du site", sub="vue par le visiteur",
        detail="Pour le visiteur, **une seule page**. Derrière, plusieurs morceaux livrés par plusieurs équipes."),
    ent("e-shell", "node", (0, -2.0), (19, 2.2), "n", parent="e-page", title="application hôte (shell)",
        detail="L'**application hôte** (*shell*) charge les morceaux, gère la navigation et la connexion."),
    ent("e-f1", "node", (-6.2, 2.0), (5.8, 3.2), "v", parent="e-page", title="recherche",
        detail="Chaque morceau est un **micro-frontend** : construit et déployé par son équipe."),
    ent("e-f2", "node", (0, 2.0), (5.8, 3.2), "v", parent="e-page", title="hôtels"),
    ent("e-f3", "node", (6.2, 2.0), (5.8, 3.2), "v", parent="e-page", title="avis"),
    ent("e-ds", "node", (12.5, -1), (7, 4.4), "n", title="design system", sub="boutons, couleurs, polices",
        detail="Le **design system** : des composants et des règles visuelles partagés par toutes les équipes."),
]
step_e = {
    "id": "micro-frontends", "label": "Micro-frontends", "title": "Micro-frontends : découper aussi l'interface",
    "body": ["Trois équipes, une seule page."],
    "show": ["e-page", "e-shell", "e-f1", "e-f2", "e-f3"], "links": [],
    "hud": [{"label": "à déployer", "value": 1}],
    "script": [
        wait(900),
        scene(say="Le back est découpé par équipe. Quand **l'interface** devient aussi grosse, on peut la découper pareil.",
              set=[{"id": "e-page", "tone": "y"}]),
        wait(900),
        scene(say="Une **application hôte** charge les morceaux et gère la navigation.",
              set=[{"id": "e-page", "tone": "v"}, {"id": "e-shell", "tone": "y"}]),
        wait(900),
        scene(say="Chaque morceau est un **micro-frontend**, livré par son équipe, à son rythme.",
              set=[{"id": "e-shell", "tone": "n"}, {"id": "e-f1", "label": "équipe Vols, v7"},
                   {"id": "e-f2", "label": "équipe Hôtels, v3"}, {"id": "e-f3", "label": "équipe Avis, v12"}],
              hud=[hud("à déployer", 4)]),
        wait(1200),
        scene(say="Un **design system** partagé garde les boutons et les couleurs identiques partout.",
              show=["e-ds"], link=[L("e-ds", "e-page", dashed=True)]),
        wait(1200),
        scene(say="Le prix : plus de code à charger, des **versions à aligner**, et une page qui dépend de quatre livraisons.",
              set=[{"id": "e-f2", "tone": "r", "label": "boutons v1 ≠ v2"}]),
        wait(3000),
    ],
}

lesson = {
    "format": "bl-scenes/0.3", "id": "api-gateway-bff-microfrontends", "title": "Passerelle, BFF, micro-frontends", "lang": "fr", "kit": "plan",
    "legend": [{"tone": "v", "label": "interface"}, {"tone": "g", "label": "service"},
               {"tone": "y", "label": "point d'entrée"}, {"tone": "n", "label": "outil commun"}],
    "entities": a_ents + b_ents + c_ents + d_ents + e_ents,
    "steps": [step_a, step_b, step_c, step_d, step_e],
}
write(lesson, *outputs(HERE, "gateway.scene.json", "gateway"))
