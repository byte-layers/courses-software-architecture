"""Scènes (Feuilleté, bl-scenes/0.3) du bit « Architecture orientée événements et CQRS ».

Exemple propre au bit : une librairie en ligne. Une commande déclenche le stock, la facturation, l'e-mail de
confirmation ; plus tard, un service de recommandations veut aussi savoir ce qui se vend.

Dessin, une sorte = un dessin :
- un service = un bloc ; celui qui publie en pervenche `v`, ceux qui réagissent en bleu `b` ;
- le journal d'événements = un `store` jaune `y` ;
- une base = un `store` ; d'écriture en bleu `b`, de lecture en vert `g` ;
- ce qui casse ou bloque passe en rose `r`, ce qui est nouveau en jaune `y`.
"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools" / "scenes"))
from paths import outputs
from scene_kit import G, L, scene, send, wait, write, hud

S = [1.8, 1.8, 1.0]
SUBS = [("stock", "stock"), ("fact", "facturation"), ("mail", "e-mails"), ("reco", "recommandations")]
SX = [-7.0, 0.0, 7.0]
POS = {"stock": G(-7.0, -7.0), "fact": G(0, -7.0), "mail": G(7.0, -7.0), "reco": G(10.0, 3.0)}
ents = [
    {"id": "orders", "kind": "node", "at": G(0, 10.0), "size": S, "tone": "v", "title": "commandes",
     "detail": "Le service **commandes** enregistre chaque commande de livre."},
    {"id": "bus", "kind": "store", "at": G(0, 2.0), "tone": "y", "title": "journal d'événements",
     "detail": "Un **journal d'événements** (Kafka, par exemple) garde les événements publiés ; chaque abonné les lit à son rythme."},
]
for sid, name in SUBS:
    ents.append({"id": sid, "kind": "node", "at": POS[sid], "size": S, "tone": "b", "title": name})
ents += [
    {"id": "client", "kind": "actor", "at": G(0, 13.0), "label": "le lecteur"},
    {"id": "w-api", "kind": "node", "at": G(-7.0, 5.0), "size": S, "tone": "v", "title": "côté écriture", "sub": "valide les commandes",
     "detail": "Le **côté écriture** reçoit les ordres (« passer commande »), vérifie les règles, et enregistre."},
    {"id": "w-db", "kind": "store", "at": G(-7.0, -5.0), "tone": "b", "title": "base d'écriture", "sub": "tables normalisées",
     "detail": "Une base pensée pour **écrire juste** : chaque information à un seul endroit."},
    {"id": "r-api", "kind": "node", "at": G(7.0, 5.0), "size": S, "tone": "g", "title": "côté lecture", "sub": "sert les écrans",
     "detail": "Le **côté lecture** répond aux questions des écrans (« mes commandes »), sans rien modifier."},
    {"id": "r-db", "kind": "store", "at": G(7.0, -5.0), "tone": "g", "title": "vue « mes commandes »", "sub": "prête à afficher",
     "detail": "Une base pensée pour **lire vite** : les données déjà assemblées comme l'écran les affiche."},
    {"id": "c-bus", "kind": "store", "at": G(0, -5.0), "tone": "y", "title": "événements"},
]
FOUR = [s for s, _ in SUBS]
THREE = FOUR[:3]
steps = []

# ---------- 1. appels directs
steps.append({
    "id": "appels-directs", "label": "Appels directs", "title": "Appels directs : commandes doit connaître tout le monde",
    "body": ["Une commande déclenche trois traitements. Commandes appelle chacun."],
    "show": ["orders"] + THREE, "links": [L("orders", s) for s in THREE],
    "hud": [hud("appels à écrire", 3)],
    "script": [
        wait(900),
        send(["orders", "stock"], label="réserve le livre"),
        send(["orders", "fact"], label="facture"),
        send(["orders", "mail"], label="confirme"),
        scene(say="Commandes **appelle** le stock, la facturation et les e-mails, un par un.",
              set=[{"id": "orders", "label": "connaît 3 services"}]),
        wait(1200),
        scene(say="Les e-mails sont en panne : faut-il bloquer la commande ? Commandes doit en décider **pour eux**.",
              set=[{"id": "mail", "tone": "r", "label": "en panne"}, {"id": "orders", "tone": "r", "label": "attend les e-mails ?"}]),
        wait(1500),
        scene(say="Une équipe veut ajouter des **recommandations** : il faut modifier et redéployer commandes.",
              show=[{"id": "reco", "tone": "y"}], link=[L("orders", "reco")], set=[{"id": "mail", "tone": "b", "label": None}, {"id": "orders", "tone": "v", "label": "à modifier"}],
              hud=[hud("appels à écrire", 4, "r")]),
        wait(3000),
    ],
})

# ---------- 2. événements
steps.append({
    "id": "evenements", "label": "Événements", "title": "Publier un événement : ce qui s'est passé",
    "body": ["Commandes n'appelle plus personne. Il annonce ce qui s'est passé."],
    "show": ["orders", "bus"] + THREE, "links": [L("orders", "bus")] + [L("bus", s) for s in THREE],
    "hud": [hud("abonnés", 3), hud("code modifié", "non")],
    "script": [
        wait(900),
        send(["orders", "bus"], label="CommandePassée"),
        scene(say="Commandes publie un **événement** : « commande passée », un fait, au passé. Il ne sait pas qui l'écoute.",
              set=[{"id": "bus", "label": "CommandePassée n° 4021"}]),
        send(["bus", "stock"], label="CommandePassée"),
        send(["bus", "mail"], label="CommandePassée"),
        scene(say="Chaque **abonné** lit l'événement et fait **son** travail : réserver, facturer, écrire.",
              set=[{"id": "stock", "label": "réservé"}, {"id": "fact", "label": "facturé"}, {"id": "mail", "label": "envoyé"}]),
        wait(1300),
        scene(say="Les recommandations s'**abonnent** au même événement. Commandes ne change **pas d'une ligne**.",
              show=[{"id": "reco", "tone": "y", "label": "nouvel abonné"}], link=[L("bus", "reco")], hud=[hud("abonnés", 4, "g"), hud("code modifié", "non", "g")]),
        send(["bus", "reco"], label="CommandePassée"),
        wait(1300),
        scene(say="Si les e-mails tombent, la commande passe quand même ; ils **rattraperont** les événements en revenant.",
              set=[{"id": "mail", "tone": "r", "label": "en panne, rattrapera"}, {"id": "reco", "tone": "b"}]),
        wait(3000),
    ],
})

# ---------- 3. le prix
steps.append({
    "id": "prix", "label": "Le prix", "title": "Le prix : un enchaînement que personne ne voit en entier",
    "body": ["Le stock manque. Que devient la commande, déjà facturée ?"],
    "show": ["orders", "bus"] + FOUR, "links": [L("orders", "bus")] + [L("bus", s) for s in FOUR],
    "hud": [hud("état", "commande passée")],
    "script": [
        wait(900),
        scene(say="Le stock n'a plus le livre. La facture, elle, est **déjà** partie.",
              set=[{"id": "stock", "tone": "r", "label": "rupture"}, {"id": "fact", "label": "facturé"}]),
        send(["stock", "bus"], label="RéservationÉchouée"),
        scene(say="Pas d'annulation globale : le stock publie à son tour un événement, « réservation échouée ».",
              set=[{"id": "bus", "label": "RéservationÉchouée"}], hud=[hud("état", "à corriger", "y")]),
        send(["bus", "fact"], label="RéservationÉchouée"),
        send(["bus", "mail"], label="RéservationÉchouée"),
        scene(say="La facturation **rembourse**, les e-mails préviennent : chacun annule sa part. C'est une **saga**, faite d'actions de **compensation**.",
              set=[{"id": "fact", "label": "remboursé", "tone": "g"}, {"id": "mail", "label": "excuses envoyées"}], hud=[hud("état", "annulée, remboursée", "g")]),
        wait(1400),
        scene(say="Le prix : l'enchaînement complet n'est écrit **nulle part**. Pour le suivre, il faut des **traces** et des identifiants de corrélation.",
              set=[{"id": "orders", "label": "qui fait quoi ?", "tone": "y"}]),
        wait(3000),
    ],
})

# ---------- 4. CQRS
steps.append({
    "id": "cqrs", "label": "CQRS", "title": "CQRS : un modèle pour écrire, un autre pour lire",
    "body": ["La page « mes commandes » assemble six tables à chaque affichage."],
    "show": ["client", "w-api", "w-db"], "links": [L("client", "w-api"), L("w-api", "w-db")],
    "hud": [hud("page commandes", "900 ms", "r")],
    "script": [
        wait(900),
        scene(say="Une seule base sert à **écrire** juste et à **lire** vite : les deux besoins se gênent.",
              set=[{"id": "w-db", "label": "6 jointures par page", "tone": "y"}]),
        wait(1300),
        scene(say="**CQRS** sépare les deux : un **côté écriture** qui reçoit les ordres et applique les règles…",
              set=[{"id": "w-db", "label": None, "tone": "b"}]),
        send(["client", "w-api", "w-db"], label="passer commande", reply="ok"),
        scene(say="…qui publie un événement à chaque changement…",
              show=["c-bus"], link=[L("w-db", "c-bus")]),
        send(["w-db", "c-bus"], label="CommandePassée"),
        scene(say="…et un **côté lecture**, qui tient une vue **déjà assemblée** pour l'écran, mise à jour par ces événements.",
              show=["r-api", "r-db"], link=[L("c-bus", "r-db"), L("client", "r-api"), L("r-api", "r-db")]),
        send(["c-bus", "r-db"], label="CommandePassée"),
        send(["client", "r-api", "r-db"], label="mes commandes ?", reply="liste"),
        scene(say="La page se lit **d'un coup**. Le prix : la vue a un léger **retard** sur l'écriture.",
              set=[{"id": "r-db", "label": "à jour en ~1 s"}], hud=[hud("page commandes", "20 ms", "g")]),
        wait(3000),
    ],
})

lesson = {
    "format": "bl-scenes/0.3", "id": "event-driven-cqrs", "title": "Événements et CQRS", "lang": "fr", "kit": "feuillete",
    "legend": [{"kind": "req", "label": "appel ou événement"}, {"kind": "res", "label": "réponse"}],
    "entities": ents, "steps": steps,
}
write(lesson, *outputs(HERE, "events.scene.json", "events"))
