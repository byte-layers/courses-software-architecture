"""Scènes (Feuilleté, bl-scenes/0.4) du bit « Synchrone ou asynchrone ».

Exemple propre au bit : une boutique de baskets en ligne. Une commande passe par trois services :
A · commandes, B · stock, C · paiement.

Dessin, une sorte = un dessin :
- un service = un bloc `node` ; A en pervenche `v` (celui que le client appelle), B et C en bleu `b` ;
- la file de messages = un `store` jaune `y` posé entre A et B ;
- ce qui ralentit passe en jaune `y`, ce qui échoue en rose `r`, ce qui est réglé en vert `g`.
Le dernier temps (« À toi ») reprend exactement ce dessin, joué par le modèle `call-chain`.
"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools" / "scenes"))
from paths import outputs
from scene_kit import L, scene, send, wait, write, hud, traffic

S = [1.8, 1.8, 1.0]
POS = {"client": [-6.0, 6.0], "a": [-2.4, 2.4], "b": [2.4, -2.4], "c": [6.6, -6.6]}
ents = [
    {"id": "client", "kind": "actor", "at": POS["client"], "label": "le client",
     "detail": "Le client valide son panier et attend la réponse de la boutique."},
    {"id": "a", "kind": "node", "at": POS["a"], "size": S, "tone": "v", "title": "A · commandes",
     "detail": "Le service A reçoit la commande. Pour répondre, il a besoin de B."},
    {"id": "b", "kind": "node", "at": POS["b"], "size": S, "tone": "b", "title": "B · stock",
     "detail": "Le service B réserve la paire en stock, puis demande le paiement à C."},
    {"id": "c", "kind": "node", "at": POS["c"], "size": S, "tone": "b", "title": "C · paiement",
     "detail": "Le service C débite la carte. Le faire deux fois pour une même commande, c'est faire payer deux fois."},
    {"id": "file", "kind": "store", "at": [0, 0], "size": [1.2, 1.2, 0.5], "tone": "y", "title": "file de messages",
     "detail": "Une **file de messages** garde les demandes déposées, jusqu'à ce qu'un service les prenne."},
]
ALL = ["client", "a", "b", "c"]
CHAIN = [L("client", "a"), L("a", "b"), L("b", "c")]
steps = []

# ---------- 1. synchrone
steps.append({
    "id": "synchrone", "label": "Synchrone", "title": "Synchrone : on attend la réponse",
    "body": ["Une commande traverse trois services, chacun attend le suivant."],
    "show": ALL, "links": CHAIN,
    "hud": [hud("réponse", "—")],
    "script": [
        wait(900),
        send(["client", "a", "b", "c"], label="commande 81", reply="payé",
             explain=["Le client envoie sa commande à A, et **attend**.", "A appelle B, et attend à son tour.",
                      "B appelle C, et attend.", "Les réponses remontent dans l'ordre inverse."]),
        scene(say="Chaque appel est **synchrone** : on attend la réponse avant de répondre soi-même.",
              set=[{"id": "a", "label": "50 ms"}, {"id": "b", "label": "60 ms"}, {"id": "c", "label": "60 ms"}],
              hud=[hud("réponse", "170 ms")]),
        wait(1400),
        scene(say="Le temps de réponse est **la somme** des temps de chaque service. Simple, et le client sait tout de suite si c'est payé."),
        wait(3000),
    ],
})
steps[-1]["script"][-2]["set"] = [{"id": "client", "label": "client : payé, 170 ms"}]

# ---------- 2. cascade
steps.append({
    "id": "cascade", "label": "Cascade", "title": "Un service lent bloque toute la chaîne",
    "body": ["Le paiement ralentit. Regardez ce qui arrive aux deux autres."],
    "show": ALL, "links": CHAIN,
    "flows": [traffic(["client", "a", "b"], gap=420, fallback="erreur", reply="ok")],
    "hud": [hud("réponse", "170 ms"), hud("échecs", "0 %")],
    "script": [
        wait(2200),
        scene(say="Chaque service n'a que **quelques places** pour traiter des requêtes en même temps : ici, quatre.",
              set=[{"id": s, "label": "occupé 1/4"} for s in ("a", "b", "c")]),
        wait(1400),
        scene(say="C ralentit : chaque paiement lui prend **dix fois** plus de temps.",
              set=[{"id": "c", "label": "lent · occupé 4/4", "tone": "y"}], hud=[hud("réponse", "1,4 s", "y")]),
        wait(1500),
        scene(say="Les places de B se remplissent de requêtes qui **attendent C**…",
              set=[{"id": "b", "label": "occupé 4/4", "tone": "y"}]),
        wait(1500),
        scene(say="…puis celles de A. Les nouvelles commandes n'ont plus de place : elles **échouent**.",
              set=[{"id": "a", "label": "occupé 4/4", "tone": "r"}], hud=[hud("réponse", "5 s", "r"), hud("échecs", "62 %", "r")]),
        wait(1300),
        scene(say="Un seul service lent, et toute la boutique tombe : c'est une **panne en cascade**.",
              set=[{"id": "client", "label": "client : erreur"}]),
        wait(3000),
    ],
})

# ---------- 3. délai d'attente et nouvelles tentatives
steps.append({
    "id": "delai", "label": "Délai, tentatives", "title": "Délai d'attente et nouvelles tentatives",
    "body": ["Deux réglages pour ne plus attendre sans fin."],
    "show": ALL, "links": CHAIN,
    "hud": [hud("échecs", "62 %", "r"), hud("appels à C", "×1")],
    "script": [
        wait(900),
        scene(say="Un **délai d'attente** (*timeout*) : B abandonne C au bout de 300 ms, au lieu d'attendre sans fin.",
              set=[{"id": "c", "label": "lent", "tone": "y"}, {"id": "b", "label": "abandonne à 300 ms", "tone": "g"}]),
        send(["b", "c"], label="payer ?", reply="trop tard"),
        scene(say="La réponse arrive vite, même en échec, et B **libère sa place** : A n'est plus bloqué.",
              set=[{"id": "a", "label": "places libres", "tone": "g"}], hud=[hud("échecs", "30 %", "y")]),
        wait(1400),
        scene(say="Une **nouvelle tentative** (*retry*) renvoie la demande après un échec. Utile contre une coupure brève…",
              set=[{"id": "b", "label": "2 nouvelles tentatives", "tone": "y"}]),
        send(["b", "c"], label="payer ? (2)"),
        send(["b", "c"], label="payer ? (3)"),
        scene(say="…mais contre un service **déjà lent**, chaque échec renvoie trois appels : la charge triple, tout sature.",
              set=[{"id": "c", "label": "submergé", "tone": "r"}], hud=[hud("appels à C", "×3", "r"), hud("échecs", "90 %", "r")]),
        wait(3000),
    ],
})

# ---------- 4. idempotence
steps.append({
    "id": "idempotence", "label": "Idempotence", "title": "Payé deux fois : l'idempotence",
    "body": ["Une nouvelle tentative peut répéter une action qui avait déjà réussi."],
    "show": ["b", "c"], "links": [L("b", "c")],
    "hud": [hud("débits", 0)],
    "script": [
        wait(900),
        send(["b", "c"], label="payer cmd 81"),
        scene(say="C débite la carte… mais sa réponse **se perd** en route, ou arrive après le délai.",
              set=[{"id": "c", "label": "débité", "tone": "g"}, {"id": "b", "label": "pas de réponse", "tone": "y"}], hud=[hud("débits", 1)]),
        wait(1200),
        send(["b", "c"], label="payer cmd 81 (2)"),
        scene(say="B réessaie. C ne sait pas que c'est la même commande : il débite **une seconde fois**.",
              set=[{"id": "c", "label": "débité deux fois", "tone": "r"}], hud=[hud("débits", 2, "r")]),
        wait(1500),
        scene(say="Le remède : une **clé d'idempotence**, un identifiant unique joint à la demande.",
              set=[{"id": "c", "label": "clé cmd-81 déjà vue", "tone": "g"}, {"id": "b", "label": "clé cmd-81", "tone": "b"}], hud=[hud("débits", 1, "g")]),
        send(["b", "c"], label="payer, clé cmd-81", reply="déjà payé"),
        scene(say="C reconnaît la clé et renvoie le premier résultat : l'opération est **idempotente**, la répéter ne change rien.",
              set=[{"id": "b", "label": "payé, une fois"}]),
        wait(3000),
    ],
})

# ---------- 5. asynchrone
steps.append({
    "id": "asynchrone", "label": "Asynchrone", "title": "Asynchrone : déposer et ne pas attendre",
    "body": ["A ne demande plus à B de répondre tout de suite : il dépose la demande."],
    "show": ALL + ["file"], "links": [L("client", "a"), L("a", "file"), L("file", "b"), L("b", "c")],
    "hud": [hud("réponse", "50 ms"), hud("en file", 0)],
    "script": [
        wait(900),
        send(["client", "a"], label="commande 82"),
        send(["a", "file"], label="à traiter : 82"),
        send(["a", "client"], label="commande reçue"),
        scene(say="A **dépose** la commande dans une file et répond tout de suite : « commande reçue ».",
              set=[{"id": "client", "label": "client : reçu, 50 ms"}], hud=[hud("en file", 1, "y")]),
        wait(1200),
        scene(say="C ralentit ? Les commandes **s'accumulent** dans la file, mais personne n'attend.",
              set=[{"id": "c", "label": "lent", "tone": "y"}, {"id": "file", "label": "en file : 12"}], hud=[hud("en file", 12, "y")]),
        wait(1400),
        send(["file", "b", "c"], label="82", reply="payé"),
        scene(say="B et C vident la file **à leur rythme**. Le client apprend le paiement plus tard, par une notification.",
              set=[{"id": "c", "label": "rattrape", "tone": "b"}, {"id": "file", "label": "en file : 3"}], hud=[hud("en file", 3)]),
        wait(1300),
        scene(say="Le prix : au moment de répondre, A **ne sait pas encore** si le paiement passera.",
              set=[{"id": "a", "label": "résultat : plus tard", "tone": "y"}]),
        wait(3000),
    ],
})

# ---------- 6. playground
steps.append({
    "id": "playground", "label": "À toi", "title": "À toi de jouer",
    "body": ["Ralentis un service, coupe-le, règle le délai d'attente et les nouvelles tentatives, ajoute la clé d'idempotence, passe en asynchrone : la scène suit.",
             "En mode **guidé**, les consignes passent une à une sous la scène."],
    "show": ALL, "links": CHAIN,
    "hud": [hud("échecs", "0 %"), hud("réponse", "170 ms"), hud("en double", 0)],
    "sim": {
        "model": "call-chain", "client": "client",
        "services": [{"id": "a"}, {"id": "b"}, {"id": "c"}],
        "traffic": {"value": 6, "min": 1, "max": 40, "step": 1},
        "timeout": {"value": 300, "min": 100, "max": 3000, "step": 100},
        "effect": "paiements",
        "queue": {"id": "queue", "at": [0, 0], "title": "file de messages"},
        "chart": True,
        "guide": [
            {"say": "Rends C lent : coche « lent » sur c.", "until": {"slow": "c", "failedMin": 30},
             "done": "Les places de C se remplissent, puis celles de B et de A : la lenteur de C remonte jusqu'au client."},
            {"say": "Active le délai d'attente des appels.", "until": {"timeout": True, "failedMax": 95},
             "done": "A et B abandonnent au bout du délai : la réponse arrive vite, même en échec."},
            {"say": "Ajoute 2 nouvelles tentatives.", "until": {"retries": 2, "duplicatesMin": 1},
             "done": "Chaque échec repart vers C : la charge triple. Et des paiements passent deux fois."},
            {"say": "Active la clé d'idempotence, puis passe en asynchrone.", "until": {"idempotency": True, "mode": "async", "failedMax": 5},
             "done": "A répond tout de suite, la file absorbe la lenteur de C, et aucun paiement ne passe deux fois."},
        ],
    },
})

lesson = {
    "format": "bl-scenes/0.4", "id": "sync-async-communication", "title": "Synchrone ou asynchrone", "lang": "fr", "kit": "feuillete",
    "legend": [{"kind": "req", "label": "requête"}, {"kind": "res", "label": "réponse"}],
    "entities": ents, "steps": steps,
}
write(lesson, *outputs(HERE, "syncasync.scene.json", "syncasync"))
