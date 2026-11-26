---
title: "L'architecture hexagonale : ports, adaptateurs, et la règle de dépendance"
description: "Pourquoi et comment protéger les règles d'une application de ses détails techniques : le sens des dépendances dans une architecture en couches, l'inversion par des ports et des adaptateurs, les variantes onion et clean, et ce que l'hexagonale n'est pas (ni un remplaçant de MVC, ni des micro-services). Quand des couches bien tenues suffisent."
tags:
  - bit
  - architecture
  - design
difficulty: intermediate
duration: 13
requires: "0.8.0"
---

Une application a des **règles** (pas deux rendez-vous sur le même créneau) et des **détails techniques** (une base, un fournisseur de SMS, un framework web). L'architecture hexagonale organise le code pour que les règles ne dépendent pas des détails. Vous verrez d'où part cette idée, comment elle s'applique, et quand elle ne vaut pas sa complexité. L'exemple suivi : une clinique vétérinaire qui prend ses rendez-vous en ligne.

**Prérequis** : [Tiers, couches et MVC](https://byte-layers.com/fr/bits/tiers-layers-mvc), pour les couches présentation, métier et accès aux données.

# L'architecture hexagonale

## Une architecture en couches bien tenue

La clinique a organisé son code en trois couches : présentation, métier, accès aux données.

```scene
lesson: assets/hexagonal.scene.json
step: couches
```

Chaque couche n'appelle que celle du **dessous**. Le métier ne sait rien des pages ; la présentation ne touche pas la base. Bien tenue, cette organisation est **correcte** : elle sépare les responsabilités et suffit à beaucoup d'applications. L'hexagonale ne corrige pas un défaut des couches : elle change **un seul sens** de dépendance.

## Le problème : les règles dépendent des détails

Regardons la flèche entre le métier et l'accès aux données.

```scene
lesson: assets/hexagonal.scene.json
step: probleme
```

Le métier **appelle** du code écrit pour Postgres et pour un fournisseur de SMS précis. Il en dépend. Conséquence : pour tester la règle des créneaux, il faut une **vraie base** ; pour changer de fournisseur de SMS, il faut **retoucher le métier**. Le cœur de l'application, ce qui a le plus de valeur, change à cause de ce qui en a le moins.

## Ports et adaptateurs : inverser la flèche

L'idée d'Alistair Cockburn (2005) : mettre le **domaine** au centre, et lui faire dire ce dont il a besoin, avec ses mots.

```scene
lesson: assets/hexagonal.scene.json
step: ports-adaptateurs
```

Ce besoin s'appelle un **port** : une interface, par exemple « ranger les rendez-vous » ou « prévenir le client ». Un **adaptateur** l'implémente pour une technique précise (Postgres, un fournisseur de SMS). La dépendance s'est **inversée** : l'adaptateur connaît le domaine, plus l'inverse. De l'autre côté, d'autres adaptateurs **appellent** le domaine : le web, l'appli mobile, et les tests, sans base.

> 💡 **Remarque.** L'hexagone n'a rien de spécial : six côtés laissaient la place de dessiner plusieurs ports. On dit aussi **ports et adaptateurs**.

## Onion et clean : la même règle, d'autres dessins

Deux variantes connues dessinent des cercles plutôt qu'un hexagone.

```scene
lesson: assets/hexagonal.scene.json
step: onion-clean
```

L'**architecture onion** (Jeffrey Palermo) et la **clean architecture** (Robert C. Martin) rangent le code en cercles : au centre le **domaine**, autour les **cas d'usage** (prendre un rendez-vous, l'annuler), à l'extérieur le web, la base et les frameworks. Leur règle commune, la **règle de dépendance** : un cercle ne connaît que les cercles plus au centre. Les noms et le nombre de cercles varient d'un auteur à l'autre ; l'idée est la même.

## Ce que l'hexagonale n'est pas

Deux confusions reviennent souvent.

```scene
lesson: assets/hexagonal.scene.json
step: ce-quelle-nest-pas
```

L'hexagonale ne **remplace pas MVC** : MVC organise l'interface web, et vit tout entier dans l'**adaptateur web** ; son modèle, c'est le domaine. Elle ne veut pas dire **micro-services** non plus : une application dessinée en hexagone se livre très souvent **d'un seul bloc**, c'est un monolithe bien rangé. L'hexagonale organise le code **dans** un programme ; le découpage en programmes est une autre décision.

## À toi : couches ou hexagonale ?

Ports et adaptateurs ajoutent des interfaces et un peu d'indirection. Ils valent ce prix quand les **règles sont riches**, testées souvent, ou quand un **détail change** (plusieurs entrées, un fournisseur qu'on remplace). Pour un service qui lit et écrit des données avec peu de règles, des **couches** bien tenues suffisent. On peut aussi n'ajouter un port que là où un détail change vraiment. Trois situations : choisis l'organisation la plus raisonnable.

```quiz
title: "Couches ou hexagonale ?"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Une petite appli interne liste et modifie les fiches du personnel. Presque aucune règle, une seule base qui ne changera pas."
    answers:
      - "Des couches bien tenues"
      - "Une hexagonale complète, avec un port par table"
      - "Des micro-services"
    correct: 1
    explanation: "Peu de règles, aucun détail qui change : les ports n'apporteraient que des fichiers en plus."
  - prompt: "Un moteur de tarification d'assurance : des centaines de règles, testées à chaque changement, appelées par un site, une appli et un traitement de nuit."
    answers:
      - "Mettre les règles dans les contrôleurs web"
      - "Une hexagonale : le domaine au centre, un adaptateur par entrée, des tests sans base"
      - "Un micro-service par règle"
    correct: 2
    explanation: "Des règles riches, plusieurs entrées, des tests fréquents : c'est le cas pour lequel l'hexagonale a été pensée."
  - prompt: "Ton équipe veut passer d'un fournisseur de SMS à un autre, et le métier appelle directement la bibliothèque du premier."
    answers:
      - "Ajouter un port « prévenir le client » et un adaptateur par fournisseur"
      - "Réécrire toute l'application en hexagonale avant de changer"
      - "Copier le code du métier pour chaque fournisseur"
    correct: 1
    explanation: "On peut introduire un port là où un détail change, sans tout réorganiser."
```

> 📖 [Hexagonal Architecture (Alistair Cockburn, en anglais)](https://alistair.cockburn.us/hexagonal-architecture/) · [The Clean Architecture (Robert C. Martin, en anglais)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

## Quatre questions pour vérifier ce que vous avez retenu

```quiz
title: "L'architecture hexagonale"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Quel problème l'architecture hexagonale résout-elle ?"
    answers:
      - "Les couches sont une mauvaise pratique"
      - "Les règles métier dépendent des détails techniques (base, fournisseurs, frameworks)"
      - "Une application doit être découpée en plusieurs programmes"
    correct: 2
    explanation: "Des couches bien tenues sont correctes. L'hexagonale inverse un sens de dépendance pour protéger les règles."
  - prompt: "Qu'est-ce qu'un port ?"
    answers:
      - "Un numéro réseau sur lequel écoute le serveur"
      - "Une interface définie par le domaine, avec ses mots, pour un besoin (ranger, prévenir…)"
      - "Un fichier de configuration"
    correct: 2
    explanation: "Le port appartient au domaine. L'adaptateur l'implémente pour une technique précise. Rien à voir avec un port réseau."
  - prompt: "Où vit MVC dans une architecture hexagonale ?"
    answers:
      - "Dans l'adaptateur web : son modèle, c'est le domaine"
      - "Nulle part, l'hexagonale l'interdit"
      - "Au centre, à la place du domaine"
    correct: 1
    explanation: "MVC organise l'interface web. Il s'insère dans l'adaptateur web, et appelle le domaine."
  - prompt: "Une application en architecture hexagonale est-elle forcément faite de micro-services ?"
    answers:
      - "Oui, chaque adaptateur est un service"
      - "Non : elle organise le code dans un programme, souvent livré d'un seul bloc"
      - "Oui, sinon ce n'est pas de l'hexagonale"
    correct: 2
    explanation: "L'hexagonale range le code à l'intérieur d'un programme. Le découpage en programmes est une décision séparée."
```

## Récap

- Des **couches** bien tenues sont correctes, et suffisent quand il y a peu de règles.
- Le problème visé : les **règles** qui dépendent des **détails techniques**.
- **Ports et adaptateurs** : le domaine définit ses **ports**, des **adaptateurs** les implémentent ; la dépendance s'**inverse**, et les règles se testent sans base.
- **Onion** et **clean** : la même **règle de dépendance**, vers le centre, dessinée en cercles.
- L'hexagonale ne remplace pas **MVC** (il vit dans l'adaptateur web) et ne veut pas dire **micro-services**.

Comment découper une application en plusieurs programmes, et quand : [Monolithe, monolithe modulaire, micro-services](https://byte-layers.com/fr/bits/monolith-to-microservices).

```ack
J'ai compris
```
