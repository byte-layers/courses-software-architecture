---
title: "Monolithe, monolithe modulaire, micro-services : ce qui se déploie ensemble"
description: "Ce qui définit un monolithe : son unité de déploiement, pas le nombre de serveurs. Déployer, le monolithe et ses copies, pourquoi « fullstack » et la séparation front / back ne sont pas des architectures, le monolithe modulaire et ses frontières, les micro-services qui se déploient chacun seul, et le piège du monolithe distribué."
tags:
  - bit
  - architecture
  - microservices
difficulty: intermediate
duration: 13
requires: "0.8.0"
---

« Monolithe » est souvent employé comme un reproche, et « micro-services » comme un progrès. Les deux mots ont pourtant un sens précis, qui ne dépend ni de la taille du code ni du nombre de serveurs : ils disent **ce qui se déploie ensemble**. Vous saurez reconnaître un monolithe, un monolithe modulaire et des micro-services, et éviter les confusions les plus courantes. L'exemple suivi : la boutique en ligne d'un vendeur de vélos.

**Prérequis** : [Tiers, couches et MVC](https://byte-layers.com/fr/bits/tiers-layers-mvc), pour la différence entre l'organisation du code et les machines.

# Monolithe, monolithe modulaire, micro-services

## Déployer : mettre une nouvelle version en service

Tout part d'un geste quotidien : livrer une correction. Sur la boutique, un développeur vient de corriger le calcul des frais de port.

```scene
lesson: assets/monolith.scene.json
step: deployer
```

**Déployer**, c'est installer une nouvelle version et la mettre en service à la place de l'ancienne. Entre les deux, la **construction** (*build*) produit un **artefact** : le paquet prêt à lancer. Ce qu'on construit et livre d'un bloc s'appelle une **unité de déploiement**. C'est elle, et rien d'autre, qui distingue les trois architectures de ce contenu.

## Le monolithe : tout se déploie ensemble

La boutique a quatre modules : catalogue, panier, paiement, livraison. Le code est bien rangé, mais tout part dans le même artefact.

```scene
lesson: assets/monolith.scene.json
step: monolithe
```

Un **monolithe** est une application livrée en **une seule unité de déploiement**. Le faire tourner sur trois serveurs ne change rien : ce sont trois **copies** du même artefact. À l'inverse, poser l'application et sa base sur une seule machine ne suffit pas à en faire un monolithe : c'est l'unité de déploiement qui compte. Le revers : une ligne changée dans le paiement, et c'est **toute la boutique** qu'on redéploie.

## Fullstack, front, back : ce ne sont pas des architectures

Trois mots reviennent dans les offres d'emploi et les discussions d'équipe. Aucun ne désigne une architecture.

```scene
lesson: assets/monolith.scene.json
step: front-back
```

« **Fullstack** » décrit un développeur qui travaille sur l'interface et sur le serveur, ou un framework qui couvre les deux dans un même projet. Séparer le **front** (l'appli du navigateur) et le **back** (l'API) donne **deux unités de déploiement**. Mais le back, avec ses quatre modules livrés ensemble, **reste un monolithe**. Ce découpage n'est pas non plus un monolithe modulaire : il coupe entre l'écran et le serveur, pas entre les domaines métier.

## Le monolithe modulaire : des frontières dans le code

On peut garder un seul déploiement et tenir des frontières strictes à l'intérieur.

```scene
lesson: assets/monolith.scene.json
step: modulaire
```

Dans un **monolithe modulaire**, chaque module a **ses tables** et une petite **interface publique** ; les autres modules ne passent que par elle. Le panier demande un prix au catalogue, il ne lit jamais ses tables. Un seul artefact à livrer, des appels de fonction rapides, et des modules qu'on pourra **sortir** un jour si l'un d'eux doit vivre à part. Beaucoup d'équipes s'arrêtent là, et elles ont raison.

## Micro-services : chacun se déploie seul

Dernière étape : chaque module devient un programme à part.

```scene
lesson: assets/monolith.scene.json
step: micro-services
```

Un **micro-service** est construit, testé et **déployé seul**, avec **ses propres données**. Le paiement change, on ne déploie que lui. En théorie, ce n'est ni la taille ni le nombre qui font un micro-service. En pratique, découper trop fin multiplie les programmes à surveiller, et chaque appel devient un appel **réseau**, plus lent et qui peut échouer.

> ⚠️ **Si deux services doivent toujours être déployés ensemble**, ou partagent la même base, ce ne sont pas des micro-services : c'est un **monolithe distribué**, qui cumule les coûts des deux.

## À toi : découper la boutique

La boutique grossit. Pour chaque situation, choisis l'organisation qui convient.

```quiz
title: "Découper la boutique"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Une équipe de quatre développeurs démarre la boutique. Le métier bouge encore chaque semaine. Que choisir ?"
    answers:
      - "Un monolithe modulaire : un seul déploiement, des frontières qu'on pourra couper plus tard"
      - "Quatre micro-services dès le départ, pour être prêts"
      - "Un seul gros module sans frontières, on rangera plus tard"
    correct: 1
    explanation: "Quand le domaine bouge et que l'équipe est petite, des frontières dans un seul déploiement coûtent peu. On sort un module en service le jour où il a une vraie raison de vivre à part."
  - prompt: "Le paiement doit être certifié et mis à jour chaque semaine par une équipe dédiée, sans bloquer le reste. Que faire de ce module ?"
    answers:
      - "Le laisser dans le monolithe : un module de plus ou de moins ne change rien"
      - "En faire un service à part, déployé seul, avec ses propres données"
      - "Lui donner un serveur plus puissant"
    correct: 2
    explanation: "Une équipe, un rythme et des contraintes propres : c'est une bonne raison d'en faire un service déployé seul."
  - prompt: "Le service Livraison lit directement les tables du service Commandes. Qu'est-ce que cela crée ?"
    answers:
      - "Rien de grave : c'est plus rapide qu'une API"
      - "Un couplage : on ne peut plus changer les tables de Commandes sans casser Livraison, ni les déployer séparément"
      - "Un monolithe modulaire"
    correct: 2
    explanation: "Une base partagée lie les deux services : c'est le chemin vers le monolithe distribué. Livraison doit passer par l'API de Commandes."
```

> 📖 [Microservices (Martin Fowler et James Lewis, en anglais)](https://martinfowler.com/articles/microservices.html) · [Monolith First (Martin Fowler, en anglais)](https://martinfowler.com/bliki/MonolithFirst.html)

## Quatre questions pour vérifier ce que vous avez retenu

```quiz
title: "Monolithe et micro-services"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Qu'est-ce qui fait d'une application un monolithe ?"
    answers:
      - "Elle tourne sur un seul serveur"
      - "Elle est livrée en une seule unité de déploiement"
      - "Son code dépasse cent mille lignes"
    correct: 2
    explanation: "Le monolithe se définit par son unité de déploiement. Il peut tourner sur dix serveurs, en dix copies."
  - prompt: "Une application est séparée en une SPA et une API ; l'API contient tous les modules métier. Qu'est-ce que l'API ?"
    answers:
      - "Un micro-service"
      - "Un monolithe modulaire, forcément"
      - "Un monolithe : tous ses modules se déploient ensemble"
    correct: 3
    explanation: "Séparer le front du back donne deux unités de déploiement, mais l'API reste un monolithe. Elle n'est modulaire que si ses modules ont de vraies frontières."
  - prompt: "Qu'est-ce qui distingue un monolithe modulaire d'un monolithe sans frontières ?"
    answers:
      - "Chaque module a ses tables et une interface publique ; les autres ne passent que par elle"
      - "Chaque module tourne sur sa machine"
      - "Chaque module a son propre artefact"
    correct: 1
    explanation: "Le monolithe modulaire garde un seul artefact. Ce sont les frontières dans le code et les données qui le rendent modulaire."
  - prompt: "Quel est le critère principal d'un micro-service ?"
    answers:
      - "Il fait moins de mille lignes"
      - "Il se déploie seul, avec ses propres données"
      - "Il est écrit dans un langage différent des autres"
    correct: 2
    explanation: "Le déploiement indépendant et les données propres. La taille n'est pas le critère, même si découper trop fin coûte cher en pratique."
```

## Récap

- **Déployer** : construire un **artefact** et le mettre en service ; ce qu'on livre d'un bloc est une **unité de déploiement**.
- **Monolithe** : une seule unité de déploiement, quel que soit le nombre de serveurs ou de copies.
- **Fullstack** est un profil ou un framework ; **front / back** fait deux unités, et le back reste souvent un monolithe.
- **Monolithe modulaire** : un seul artefact, des modules avec leurs tables et une interface publique.
- **Micro-services** : chacun se déploie seul, avec ses données ; deux services liés par leur déploiement ou leur base forment un **monolithe distribué**.

Ce que les micro-services coûtent, et quand s'en passer : [Le prix des micro-services](https://byte-layers.com/fr/bits/microservices-costs).

```ack
J'ai compris
```
