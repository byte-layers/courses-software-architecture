---
title: "Tiers, couches et MVC : trois notions à ne pas mélanger"
description: "Le tiers dit sur quelles machines tourne une application, la couche dit comment son code est rangé, MVC dit comment un écran se construit. Trois questions différentes, avec un site de réservation de cinéma pour exemple : couches présentation, métier et accès aux données, le piège des deux « présentation », le contrôleur qui orchestre et le modèle qui porte les règles, MVC sur le serveur ou dans le navigateur."
tags:
  - bit
  - architecture
  - mvc
difficulty: intermediate
duration: 12
requires: "0.8.0"
---

On entend souvent « une architecture trois tiers », « une architecture en couches » et « une architecture MVC » comme s'il s'agissait de trois variantes de la même chose. Ce n'est pas le cas : chacun de ces mots répond à une question différente. Vous saurez les distinguer, et placer la logique métier au bon endroit. L'exemple suivi : le site de réservation d'un cinéma.

**Prérequis** : [Les architectures d'un programme, du poste seul au n tiers](https://byte-layers.com/fr/bits/program-architectures), pour les trois rôles (afficher, décider, stocker) et le trois tiers.

# Tiers, couches et MVC

## Trois mots, trois questions

Un cinéma vend ses places en ligne. Le spectateur choisit une séance, demande trois places, et le site confirme. Deux règles : **dix places au plus** par réservation, et une place ne se vend qu'une fois.

```scene
lesson: assets/tiers-layers-mvc.scene.json
step: trois-questions
```

Le **tiers** répond à « sur quelles machines ? » : il se voit sur un plan du réseau. La **couche** et **MVC** répondent à « comment le code est-il rangé ? » : ils se voient en ouvrant le code. Une même application a donc, en même temps, des tiers, des couches et, souvent, un patron comme MVC.

## Trois couches dans un seul programme

Ouvrons le programme qui tourne sur le serveur web du cinéma. Son code est rangé en **couches** : chacune a une responsabilité, et n'appelle que celle du dessous.

```scene
lesson: assets/tiers-layers-mvc.scene.json
step: couches
```

La **présentation** reçoit la demande, le **métier** applique les règles (on dit aussi le **domaine**), l'**accès aux données** parle à la base. Le métier ne sait rien du HTML ni du SQL : on peut changer l'un ou l'autre sans toucher aux règles. C'est l'**architecture en couches** (*layered architecture*). Trois couches, mais **un seul programme** sur une seule machine : un seul tiers.

## Le tiers présentation n'est pas la couche présentation

Le même schéma cache un piège de vocabulaire, parce que les deux notions emploient le même mot.

```scene
lesson: assets/tiers-layers-mvc.scene.json
step: deux-presentations
```

Le **tiers présentation** est une **machine** : le poste et son navigateur. La **couche présentation** est du **code**, et dans ce site elle tourne sur le **serveur**. On peut d'ailleurs ranger un client lourd, installé sur un seul poste, en trois couches : il aura trois couches et un seul tiers. Quand quelqu'un dit « présentation », demandez-vous s'il parle d'une machine ou d'un dossier de code.

## À toi : combien de tiers, combien de couches ?

Deux situations. Compte d'abord les machines, puis les rangements du code.

```quiz
title: "Compter les tiers et les couches"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Un logiciel de caisse est installé sur un seul poste. Son code est rangé en présentation, métier et accès aux données ; ses données sont dans un fichier sur le même poste. Combien de tiers, combien de couches ?"
    answers:
      - "Un tiers, trois couches"
      - "Trois tiers, trois couches"
      - "Un tiers, une couche"
    correct: 1
    explanation: "Une seule machine, donc un seul tiers. Le code, lui, est rangé en trois couches : le rangement du code ne dépend pas du nombre de machines."
  - prompt: "Un site de cinéma : le navigateur, un serveur web dont le programme a trois couches, une base de données sur sa propre machine. Combien de tiers ?"
    answers:
      - "Trois : le poste, le serveur web, le serveur de base de données"
      - "Cinq : trois couches, plus le navigateur et la base"
      - "Un, puisqu'il n'y a qu'un programme à nous"
    correct: 1
    explanation: "On compte les niveaux de machines : trois. Les couches du programme ne s'ajoutent pas aux tiers, elles sont à l'intérieur de l'un d'eux."
```

## MVC : un clic, un écran

Reste le troisième mot. **MVC** (modèle, vue, contrôleur) n'est pas une architecture de système : c'est un **patron de présentation**, une façon de découper le code qui reçoit une action et construit l'écran qui répond.

```scene
lesson: assets/tiers-layers-mvc.scene.json
step: mvc
```

La **vue** affiche, le **contrôleur** reçoit le clic et **orchestre**, le **modèle** porte les **règles métier** et les données. Le contrôleur ne décide pas si trois places sont possibles : il le demande au modèle, puis choisit la page à montrer. Dans une architecture en couches, contrôleur et vue appartiennent à la couche présentation, et le modèle est le domaine, ou la porte qui y mène.

## Où vit MVC : sur le serveur ou dans le navigateur

Le même écran de réservation peut se construire à deux endroits.

```scene
lesson: assets/tiers-layers-mvc.scene.json
step: ou-vit-mvc
```

Avec le **rendu serveur**, contrôleur, modèle et vue (un **gabarit** de page) tournent sur le serveur, qui envoie une page toute faite. Avec une **application dans le navigateur** (*SPA*, *Single Page Application*), la vue et son contrôleur tournent sur le poste ; le serveur expose une **API** qui répond en données. Le navigateur peut vérifier un champ pour le confort, mais les **règles qui comptent** restent sur le serveur : le poste ne décide pas.

> 💡 **Remarque.** Les frameworks du navigateur (Angular, Vue, React) découpent l'écran en composants et emploient des variantes de MVC (MVVM…). Ils restent dans la même famille : séparer ce qu'on affiche de ce qu'on décide.

> 📖 [MVC (glossaire MDN)](https://developer.mozilla.org/fr/docs/Glossary/MVC) · [Presentation Domain Data Layering (Martin Fowler, en anglais)](https://martinfowler.com/bliki/PresentationDomainDataLayering.html)

## À toi : où va ce code ?

Trois morceaux de code du site de cinéma. Range chacun dans la bonne pièce de MVC.

```quiz
title: "Ranger le code dans MVC"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Refuser une réservation de plus de dix places."
    answers:
      - "Le modèle : c'est une règle métier"
      - "Le contrôleur : c'est lui qui reçoit la demande"
      - "La vue : elle affiche le message d'erreur"
    correct: 1
    explanation: "Une règle du cinéma vit dans le modèle (le domaine). Écrite dans le contrôleur, elle serait à recopier dans chaque contrôleur qui réserve : c'est l'erreur la plus courante."
  - prompt: "Après la réservation, choisir d'afficher la page de confirmation ou la page d'erreur."
    answers:
      - "Le modèle"
      - "Le contrôleur : il orchestre et choisit la vue"
      - "La base de données"
    correct: 2
    explanation: "Le contrôleur demande au modèle, lit sa réponse, puis choisit la vue. Il orchestre, il ne décide pas des règles."
  - prompt: "Afficher le bouton « Réserver » en gris quand la séance est complète."
    answers:
      - "Le contrôleur"
      - "Le modèle"
      - "La vue : elle montre l'état que le modèle lui donne"
    correct: 3
    explanation: "Savoir que la séance est complète, c'est le modèle ; le montrer en gris, c'est la vue."
```

## Quatre questions pour vérifier ce que vous avez retenu

```quiz
title: "Tiers, couches et MVC"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Quelle notion répond à la question « sur quelles machines tourne l'application ? »"
    answers:
      - "Les tiers"
      - "Les couches"
      - "MVC"
    correct: 1
    explanation: "Un tiers est un niveau de machines. Couches et MVC rangent le code, quelle que soit la machine."
  - prompt: "Dans une architecture en couches bien tenue, que s'interdit la couche métier ?"
    answers:
      - "Appliquer les règles du domaine"
      - "Écrire elle-même du SQL ou du HTML"
      - "Être appelée par la couche présentation"
    correct: 2
    explanation: "Le métier porte les règles et laisse le HTML à la présentation, le SQL à l'accès aux données. Chaque couche n'appelle que celle du dessous."
  - prompt: "MVC, c'est :"
    answers:
      - "Une architecture trois tiers, avec une machine par lettre"
      - "Un patron de présentation, qui découpe le code qui construit un écran"
      - "Une architecture qui remplace l'architecture en couches"
    correct: 2
    explanation: "MVC organise la présentation. Il vit dans un tiers (le serveur, ou le navigateur pour une SPA) et dans la couche présentation d'une architecture en couches."
  - prompt: "Dans MVC, où vit la logique métier ?"
    answers:
      - "Dans le contrôleur, qui reçoit les demandes"
      - "Dans la vue, qui connaît l'écran"
      - "Dans le modèle, c'est-à-dire le domaine"
    correct: 3
    explanation: "Le contrôleur orchestre, la vue affiche, le modèle porte les règles et les données."
```

## Récap

- **Tiers** : un niveau de machines ; il se voit sur le réseau.
- **Couches** : un rangement du code d'un programme (présentation, métier ou domaine, accès aux données) ; chacune n'appelle que celle du dessous ; plusieurs couches tiennent dans un seul tiers.
- Le **tiers présentation** est une machine, la **couche présentation** est du code, souvent sur le serveur.
- **MVC** est un **patron de présentation** : la vue affiche, le contrôleur orchestre, le modèle porte les règles métier.
- Avec le **rendu serveur**, MVC tourne sur le serveur ; avec une **SPA**, la vue et son contrôleur tournent dans le navigateur, et les règles qui comptent restent derrière l'API.

Pour aller plus loin dans l'organisation du code : [Couches, hexagonale, onion, clean : vers qui pointent les dépendances](https://byte-layers.com/fr/bits/hexagonal-architecture). Pour ce qui se déploie ensemble : [Monolithe, monolithe modulaire, micro-services](https://byte-layers.com/fr/bits/monolith-to-microservices).

```ack
J'ai compris
```
