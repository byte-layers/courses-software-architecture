---
title: "Les protocoles entre programmes : de TCP à gRPC"
description: "Comment deux programmes se parlent à travers le réseau : le modèle OSI comme repère, TCP ou UDP (livraison garantie ou rapide), REST sur HTTP, GraphQL, gRPC entre services, et quand le serveur doit parler le premier : polling, SSE, WebSocket. Pour chacun, le problème qu'il résout et ce qu'il coûte."
tags:
  - bit
  - architecture
  - network
  - api
difficulty: intermediate
duration: 14
requires: "0.8.0"
---

Deux programmes sur deux machines n'ont qu'une façon de se parler : s'envoyer des messages à travers le réseau, selon des règles communes. Ces règles sont les **protocoles**. Vous saurez situer les plus courants, ce que chacun résout, et lequel choisir pour quel besoin. L'exemple suivi : un transporteur de colis, son appli de suivi et ses services internes.

**Prérequis** : [Le web : une adresse, une requête, une page](https://byte-layers.com/fr/bits/web-request-response), pour HTTP, les requêtes et les codes de statut.

# Les protocoles entre programmes

## Le modèle OSI, un repère pour ranger les protocoles

Un message qui part d'un programme passe par plusieurs protocoles, chacun posé sur le précédent, comme une lettre dans une enveloppe, elle-même dans un sac postal.

```scene
lesson: assets/protocols.scene.json
step: osi
```

Le **modèle OSI** range ces protocoles en sept couches, du câble jusqu'à l'application. C'est un **repère** : les protocoles réels ne s'y rangent pas toujours exactement. **IP** amène les paquets jusqu'à la bonne **machine** ; **TCP** ou **UDP**, jusqu'au bon **programme**, grâce à un numéro de **port**. Ce contenu parle des couches **transport** et **application**.

## TCP ou UDP : livraison garantie, ou livraison rapide

Le transporteur envoie des données en quatre paquets, et le troisième se perd. Les deux protocoles de transport réagissent différemment.

```scene
lesson: assets/protocols.scene.json
step: tcp-udp
```

**TCP** ouvre une connexion, numérote les paquets, fait accuser réception et **renvoie** ce qui manque : tout arrive, dans l'ordre, au prix d'un peu d'attente. C'est lui sous le web, les API et les bases de données. **UDP** envoie sans rien vérifier : ce qui se perd est perdu, mais rien ne ralentit. Il convient aux appels vidéo, aux jeux, au DNS.

> 💡 **Remarque.** HTTP/3 s'appuie sur **QUIC**, un protocole posé sur UDP qui refait lui-même les garanties de TCP, plus vite.

## REST : des ressources et des verbes, sur HTTP

L'appli de suivi parle à l'API du transporteur en HTTP. La façon la plus courante d'organiser une telle API s'appelle REST.

```scene
lesson: assets/protocols.scene.json
step: rest
```

**REST** n'est pas un protocole de plus : c'est une **façon d'utiliser HTTP**. L'adresse désigne une **ressource** (le colis 42), le **verbe** HTTP dit ce qu'on en fait : `GET` pour lire, `POST` pour créer, `PATCH` ou `PUT` pour modifier, `DELETE` pour supprimer. Les réponses sont souvent en JSON, avec les codes de statut HTTP. Simple, lisible et compris partout.

## GraphQL : le client demande exactement ce qu'il affiche

Un écran de l'appli mobile affiche le colis, son expéditeur et ses trois dernières étapes. En REST, ce sont trois ressources.

```scene
lesson: assets/protocols.scene.json
step: graphql
```

Avec **GraphQL**, l'API a une seule adresse. Le client envoie une requête qui décrit **exactement les champs** voulus, et reçoit ces champs en une fois : moins d'allers-retours, des réponses taillées pour l'écran. En échange, le serveur est plus complexe à écrire, à mettre en cache et à protéger contre les requêtes trop gourmandes.

## gRPC : un contrat strict et des messages compacts, entre services

Derrière l'appli, deux services internes s'appellent des milliers de fois par seconde.

```scene
lesson: assets/protocols.scene.json
step: grpc
```

**gRPC** part d'un **contrat** écrit une fois (un fichier `.proto`), dont un outil génère le code des deux côtés : on appelle le service distant comme une fonction. Les messages voyagent en **binaire**, compacts, sur HTTP/2, et peuvent arriver en flux continu. Rapide et typé, mais peu lisible et mal pris en charge par les navigateurs : on le réserve aux échanges **entre services**.

## Polling, SSE, WebSocket : quand le serveur a quelque chose à dire

La page de suivi doit montrer le livreur qui avance. Or en HTTP, c'est toujours le client qui pose la question.

```scene
lesson: assets/protocols.scene.json
step: temps-reel
```

Le **polling** redemande à intervalle régulier : simple, mais la plupart des réponses disent « rien de neuf ». Avec **SSE** (*Server-Sent Events*), une connexion HTTP reste ouverte et le **serveur envoie** quand il a du neuf, dans un seul sens. Le **WebSocket** ouvre une connexion dans les **deux sens**, pour discuter avec le livreur ou jouer en ligne.

## À toi : quel protocole pour quel besoin ?

Quatre besoins du transporteur. Choisis la technique la mieux adaptée.

```quiz
title: "Quel protocole ?"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Une API publique pour que des boutiques en ligne créent des envois et suivent leurs colis."
    answers:
      - "REST sur HTTP, en JSON"
      - "gRPC"
      - "UDP"
    correct: 1
    explanation: "Une API ouverte à des clients variés gagne à être simple et comprise partout : REST en JSON."
  - prompt: "Deux services internes échangent des milliers de positions par seconde, écrits dans deux langages différents."
    answers:
      - "Du polling toutes les secondes"
      - "gRPC, avec un contrat .proto"
      - "Une page HTML"
    correct: 2
    explanation: "Entre services, gRPC apporte des messages compacts, un contrat typé et du code généré dans chaque langage."
  - prompt: "La page de suivi affiche la position du livreur, mise à jour quand elle change. Le client n'envoie rien."
    answers:
      - "SSE : le serveur pousse les nouvelles positions"
      - "WebSocket, forcément"
      - "Recharger la page à la main"
    correct: 1
    explanation: "Un seul sens, du serveur vers la page : SSE suffit. Le WebSocket sert quand le client doit aussi envoyer."
  - prompt: "Un appel vidéo entre le client et le livreur, où une image perdue vaut mieux qu'une image en retard."
    answers:
      - "TCP, pour ne rien perdre"
      - "UDP, pour ne pas attendre"
      - "REST"
    correct: 2
    explanation: "En vidéo, attendre un paquet renvoyé fige l'image. UDP laisse passer la perte et garde le rythme."
```

> 📖 [HTTP (MDN)](https://developer.mozilla.org/fr/docs/Web/HTTP) · [WebSocket (MDN)](https://developer.mozilla.org/fr/docs/Web/API/WebSockets_API) · [gRPC, introduction (en anglais)](https://grpc.io/docs/what-is-grpc/introduction/) · [GraphQL, introduction](https://graphql.org/learn/)

## Quatre questions pour vérifier ce que vous avez retenu

```quiz
title: "Les protocoles entre programmes"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Qu'apporte TCP par rapport à UDP ?"
    answers:
      - "Tout arrive, dans l'ordre : ce qui se perd est renvoyé"
      - "Les messages arrivent plus vite"
      - "Les messages sont chiffrés"
    correct: 1
    explanation: "TCP accuse réception et renvoie ce qui manque. UDP est plus rapide parce qu'il ne fait rien de tout ça. Le chiffrement, c'est TLS, au-dessus."
  - prompt: "Dans une API REST, que désigne l'adresse /colis/42 ?"
    answers:
      - "Une action à exécuter sur le serveur"
      - "Une ressource : le colis 42 ; le verbe HTTP dit ce qu'on en fait"
      - "Le numéro de port du service"
    correct: 2
    explanation: "REST sépare la ressource (l'adresse) de l'action (le verbe : GET, POST, PATCH, DELETE)."
  - prompt: "Quel problème GraphQL résout-il d'abord ?"
    answers:
      - "Le chiffrement des échanges"
      - "Les écrans qui doivent appeler plusieurs ressources et recevoir plus que ce qu'ils affichent"
      - "La perte de paquets sur le réseau"
    correct: 2
    explanation: "Le client décrit les champs dont il a besoin et les reçoit en une requête."
  - prompt: "Quelle technique permet au serveur et au navigateur de s'envoyer des messages dans les deux sens, sur une connexion qui reste ouverte ?"
    answers:
      - "Le polling"
      - "SSE"
      - "WebSocket"
    correct: 3
    explanation: "SSE ne pousse que du serveur vers le navigateur ; le polling redemande. Le WebSocket est bidirectionnel."
```

## Récap

- Le **modèle OSI** est un repère : **IP** trouve la machine, **TCP** ou **UDP** le programme, puis le protocole d'**application**.
- **TCP** : tout arrive, dans l'ordre, un peu plus tard ; **UDP** : rapide, sans garantie.
- **REST** : une façon d'utiliser HTTP, des **ressources** et des **verbes**.
- **GraphQL** : le client choisit ses champs, en une requête ; **gRPC** : un contrat `.proto`, des messages binaires, entre services.
- Quand le serveur a du neuf : **polling** (on redemande), **SSE** (le serveur pousse), **WebSocket** (les deux sens).

Ce que change le fait d'attendre ou non la réponse : [Synchrone ou asynchrone](https://byte-layers.com/fr/bits/sync-async-communication). Les messages qu'on dépose sans attendre : [Files de messages et journaux d'événements](https://byte-layers.com/fr/bits/queues-and-event-logs).

```ack
J'ai compris
```
