---
title: "Six organisations, six architectures"
description: "Six organisations fictives (éditeur de facturation, site d'information, place de marché, banque, transporteur connecté, messagerie) : pour chacune, ce qui pèse vraiment (équipes, charge, données), l'architecture retenue, et ce qu'elle a refusé. Quiz par cas et phrases à compléter pour retrouver ce qui revient d'un cas à l'autre."
tags:
  - bit
  - architecture
  - system-design
difficulty: intermediate
duration: 18
requires: "0.8.0"
---

Il n'existe pas de bonne architecture en général, seulement des architectures adaptées à une situation. Ce bit présente six organisations inventées. Pour chacune : ce qu'elle fait, ce qui pèse vraiment dans sa décision, et l'architecture qu'elle a retenue. Avant de lire leur choix, **décidez vous-même** dans le quiz : les écarts sont ce que vous apprendrez.

**Prérequis** : [Monolithe, monolithe modulaire, micro-services](https://byte-layers.com/fr/bits/monolith-to-microservices) et [Tenir la charge : vertical, horizontal, répartiteur](https://byte-layers.com/fr/bits/scaling-load-balancing).

> 💡 **Remarque.** Les organisations sont inventées et volontairement simplifiées : une vraie décision pèse aussi le budget, les compétences de l'équipe et l'existant. Les termes nouveaux sont expliqués au passage.

# Six organisations, six architectures

## 1 · Factulo : cinq développeurs, un produit qui bouge

**Factulo** vend un logiciel de facturation en ligne à des artisans. Cinq développeurs, un métier qui change chaque mois au gré des demandes des clients, 2 000 utilisateurs, une charge stable. Décide avant de lire leur choix.

```quiz
title: "Factulo"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Quelle architecture pour Factulo ?"
    answers:
      - "Huit micro-services, un par module"
      - "Un monolithe modulaire, une base, deux copies derrière un répartiteur"
      - "Une architecture orientée événements avec un journal d'événements"
    correct: 2
    explanation: "Une seule équipe, une charge modeste : les micro-services n'apporteraient que leurs coûts (réseau, déploiements, observabilité). Deux copies suffisent pour survivre à une panne."
  - prompt: "Qu'est-ce qui leur permettra de découper plus tard, si l'équipe grandit ?"
    answers:
      - "Mettre tout le code dans un seul fichier"
      - "Rien : un monolithe ne se découpe jamais"
      - "Des modules aux frontières nettes, chacun avec ses tables et une petite interface"
    correct: 3
    explanation: "Des frontières tenues dans le code rendent le découpage possible le jour où il devient utile."
```

**Leur choix** : un **monolithe modulaire**, en deux copies. Ils ont refusé les micro-services : rien, ni l'organisation ni la charge, ne les justifiait encore.

## 2 · L'Écho du soir : un site d'information et ses pics

**L'Écho du soir** publie des articles en ligne. Un soir d'élection, le trafic est **multiplié par trente** en dix minutes. Presque toutes les requêtes **lisent** les mêmes articles ; très peu écrivent.

```quiz
title: "L'Écho du soir"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Qu'est-ce qui absorbe le mieux un pic de lectures sur les mêmes pages ?"
    answers:
      - "Un cache et un CDN : des copies des pages servies au plus près des lecteurs"
      - "Un plus gros serveur de base de données"
      - "Découper le site en micro-services"
    correct: 1
    explanation: "Un CDN (réseau de serveurs répartis dans le monde) garde des copies des pages et répond sans solliciter l'application. La plupart des lectures n'atteignent jamais le serveur."
  - prompt: "Pour le reste du trafic, comment ajouter des copies de l'application rapidement ?"
    answers:
      - "Garder la session de chaque lecteur en mémoire sur une seule machine"
      - "Agrandir la machine pendant la soirée"
      - "Des copies sans état, ajoutées derrière le répartiteur"
    correct: 3
    explanation: "Sans état, n'importe quelle copie peut répondre à n'importe qui : on en ajoute autant que nécessaire."
```

**Leur choix** : un **CDN** devant le site, un **cache** pour les articles, des copies **sans état** qu'on ajoute les soirs de pic. L'application reste un monolithe : le problème était la lecture, pas l'organisation.

## 3 · Marchéo : douze équipes sur une place de marché

**Marchéo** met en relation 40 000 vendeurs et leurs clients. Douze équipes : catalogue, recherche, panier, paiement, livraison, litiges… Chacune veut livrer **plusieurs fois par jour** sans attendre les autres. Un site et une appli mobile.

```quiz
title: "Marchéo"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Qu'est-ce qui justifie des micro-services chez Marchéo ?"
    answers:
      - "Le nombre de pages du site"
      - "Douze équipes qui doivent livrer chacune à son rythme"
      - "La mode"
    correct: 2
    explanation: "Les micro-services répondent d'abord à un problème d'organisation : chaque équipe possède et déploie son service."
  - prompt: "Que mettre devant les services pour le site et l'appli ?"
    answers:
      - "Une passerelle d'API, et un BFF pour l'appli mobile"
      - "Rien : chaque appli appelle les douze services directement"
      - "Une seule base partagée par tous"
    correct: 1
    explanation: "La passerelle donne une entrée unique et centralise l'authentification ; le BFF assemble des réponses taillées pour le mobile."
```

**Leur choix** : des **micro-services par domaine métier**, chacun avec sa base, une **passerelle d'API**, un **BFF** mobile, et une **observabilité** soignée (journaux centralisés, traces). Le prix est assumé : une équipe plateforme dédiée à l'outillage.

## 4 · Banque Arpège : un compte ne doit jamais être faux

**Banque Arpège** tient les comptes de ses clients. Un virement débite un compte et en crédite un autre. Un solde faux, même une seconde, est **inacceptable** ; un service indisponible quelques secondes est **gênant mais tolérable**.

```quiz
title: "Banque Arpège"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Si le réseau coupe entre deux centres de données, que doit préférer le système des comptes ?"
    answers:
      - "Continuer à accepter des virements des deux côtés, et réconcilier plus tard"
      - "Refuser des opérations un moment, plutôt que d'afficher un solde faux"
      - "Choisir au hasard"
    correct: 2
    explanation: "C'est le choix de la cohérence. Quand le réseau se coupe entre deux copies des données, on ne peut pas garder à la fois des réponses toujours justes et un service toujours disponible ; la banque choisit le juste."
  - prompt: "Le client clique deux fois sur « Virer 100 € » parce que la page tardait. Que doit garantir le système ?"
    answers:
      - "Que le second clic soit plus rapide"
      - "Rien : c'est au client de faire attention"
      - "Que l'opération soit idempotente : la rejouer ne vire pas 200 €"
    correct: 3
    explanation: "Une opération idempotente produit le même résultat qu'on l'exécute une fois ou deux. On lui donne un identifiant unique, et le second envoi est reconnu."
```

**Leur choix** : le cœur des comptes reste un **monolithe** aux règles riches, en **architecture hexagonale** pour tester ces règles sans base, avec une base qui garantit la **cohérence**. Les fonctions autour (notifications, relevés) sont à part et **asynchrones**.

## 5 · Roulio : 30 000 camions qui envoient leur position

**Roulio** suit une flotte de camions. Chaque camion envoie sa **position toutes les dix secondes** ; le matin, tous démarrent ensemble. Plusieurs usages lisent ces positions : la carte en direct, la facturation au kilomètre, les alertes de retard.

```quiz
title: "Roulio"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Comment encaisser le pic du matin sans perdre de positions ?"
    answers:
      - "Déposer les positions dans une file de messages, lue par les traitements à leur rythme"
      - "Faire attendre chaque camion jusqu'à ce que tous les traitements aient répondu"
      - "Ignorer les positions quand le serveur est occupé"
    correct: 1
    explanation: "La file sert de tampon : les camions déposent et repartent, les traitements rattrapent leur retard ensuite. C'est une communication asynchrone."
  - prompt: "La carte, la facturation et les alertes doivent toutes lire chaque position. Quel outil le permet ?"
    answers:
      - "Une file classique, où chaque message n'est lu qu'une fois"
      - "Un journal d'événements, que chaque usage lit à son propre rythme"
      - "Un appel direct à chacun des trois usages"
    correct: 2
    explanation: "Dans un journal d'événements, les messages restent ; chaque groupe de lecteurs avance avec sa propre position. Une file classique distribue chaque message à un seul lecteur."
```

**Leur choix** : un **journal d'événements** reçoit les positions ; la carte, la facturation et les alertes le lisent chacune à leur rythme. La facturation peut prendre une heure de retard un matin, sans que les camions s'en aperçoivent.

## 6 · Papoti : une messagerie dans le monde entier

**Papoti** est une messagerie avec des utilisateurs sur trois continents. Un message doit apparaître **tout de suite** chez le destinataire. Le compteur de réactions sous un message peut être **un peu en retard** sans gêner personne.

```quiz
title: "Papoti"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Comment le serveur prévient-il l'appli qu'un message est arrivé ?"
    answers:
      - "L'appli redemande toutes les minutes"
      - "Par courriel"
      - "Par une connexion WebSocket qui reste ouverte, dans les deux sens"
    correct: 3
    explanation: "Le WebSocket laisse le serveur pousser le message dès qu'il arrive, et l'appli envoyer les siens sur la même connexion."
  - prompt: "Les données sont copiées sur trois continents. Si le réseau coupe entre deux, que préférer pour le compteur de réactions ?"
    answers:
      - "Bloquer toute la messagerie jusqu'au retour du réseau"
      - "Rester disponible, et laisser le compteur se mettre à jour un peu plus tard"
      - "Supprimer les réactions"
    correct: 2
    explanation: "C'est le choix de la disponibilité : un compteur un peu en retard ne fait de tort à personne. On parle de cohérence à terme."
```

**Leur choix** : des **WebSockets** pour les messages, des données **répliquées** par continent, et une **cohérence à terme** pour ce qui peut attendre. Le contraire exact de la banque, pour de bonnes raisons.

## Ce qui revient d'un cas à l'autre

Six choix différents, mais les mêmes questions à chaque fois. Complète la phrase avec un mot par trou.

```fill
place: stage
text: "Les micro-services répondent d'abord à un problème d'_____ : plusieurs équipes. Un pic de lectures se traite par un _____ avant d'ajouter des machines. Quand les données ne doivent jamais être fausses, on choisit la _____ plutôt que la disponibilité. Pour encaisser un pic d'écritures sans faire attendre l'émetteur, on passe par une _____ de messages."
blanks:
  - answers: ["organisation", "équipes", "equipes"]
    hint: "Marchéo : douze équipes, pas douze fois plus de charge."
  - answers: ["cache", "CDN"]
    hint: "L'Écho du soir garde des copies des pages."
  - answers: ["cohérence", "coherence"]
    hint: "Banque Arpège refuse un solde faux."
  - answers: ["file", "queue"]
    hint: "Roulio : les camions déposent et repartent."
```

> 📖 [Microservices, Monolith First (Martin Fowler, en anglais)](https://martinfowler.com/bliki/MonolithFirst.html) · [Le théorème CAP (Wikipédia)](https://fr.wikipedia.org/wiki/Th%C3%A9or%C3%A8me_CAP)

## Quatre questions pour vérifier ce que vous avez retenu

```quiz
title: "Six organisations, six architectures"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Une équipe de six personnes, un métier qui change souvent, une charge modeste. Quel point de départ ?"
    answers:
      - "Un monolithe modulaire"
      - "Des micro-services, pour être prêts"
      - "Un journal d'événements"
    correct: 1
    explanation: "Comme Factulo : des frontières nettes dans un seul déploiement, découpables plus tard."
  - prompt: "Pourquoi la banque et la messagerie font-elles des choix opposés quand le réseau coupe ?"
    answers:
      - "Parce que l'une est plus moderne"
      - "Parce que la messagerie n'a pas de base de données"
      - "Parce que ce qui coûte le plus cher n'est pas le même : un solde faux pour l'une, un service bloqué pour l'autre"
    correct: 3
    explanation: "On ne peut pas tout avoir pendant une coupure : on choisit d'après ce qui fait le plus de tort."
  - prompt: "Plusieurs usages doivent lire chacun tous les événements, à leur propre rythme. Quel outil ?"
    answers:
      - "Une file où chaque message est lu une fois"
      - "Un journal d'événements"
      - "Un appel synchrone vers chaque usage"
    correct: 2
    explanation: "Le journal garde les messages ; chaque groupe de lecteurs avance seul."
  - prompt: "Le trafic d'un site est presque entièrement fait de lectures des mêmes pages. Que mettre en premier ?"
    answers:
      - "Des micro-services"
      - "Une base plus grosse"
      - "Un cache et un CDN"
    correct: 3
    explanation: "Servir des copies au plus près des lecteurs évite que la plupart des requêtes atteignent l'application."
```

## Récap

- Une architecture se choisit d'après ce qui pèse : l'**organisation** (combien d'équipes), la **charge** (combien, et quand), les **données** (ce qui ne doit jamais être faux).
- Petite équipe, métier mouvant : un **monolithe modulaire**.
- Pic de lectures : **cache**, **CDN**, copies **sans état**.
- Plusieurs équipes autonomes : **micro-services**, **passerelle**, **BFF**, **observabilité**.
- Données critiques : la **cohérence** d'abord, et des opérations **idempotentes**.
- Pic d'écritures, plusieurs lecteurs : **file** ou **journal d'événements**.
- Temps réel et monde entier : **WebSocket**, **réplication**, **cohérence à terme** pour ce qui peut attendre.

Ce qui se passe quand on attend la réponse, ou non : [Synchrone ou asynchrone](https://byte-layers.com/fr/bits/sync-async-communication).

```ack
J'ai compris
```
