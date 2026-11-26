"""Scènes 2D (kit plan) du bit « Le prix des micro-services ».

Exemple propre au bit : une plateforme de livraison de repas (commandes, restaurants, livreurs, paiement, notifications).

Dessin, une sorte = un dessin :
- un service (programme déployé seul) = un plateau vert `g`, qui porte ce qu'il contient ;
- un module de code ou une fonction = une boîte pervenche `v` ;
- un journal (logs), une mesure, une trace = une boîte jaune `y` ;
- le réseau = un lien pointillé ; ce qui casse passe en rose `r`.
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

# ---------- 1. un appel de fonction devient un appel réseau
n_ents = [
    ent("n-mono", "layer", (-9.0, 0), (13, 9), "g", title="un seul programme",
        detail="Dans un monolithe, le module Commandes appelle le module Paiement comme une fonction : dans la même mémoire."),
    ent("n-cmd", "node", (0, -2.0), (10.5, B), "v", parent="n-mono", title="commandes"),
    ent("n-pay", "node", (0, 2.4), (10.5, B), "v", parent="n-mono", title="paiement"),
    ent("n-s1", "layer", (9.0, -4.0), (12, 4.4), "g", title="service Commandes",
        detail="Deux services : deux programmes, souvent sur deux machines. Entre eux, le réseau."),
    ent("n-s1c", "node", (0, 0.6), (10, B), "v", parent="n-s1", title="commandes"),
    ent("n-s2", "layer", (9.0, 4.4), (12, 4.4), "g", title="service Paiement"),
    ent("n-s2c", "node", (0, 0.6), (10, B), "v", parent="n-s2", title="paiement"),
]
step_n = {
    "id": "appel-reseau", "label": "Appel réseau", "title": "Un appel de fonction devient un appel réseau",
    "body": ["La même demande, « payer cette commande », dans un programme ou entre deux services."],
    "show": ["n-mono", "n-cmd", "n-pay"], "links": [L("n-cmd", "n-pay")],
    "hud": [{"label": "en mémoire", "value": "—"}, {"label": "par le réseau", "value": "—"}],
    "script": [
        wait(800),
        send(["n-cmd", "n-pay"], label="payer", reply="payé",
             explain=["Dans un seul programme, Commandes appelle Paiement comme une **fonction**.", "La réponse arrive presque aussitôt."]),
        scene(say="Un appel de fonction : quelques **microsecondes**, et il ne se perd pas en route.",
              hud=[hud("en mémoire", "< 0,01 ms", "g")]),
        wait(900),
        scene(say="Avec deux services, la même demande traverse **le réseau**.",
              show=["n-s1", "n-s1c", "n-s2", "n-s2c"], link=[L("n-s1c", "n-s2c", dashed=True)]),
        send(["n-s1c", "n-s2c"], label="payer", reply="payé",
             explain=["La demande part sur le réseau, vers une autre machine.", "La réponse refait le chemin inverse."]),
        scene(say="Quelques **millisecondes** à chaque appel, et l'appel peut **échouer** : réseau coupé, service arrêté.",
              hud=[hud("par le réseau", "5 à 50 ms", "y")]),
        wait(1200),
        scene(say="Une page qui enchaîne dix appels paie dix fois ce prix.", set=[{"id": "n-s2", "tone": "y"}]),
        wait(3000),
    ],
}

# ---------- 2. plusieurs déploiements, des contrats
c_ents = [
    ent("c-cmd", "layer", (-9.0, 0), (12, 6), "g", title="service Commandes",
        detail="Le service Commandes expose une **API** : la liste des demandes qu'il accepte et de ce qu'il répond. C'est un **contrat**."),
    ent("c-cmdv", "node", (0, 0.8), (10, B), "v", parent="c-cmd", title="API v1", sub="champ « adresse »"),
    ent("c-res", "layer", (9.0, 0), (12, 6), "g", title="service Restaurants",
        detail="Le service Restaurants lit les commandes par cette API. Il est déployé par une autre équipe, à un autre moment."),
    ent("c-resv", "node", (0, 0.8), (10, B), "v", parent="c-res", title="lit « adresse »"),
]
step_c = {
    "id": "contrats", "label": "Contrats", "title": "Plusieurs déploiements, un contrat à tenir",
    "body": ["Deux équipes, deux services, deux calendriers de mise en service."],
    "show": [e["id"] for e in c_ents], "links": [L("c-resv", "c-cmdv", dashed=True)],
    "hud": [{"label": "commandes lues", "value": "oui"}],
    "script": [
        wait(800),
        send(["c-resv", "c-cmdv"], label="commande 42 ?", reply="adresse : 3 rue…"),
        scene(say="L'équipe Commandes renomme le champ « adresse » en « livraison », et déploie.",
              set=[{"id": "c-cmdv", "title": "API v2", "sub": "champ « livraison »", "tone": "y"}]),
        wait(800),
        send(["c-resv", "c-cmdv"], label="commande 42 ?", reply="champ inconnu"),
        scene(say="Restaurants n'a pas été redéployé : il cherche encore « adresse ». **Il casse**.",
              set=[{"id": "c-resv", "tone": "r", "label": "adresse introuvable"}], hud=[hud("commandes lues", "non", "r")]),
        wait(1200),
        scene(say="La parade : un **contrat versionné**. La v1 reste servie tant que quelqu'un s'en sert.",
              set=[{"id": "c-cmdv", "title": "API v1 et v2", "sub": "les deux, le temps de migrer", "tone": "g"},
                   {"id": "c-resv", "tone": "v", "label": None}], hud=[hud("commandes lues", "oui", "g")]),
        wait(3000),
    ],
}

# ---------- 3 et 4. déboguer, puis observer (même dessin)
SV = [("o-gw", "accueil", -12.0, -4.0), ("o-cmd", "commandes", 0.0, -4.0), ("o-res", "restaurants", 12.0, -4.0),
      ("o-pay", "paiement", -6.0, 3.0), ("o-not", "notifications", 6.0, 3.0)]
o_ents = []
for i, (sid, name, x, y) in enumerate(SV):
    first = i == 0
    o_ents += [ent(sid, "layer", (x, y), (10, 5.2), "g", title=name,
                   detail="Sur le schéma, cinq services, chacun sur sa machine, chacun avec **son propre journal**." if first else None),
               ent(f"{sid}-log", "node", (0, 0.8), (8.4, 1.6), "y", parent=sid, title="son journal" if first else None,
                   detail="Le **journal** (*log*) : les lignes qu'un programme écrit pour dire ce qu'il fait et ce qui rate." if first else None)]
o_ents += [
    ent("o-central", "node", (0, 10.0), (20, 2.4), "y", title="journaux centralisés", sub="tous les services, un seul endroit",
        detail="Un outil reçoit les journaux de tous les services (Loki, Elasticsearch…) : on cherche au même endroit."),
]
O_LINKS = [L("o-gw", "o-cmd"), L("o-cmd", "o-res"), L("o-cmd", "o-pay"), L("o-pay", "o-not")]
O_SHOW = [e["id"] for e in o_ents if e["id"] != "o-central"]
step_d = {
    "id": "deboguer", "label": "Déboguer", "title": "Une erreur, cinq programmes : où chercher ?",
    "body": ["Un client voit « Erreur, réessayez plus tard ». La commande a traversé quatre services."],
    "show": O_SHOW, "links": O_LINKS,
    "hud": [{"label": "journaux à lire", "value": "—"}],
    "script": [
        wait(800),
        send(["o-gw", "o-cmd", "o-pay", "o-not"], label="commande",
             explain=["L'accueil reçoit la commande et la passe au service Commandes.",
                      "Commandes demande le paiement.", "Paiement prévient Notifications… qui échoue."]),
        scene(say="Notifications échoue. Le client, lui, ne voit qu'une **erreur générique**.",
              set=[{"id": "o-not", "tone": "r"}, {"id": "o-gw-log", "label": "erreur 500"}]),
        wait(1000),
        scene(say="Pour comprendre, il faut lire **cinq journaux**, sur cinq machines, et deviner quelles lignes vont ensemble.",
              set=[{"id": f"{s}-log", "tone": "r"} for s, *_ in SV], hud=[hud("journaux à lire", "5", "r")]),
        wait(3000),
    ],
}
step_o = {
    "id": "observer", "label": "Observer", "title": "Observabilité : journaux centralisés et identifiant de corrélation",
    "body": ["Le même système, mais équipé pour qu'on le comprenne de l'extérieur."],
    "show": O_SHOW, "links": O_LINKS,
    "hud": [{"label": "journaux à lire", "value": "5"}, {"label": "identifiant", "value": "—"}],
    "script": [
        wait(800),
        scene(say="Chaque service envoie ses journaux à **un seul endroit**.",
              show=["o-central"], link=[L(f"{s}-log", "o-central", dashed=True) for s, *_ in SV],
              hud=[hud("journaux à lire", "1 endroit", "g")], ms=1000),
        wait(900),
        scene(say="À l'entrée, la requête reçoit un **identifiant de corrélation**, que chaque service recopie.",
              set=[{"id": "o-gw-log", "label": "id 7f3a"}], hud=[hud("identifiant", "7f3a", "y")]),
        send(["o-gw", "o-cmd", "o-pay", "o-not"], label="id 7f3a",
             explain=["L'accueil transmet l'identifiant avec la commande.", "Commandes le transmet au paiement.",
                      "Paiement le transmet à Notifications."]),
        scene(say="Chacun l'écrit dans ses lignes de journal.",
              set=[{"id": f"{s}-log", "label": "id 7f3a"} for s, *_ in SV[1:]] + [{"id": "o-res-log", "label": None}]),
        wait(900),
        scene(say="Une recherche « 7f3a » montre **tout le parcours**, et la ligne qui a échoué.",
              set=[{"id": "o-not", "tone": "r"}, {"id": "o-central", "label": "7f3a : notifications, délai dépassé"}]),
        wait(3200),
    ],
}

# ---------- 5. quand ne pas faire de micro-services
W_ROWS = [("w1", "une petite équipe", "un seul produit"), ("w2", "un métier qui bouge", "chaque semaine"),
          ("w3", "pas d'outillage", "ni déploiement automatique, ni supervision"), ("w4", "une charge uniforme", "tout monte en même temps")]
Y_ROWS = [("y1", "plusieurs équipes", "chacune son domaine"), ("y2", "des rythmes différents", "chaque partie livre à son pas"),
          ("y3", "une charge à part", "une partie doit tenir seule un pic"), ("y4", "un outillage mûr", "déploiement et supervision automatisés")]
w_ents = [ent("w-left", "layer", (-9.0, 0), (16.5, 14), "n", title="plutôt un monolithe modulaire",
              detail="Dans ces situations, les micro-services ajoutent leurs coûts sans rien apporter."),
          ent("w-right", "layer", (9.0, 0), (16.5, 14), "n", title="les micro-services se justifient",
              detail="Dans ces situations, déployer chaque partie seule apporte plus que ce que ça coûte.")]
for i, (wid, text, sub) in enumerate(W_ROWS):
    w_ents.append(ent(wid, "node", (0, -3.6 + i * 2.8), (14.5, 2.2), "n", parent="w-left", title=text, sub=sub))
for i, (yid, text, sub) in enumerate(Y_ROWS):
    w_ents.append(ent(yid, "node", (0, -3.6 + i * 2.8), (14.5, 2.2), "n", parent="w-right", title=text, sub=sub))
step_w = {
    "id": "quand-pas", "label": "Quand s'en passer", "title": "Quand ne pas faire de micro-services",
    "body": ["Les micro-services répondent à des problèmes d'organisation et de charge. Sans ces problèmes, ils ne répondent à rien."],
    "show": ["w-left", "w-right"], "links": [],
    "script": [
        wait(800),
        scene(say="À gauche, des situations où **un monolithe modulaire** suffit.",
              show=[w for w, *_ in W_ROWS], set=[{"id": "w-left", "tone": "y"}]),
        wait(1600),
        scene(say="À droite, celles où déployer chaque partie **seule** vaut son prix.",
              show=[y for y, *_ in Y_ROWS], set=[{"id": "w-left", "tone": "n"}, {"id": "w-right", "tone": "g"}]),
        wait(1600),
        scene(say="Sans outillage, rien ne compense : c'est la condition qui passe avant toutes les autres.",
              set=[{"id": "w3", "tone": "r"}, {"id": "y4", "tone": "y"}]),
        wait(3200),
    ],
}

lesson = {
    "format": "bl-scenes/0.3", "id": "microservices-costs", "title": "Le prix des micro-services", "lang": "fr", "kit": "plan",
    "legend": [{"tone": "g", "label": "service"}, {"tone": "v", "label": "code"}, {"tone": "y", "label": "journal, mesure"}],
    "entities": n_ents + c_ents + o_ents + w_ents,
    "steps": [step_n, step_c, step_d, step_o, step_w],
}
write(lesson, *outputs(HERE, "costs.scene.json", "costs"))
