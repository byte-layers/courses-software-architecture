---
title: "Files de messages et journaux d'événements"
description: "Comment des programmes se passent des messages sans s'attendre : le broker, la file où chaque message va à un seul consommateur, l'attente qui grossit quand on produit plus vite qu'on ne traite, l'acquittement (au moins une fois, au plus une fois) et les consommateurs idempotents, puis le journal d'événements où les messages restent et où chaque groupe lit tout à son rythme. Un playground pour tout essayer."
tags:
  - bit
  - architecture
  - messaging
  - system-design
difficulty: intermediate
duration: 15
requires: "0.12.0"
---

Un programme qui n'a pas besoin d'une réponse immédiate peut **déposer un message** et passer à la suite ; un autre le traitera quand il pourra. Entre les deux, un intermédiaire garde les messages. Vous verrez ses deux grandes formes, la **file** et le **journal**, ce qui arrive quand un lecteur plante, et un playground pour tout essayer. L'exemple suivi : une plateforme de cours en ligne qui envoie un e-mail de bienvenue à chaque inscription.

**Prérequis** : [Synchrone ou asynchrone](https://byte-layers.com/fr/bits/sync-async-communication), pour ce que change le fait de ne pas attendre la réponse.

# Files de messages et journaux d'événements

## La file : chaque message à un seul consommateur

À chaque inscription, le site publie un message. Des programmes à part envoient les e-mails.

```scene
lesson: assets/queues.scene.json
step: file
```

Le site est le **producteur** : il dépose le message dans le **broker** et continue. Les **consommateurs** prennent les messages un par un. Dans une **file de messages**, chaque message va à **un seul** consommateur ; quand il a fini, il l'**acquitte**, et le broker l'efface. Plusieurs consommateurs **se partagent** ainsi le travail. RabbitMQ et Amazon SQS fonctionnent sur ce modèle.

## Quand on produit plus vite qu'on ne traite

C'est la rentrée : les inscriptions arrivent plus vite que les e-mails ne partent.

```scene
lesson: assets/queues.scene.json
step: retard
```

Quand la production dépasse la capacité des consommateurs, les messages **attendent** dans le broker. Rien n'est perdu et le site ne ralentit pas : la file sert de **tampon**. Mais l'attente grossit tant que l'écart dure, et chaque message attend plus longtemps. Le remède : **ajouter des consommateurs**, sans toucher au site. Surveiller le nombre de messages en attente dit quand le faire.

## Un consommateur plante : perdu ou traité deux fois ?

Un consommateur peut s'arrêter au milieu d'un message. Tout dépend du moment où il acquitte.

```scene
lesson: assets/queues.scene.json
step: acquittement
```

**Acquitter après** le traitement : si le consommateur plante avant, le broker redonne le message à un autre. Rien n'est perdu, mais un message peut être traité **deux fois** : c'est la livraison **au moins une fois**. **Acquitter avant** : jamais de doublon, mais un plantage **perd** le message (**au plus une fois**). Le choix courant : acquitter après, avec des consommateurs **idempotents**, qui reconnaissent un message déjà traité.

> 💡 **Remarque.** On entend parler de livraison « exactement une fois ». Elle n'existe que dans des conditions précises, souvent en combinant au moins une fois et idempotence. Partez du principe qu'un message peut arriver deux fois.

## Le journal d'événements : les messages restent

La facturation veut lire, elle aussi, chaque inscription, y compris celles du mois dernier.

```scene
lesson: assets/queues.scene.json
step: journal
```

Dans un **journal d'événements**, les messages ne sont pas effacés après lecture : ils restent, numérotés, dans l'ordre, pendant une durée de **rétention** choisie. Chaque **groupe de consommateurs** retient sa **position**. Un nouveau groupe peut partir du début et **relire l'historique**, sans gêner les autres. Apache Kafka est l'exemple le plus connu. Dans un même groupe, les consommateurs se partagent toujours les messages.

## À toi : vider la file

Le même schéma, mais c'est toi qui pilotes : laisse l'attente monter, ajoute un consommateur, fais-en planter un, passe en journal et ajoute le groupe facturation. Le mode **guidé**, dans la barre de la scène, te donne quatre consignes.

```scene
lesson: assets/queues.scene.json
step: playground
```

> 💡 **Remarque.** Le playground simplifie : les consommateurs ont une vitesse fixe, le journal garde tout sans limite de rétention, et un nouveau groupe part toujours du début.

> 📖 [Message queue (Wikipédia, en anglais)](https://en.wikipedia.org/wiki/Message_queue) · [RabbitMQ, tutoriels](https://www.rabbitmq.com/tutorials) · [Apache Kafka, introduction (en anglais)](https://kafka.apache.org/intro)

## Quatre questions pour vérifier ce que vous avez retenu

```quiz
title: "Files de messages et journaux d'événements"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Dans une file de messages avec trois consommateurs, qui reçoit un message donné ?"
    answers:
      - "Les trois consommateurs"
      - "Un seul des trois"
      - "Le premier consommateur, toujours"
    correct: 2
    explanation: "Les consommateurs d'une file se partagent les messages : chacun va à un seul, puis il est effacé."
  - prompt: "Le site produit 20 messages par seconde ; deux consommateurs en traitent 6 chacun. Que se passe-t-il ?"
    answers:
      - "Des messages sont perdus"
      - "Le site ralentit"
      - "Les messages s'accumulent dans le broker : 8 de plus attendent chaque seconde"
    correct: 3
    explanation: "La file sert de tampon. L'attente grossit tant que la capacité (12) reste sous la production (20) : il faut ajouter des consommateurs."
  - prompt: "On acquitte après le traitement. Un consommateur plante au milieu d'un message. Que devient ce message ?"
    answers:
      - "Il est redonné à un autre consommateur, et peut donc être traité deux fois"
      - "Il est perdu"
      - "Il reste bloqué pour toujours"
    correct: 1
    explanation: "C'est la livraison au moins une fois. D'où des consommateurs idempotents."
  - prompt: "Un nouveau service doit traiter toutes les inscriptions depuis trois mois, sans gêner les e-mails. Quel outil ?"
    answers:
      - "Une file de messages, où chaque message est lu une fois puis effacé"
      - "Un journal d'événements, où il lit l'historique avec son propre groupe"
      - "Un appel synchrone au site"
    correct: 2
    explanation: "Les messages restent dans le journal. Un nouveau groupe part du début, à son rythme, sans toucher à la position des autres."
```

## Récap

- Un **producteur** dépose des messages dans un **broker** ; des **consommateurs** les lisent quand ils peuvent.
- **File** : chaque message va à **un seul** consommateur, puis il est effacé ; les consommateurs se partagent le travail.
- Production plus forte que la capacité : l'**attente** grossit sans rien perdre ; on **ajoute des consommateurs**.
- **Acquitter après** : au moins une fois, des **doublons** possibles ; **avant** : au plus une fois, des **pertes** possibles. Consommateurs **idempotents**.
- **Journal d'événements** : les messages restent ; chaque **groupe** a sa **position** et peut **relire l'historique**.

Construire tout un système autour de ces événements : [Architecture orientée événements et CQRS](https://byte-layers.com/fr/bits/event-driven-cqrs).

```ack
J'ai compris
```
