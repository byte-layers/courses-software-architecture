---
title: "Découper une application de VTC"
description: "Un défi en quatre décisions sur Hopla, une application de VTC encore monolithique : les modules qui méritent de devenir des services, où vivent leurs données, comment ils se parlent, et comment encaisser la panne du prestataire de paiement un vendredi soir. Chaque décision est un questionnaire noté."
tags:
  - challenge
  - architecture
  - system-design
difficulty: advanced
duration: 25
introTitle: "Le défi"
requires: "0.8.0"
options:
  allowManualProgress: false
  autoCompleteOnNext: unverifiable
---

Ce challenge vous permet de prouver que vous savez découper une application en services **pour de bonnes raisons**, et choisir pour chacun sa base et sa façon de communiquer. L'application à découper est **Hopla**, une application de VTC inventée. Il n'y a **rien à installer** : chaque tâche décrit une situation et se termine par un **questionnaire noté**. La tâche est validée quand toutes ses réponses sont justes.

Si vous êtes bloqué, les **indices** se dévoilent un par un, et la **solution** reste en dernier recours. Les utiliser ne coûte rien. Un conseil : répondez d'abord sans indice ; l'explication qui suit chaque réponse donne le raisonnement, et donc la réponse.

## Avant de commencer

- **Ce qu'il faut savoir** : ce qu'enseignent [Monolithe, monolithe modulaire, micro-services](https://byte-layers.com/fr/bits/monolith-to-microservices), [Le prix des micro-services](https://byte-layers.com/fr/bits/microservices-costs), [Synchrone ou asynchrone](https://byte-layers.com/fr/bits/sync-async-communication), [Les protocoles entre programmes](https://byte-layers.com/fr/bits/communication-protocols) et [Six organisations, six architectures](https://byte-layers.com/fr/bits/architecture-case-studies).
- **Ce qu'il faut avoir** : rien de plus que cette page. Aucun fichier n'est créé sur votre machine.
- **Les questions à plusieurs réponses** sont signalées sous la question ; il faut cocher toutes les bonnes, et aucune autre.

> Hopla est inventée et simplifiée : une vraie décision pèse aussi le budget, les compétences de l'équipe et l'existant. Les chiffres sont des ordres de grandeur.

# Tâche 1 : les modules qui deviennent des services

## Hopla aujourd'hui

**Hopla** met en relation des passagers et des chauffeurs dans dix villes. Toute l'application est un **monolithe modulaire** : un seul programme, une seule base, des modules bien séparés dans le code, déployé toutes les deux semaines. Quarante développeurs, en quatre équipes. Le monolithe commence à gêner, et la direction demande « des micro-services ».

| Module | Ce qu'il fait | Charge | Équipe, rythme | Contraintes |
|---|---|---|---|---|
| passagers | comptes, profils, moyens de paiement enregistrés | faible | Produit, toutes les deux semaines | aucune particulière |
| chauffeurs | comptes, documents (permis, assurance), validation | faible | Produit, toutes les deux semaines | aucune particulière |
| courses en direct | reçoit la position de 20 000 chauffeurs toutes les 4 secondes, trouve le chauffeur le plus proche, suit la course | 5 000 positions par seconde le samedi soir, presque rien à 4 h du matin | Temps réel, veut déployer chaque jour | doit répondre en moins d'une seconde |
| tarification | calcule le prix, applique la majoration quand la demande dépasse l'offre | une fois par demande de course | Tarifs, change ses règles **plusieurs fois par semaine** | aucune particulière |
| paiement | débite la carte par un prestataire, rembourse | une fois par course | Paiement, toutes les deux semaines | audits de sécurité, accès au code et aux données réservé à cette équipe |
| factures | produit la facture PDF de chaque course et le relevé mensuel | faible, en fin de mois | Produit, toutes les deux semaines | aucune particulière |
| notifications | envoie les SMS et notifications « votre chauffeur arrive » | quelques messages par course | Produit, toutes les deux semaines | aucune particulière |

Un module mérite de devenir un service à part quand il a une **raison propre** : une charge très différente des autres, une équipe qui veut livrer à un autre rythme, ou des contraintes que le reste n'a pas. Sans raison, il reste un module du monolithe : chaque service de plus a un prix.

```hint
Un service de plus, c'est un déploiement, une base, une surveillance et des appels réseau qui peuvent échouer de plus. Pour chaque module, cherchez dans le tableau une raison qui le distingue des autres. « Faible, Produit, toutes les deux semaines, aucune particulière » n'en est pas une.
```

```hint
Il y a trois raisons possibles, et chacune désigne un module différent : la charge qui varie énormément, l'équipe qui change ses règles plusieurs fois par semaine, et les audits avec accès réservé.
```

```quiz
title: "Tâche 1 : les services"
tracksProgress: true
showNotice: false
questions:
  - prompt: "Quels modules sortent du monolithe pour devenir des services ?"
    answers:
      - "passagers"
      - "chauffeurs"
      - "courses en direct"
      - "tarification"
      - "paiement"
      - "factures"
      - "notifications"
    correct: [3, 4, 5]
    explanation: "Courses en direct a sa charge : 5 000 positions par seconde le samedi soir, presque rien la nuit ; en service, on ajoute des copies de ce seul service. Tarification a son rythme : l'équipe livre plusieurs fois par semaine sans attendre le déploiement commun. Paiement a ses contraintes : un code et une base isolés, auditables, accessibles à une seule équipe. Les quatre autres n'ont aucune raison propre : en faire des services ajouterait un déploiement, une base et des appels réseau, sans rien gagner."
```

````solution
Trois services : **courses en direct**, **tarification**, **paiement**.

| Module | Verdict |
|---|---|
| courses en direct | extrait : sa charge passe de presque rien à 5 000 positions par seconde |
| tarification | extrait : l'équipe Tarifs livre ses règles plusieurs fois par semaine |
| paiement | extrait : code et base isolés, auditables, accessibles à une seule équipe |
| passagers, chauffeurs, factures, notifications | restent des modules du monolithe : rien ne les distingue |

Le résultat n'est pas « des micro-services partout » : c'est **un monolithe modulaire et trois services**. On en sortira d'autres le jour où une vraie raison apparaîtra.
````

# Tâche 2 : à qui appartiennent les données

## Une base par service

Chaque service extrait a **sa propre base** : personne d'autre n'y lit ni n'y écrit. Deux questions en découlent.

**Les factures.** Le module factures, resté dans le monolithe, a besoin pour chaque course terminée de la distance, du prix et du passager. Ces informations naissent dans le service courses en direct.

**Les positions.** Le service courses en direct reçoit 5 000 positions par seconde. Pour trouver le chauffeur le plus proche, il n'a besoin que de la **dernière** position de chaque chauffeur ; une position de plus de 30 secondes ne sert plus à rien.

```hint
Si le monolithe lit la base du service courses en direct, que se passe-t-il le jour où l'équipe Temps réel renomme une colonne ? Et si tout revient dans une seule base, qu'a-t-on gagné à découper ?
```

```hint
Pour les positions : il faut écrire très vite, lire très vite, et oublier ce qui a plus de 30 secondes.
```

```quiz
title: "Tâche 2 : les données"
tracksProgress: true
showNotice: false
questions:
  - prompt: "Comment le module factures obtient-il la distance, le prix et le passager de chaque course terminée ?"
    answers:
      - "Il se connecte à la base du service courses en direct et y lit ce qu'il lui faut"
      - "On remet toutes les données dans une seule base partagée par tous"
      - "Le service courses en direct publie un événement « course terminée » avec ces informations ; le monolithe s'y abonne et garde sa copie"
    correct: 3
    explanation: "Lire la base d'un autre service le lie à ses tables : le jour où l'équipe Temps réel change une colonne, les factures cassent. Une base partagée, c'est revenir au couplage du monolithe. L'événement donne au monolithe ce qu'il lui faut sans qu'il connaisse la base du service ; sa copie arrive avec un léger retard, sans gravité pour une facture."
  - prompt: "Où le service courses en direct garde-t-il les positions des chauffeurs ?"
    answers:
      - "Dans une base relationnelle qui garde chaque position, avec une transaction par écriture"
      - "Dans un stockage clé-valeur en mémoire (un chauffeur, sa dernière position), répliqué, où chaque position expire après 30 secondes"
      - "Dans un fichier par chauffeur, réécrit à chaque position"
    correct: 2
    explanation: "Une transaction et une ligne gardée pour chaque position, 5 000 fois par seconde, pour n'en lire que la dernière : trop lourd. Des milliers de fichiers réécrits sur une machine : ni copie ni expiration. Un stockage clé-valeur en mémoire (Redis, par exemple) écrit et lit en une fraction de milliseconde, et la durée de vie efface les positions périmées. Perdre une position n'est pas grave : la suivante arrive dans 4 secondes."
```

````solution
- **Factures** : le service courses en direct publie « course terminée » ; le monolithe s'abonne et garde sa copie. Aucun service ne lit la base d'un autre.
- **Positions** : un stockage clé-valeur en mémoire, répliqué, avec une durée de vie de 30 secondes. Il tient la charge et oublie de lui-même ce qui ne sert plus.
````

# Tâche 3 : comment ils se parlent

## Quatre échanges

| Façon de communiquer | En une phrase |
|---|---|
| REST | requête HTTP vers une API, réponse attendue |
| WebSocket | une connexion qui reste ouverte, le serveur envoie quand il veut |
| événement | déposé dans un journal d'événements, lu par les abonnés à leur rythme |
| gRPC | appel synchrone entre services, contrat typé, format binaire compact |

Quatre échanges de Hopla, une façon de communiquer pour chacun. Un échange qui attend une réponse est synchrone ; un échange que plusieurs services traitent à leur rythme est asynchrone ; quand c'est le serveur qui a des nouvelles à donner, la connexion reste ouverte.

```hint
Pour le suivi de la voiture : faut-il que l'application redemande toutes les 4 secondes « où est la voiture ? », ou que le serveur le lui dise ?
```

```hint
Pour la fin de course : trois services réagissent, et le passager n'a pas à attendre la facture pour sortir de la voiture. Pour le prix : les deux bouts sont des services internes, le volume est élevé, et il faut la réponse pour continuer.
```

```quiz
title: "Tâche 3 : les échanges"
tracksProgress: true
showNotice: false
questions:
  - prompt: "L'application du passager demande une course, et attend un numéro de course en retour."
    answers: ["REST", "WebSocket", "événement", "gRPC"]
    correct: 1
    explanation: "Une question, une réponse, depuis une application mobile, à travers la passerelle d'API : c'est le cas le plus simple, une requête HTTP vers une API REST."
  - prompt: "L'application du passager affiche la voiture qui approche, mise à jour toutes les 4 secondes."
    answers: ["REST", "WebSocket", "événement", "gRPC"]
    correct: 2
    explanation: "Redemander toutes les 4 secondes, c'est une requête presque toujours inutile par passager. C'est le serveur qui a des nouvelles : une connexion WebSocket reste ouverte, et il pousse chaque position."
  - prompt: "La course se termine ; les factures, les notifications et le paiement doivent chacun réagir."
    answers: ["REST", "WebSocket", "événement", "gRPC"]
    correct: 3
    explanation: "Trois services réagissent, chacun à son rythme, et la course ne doit pas attendre la facture. Un événement est publié une fois et lu par chaque abonné ; on en ajoute un sans toucher au service des courses."
  - prompt: "Pendant la demande, le service courses en direct demande le prix au service tarification, des centaines de fois par seconde, et ne peut rien proposer sans lui."
    answers: ["REST", "WebSocket", "événement", "gRPC"]
    correct: 4
    explanation: "Il faut attendre la réponse : c'est synchrone, donc pas un événement. Entre deux services internes, à fort volume, un format binaire compact et un contrat typé partagé par les deux équipes coûtent moins et cassent moins : gRPC. REST fonctionnerait aussi ; c'est un choix de volume et de confort, pas une obligation."
```

````solution
| Échange | Choix | Pourquoi |
|---|---|---|
| demande de course | REST | une question, une réponse, depuis une application mobile, à travers la passerelle d'API |
| suivi de la voiture | WebSocket | le serveur pousse la position toutes les 4 secondes, sans que l'application redemande |
| fin de course | événement | trois abonnés, chacun à son rythme ; on en ajoute un sans toucher au service des courses |
| prix | gRPC | appel interne synchrone, très fréquent : format compact, contrat partagé par les deux équipes |
````

# Tâche 4 : le vendredi soir où le paiement ralentit

## Le prestataire répond en 20 secondes

Vendredi, 23 h. Le prestataire de paiement répond en **20 secondes** au lieu d'une demi-seconde. Aujourd'hui, le service courses en direct demande au service paiement de débiter la carte **avant** de chercher un chauffeur : les demandes s'accumulent, et plus aucune course ne part.

Il faut que les courses partent même quand le prestataire est lent, sans aggraver la charge sur le prestataire, et sans qu'aucun passager soit débité deux fois.

```hint
Deux propositions aggravent la situation : l'une garde chaque demande bloquée plus longtemps, l'autre multiplie les appels vers un prestataire déjà saturé. Une troisième ne change rien au problème, qui est l'attente.
```

```hint
Une fois le débit dans une file, il sera retenté. Que faut-il pour qu'un débit retenté ne débite pas une seconde fois ? Et pour ne pas marteler le prestataire pendant qu'il est malade ?
```

```quiz
title: "Tâche 4 : la panne"
tracksProgress: true
showNotice: false
questions:
  - prompt: "Quelles mesures Hopla retient-elle ? (trois réponses)"
    answers:
      - "Augmenter le délai d'attente du service paiement à 60 secondes, pour ne plus avoir d'échec"
      - "Accepter la course sans attendre le débit ; le débit part en fin de course, déposé dans une file, et le service paiement le traite à son rythme"
      - "Réessayer immédiatement cinq fois chaque débit qui échoue"
      - "Joindre à chaque débit une clé d'idempotence, l'identifiant de la course, que le service paiement transmet au prestataire"
      - "Un disjoncteur : après une série d'échecs, le service paiement cesse quelques instants d'appeler le prestataire, et les débits attendent dans la file"
      - "Remettre le paiement dans le monolithe"
    correct: [2, 4, 5]
    explanation: "Un délai plus long garde chaque demande bloquée plus longtemps : les places du service se remplissent plus vite, c'est la panne en cascade. Cinq tentatives immédiates multiplient par six les appels vers un prestataire déjà saturé. Dans le monolithe, l'appel attend tout autant, et la lenteur bloquerait tout. Ce qui marche : le débit passe en asynchrone dans une file, la clé d'idempotence empêche un débit retenté de débiter deux fois, et le disjoncteur laisse le prestataire se remettre."
```

````solution
Trois mesures : **le débit en asynchrone**, **la clé d'idempotence**, **le disjoncteur**.

| Proposition | Verdict |
|---|---|
| délai d'attente à 60 secondes | écarté : plus d'attente, plus de places occupées, panne en cascade plus rapide |
| débit en fin de course, via une file | retenu : la course ne dépend plus du prestataire |
| cinq tentatives immédiates | écarté : multiplie la charge au pire moment |
| clé d'idempotence | retenu : un débit retenté avec la même clé n'est pas exécuté deux fois |
| disjoncteur | retenu : on cesse d'appeler un prestataire malade, la file garde les débits |
| paiement dans le monolithe | écarté : ne change rien à l'attente, et la propage à tout le monolithe |

Le prix du débit en fin de course : il peut échouer après la course. Hopla l'accepte, comme beaucoup de services de ce type : la carte est vérifiée à l'enregistrement, et un débit refusé se traite après coup (nouvelle tentative, autre carte, compte suspendu).
````

## Ce que vous avez construit

| Partie | Base | Reçoit | Publie ou appelle |
|---|---|---|---|
| monolithe modulaire (passagers, chauffeurs, factures, notifications) | relationnelle | REST depuis les applications, l'événement « course terminée » | — |
| courses en direct | clé-valeur en mémoire, plus un historique des courses | REST (demande), positions des chauffeurs | WebSocket vers le passager, gRPC vers la tarification, l'événement « course terminée » |
| tarification | ses règles de prix | gRPC | — |
| paiement | ses débits, avec leur clé d'idempotence | l'événement « course terminée », via sa file | le prestataire, derrière un disjoncteur |

Pour aller plus loin, dessinez ce schéma sur [Excalidraw](https://excalidraw.com/) ou en [Mermaid](https://mermaid.js.org/), avec la passerelle d'API devant les applications. Puis comparez avec un cas réel : [l'architecture micro-services d'Uber (en anglais)](https://www.uber.com/en-FR/blog/microservice-architecture/) et [l'évolution de sa couche d'API, en schémas (ByteByteGo, en anglais)](https://bytebytego.com/guides/evolution-of-ubers-api-layer/). Uber est allé jusqu'à des milliers de services, puis les a regroupés en domaines : la bonne taille d'un service se rediscute avec la croissance.

