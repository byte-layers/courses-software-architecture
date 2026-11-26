---
title: "Passerelle d'API, BFF et micro-frontends : devant les micro-services"
description: "Ce qu'on place devant des micro-services pour que les interfaces s'en servent : la passerelle d'API (une seule entrée, routage, authentification, limite de débit), l'annuaire de services pour trouver des copies qui bougent, le BFF taillé pour chaque interface, et les micro-frontends qui découpent l'interface elle-même, avec une application hôte et un design system partagé. Et quand s'en passer."
tags:
  - bit
  - architecture
  - microservices
  - api
difficulty: intermediate
duration: 13
requires: "0.8.0"
---

Des micro-services, chacun avec son API, c'est bien pour les équipes du back. Pour un site ou une appli mobile, c'est beaucoup d'adresses à connaître et de réponses à assembler. Vous verrez les pièces qu'on place **devant** les services pour simplifier la vie des interfaces, ce que chacune résout, et quand elle n'est pas utile. L'exemple suivi : une agence de voyages en ligne, avec un site, une appli mobile et quatre services.

**Prérequis** : [Monolithe, monolithe modulaire, micro-services](https://byte-layers.com/fr/bits/monolith-to-microservices), pour ce qu'est un service déployé seul, et [Tenir la charge : vertical, horizontal, répartiteur](https://byte-layers.com/fr/bits/scaling-load-balancing), pour les copies d'un même programme.

# Devant les micro-services

## Sans passerelle : chaque appli parle à chaque service

L'agence a quatre services : vols, hôtels, paiement, avis. Le site et l'appli les appellent directement.

```scene
lesson: assets/gateway.scene.json
step: sans-passerelle
```

Chaque appli connaît **quatre adresses**. Chaque service vérifie lui-même qui est connecté : le même code, quatre fois. Et quand un service change d'adresse ou se découpe en deux, il faut **republier les applis**, ce qui prend des jours pour une appli mobile, le temps que chacun la mette à jour.

## La passerelle d'API : une seule porte d'entrée

On place un programme devant tous les services.

```scene
lesson: assets/gateway.scene.json
step: passerelle
```

La **passerelle d'API** (*API gateway*) est le seul point d'entrée. Elle **route** chaque requête vers le bon service d'après son chemin (`/vols`, `/hotels`). Elle prend en charge ce qui est commun : vérifier **qui est connecté**, **limiter le débit** d'un client trop bavard, journaliser. Les services peuvent bouger derrière elle sans que les applis le sachent. En échange, elle devient un passage obligé : elle doit tenir la charge et ne jamais tomber.

> 💡 **Remarque.** Une passerelle ressemble à un reverse proxy, et elle en est souvent un. Elle y ajoute des règles d'API : authentification, quotas, transformation des requêtes.

## L'annuaire de services : trouver des copies qui bougent

Derrière la passerelle, chaque service tourne en plusieurs copies, et ces copies changent d'adresse à chaque redémarrage.

```scene
lesson: assets/gateway.scene.json
step: annuaire
```

L'**annuaire de services** (*service registry*) tient la liste des copies en service. Chaque copie s'y **inscrit** au démarrage et donne régulièrement signe de vie ; celle qui se tait est **retirée**. La passerelle, ou tout service qui en appelle un autre, demande à l'annuaire où envoyer sa requête. C'est la **découverte de services**. Souvent, la plateforme qui fait tourner les services la fournit déjà, sous la forme d'un nom DNS interne.

## Le BFF : un back taillé pour chaque interface

L'écran d'un voyage n'affiche pas la même chose sur le site et sur l'appli.

```scene
lesson: assets/gateway.scene.json
step: bff
```

Un **BFF** (*Backend For Frontend*) est un petit back écrit **pour une seule interface**, souvent par l'équipe qui fait cette interface. Il appelle les services nécessaires et renvoie **une seule réponse**, réduite à ce que l'écran affiche : moins d'allers-retours sur un réseau mobile lent. Le site a son BFF, l'appli le sien, et chacun évolue sans gêner l'autre. Le prix : un programme de plus par interface, à déployer et à surveiller.

## Micro-frontends : découper aussi l'interface

Quand le site devient aussi gros que le back, plusieurs équipes s'y marchent dessus.

```scene
lesson: assets/gateway.scene.json
step: micro-frontends
```

Les **micro-frontends** découpent l'interface par équipe, comme les micro-services découpent le back. Une **application hôte** (*shell*) charge les morceaux, gère la navigation et la connexion. Chaque morceau est construit et **déployé par son équipe**. Un **design system** partagé (boutons, couleurs, polices) garde une page cohérente. Le prix : plus de code à charger, des **versions à aligner**, et une page qui dépend de plusieurs livraisons.

## À toi : de quoi cette équipe a-t-elle besoin ?

Aucune de ces pièces n'est obligatoire. Une **passerelle** se justifie dès que plusieurs services sont exposés à l'extérieur. Un **annuaire**, quand les copies bougent et que la plateforme ne le fournit pas. Un **BFF**, quand des interfaces très différentes appellent les mêmes services. Des **micro-frontends**, seulement quand plusieurs équipes se gênent dans la même interface. Trois situations : choisis la réponse la plus raisonnable.

```quiz
title: "De quoi ont-ils besoin ?"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Une équipe de quatre personnes : un site, une API monolithique, une seule base."
    answers:
      - "Rien de tout ça : le site appelle l'API directement"
      - "Une passerelle, un annuaire et un BFF"
      - "Des micro-frontends"
    correct: 1
    explanation: "Un seul back, une seule adresse : une passerelle n'aurait rien à router, un BFF rien à assembler."
  - prompt: "Douze services, un site et une appli mobile. Chaque appli connaît les douze adresses, et chaque service vérifie le jeton à sa façon."
    answers:
      - "Une passerelle d'API devant les services"
      - "Fusionner les douze services en un"
      - "Des micro-frontends"
    correct: 1
    explanation: "Une entrée unique qui route et vérifie l'authentification une fois : c'est le rôle de la passerelle."
  - prompt: "Une montre connectée doit afficher un voyage avec trois chiffres, mais l'API renvoie des pages entières pensées pour le site."
    answers:
      - "Faire trois appels depuis la montre et trier les données sur place"
      - "Un BFF pour la montre, qui assemble et réduit la réponse"
      - "Changer l'API du site pour qu'elle renvoie trois chiffres"
    correct: 2
    explanation: "Le BFF taille la réponse pour son interface, sans changer ce que reçoivent les autres."
```

> 📖 [Pattern : API Gateway (microservices.io, en anglais)](https://microservices.io/patterns/apigateway.html) · [Backends for Frontends (Sam Newman, en anglais)](https://samnewman.io/patterns/architectural/bff/) · [Micro Frontends (martinfowler.com, en anglais)](https://martinfowler.com/articles/micro-frontends.html)

## Quatre questions pour vérifier ce que vous avez retenu

```quiz
title: "Devant les micro-services"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Que fait une passerelle d'API ?"
    answers:
      - "Elle stocke les données de tous les services"
      - "Elle sert de point d'entrée unique, route les requêtes et prend en charge ce qui est commun (authentification, débit)"
      - "Elle remplace les services"
    correct: 2
    explanation: "Les applis ne connaissent qu'elle. Elle route, vérifie, limite, et les services peuvent bouger derrière."
  - prompt: "À quoi sert un annuaire de services ?"
    answers:
      - "À lister les adresses des copies en service, qui changent à chaque redémarrage"
      - "À documenter l'API de chaque service"
      - "À garder les mots de passe des services"
    correct: 1
    explanation: "Chaque copie s'inscrit et donne signe de vie ; celle qui se tait est retirée. Les appelants demandent à l'annuaire où aller."
  - prompt: "Qu'est-ce qui distingue un BFF d'une passerelle d'API ?"
    answers:
      - "Rien, ce sont deux noms pour la même chose"
      - "Le BFF est écrit pour une seule interface et assemble ce qu'elle affiche ; la passerelle sert tout le monde"
      - "Le BFF tourne dans le navigateur"
    correct: 2
    explanation: "La passerelle est commune et générique. Le BFF est propre à une interface : une par site, une par appli."
  - prompt: "Quand des micro-frontends valent-ils leur prix ?"
    answers:
      - "Dès qu'un site a plus de dix pages"
      - "Quand plusieurs équipes se gênent pour livrer la même interface"
      - "Quand le back est en micro-services, toujours"
    correct: 2
    explanation: "Comme les micro-services, ils répondent à un problème d'organisation. Une seule équipe n'y gagne que des versions à aligner."
```

## Récap

- Sans rien devant, chaque interface connaît **chaque service** et chaque service refait l'**authentification**.
- La **passerelle d'API** : une entrée unique qui **route**, **authentifie** et **limite le débit** ; un passage obligé à rendre solide.
- L'**annuaire de services** : la liste des copies en service, pour la **découverte de services** ; souvent fourni par la plateforme.
- Le **BFF** : un back par interface, qui assemble une réponse taillée pour son écran.
- Les **micro-frontends** : l'interface découpée par équipe, une **application hôte** et un **design system** partagé ; seulement quand plusieurs équipes se gênent.

Comment ces services se parlent derrière la passerelle, en attendant la réponse ou non : [Synchrone ou asynchrone](https://byte-layers.com/fr/bits/sync-async-communication).

```ack
J'ai compris
```
