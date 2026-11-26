"""Scènes du bit « Tenir la charge » (courses-software-architecture/scaling-load-balancing), format 0.4.

Exemple propre au bit : la billetterie en ligne d'un festival, le jour où la vente ouvre.

Dessin (kit Feuilleté), une sorte = un dessin :
- les spectateurs = un acteur, devant (en bas) ;
- un serveur d'application = un node bleu `b` ; le premier porte le nom, les copies seulement leur état ;
- le répartiteur / reverse proxy = un node pervenche `v` ;
- le serveur de fichiers fixes = un node neutre `n` ; le magasin de sessions = un store jaune `y`.
Lecture de bas en haut : spectateurs → répartiteur → serveurs.
L'étape « playground » reprend le dessin de l'étape « horizontal » (règle : même dessin, on regarde puis on joue).
"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools" / "scenes"))
from paths import outputs
from scene_kit import G, L, scene, send, wait, write, hud, traffic

S = [1.8, 1.8, 1.0]
ROW = -2.0
X3 = [-4.5, 0, 4.5]

DS = ("Un **serveur d'application** fait tourner la billetterie. Sur le schéma, plusieurs copies identiques : "
      "elles forment **un seul tiers**, puisqu'on compte les niveaux de machines, pas les exemplaires.")
ents = [
    {"id": "users", "kind": "actor", "at": G(0, 13.0), "label": "les spectateurs",
     "detail": "Les spectateurs envoient leurs requêtes à **une seule adresse**, celle du site. Ils ne savent pas quelle machine leur répond."},
    {"id": "solo", "kind": "node", "at": G(0, 3.0), "size": S, "tone": "b", "title": "serveur d'application",
     "detail": "Une seule machine fait tout tourner. Sa **capacité** : le nombre de requêtes par seconde qu'elle sert sans ralentir."},
    {"id": "big", "kind": "node", "at": G(0, 3.0), "size": [2.8, 2.8, 1.6], "tone": "b", "title": "serveur d'application",
     "sub": "4 fois plus puissant",
     "detail": "La même application sur une machine plus puissante : plus de processeurs, plus de mémoire. C'est la **mise à l'échelle verticale**."},
    {"id": "lb", "kind": "node", "at": G(0, 5.6), "size": S, "tone": "v", "title": "répartiteur", "sub": "à tour de rôle",
     "detail": "Le **répartiteur de charge** (*load balancer*) reçoit toutes les requêtes et les distribue aux copies. "
               "Il vérifie aussi, toutes les quelques secondes, que chaque copie répond : ce sont les **contrôles de santé**."},
    {"id": "static", "kind": "node", "at": G(-9.0, -2.0), "size": S, "tone": "n", "title": "fichiers fixes", "sub": "images, CSS, JS",
     "detail": "Un serveur qui ne fait que renvoyer des fichiers qui ne changent pas : affiches, feuilles de style, scripts."},
    {"id": "sessions", "kind": "store", "at": G(0, -8.5), "tone": "y", "title": "magasin de sessions",
     "detail": "Un **magasin de sessions** partagé (Redis, Memcached ou la base de données) : toutes les copies y lisent qui est connecté et ce qu'il y a dans son panier."},
]
for k in range(1, 6):
    e = {"id": f"web{k}", "kind": "node", "at": G(X3[(k - 1) % 3], ROW), "size": S, "tone": "b"}
    if k == 1:
        e.update(title="serveur d'application", detail=DS)
    ents.append(e)

LB3 = [L("lb", "web1"), L("lb", "web2"), L("lb", "web3")]
TRAFFIC = traffic(["users", "lb"], gap=300, fallback="erreur")

steps = []

# ---------- 1. une seule machine : on mesure
steps.append({
    "id": "une-machine", "label": "Une machine", "title": "Une machine, et la vente qui ouvre",
    "body": ["La vente ouvre à 10 h. Le trafic grimpe, la machine sature."],
    "show": ["users", "solo"], "links": [L("users", "solo")],
    "flows": [traffic(["users", "solo"], gap=420)],
    "hud": [hud("trafic", "100 req/s"), hud("temps de réponse", "80 ms"), hud("échecs", "0 %")],
    "script": [
        wait(1800),
        scene(say="9 h 59 : cent requêtes par seconde, la machine est **chargée à 50 %**.",
              set=[{"id": "solo", "label": "charge 50 %"}]),
        wait(1600),
        scene(say="10 h : la vente ouvre, le trafic est multiplié par **six**.",
              set=[{"id": "solo", "label": "charge 300 %", "tone": "r"}],
              hud=[hud("trafic", "600 req/s", "r"), hud("temps de réponse", "2 s", "r")]),
        wait(1400),
        scene(say="Elle ne sert que ce qu'elle peut : le reste attend, puis **échoue**.",
              hud=[hud("échecs", "66 %", "r")]),
        wait(3000),
    ],
})

# ---------- 2. vertical
steps.append({
    "id": "vertical", "label": "Vertical", "title": "Mise à l'échelle verticale : une machine plus grosse",
    "body": ["Première idée : la même application, sur une machine plus puissante."],
    "show": ["users", "solo"], "links": [L("users", "solo")],
    "hud": [hud("trafic", "600 req/s"), hud("en service", "oui"), hud("échecs", "66 %", "r")],
    "script": [
        wait(600),
        send(["users", "solo"], label="réserver", reply="erreur"),
        scene(say="Pour changer de machine, on **arrête** l'application : le site est coupé.",
              hide=["solo"], hud=[hud("en service", "non", "r"), hud("échecs", "100 %", "r")]),
        wait(1200),
        scene(say="Elle redémarre sur une machine **quatre fois plus puissante**.",
              show=["big"], link=[L("users", "big")], hud=[hud("en service", "oui", None)], ms=1000),
        wait(800),
        scene(say="Elle tient les 600 requêtes par seconde.",
              set=[{"id": "big", "label": "charge 75 %"}], hud=[hud("échecs", "0 %", None)]),
        send(["users", "big"], label="réserver", reply="confirmé"),
        wait(1400),
        scene(say="Mais une machine a un **plafond**, coûte de plus en plus cher, et reste **seule** : si elle tombe, tout tombe.",
              set=[{"id": "big", "tone": "y"}]),
        wait(3000),
    ],
})

# ---------- 3. horizontal (même dessin que le playground)
steps.append({
    "id": "horizontal", "label": "Horizontal", "title": "Mise à l'échelle horizontale : des copies et un répartiteur",
    "body": ["Deuxième idée : plusieurs copies de la même application, et une seule adresse devant."],
    "show": ["users", "lb", "web1"], "links": [L("lb", "web1")],
    "flows": [TRAFFIC],
    "hud": [hud("trafic", "600 req/s"), hud("en service", "1"), hud("échecs", "66 %", "r")],
    "script": [
        wait(1600),
        scene(say="Devant, un **répartiteur** reçoit toutes les requêtes. Pour l'instant, une seule copie derrière.",
              set=[{"id": "web1", "label": "charge 300 %", "tone": "r"}]),
        wait(1400),
        scene(say="On démarre **deux copies** de plus, identiques. Le répartiteur les ajoute.",
              show=["web2", "web3"], link=[L("lb", "web2"), L("lb", "web3")],
              set=[{"id": "web1", "label": "charge 100 %", "tone": "y"}],
              hud=[hud("en service", "3"), hud("échecs", "0 %", None)], ms=1000),
        wait(1400),
        scene(say="Chaque copie reçoit **un tiers** du trafic, à tour de rôle.",
              set=[{"id": "web1", "label": None, "tone": None}]),
        wait(1400),
        scene(say="Le jour où le trafic double encore, on ajoute des copies : **sans arrêter** le site.",
              set=[{"id": "lb", "tone": "y"}]),
        wait(3000),
    ],
})

# ---------- 4. reverse proxy
steps.append({
    "id": "reverse-proxy", "label": "Reverse proxy", "title": "Répartiteur et reverse proxy",
    "body": ["La même machine de devant peut faire plus que répartir."],
    "show": ["users", "lb", "web1", "web2", "web3"], "links": LB3,
    "hud": [hud("adresse publique", "1"), hud("machines cachées", "3")],
    "script": [
        wait(900),
        scene(say="Un **reverse proxy** reçoit les requêtes **à la place** des serveurs : ils restent cachés derrière lui.",
              set=[{"id": "lb", "title": "reverse proxy", "sub": "et répartiteur"}]),
        wait(800),
        scene(say="Il peut **aiguiller** selon l'adresse : les affiches vont au serveur de fichiers fixes…",
              show=["static"], link=[L("lb", "static")], hud=[hud("machines cachées", "4")]),
        send(["users", "lb", "static"], label="/affiche.jpg", reply="image"),
        send(["users", "lb", "web2"], label="/reserver", reply="confirmé",
             explain=["Le spectateur réserve : la requête arrive au reverse proxy.",
                      "…et les réservations vont à l'une des copies de l'application.",
                      "La réponse revient par le même chemin."]),
        scene(say="Il porte aussi souvent le **chiffrement HTTPS**, pour que les copies n'aient pas à le faire.",
              set=[{"id": "lb", "label": "HTTPS ici"}]),
        wait(3000),
    ],
})

# ---------- 5. sans état
steps.append({
    "id": "sans-etat", "label": "Sans état", "title": "Des copies sans état",
    "body": ["Une copie ne doit rien garder pour elle que les autres auraient besoin de savoir."],
    "show": ["users", "lb", "web1", "web2", "web3"], "links": LB3,
    "hud": [hud("panier retrouvé", "—")],
    "script": [
        wait(900),
        send(["users", "lb", "web1"], label="2 billets au panier", reply="ajoutés",
             explain=["Le spectateur met deux billets dans son panier.",
                      "La requête tombe sur la première copie, qui garde le panier **dans sa mémoire**.",
                      "Elle répond : c'est ajouté."]),
        scene(say="La première copie garde le panier pour elle : c'est son **état**.",
              set=[{"id": "web1", "label": "panier : 2 billets"}]),
        send(["users", "lb", "web2"], label="payer", reply="panier vide",
             explain=["Le spectateur clique sur « Payer ».", "À tour de rôle, la requête part vers la deuxième copie.",
                      "Elle ne connaît pas ce panier : il est vide."]),
        scene(say="La deuxième copie n'a jamais vu ce panier : **panier vide**.",
              set=[{"id": "web2", "label": "panier vide ?", "tone": "r"}], hud=[hud("panier retrouvé", "non", "r")]),
        wait(1200),
        scene(say="Le remède : ranger l'état **hors des copies**, dans un magasin de sessions partagé.",
              show=["sessions"], link=[L("web1", "sessions"), L("web2", "sessions"), L("web3", "sessions")],
              set=[{"id": "web1", "label": None}, {"id": "web2", "label": None, "tone": None}], ms=1000),
        send(["users", "lb", "web3", "sessions"], label="payer", reply="2 billets",
             explain=["Le spectateur paie.", "La requête tombe sur la troisième copie.",
                      "Elle lit le panier dans le magasin partagé.", "Elle le retrouve : deux billets."]),
        scene(say="N'importe quelle copie sert n'importe qui : les copies sont **sans état**.",
              hud=[hud("panier retrouvé", "oui", "g")]),
        wait(3000),
    ],
})

# ---------- 6. playground
steps.append({
    "id": "playground", "label": "À toi", "title": "À toi : tenir la vente",
    "body": ["Monte le trafic, coupe une copie, ajoutes-en : la scène suit."],
    "hud": [hud("trafic", "300 req/s"), hud("en service", "3 / 3"), hud("échecs", "0 %")],
    "flows": [TRAFFIC],
    "show": ["users", "lb", "web1", "web2", "web3"], "links": LB3,
    "sim": {
        "model": "load-balancer", "balancer": "lb",
        "servers": [{"id": "web1"}, {"id": "web2"}, {"id": "web3"}, {"id": "web4"}, {"id": "web5"}],
        "traffic": {"value": 300, "min": 50, "max": 1200, "step": 50},
        "capacity": {"value": 200, "min": 100, "max": 400, "step": 10},
        "health": 3000, "boot": 3500,
        "algorithms": ["round-robin"],
        "spike": {"factor": 3, "ms": 6000},
        "controls": ["traffic", "servers", "add", "spike"],
        "chart": True,
        "guide": [
            {"say": "Monte le trafic jusqu'à 900 requêtes par seconde.", "until": {"traffic": 900},
             "done": "Trois copies de 200 requêtes par seconde : il en manque, des requêtes échouent."},
            {"say": "Ajoute des copies jusqu'à ne plus avoir d'échecs.", "until": {"inService": 5, "failedMax": 0},
             "done": "Cinq copies en service : la charge passe, et aucune n'a été arrêtée pour ça."},
            {"say": "Fais tomber une copie : décoche web1.", "until": {"down": "web1"},
             "done": "Tant que les contrôles de santé ne l'ont pas retirée, ses requêtes échouent."},
            {"say": "Attends que le répartiteur la retire.", "until": {"retired": "web1"},
             "done": "Retirée : les autres prennent sa part. Avec une seule grosse machine, le site serait coupé."},
        ],
    },
})

lesson = {
    "format": "bl-scenes/0.4", "id": "scaling-load-balancing", "title": "Tenir la charge", "lang": "fr", "kit": "feuillete",
    "legend": [{"kind": "req", "label": "requête"}, {"tone": "b", "label": "application"},
               {"tone": "v", "label": "répartiteur"}],
    "entities": ents, "steps": steps,
}
write(lesson, *outputs(HERE, "scaling.scene.json", "scaling"))
