"""Scènes (Feuilleté, bl-scenes/0.3) du bit « Réplication, partitionnement et théorème CAP ».

Exemple propre au bit : un site de petites annonces entre particuliers.

Dessin, une sorte = un dessin :
- l'application = un bloc bleu `b` ;
- une base (principale, réplique, partition, nœud) = un `store` ; la principale en bleu `b`, ses répliques en gris `n` ;
- ce qui est en retard passe en jaune `y`, ce qui échoue ou diverge en rose `r`, ce qui est juste en vert `g`.
"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools" / "scenes"))
from paths import outputs
from scene_kit import G, L, scene, send, wait, write, hud, traffic

S = [1.8, 1.8, 1.0]
ents = [
    {"id": "users", "kind": "actor", "at": G(0, 13.0), "label": "les visiteurs",
     "detail": "Les visiteurs lisent beaucoup d'annonces, et en publient peu."},
    {"id": "app", "kind": "node", "at": G(0, 5.0), "size": S, "tone": "b", "title": "application",
     "detail": "L'**application** du site, en plusieurs copies sans état (une seule est dessinée)."},
    {"id": "pri", "kind": "store", "at": G(0, -5.0), "tone": "b", "title": "base principale",
     "detail": "La **principale** reçoit toutes les écritures."},
    {"id": "r1", "kind": "store", "at": G(-9.0, -3.0), "tone": "n", "title": "réplique",
     "detail": "Sur le schéma, deux **répliques** : des copies de la principale, qui servent les lectures."},
    {"id": "r2", "kind": "store", "at": G(9.0, -3.0), "tone": "n"},
    {"id": "s1", "kind": "store", "at": G(-6.5, -4.0), "tone": "b", "title": "partition « Nord »",
     "detail": "Une **partition** (*shard*) : une base qui ne garde qu'une **part** des annonces."},
    {"id": "s2", "kind": "store", "at": G(6.5, -4.0), "tone": "b", "title": "partition « Sud »"},
    {"id": "u-p", "kind": "actor", "at": G(-8.0, 11.0), "label": "client à Paris"},
    {"id": "u-l", "kind": "actor", "at": G(8.0, 11.0), "label": "client à Lyon"},
    {"id": "n-p", "kind": "store", "at": G(-8.0, -1.0), "tone": "b", "title": "nœud de Paris",
     "detail": "Deux **nœuds** : deux machines qui gardent chacune une copie des mêmes données, et se recopient."},
    {"id": "n-l", "kind": "store", "at": G(8.0, -1.0), "tone": "b", "title": "nœud de Lyon"},
]
REPL = [L("users", "app"), L("app", "pri"), L("app", "r1"), L("app", "r2"), L("pri", "r1", dashed=True), L("pri", "r2", dashed=True)]
steps = []

# ---------- 1. réplication
steps.append({
    "id": "replication", "label": "Réplication", "title": "La réplication : des copies pour lire",
    "body": ["Cent lectures pour une écriture. La base principale sature."],
    "show": ["users", "app", "pri"], "links": [L("users", "app"), L("app", "pri")],
    "flows": [traffic(["users", "app"], gap=320)],
    "hud": [hud("lectures", "5 000/s"), hud("charge base", "95 %", "r")],
    "script": [
        wait(1500),
        scene(say="Deux **répliques** rejoignent la principale. Chaque écriture leur est **recopiée**.",
              show=["r1", "r2"], link=[L("pri", "r1", dashed=True), L("pri", "r2", dashed=True), L("app", "r1"), L("app", "r2")]),
        send(["app", "pri"], label="publier l'annonce", explain=["Les **écritures** vont toujours à la principale."]),
        send(["pri", "r1"], label="copie"),
        scene(say="Les **écritures** vont à la principale ; les **lectures** se répartissent sur les répliques.",
              set=[{"id": "r1", "label": "lectures"}, {"id": "r2", "label": "lectures"}, {"id": "pri", "label": "écritures"}]),
        send(["app", "r2"], label="lire", reply="annonce"),
        scene(say="Trois machines se partagent les lectures : la charge de chacune **baisse**.",
              hud=[hud("charge base", "35 %", "g")]),
        wait(3000),
    ],
})

# ---------- 2. le retard de réplication
steps.append({
    "id": "retard", "label": "Le retard", "title": "Le retard de réplication : l'annonce introuvable",
    "body": ["La recopie prend un peu de temps. Parfois, ça se voit."],
    "show": ["users", "app", "pri", "r1", "r2"], "links": REPL,
    "hud": [hud("retard", "0,5 s")],
    "script": [
        wait(900),
        send(["users", "app", "pri"], label="publier « vélo »", reply="publiée"),
        scene(say="Une visiteuse publie une annonce de vélo. La principale l'enregistre.",
              set=[{"id": "pri", "label": "vélo : oui", "tone": "g"}]),
        send(["users", "app", "r1"], label="mes annonces ?", reply="aucune"),
        scene(say="Elle recharge la page. La lecture tombe sur une réplique **pas encore à jour** : « aucune annonce ».",
              set=[{"id": "r1", "label": "vélo : pas encore", "tone": "y"}]),
        wait(1300),
        scene(say="Une demi-seconde plus tard, la copie arrive : la réplique finit par dire la même chose. C'est la **cohérence à terme**.",
              set=[{"id": "r1", "label": "vélo : oui", "tone": "n"}]),
        wait(1300),
        scene(say="Parade courante : juste après une écriture, **relire ses propres données** sur la principale.",
              set=[{"id": "app", "label": "relit sur la principale"}]),
        send(["app", "pri"], label="mes annonces ?", reply="vélo"),
        wait(3000),
    ],
})

# ---------- 3. partitionnement
steps.append({
    "id": "partitionnement", "label": "Partitionnement", "title": "Le partitionnement : couper les données en parts",
    "body": ["Trop d'annonces et trop d'écritures pour une seule principale."],
    "show": ["users", "app", "pri"], "links": [L("users", "app"), L("app", "pri")],
    "hud": [hud("annonces", "80 millions")],
    "script": [
        wait(900),
        scene(say="Les répliques aident à lire, pas à **écrire** : toutes les écritures passent encore par une seule machine.",
              set=[{"id": "pri", "label": "pleine", "tone": "r"}]),
        wait(1300),
        scene(say="On coupe les annonces en **partitions**, selon une **clé** : ici, la région.",
              hide=["pri"], show=["s1", "s2"], link=[L("app", "s1"), L("app", "s2")], ms=900),
        send(["app", "s1"], label="annonce à Lille"),
        send(["app", "s2"], label="annonce à Nice"),
        scene(say="Chaque partition garde **sa part** et reçoit **ses** écritures. Chacune a ses propres répliques.",
              set=[{"id": "s1", "label": "40 millions"}, {"id": "s2", "label": "40 millions"}]),
        wait(1300),
        scene(say="Deux pièges : une recherche « dans toute la France » doit interroger **toutes** les partitions…",
              set=[{"id": "app", "label": "recherche : 2 partitions"}]),
        wait(1300),
        scene(say="…et l'été, le Sud reçoit trois fois plus d'annonces : une partition **trop chaude**. Le choix de la clé décide de tout.",
              set=[{"id": "s2", "label": "l'été : ×3", "tone": "r"}, {"id": "app", "label": None}]),
        wait(3000),
    ],
})

# ---------- 4. CAP
steps.append({
    "id": "cap", "label": "CAP", "title": "Le réseau se coupe : cohérence ou disponibilité",
    "body": ["Deux nœuds, à Paris et à Lyon, gardent les mêmes données et se recopient."],
    "show": ["u-p", "u-l", "n-p", "n-l"], "links": [L("u-p", "n-p"), L("u-l", "n-l"), L("n-p", "n-l", dashed=True)],
    "hud": [hud("réseau", "relié"), hud("Paris", "50 €"), hud("Lyon", "50 €")],
    "script": [
        wait(900),
        scene(say="Tant que le réseau tient, une écriture à Paris est recopiée à Lyon : les deux disent la **même chose**.",
              set=[{"id": "n-p", "label": "vélo : 50 €"}, {"id": "n-l", "label": "vélo : 50 €"}]),
        wait(1300),
        scene(say="Le lien entre les deux villes **se coupe**. Chaque nœud marche, mais ils ne se parlent plus : c'est une **partition réseau**.",
              unlink=[L("n-p", "n-l", dashed=True)], hud=[hud("réseau", "coupé", "r")]),
        send(["u-p", "n-p"], label="vélo à 40 €", reply="enregistré"),
        scene(say="À Paris, le vendeur baisse son prix. Lyon ne peut pas le savoir. Un client lyonnais demande le prix : **deux choix**.",
              set=[{"id": "n-p", "label": "vélo : 40 €"}], hud=[hud("Paris", "40 €")]),
        send(["u-l", "n-l"], label="prix ?", reply="indisponible"),
        scene(say="**Cohérence** : Lyon refuse de répondre plutôt que de risquer un prix faux. Le service est **indisponible** pour ce client.",
              set=[{"id": "n-l", "label": "refuse : pas sûr", "tone": "y"}], hud=[hud("Lyon", "pas de réponse", "y")]),
        wait(1300),
        send(["u-l", "n-l"], label="prix ?", reply="50 €"),
        scene(say="**Disponibilité** : Lyon répond avec ce qu'il a, 50 €. Le service répond, mais la réponse est **périmée**.",
              set=[{"id": "n-l", "label": "répond : 50 €", "tone": "r"}], hud=[hud("Lyon", "50 €, périmé", "r")]),
        wait(1300),
        scene(say="Le réseau revient : les nœuds se **réconcilient**. Pendant la coupure, il fallait choisir l'un **ou** l'autre.",
              link=[L("n-p", "n-l", dashed=True)], set=[{"id": "n-l", "label": "vélo : 40 €", "tone": "b"}], hud=[hud("réseau", "relié", "g"), hud("Lyon", "40 €", "g")]),
        wait(3000),
    ],
})

lesson = {
    "format": "bl-scenes/0.3", "id": "replication-sharding-cap", "title": "Réplication, partitionnement, CAP", "lang": "fr", "kit": "feuillete",
    "legend": [{"kind": "req", "label": "requête"}, {"kind": "res", "label": "réponse"}],
    "entities": ents, "steps": steps,
}
write(lesson, *outputs(HERE, "data.scene.json", "data"))
