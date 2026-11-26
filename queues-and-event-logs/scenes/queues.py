"""Scènes (Feuilleté, bl-scenes/0.4) du bit « Files de messages et journaux d'événements ».

Exemple propre au bit : une plateforme de cours en ligne. À chaque inscription, le site publie un message ;
des consommateurs envoient l'e-mail de bienvenue ; plus tard, la facturation lit les mêmes événements.

Dessin, une sorte = un dessin :
- le producteur (le site) = un bloc pervenche `v` ;
- le broker = un `store` jaune `y`, au centre ;
- un consommateur = un bloc bleu `b` ; un autre groupe de lecteurs (facturation) = un bloc vert `g` ;
- ce qui plante passe en rose `r`.
Le dernier temps (« À toi ») reprend ce dessin, joué par le modèle `queue`.
"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools" / "scenes"))
from paths import outputs
from scene_kit import L, scene, send, wait, write, hud, traffic

S = [1.8, 1.8, 1.0]
ents = [
    {"id": "site", "kind": "node", "at": [6.5, 6.5], "size": S, "tone": "v", "title": "site", "sub": "producteur",
     "detail": "Le **producteur** : le site publie un message à chaque inscription, puis passe à la suivante sans attendre qu'on le traite."},
    {"id": "broker", "kind": "store", "at": [2.8, 2.8], "size": [2.2, 2.2, 1.0], "tone": "y", "title": "broker",
     "detail": "Le **broker** reçoit les messages et les garde jusqu'à ce qu'on les lise. RabbitMQ, Kafka, Amazon SQS en sont des exemples."},
    {"id": "c1", "kind": "node", "at": [-2.125, 0.125], "size": S, "tone": "b", "title": "consommateur",
     "detail": "Un **consommateur** prend un message, le traite (envoyer l'e-mail de bienvenue), puis l'**acquitte** : il dit au broker que c'est fait."},
    {"id": "c2", "kind": "node", "at": [0.125, -2.125], "size": S, "tone": "b"},
    {"id": "c3", "kind": "node", "at": [-4.6, -2.3], "size": S, "tone": "b"},
    {"id": "fact", "kind": "node", "at": [6.8, -1.2], "size": S, "tone": "g", "title": "facturation", "sub": "un autre groupe",
     "detail": "Un second **groupe de consommateurs** : la facturation lit **tous** les événements, à son propre rythme."},
]
BASE = ["site", "broker", "c1", "c2"]
LINKS = [L("site", "broker"), L("broker", "c1"), L("broker", "c2")]
steps = []

# ---------- 1. la file
steps.append({
    "id": "file", "label": "La file", "title": "La file de messages : chaque message à un seul consommateur",
    "body": ["Le site publie une inscription ; un consommateur la traite."],
    "show": BASE, "links": LINKS,
    "hud": [hud("en attente", 0)],
    "script": [
        wait(900),
        send(["site", "broker"], label="inscription Léa"),
        scene(say="Le site **dépose** le message dans le broker et passe à la suite, sans attendre.",
              set=[{"id": "broker", "label": "en attente : 1"}], hud=[hud("en attente", 1, "y")]),
        wait(700),
        scene(say="Le broker le donne à **un seul** consommateur, qui envoie l'e-mail de bienvenue.",
              set=[{"id": "c1", "label": "e-mail envoyé"}]),
        send(["broker", "c1"], label="inscription Léa", reply="acquitté"),
        scene(say="Le consommateur **acquitte** : le broker efface le message. Il ne sera traité qu'une fois.",
              set=[{"id": "c1", "label": None}, {"id": "broker", "label": "en attente : 0"}], hud=[hud("en attente", 0)]),
        send(["site", "broker", "c2"], label="inscription Sam"),
        scene(say="Le message suivant va à l'autre consommateur : ils **se partagent** le travail.",
              set=[{"id": "c2", "label": "e-mail envoyé"}]),
        wait(3000),
    ],
})

# ---------- 2. le retard
steps.append({
    "id": "retard", "label": "Le retard", "title": "Quand on produit plus vite qu'on ne traite",
    "body": ["La rentrée : les inscriptions affluent."],
    "show": BASE, "links": LINKS,
    "flows": [traffic(["site", "broker"], gap=260)],
    "hud": [hud("produits", "12 msg/s"), hud("traités", "10 msg/s"), hud("en attente", 0)],
    "script": [
        wait(1600),
        scene(say="12 inscriptions par seconde, et deux consommateurs qui en traitent **5 chacun**.",
              set=[{"id": "c1", "label": "5 msg/s"}, {"id": "c2", "label": "5 msg/s"}]),
        wait(1300),
        scene(say="2 messages de plus attendent **chaque seconde** : l'attente grossit, sans rien perdre.",
              set=[{"id": "broker", "label": "en attente : 120", "tone": "y"}], hud=[hud("en attente", 120, "y")]),
        wait(1500),
        scene(say="On ajoute un troisième consommateur : **15 messages par seconde** de capacité.",
              show=[{"id": "c3", "label": "5 msg/s"}], link=[L("broker", "c3")], hud=[hud("traités", "15 msg/s", "g")]),
        wait(1600),
        scene(say="L'attente se vide. Ajouter des consommateurs, c'est **monter en charge** sans toucher au site.",
              set=[{"id": "broker", "label": "en attente : 0", "tone": "y"}], hud=[hud("en attente", 0, "g")]),
        wait(3000),
    ],
})

# ---------- 3. l'acquittement
steps.append({
    "id": "acquittement", "label": "Acquitter", "title": "Un consommateur plante : perdu ou traité deux fois ?",
    "body": ["Le moment où l'on acquitte décide de ce qui arrive en cas de panne."],
    "show": BASE, "links": LINKS,
    "hud": [hud("perdus", 0), hud("doublons", 0)],
    "script": [
        wait(900),
        send(["broker", "c1"], label="inscription Noé"),
        scene(say="c1 envoie l'e-mail de Noé… et **plante** avant d'acquitter.",
              set=[{"id": "c1", "label": "e-mail envoyé, puis plante", "tone": "r"}]),
        wait(1200),
        scene(say="**Acquitter après** le traitement : le broker n'a pas reçu l'accusé, il redonne le message.",
              set=[{"id": "broker", "label": "acquitter : après"}]),
        send(["broker", "c2"], label="inscription Noé"),
        scene(say="Noé reçoit **deux** e-mails. Rien n'est perdu, mais un message peut être traité deux fois : **au moins une fois**.",
              set=[{"id": "c2", "label": "e-mail envoyé"}], hud=[hud("doublons", 1, "y")]),
        wait(1500),
        scene(say="**Acquitter avant** le traitement : si c1 plante, le message est déjà effacé. Jamais de doublon, mais une perte : **au plus une fois**.",
              set=[{"id": "broker", "label": "acquitter : avant"}, {"id": "c2", "label": None}], hud=[hud("doublons", 0), hud("perdus", 1, "r")]),
        wait(1500),
        scene(say="En pratique : acquitter après, et des consommateurs **idempotents**, qui reconnaissent un message déjà traité.",
              set=[{"id": "c1", "label": "redémarré", "tone": "b"}, {"id": "broker", "label": "acquitter : après"}], hud=[hud("perdus", 0, "g")]),
        wait(3000),
    ],
})

# ---------- 4. le journal
steps.append({
    "id": "journal", "label": "Le journal", "title": "Le journal d'événements : les messages restent",
    "body": ["La facturation veut lire, elle aussi, chaque inscription."],
    "show": BASE, "links": LINKS,
    "hud": [hud("e-mails", "position 900"), hud("facturation", "—")],
    "script": [
        wait(900),
        scene(say="Dans un **journal d'événements**, les messages ne sont pas effacés : ils restent, numérotés, dans l'ordre.",
              set=[{"id": "broker", "label": "journal : 900 événements"}]),
        wait(1300),
        scene(say="Les consommateurs des e-mails forment un **groupe** : ils retiennent leur **position** dans le journal.",
              set=[{"id": "c1", "label": "groupe e-mails"}, {"id": "c2", "label": "groupe e-mails"}]),
        wait(1300),
        scene(say="La facturation arrive, avec **son propre groupe** et sa propre position.",
              show=["fact"], link=[L("broker", "fact")], hud=[hud("facturation", "position 0", "y")]),
        send(["broker", "fact"], label="événements 1 à 900"),
        scene(say="Elle part du début et **relit tout** l'historique, sans rien changer pour les e-mails.",
              set=[{"id": "fact", "label": "rattrape son retard"}], hud=[hud("facturation", "position 640", "y")]),
        wait(1300),
        send(["site", "broker"], label="inscription Lou"),
        scene(say="Chaque nouvel événement est lu par **les deux groupes**, chacun à son rythme.",
              set=[{"id": "fact", "label": "à jour"}], hud=[hud("e-mails", "position 901"), hud("facturation", "position 901", "g")]),
        wait(3000),
    ],
})

# ---------- 5. playground
steps.append({
    "id": "playground", "label": "À toi", "title": "À toi de jouer",
    "body": ["Change la production, ajoute des consommateurs, fais-en planter un, choisis quand acquitter, passe du mode file au mode journal : la scène suit.",
             "En mode **guidé**, les consignes passent une à une sous la scène."],
    "show": BASE, "links": LINKS,
    "hud": [hud("produits", "12 msg/s"), hud("en attente", 0), hud("perdus", 0), hud("doublons", 0)],
    "sim": {
        "model": "queue", "producer": "site", "broker": "broker",
        "consumers": [{"id": "c1"}, {"id": "c2"}, {"id": "c3"}],
        "groups": [{"id": "facturation", "at": [6.8, -1.2], "title": "facturation", "speed": 3}],
        "production": {"value": 12, "min": 1, "max": 40, "step": 1},
        "capacity": {"value": 5, "min": 1, "max": 20, "step": 1},
        "crash": "c1",
        "chart": True,
        "guide": [
            {"say": "Regarde le broker : les messages s'accumulent.", "until": {"backlogMin": 10},
             "done": "12 messages arrivent chaque seconde, 10 repartent : 2 de plus attendent, chaque seconde."},
            {"say": "Ajoute un consommateur.", "until": {"consumers": 3, "backlogMax": 0},
             "done": "15 messages par seconde de capacité pour 12 produits : l'attente s'est vidée."},
            {"say": "Fais planter c1, avec l'acquittement après le traitement.", "until": {"crashed": True, "ack": "after", "duplicatesMin": 1},
             "done": "c1 plante au milieu d'un message : le broker le redonne à un autre. Rien n'est perdu, mais il est traité deux fois."},
            {"say": "Passe en journal, puis ajoute le groupe facturation.", "until": {"mode": "log", "groups": 2},
             "done": "La facturation part du début du journal : elle relit tout, à son rythme. Les messages, eux, restent."},
        ],
    },
})

lesson = {
    "format": "bl-scenes/0.4", "id": "queues-and-event-logs", "title": "Files et journaux", "lang": "fr", "kit": "feuillete",
    "legend": [{"kind": "req", "label": "message"}, {"kind": "res", "label": "acquittement"}],
    "entities": ents, "steps": steps,
}
write(lesson, *outputs(HERE, "queues.scene.json", "queues"))
