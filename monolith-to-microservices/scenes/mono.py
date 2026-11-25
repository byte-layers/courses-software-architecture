"""Scènes 2D (kit plan) du bit « Monolithe, monolithe modulaire, micro-services ».

Exemple propre au bit : la boutique en ligne d'un vendeur de vélos (catalogue, panier, paiement, livraison).

Dessin, une sorte = un dessin :
- une unité de déploiement (ce qu'on livre d'un bloc) = un plateau vert `g` ;
- un module de code = une boîte pervenche `v` ;
- des données (tables, base) = une boîte bleue `b` ;
- une machine = un plateau gris `n` ;
- ce qu'on veut faire remarquer passe en jaune `y`, ce qui casse en rose `r`.
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
MODS = [("cat", "catalogue"), ("pan", "panier"), ("pay", "paiement"), ("liv", "livraison")]

# ---------- 1. déployer
d_ents = [
    ent("d-src", "node", (-13, 0), (7, 2.6), "y", title="code source", sub="des centaines de fichiers",
        detail="Le **code source** de la boutique : ce que les développeurs écrivent et modifient."),
    ent("d-build", "node", (-4.3, 0), (7, 2.6), "v", title="construction", sub="compiler, empaqueter, tester",
        detail="La **construction** (*build*) transforme le code en quelque chose qu'on peut lancer, et passe les tests."),
    ent("d-art", "node", (4.3, 0), (7, 2.6), "g", title="artefact", sub="une archive, une image",
        detail="L'**artefact** : le paquet prêt à lancer (une archive `.jar`, une image de conteneur…). C'est lui qu'on livre."),
    ent("d-srv", "layer", (13, 0), (7.4, 5.0), "n", title="serveur",
        detail="La machine où tourne la version en service."),
    ent("d-run", "node", (0, 0.8), (6, B), "g", parent="d-srv", title="v1 en service"),
]
step_d = {
    "id": "deployer", "label": "Déployer", "title": "Déployer : mettre une nouvelle version en service",
    "body": ["Une ligne de code corrigée n'aide personne tant qu'elle n'est pas en service."],
    "show": ["d-src", "d-srv", "d-run"], "links": [],
    "hud": [{"label": "en service", "value": "v1"}],
    "script": [
        wait(900),
        scene(say="Un développeur corrige le calcul des frais de port dans le **code source**.",
              set=[{"id": "d-src", "label": "frais de port corrigés"}]),
        wait(700),
        scene(say="La **construction** compile, empaquette et passe les tests.", show=["d-build"], link=[L("d-src", "d-build")]),
        send(["d-src", "d-build"], label="v2"),
        scene(say="Elle produit un **artefact** : le paquet prêt à lancer.", show=["d-art"], link=[L("d-build", "d-art")]),
        send(["d-build", "d-art"], label="v2"),
        scene(say="**Déployer**, c'est installer cet artefact et le mettre en service à la place de l'ancien.",
              link=[L("d-art", "d-run")]),
        send(["d-art", "d-run"], label="v2"),
        scene(say="Ce qu'on livre d'un bloc s'appelle une **unité de déploiement**.",
              set=[{"id": "d-run", "title": "v2 en service", "tone": "y"}], hud=[hud("en service", "v2")]),
        wait(3000),
    ],
}

# ---------- 2. le monolithe
MX, MW, MH = -8.5, 14.0, 10.0
POS4 = [(-3.4, -1.4), (3.4, -1.4), (-3.4, 2.6), (3.4, 2.6)]
m_ents = [ent("m-app", "layer", (MX, 0), (MW, MH), "g", title="boutique", sub="une seule unité de déploiement",
              detail="Tout le code de la boutique est construit et livré **d'un bloc** : un seul artefact.")]
for (mid, name), (x, y) in zip(MODS, POS4):
    m_ents.append(ent(f"m-{mid}", "node", (x, y), (6.0, B), "v", parent="m-app", title=name))
for i, y in enumerate([-6.0, 0.0, 6.0]):
    m_ents += [ent(f"m-s{i}", "layer", (9.5, y), (8.0, 4.2), "n", title="serveur" if i == 0 else None,
                   detail="Sur le schéma, trois serveurs : trois **copies** du même artefact, derrière un répartiteur." if i == 0 else None),
               ent(f"m-c{i}", "node", (0, 0.6), (6.4, B), "g", parent=f"m-s{i}", title="boutique v1")]
step_m = {
    "id": "monolithe", "label": "Monolithe", "title": "Le monolithe : tout se déploie ensemble",
    "body": ["Une boutique, quatre modules, un seul artefact."],
    "show": ["m-app"] + [f"m-{m}" for m, _ in MODS], "links": [],
    "hud": [{"label": "à déployer", "value": 1}],
    "script": [
        wait(900),
        scene(say="Quatre modules dans le code, mais **un seul artefact** : c'est un **monolithe**.",
              set=[{"id": "m-app", "tone": "y"}]),
        wait(900),
        scene(say="On le fait tourner sur **trois serveurs** pour tenir la charge.",
              show=[f"m-s{i}" for i in range(3)] + [f"m-c{i}" for i in range(3)],
              link=[L("m-app", f"m-s{i}", dashed=True) for i in range(3)], set=[{"id": "m-app", "tone": "g"}]),
        wait(900),
        scene(say="Trois machines, trois copies : c'est **toujours un monolithe**.", hud=[hud("à déployer", "1, en 3 copies")]),
        wait(1100),
        scene(say="Une ligne change dans le paiement…", set=[{"id": "m-pay", "tone": "y", "label": "1 ligne changée"}]),
        wait(800),
        scene(say="…et c'est **toute la boutique** qu'on reconstruit et qu'on redéploie.",
              set=[{"id": f"m-c{i}", "title": "boutique v2", "tone": "y"} for i in range(3)]),
        wait(3000),
    ],
}

# ---------- 3. fullstack, front, back
f_ents = [
    ent("f-who", "node", (-10.5, -3.5), (10, 2.6), "n", title="« fullstack »", sub="un profil de développeur",
        detail="Un développeur **fullstack** sait travailler sur l'interface et sur le serveur. C'est un **profil**, pas une architecture."),
    ent("f-fw", "node", (-10.5, 1.5), (10, 2.6), "n", title="framework fullstack", sub="un projet, souvent un seul artefact",
        detail="Un **framework fullstack** (Next.js, Laravel, Rails, Symfony…) couvre les pages et le serveur dans un même projet. Livré d'un bloc, c'est un monolithe."),
    ent("f-front", "layer", (8.5, -5.4), (13, 5.4), "g", title="front", sub="l'appli du navigateur",
        detail="Le **front** : l'application qui tourne dans le navigateur, livrée à part (souvent de simples fichiers)."),
    ent("f-fspa", "node", (0, 1.3), (11, B), "v", parent="f-front", title="écrans de la boutique"),
    ent("f-back", "layer", (8.5, 3.6), (13, 9.0), "g", title="back", sub="l'API",
        detail="Le **back** : le serveur qui expose l'API. À lui seul, avec ses quatre modules, il reste **un monolithe**."),
]
for (mid, name), (x, y) in zip(MODS, [(-3.1, -1.2), (3.1, -1.2), (-3.1, 2.4), (3.1, 2.4)]):
    f_ents.append(ent(f"f-{mid}", "node", (x, y), (5.6, B), "v", parent="f-back", title=name))
step_f = {
    "id": "front-back", "label": "Front et back", "title": "Fullstack, front, back : ce ne sont pas des architectures",
    "body": ["Trois mots qu'on prend souvent pour des architectures."],
    "show": ["f-who", "f-fw"], "links": [],
    "script": [
        wait(900),
        scene(say="« **Fullstack** » décrit une personne, ou un framework qui couvre pages et serveur : pas une architecture.",
              set=[{"id": "f-who", "tone": "y"}]),
        wait(1000),
        scene(say="À droite, on sépare le **front** (l'appli du navigateur) et le **back** (l'API).",
              show=["f-front", "f-fspa", "f-back"] + [f"f-{m}" for m, _ in MODS],
              link=[L("f-fspa", "f-back")], set=[{"id": "f-who", "tone": "n"}]),
        wait(1000),
        scene(say="Cela fait **deux unités de déploiement**…", set=[{"id": "f-front", "label": "unité 1"}, {"id": "f-back", "label": "unité 2"}]),
        wait(1000),
        scene(say="…mais le back, avec ses quatre modules livrés ensemble, **reste un monolithe**.",
              set=[{"id": "f-back", "tone": "y"}]),
        wait(3000),
    ],
}

# ---------- 4. le monolithe modulaire
QW, QH = 8.6, 5.2
QPOS = [(-4.8, -2.4), (4.8, -2.4), (-4.8, 3.6), (4.8, 3.6)]
q_ents = [ent("q-app", "layer", (0, 0), (21, 14), "g", title="boutique", sub="une seule unité de déploiement",
              detail="Toujours **un seul artefact**, mais le code est découpé en modules aux frontières nettes.")]
for (mid, name), (x, y) in zip(MODS, QPOS):
    first = mid == "cat"
    q_ents += [ent(f"q-{mid}", "layer", (x, y), (QW, QH), "v", parent="q-app", title=name,
                   detail="Chaque **module** n'expose qu'une petite **interface publique** ; le reste est privé." if first else None),
               ent(f"q-{mid}-i", "node", (0, -0.6), (QW - 1.4, 1.5), "v", parent=f"q-{mid}", title="interface" if first else None),
               ent(f"q-{mid}-t", "node", (0, 1.4), (QW - 1.4, 1.5), "b", parent=f"q-{mid}", title="ses tables" if first else None,
                   detail="Chaque module a **ses tables** ; les autres n'y touchent pas." if first else None)]
step_q = {
    "id": "modulaire", "label": "Modulaire", "title": "Le monolithe modulaire : des frontières dans le code",
    "body": ["Toujours un seul artefact, mais des frontières tenues à l'intérieur."],
    "show": [e["id"] for e in q_ents], "links": [],
    "hud": [{"label": "à déployer", "value": 1}, {"label": "modules", "value": 4}],
    "script": [
        wait(900),
        scene(say="Chaque module a ses **tables** et une petite **interface** : le reste ne regarde que lui.",
              set=[{"id": "q-cat", "tone": "y"}]),
        wait(800),
        scene(say="Le panier a besoin d'un prix : il passe par l'interface du catalogue.",
              link=[L("q-pan-i", "q-cat-i")], set=[{"id": "q-cat", "tone": "v"}]),
        send(["q-pan-i", "q-cat-i"], label="prix ?", reply="1 290 €"),
        scene(say="Il ne va **jamais** lire directement les tables du catalogue.",
              set=[{"id": "q-cat-t", "tone": "y", "label": "à lui seul"}]),
        wait(1200),
        scene(say="Un seul déploiement, mais des modules **séparables** le jour où il le faudra.",
              set=[{"id": "q-app", "tone": "y"}, {"id": "q-cat-t", "tone": "b", "label": None}]),
        wait(3000),
    ],
}

# ---------- 5. micro-services
SW, SH = 10.0, 5.6
SPOS = [(-6.5, -4.0), (6.5, -4.0), (-6.5, 4.0), (6.5, 4.0)]
s_ents = []
for (mid, name), (x, y) in zip(MODS, SPOS):
    first = mid == "cat"
    s_ents += [ent(f"s-{mid}", "layer", (x, y), (SW, SH), "g", title=name, sub="service",
                   detail="Un **micro-service** : construit, testé et **déployé seul**, avec sa propre base." if first else None),
               ent(f"s-{mid}-c", "node", (0, -0.5), (SW - 1.6, 1.5), "v", parent=f"s-{mid}", title="code" if first else None,
                   label="v1"),
               ent(f"s-{mid}-d", "node", (0, 1.5), (SW - 1.6, 1.5), "b", parent=f"s-{mid}", title="sa base" if first else None)]
step_s = {
    "id": "micro-services", "label": "Micro-services", "title": "Micro-services : chacun se déploie seul",
    "body": ["Les modules deviennent des programmes à part."],
    "show": [e["id"] for e in s_ents], "links": [L("s-pan-c", "s-cat-c"), L("s-pan-c", "s-pay-c"), L("s-pay-c", "s-liv-c")],
    "hud": [{"label": "à déployer", "value": 4}],
    "script": [
        wait(900),
        scene(say="Chaque module est devenu un **service** : son code, **sa base**, son artefact.",
              set=[{"id": "s-cat", "tone": "y"}]),
        wait(900),
        scene(say="Le paiement change ? On ne déploie **que lui**.",
              set=[{"id": "s-cat", "tone": "g"}, {"id": "s-pay-c", "label": "v2", "tone": "y"}]),
        wait(1100),
        scene(say="Les autres restent en v1, et continuent de servir.",
              set=[{"id": f"s-{m}-c", "label": "v1, inchangé"} for m in ("cat", "pan", "liv")]),
        wait(900),
        send(["s-pan-c", "s-pay-c"], label="payer 1 290 €", reply="payé",
             explain=["Les services se parlent **par le réseau**, par leurs API.", "La réponse revient par le réseau aussi."]),
        scene(say="Le prix de cette liberté : un appel réseau là où il y avait un appel de fonction.",
              set=[{"id": "s-pay-c", "tone": "v"}]),
        wait(3000),
    ],
}

lesson = {
    "format": "bl-scenes/0.3", "id": "monolith-to-microservices", "title": "Monolithe et micro-services", "lang": "fr", "kit": "plan",
    "legend": [{"tone": "g", "label": "unité de déploiement"}, {"tone": "v", "label": "module de code"},
               {"tone": "b", "label": "données"}, {"tone": "n", "label": "machine"}],
    "entities": d_ents + m_ents + f_ents + q_ents + s_ents,
    "steps": [step_d, step_m, step_f, step_q, step_s],
}
write(lesson, *outputs(HERE, "monolith.scene.json", "monolith"))
