---
title: "Le prix des micro-services : réseau, déploiements, observabilité, et quand s'en passer"
description: "Ce que coûtent les micro-services : l'appel de fonction qui devient un appel réseau (latence, échec possible), les déploiements multiples et les contrats d'API à tenir, le débogage à travers plusieurs programmes, l'observabilité (journaux centralisés, métriques, traces, identifiant de corrélation), et les situations où un monolithe modulaire suffit."
tags:
  - bit
  - architecture
  - microservices
  - observability
difficulty: intermediate
duration: 13
requires: "0.8.0"
---

Découper une application en micro-services apporte de la liberté : chaque partie se déploie seule. Cette liberté a un prix, qu'on découvre souvent après coup. Vous verrez les quatre principaux postes de ce prix, les outils qui le rendent supportable, et les situations où il vaut mieux ne pas le payer. L'exemple suivi : une plateforme de livraison de repas.

**Prérequis** : [Monolithe, monolithe modulaire, micro-services](https://byte-layers.com/fr/bits/monolith-to-microservices), pour l'unité de déploiement et ce qu'est un micro-service.

# Le prix des micro-services

## Un appel de fonction devient un appel réseau

La plateforme doit faire payer une commande. Comparons la même demande dans un seul programme, puis entre deux services.

```scene
lesson: assets/costs.scene.json
step: appel-reseau
```

Dans un programme, un appel de fonction prend quelques microsecondes et ne se perd pas. Entre deux services, la demande traverse le **réseau** : quelques millisecondes à chaque fois, et elle peut **échouer** (réseau coupé, service arrêté ou surchargé). Une page qui enchaîne dix appels paie dix fois cette **latence**. Chaque appel doit maintenant prévoir le cas où la réponse ne vient pas.

## Plusieurs déploiements, un contrat à tenir

Chaque service se déploie seul, souvent par une équipe différente. C'est l'avantage, et c'est aussi un risque.

```scene
lesson: assets/costs.scene.json
step: contrats
```

L'**API** d'un service est un **contrat** : la liste des demandes acceptées et de ce qu'il répond. La changer sans prévenir casse ceux qui s'en servent, déployés à un autre moment. La parade : un contrat **versionné**, où l'ancienne version reste servie le temps que chacun migre, et des tests qui vérifient le contrat avant chaque déploiement. Avec un monolithe, le compilateur ou les tests auraient vu l'erreur dans le même projet.

## Une erreur, cinq programmes : où chercher ?

Un client voit « Erreur, réessayez plus tard ». Derrière, sa commande a traversé quatre services.

```scene
lesson: assets/costs.scene.json
step: deboguer
```

Chaque service écrit son **journal** (*log*) : les lignes qui disent ce qu'il fait et ce qui rate. Avec cinq services sur cinq machines, il faut ouvrir cinq journaux, et deviner quelles lignes parlent de la même commande. C'est le **débogage distribué** : l'erreur se voit à un endroit, sa cause est ailleurs.

## Observabilité : journaux centralisés et identifiant de corrélation

Le remède s'appelle l'**observabilité** : pouvoir comprendre ce que fait le système depuis l'extérieur, sans se connecter à chaque machine.

```scene
lesson: assets/costs.scene.json
step: observer
```

Les journaux de tous les services vont à **un seul endroit**. À l'entrée, chaque requête reçoit un **identifiant de corrélation** (*correlation ID*), que chaque service transmet et recopie dans ses lignes : une recherche montre tout le parcours. Deux autres outils complètent les journaux : les **métriques** (des chiffres dans le temps : requêtes, erreurs, temps de réponse) et les **traces**, qui chronomètrent chaque étape d'une requête d'un service à l'autre.

> 💡 **Remarque.** OpenTelemetry est le standard ouvert qui produit ces trois signaux. Grafana, Loki, Prometheus, Jaeger ou Elasticsearch servent à les ranger et à les lire.

## À toi : suivre une commande

Le même système de livraison. Utilise ce que tu viens de voir pour trouver la panne.

```quiz
title: "Suivre une commande"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Un client signale une erreur à 12 h 03. Que cherches-tu en premier dans les journaux centralisés ?"
    answers:
      - "L'identifiant de corrélation de sa requête, pour voir tout son parcours"
      - "Toutes les lignes de 12 h 03, de tous les services"
      - "Le journal de l'accueil seulement, puisque c'est lui qui a répondu"
    correct: 1
    explanation: "L'identifiant de corrélation relie les lignes de tous les services qui ont traité cette requête. Toutes les lignes de 12 h 03 en mélangent des milliers d'autres."
  - prompt: "L'identifiant 7f3a apparaît dans Accueil, Commandes et Paiement, mais pas dans Notifications. Qu'en conclus-tu ?"
    answers:
      - "Notifications a planté avant d'écrire quoi que ce soit, ou Paiement ne lui a pas transmis l'identifiant"
      - "La requête n'est jamais passée par Paiement"
      - "Tout s'est bien passé"
    correct: 1
    explanation: "La trace s'arrête entre Paiement et Notifications : soit Notifications n'a pas reçu ou pas traité la requête, soit l'identifiant a été perdu en route. C'est là qu'on regarde."
  - prompt: "Les erreurs de Paiement montent depuis une heure, sans qu'aucun client ne se plaigne encore. Quel outil le montre le mieux ?"
    answers:
      - "Une trace d'une seule requête"
      - "Une métrique : le nombre d'erreurs par minute, dans le temps"
      - "Le code source de Paiement"
    correct: 2
    explanation: "Une métrique suit une quantité dans le temps : on voit la courbe monter, et une alerte peut prévenir avant les clients."
```

## Quand ne pas faire de micro-services

Toutes ces dépenses ne valent que si elles résolvent un vrai problème.

```scene
lesson: assets/costs.scene.json
step: quand-pas
```

Les micro-services répondent à des problèmes d'**organisation** (plusieurs équipes, des rythmes différents) et de **charge** (une partie qui doit tenir seule). Une petite équipe, un métier qui bouge encore, une charge qui monte partout pareil : un **monolithe modulaire** fait mieux, pour moins cher. Et sans déploiement automatique ni supervision, rien ne compense le coût.

> 📖 [Microservice Prerequisites (Martin Fowler, en anglais)](https://martinfowler.com/bliki/MicroservicePrerequisites.html) · [OpenTelemetry : observabilité (en anglais)](https://opentelemetry.io/docs/concepts/observability-primer/)

## Quatre questions pour vérifier ce que vous avez retenu

```quiz
title: "Le prix des micro-services"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Pourquoi un appel entre deux services coûte-t-il plus cher qu'un appel de fonction ?"
    answers:
      - "Il traverse le réseau : il prend des millisecondes et peut échouer"
      - "Il demande d'écrire plus de code"
      - "Il utilise plus de mémoire sur le serveur"
    correct: 1
    explanation: "Le réseau ajoute de la latence et la possibilité que la réponse ne vienne jamais. Chaque appel doit prévoir ce cas."
  - prompt: "L'équipe Commandes renomme un champ de son API et déploie. Le service Restaurants casse. Quelle pratique l'aurait évité ?"
    answers:
      - "Déployer Restaurants plus souvent"
      - "Versionner le contrat : garder l'ancienne version servie le temps que Restaurants migre"
      - "Mettre les deux services sur la même machine"
    correct: 2
    explanation: "Un contrat versionné laisse les deux versions coexister. Chaque service migre à son rythme, ce qui est tout l'intérêt de déployer séparément."
  - prompt: "À quoi sert un identifiant de corrélation ?"
    answers:
      - "À chiffrer les échanges entre services"
      - "À relier les lignes de journal de tous les services qui ont traité la même requête"
      - "À identifier l'utilisateur connecté"
    correct: 2
    explanation: "Il est créé à l'entrée et transmis de service en service. Une recherche sur cet identifiant montre tout le parcours d'une requête."
  - prompt: "Une équipe de trois développeurs lance un produit dont le métier change chaque semaine. Que lui conseiller ?"
    answers:
      - "Des micro-services, pour être prêts à grandir"
      - "Un monolithe modulaire, en gardant des frontières qu'on pourra couper plus tard"
      - "Un micro-service par écran"
    correct: 2
    explanation: "Sans plusieurs équipes ni charge à part, les micro-services n'apportent que leurs coûts. Des frontières nettes dans un seul déploiement préparent l'avenir pour moins cher."
```

## Récap

- Un appel entre services traverse le **réseau** : **latence** à chaque appel, et un échec toujours possible.
- Chaque service se déploie seul : son **API** est un **contrat**, à **versionner** pour ne casser personne.
- Le **débogage distribué** : l'erreur se voit à un endroit, sa cause est dans un autre service.
- L'**observabilité** : **journaux centralisés**, **métriques**, **traces**, et un **identifiant de corrélation** qui suit chaque requête.
- Sans plusieurs équipes, sans charge à part, sans outillage : un **monolithe modulaire** suffit.

Comment ces services se parlent, et ce que change le fait d'attendre ou non la réponse : [Synchrone ou asynchrone](https://byte-layers.com/fr/bits/sync-async-communication).

```ack
J'ai compris
```
