"""Scènes (Feuilleté, bl-scenes/0.3) du bit « Rester en service : SPOF, redondance, bascule ».

Exemple propre au bit : une épicerie en ligne, dont le site doit prendre des commandes jour et nuit.

Dessin, une sorte = un dessin :
- un programme (répartiteur, application) = un bloc ; le répartiteur en pervenche `v`, l'application en bleu `b` ;
- une base = un `store` bleu `b` ; sa copie de secours (réplique) aussi, estompée tant qu'elle ne sert pas ;
- un centre de données = une `zone` grise ;
- un point unique de défaillance passe en jaune `y`, ce qui tombe en rose `r`, ce qui prend le relais en vert `g`.
"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools" / "scenes"))
from paths import outputs
from scene_kit import G, L, scene, send, wait, write, hud, traffic

S = [1.8, 1.8, 1.0]
X3 = [-5.0, 0.0, 5.0]
ents = [
    {"id": "users", "kind": "actor", "at": G(0, 14.0), "label": "les clients",
     "detail": "Les clients passent commande à toute heure."},
    {"id": "lb", "kind": "node", "at": G(0, 6.5), "size": S, "tone": "v", "title": "répartiteur",
     "detail": "Le **répartiteur** distribue les requêtes aux copies de l'application."},
    {"id": "lb2", "kind": "node", "at": G(6.5, 6.5), "size": S, "tone": "v", "title": "répartiteur de secours",
     "detail": "Un second répartiteur, prêt à reprendre l'**adresse** du premier s'il tombe."},
    {"id": "db", "kind": "store", "at": G(-3.5, -8.0), "tone": "b", "title": "base principale",
     "detail": "La **base principale** reçoit toutes les écritures : commandes, stocks, paiements."},
    {"id": "db2", "kind": "store", "at": G(4.5, -8.0), "tone": "b", "title": "réplique",
     "detail": "Une **réplique** : une copie de la base, tenue à jour en continu par la principale."},
]
for k in range(3):
    e = {"id": f"app{k}", "kind": "node", "at": G(X3[k], -0.5), "size": S, "tone": "b"}
    if k == 0:
        e.update(title="application", detail="Sur le schéma, trois **copies** de l'application, sans état.")
    ents.append(e)
# zones (étape « zones »), en coordonnées du plan
ZA, ZB = [-3.6, 1.6], [1.6, -3.6]
ents += [
    {"id": "zone-a", "kind": "zone", "at": ZA, "size": [5.6, 5.6], "tone": "n", "label": "centre A"},
    {"id": "zone-b", "kind": "zone", "at": ZB, "size": [5.6, 5.6], "tone": "n", "label": "centre B"},
    {"id": "za-app", "kind": "node", "at": [ZA[0] + 1.1, ZA[1] + 1.1], "size": S, "tone": "b", "title": "application"},
    {"id": "zb-app", "kind": "node", "at": [ZB[0] + 1.1, ZB[1] + 1.1], "size": S, "tone": "b"},
    {"id": "za-db", "kind": "store", "at": [ZA[0] - 1.2, ZA[1] - 1.2], "tone": "b", "title": "base"},
    {"id": "zb-db", "kind": "store", "at": [ZB[0] - 1.2, ZB[1] - 1.2], "tone": "b"},
    {"id": "z-lb", "kind": "node", "at": [4.2, 4.2], "size": S, "tone": "v", "title": "répartiteur", "sub": "géré, dans les deux centres"},
    {"id": "z-users", "kind": "actor", "at": [7.6, 7.6], "label": "les clients"},
]
APPS = [f"app{k}" for k in range(3)]
BASE_LINKS = [L("users", "lb")] + [L("lb", a) for a in APPS] + [L(a, "db") for a in APPS]
TRAFFIC = traffic(["users", "lb"], gap=320, fallback="erreur")
steps = []

# ---------- 1. SPOF
steps.append({
    "id": "spof", "label": "SPOF", "title": "Trouver les points uniques de défaillance",
    "body": ["Trois copies de l'application. Le site est-il à l'abri d'une panne ?"],
    "show": ["users", "lb", "db"] + APPS, "links": BASE_LINKS,
    "flows": [TRAFFIC],
    "hud": [hud("en service", "oui"), hud("échecs", "0 %")],
    "script": [
        wait(1800),
        scene(say="Une copie de l'application tombe : les deux autres **prennent le relais**. Rien ne se voit.",
              set=[{"id": "app1", "label": "en panne", "tone": "r"}], unlink=[L("lb", "app1"), L("app1", "db")]),
        wait(1600),
        scene(say="Mais il n'y a qu'**un** répartiteur, et qu'**une** base.",
              set=[{"id": "app1", "label": None, "tone": "b"}, {"id": "lb", "tone": "y", "label": "un seul"}, {"id": "db", "tone": "y", "label": "une seule"}],
              link=[L("lb", "app1"), L("app1", "db")]),
        wait(1500),
        scene(say="La base tombe : les trois copies n'ont plus de données, **tout le site** est coupé.",
              set=[{"id": "db", "tone": "r", "label": "en panne"}], hud=[hud("en service", "non", "r"), hud("échecs", "100 %", "r")]),
        wait(1300),
        scene(say="Un élément dont la panne arrête tout s'appelle un **point unique de défaillance** (*SPOF*).",
              set=[{"id": "db", "tone": "y", "label": "SPOF"}, {"id": "lb", "label": "SPOF"}]),
        wait(3000),
    ],
})

# ---------- 2. redondance
steps.append({
    "id": "redondance", "label": "Redondance", "title": "La redondance : un second exemplaire de chaque élément",
    "body": ["Pour chaque SPOF, un second exemplaire prêt à servir."],
    "show": ["users", "lb", "db"] + APPS, "links": BASE_LINKS,
    "hud": [hud("SPOF", 2, "y")],
    "script": [
        wait(900),
        scene(say="La base reçoit une **réplique** : une copie tenue à jour en continu.",
              show=[{"id": "db2", "dim": True}], link=[L("db", "db2", dashed=True)]),
        send(["db", "db2"], label="commande 512"),
        scene(say="Chaque écriture de la principale est **recopiée** sur la réplique : c'est la **réplication**.",
              set=[{"id": "db2", "label": "à jour"}], hud=[hud("SPOF", 1, "y")]),
        wait(1200),
        scene(say="Le répartiteur a un **jumeau**, prêt à reprendre son adresse s'il tombe.",
              show=[{"id": "lb2", "dim": True}], link=[L("lb", "lb2", dashed=True)], hud=[hud("SPOF", 0, "g")]),
        wait(1300),
        scene(say="Plus aucun élément n'est seul. C'est la **redondance** : elle coûte deux fois plus de machines.",
              set=[{"id": "db", "tone": "b"}, {"id": "lb", "tone": "v"}]),
        wait(3000),
    ],
})

# ---------- 3. bascule
steps.append({
    "id": "bascule", "label": "Bascule", "title": "La bascule : la réplique prend le relais",
    "body": ["La base principale tombe en pleine soirée."],
    "show": ["users", "lb", "db", "db2"] + APPS, "links": BASE_LINKS + [L("db", "db2", dashed=True)],
    "flows": [TRAFFIC],
    "hud": [hud("en service", "oui"), hud("coupure", "0 s")],
    "script": [
        wait(1800),
        scene(say="La base principale tombe. Les écritures **échouent**.",
              set=[{"id": "db", "tone": "r", "label": "en panne"}], hud=[hud("en service", "non", "r")]),
        wait(1300),
        scene(say="Des **contrôles de santé** constatent qu'elle ne répond plus, plusieurs fois de suite.",
              set=[{"id": "db2", "label": "principale ? pas de réponse"}], hud=[hud("coupure", "10 s", "r")]),
        wait(1300),
        scene(say="La réplique est **promue** : elle devient la base principale, et les copies s'y connectent.",
              set=[{"id": "db2", "tone": "g", "label": "nouvelle principale", "title": "base principale"}, {"id": "db", "dim": True}],
              unlink=[L(a, "db") for a in APPS] + [L("db", "db2", dashed=True)], link=[L(a, "db2") for a in APPS],
              hud=[hud("en service", "oui", "g"), hud("coupure", "20 s", "y")]),
        wait(1500),
        scene(say="Le site revient après **une vingtaine de secondes**. Si la recopie avait du retard, les toutes dernières commandes peuvent manquer.",
              set=[{"id": "db2", "label": "il manque 2 commandes ?"}]),
        wait(3000),
    ],
})

# ---------- 4. zones
steps.append({
    "id": "zones", "label": "Deux centres", "title": "Deux centres de données : survivre à une panne de site",
    "body": ["Un orage coupe le courant de tout un centre de données."],
    "show": ["z-users", "z-lb", "zone-a", "zone-b", "za-app", "zb-app", "za-db", "zb-db"],
    "links": [L("z-users", "z-lb"), L("z-lb", "za-app"), L("z-lb", "zb-app"), L("za-app", "za-db"), L("zb-app", "zb-db"), L("za-db", "zb-db", dashed=True)],
    "hud": [hud("en service", "oui")],
    "script": [
        wait(900),
        scene(say="Tout est en double, mais **au même endroit** : une coupure de courant emporte les deux exemplaires.",
              set=[{"id": "zone-a", "tone": "y"}]),
        wait(1300),
        scene(say="On répartit donc les exemplaires dans **deux centres de données**, éloignés l'un de l'autre.",
              set=[{"id": "zone-a", "tone": "n"}, {"id": "za-db", "label": "principale"}, {"id": "zb-db", "label": "réplique"}]),
        send(["z-users", "z-lb", "za-app"], label="commande"),
        scene(say="Le centre A perd le courant : son application et sa base tombent **ensemble**.",
              set=[{"id": "zone-a", "tone": "r"}, {"id": "za-app", "tone": "r", "label": "hors service"}, {"id": "za-db", "tone": "r", "label": "hors service"}],
              unlink=[L("z-lb", "za-app")], hud=[hud("en service", "bascule…", "y")]),
        wait(1300),
        scene(say="Le centre B **prend tout** : sa réplique est promue, le répartiteur ne lui envoie plus que lui.",
              set=[{"id": "zb-db", "tone": "g", "label": "nouvelle principale"}], hud=[hud("en service", "oui", "g")]),
        send(["z-users", "z-lb", "zb-app"], label="commande"),
        wait(3000),
    ],
})

lesson = {
    "format": "bl-scenes/0.3", "id": "high-availability", "title": "Haute disponibilité", "lang": "fr", "kit": "feuillete",
    "legend": [{"kind": "req", "label": "requête"}, {"kind": "res", "label": "réponse"}],
    "entities": ents, "steps": steps,
}
write(lesson, *outputs(HERE, "ha.scene.json", "ha"))
