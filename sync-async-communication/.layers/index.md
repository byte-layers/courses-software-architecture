---
title: "Synchrone ou asynchrone : attendre la réponse, ou non"
description: "Ce que change le fait d'attendre la réponse d'un autre service : la somme des temps, la panne en cascade quand un service ralentit, le délai d'attente et les nouvelles tentatives (et la tempête qu'elles peuvent créer), l'idempotence pour ne pas payer deux fois, puis l'asynchrone avec une file de messages. Un playground pour tout essayer."
tags:
  - bit
  - architecture
  - microservices
  - system-design
difficulty: intermediate
duration: 15
requires: "0.12.0"
---

Quand un service en appelle un autre, il a deux façons de faire : **attendre la réponse** avant de continuer, ou **déposer sa demande** et passer à la suite. Ce choix décide de ce qui arrive quand un service ralentit ou tombe. Vous verrez les deux, les réglages qui évitent les pannes en chaîne, et un playground pour les essayer. L'exemple suivi : une boutique de baskets en ligne, où une commande passe par trois services.

**Prérequis** : [Le prix des micro-services](https://byte-layers.com/fr/bits/microservices-costs), pour l'appel réseau qui peut échouer.

# Synchrone ou asynchrone

## Synchrone : on attend la réponse

Le client valide son panier. La commande passe par A (commandes), B (stock) et C (paiement).

```scene
lesson: assets/syncasync.scene.json
step: synchrone
```

Chaque appel est **synchrone** : A attend B, qui attend C, avant de répondre. C'est le fonctionnement habituel d'un appel HTTP. Le temps de réponse est la **somme** des temps de chaque service. L'avantage est réel : c'est simple à écrire et à suivre, et le client sait **tout de suite** si son paiement est passé.

## Un service lent bloque toute la chaîne

Un après-midi, le prestataire de paiement répond dix fois plus lentement.

```scene
lesson: assets/syncasync.scene.json
step: cascade
```

Chaque service ne traite qu'un nombre limité de requêtes en même temps : ses **places** (processus, connexions). Les places de B se remplissent de requêtes qui attendent C, puis celles de A. Les nouvelles commandes échouent alors que A et B n'ont rien de cassé. Un seul service lent fait tomber toute la boutique : c'est une **panne en cascade**.

## Délai d'attente et nouvelles tentatives

Deux réglages courants, à manier ensemble.

```scene
lesson: assets/syncasync.scene.json
step: delai
```

Un **délai d'attente** (*timeout*) fait abandonner un appel trop long : la réponse arrive vite, même en échec, et la place se libère. Une **nouvelle tentative** (*retry*) renvoie la demande après un échec, ce qui rattrape une coupure brève. Mais contre un service déjà surchargé, chaque échec renvoie plusieurs appels : la charge **se multiplie** et tout sature.

> 💡 **Remarque.** On espace donc les tentatives de plus en plus (*backoff* exponentiel), on en limite le nombre, et un **disjoncteur** (*circuit breaker*) peut cesser d'appeler un service qui échoue sans arrêt, le temps qu'il se remette.

## Payé deux fois : l'idempotence

Une nouvelle tentative a un piège : elle peut répéter une action qui avait **déjà réussi**.

```scene
lesson: assets/syncasync.scene.json
step: idempotence
```

C a débité la carte, mais sa réponse s'est perdue. B réessaie, et C débite une seconde fois. Le remède : une **clé d'idempotence**, un identifiant unique joint à la demande. C garde les clés déjà traitées et renvoie le premier résultat. L'opération devient **idempotente** : l'exécuter une ou deux fois donne le même résultat. Toute opération qu'on peut réessayer doit l'être.

## Asynchrone : déposer et ne pas attendre

A n'a pas besoin du paiement pour dire au client que sa commande est enregistrée.

```scene
lesson: assets/syncasync.scene.json
step: asynchrone
```

En **asynchrone**, A dépose la commande dans une **file de messages** et répond tout de suite. B et C la traitent **à leur rythme** ; si C ralentit, les messages s'accumulent, mais personne n'attend et rien ne tombe. Le client est prévenu plus tard, par une notification. Le prix : au moment de répondre, A **ne sait pas encore** si le paiement passera, et il faut gérer ce cas après coup.

## À toi : sauver la boutique

Le même schéma, mais c'est toi qui pilotes : rends C lent, règle le délai et les nouvelles tentatives, ajoute la clé d'idempotence, passe en asynchrone. Le mode **guidé**, dans la barre de la scène, te donne quatre consignes.

```scene
lesson: assets/syncasync.scene.json
step: playground
```

> 💡 **Remarque.** Le playground simplifie : chaque service a quatre places et un temps de traitement fixe, et la file n'a pas de limite. Les ordres de grandeur sont parlants, pas les chiffres exacts.

> 📖 [Timeouts, retries and backoff with jitter (AWS Builders' Library, en anglais)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) · [Circuit Breaker (Martin Fowler, en anglais)](https://martinfowler.com/bliki/CircuitBreaker.html)

## Quatre questions pour vérifier ce que vous avez retenu

```quiz
title: "Synchrone ou asynchrone"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "A appelle B, qui appelle C, en synchrone. C devient très lent. Que se passe-t-il pour A ?"
    answers:
      - "Rien, A n'appelle pas C directement"
      - "Ses places se remplissent de requêtes qui attendent B, et les nouvelles requêtes échouent"
      - "A appelle C directement à la place de B"
    correct: 2
    explanation: "La lenteur remonte la chaîne : B attend C, A attend B. C'est la panne en cascade."
  - prompt: "Pourquoi des nouvelles tentatives peuvent-elles aggraver une panne ?"
    answers:
      - "Parce qu'elles sont plus lentes que le premier appel"
      - "Parce qu'elles désactivent le délai d'attente"
      - "Parce que chaque échec renvoie plusieurs appels vers un service déjà surchargé"
    correct: 3
    explanation: "Trois tentatives triplent la charge au pire moment. D'où l'espacement croissant, une limite, et le disjoncteur."
  - prompt: "Qu'est-ce qu'une opération idempotente ?"
    answers:
      - "Une opération qui donne le même résultat qu'on l'exécute une fois ou plusieurs"
      - "Une opération qui ne peut jamais échouer"
      - "Une opération chiffrée"
    correct: 1
    explanation: "Avec une clé d'idempotence, le second « payer » est reconnu et ne débite pas une seconde fois."
  - prompt: "Que perd A quand il passe en asynchrone avec une file de messages ?"
    answers:
      - "La possibilité de répondre vite"
      - "La certitude, au moment de répondre, que la suite réussira"
      - "La possibilité d'avoir plusieurs services"
    correct: 2
    explanation: "A répond « commande reçue » avant le paiement. Si le paiement échoue plus tard, il faut le traiter après coup."
```

## Récap

- **Synchrone** : on attend la réponse ; simple, résultat immédiat, temps de réponse = **somme** des temps.
- Un service lent remplit les **places** de ceux qui l'attendent : **panne en cascade**.
- **Délai d'attente** pour ne pas attendre sans fin ; **nouvelles tentatives** espacées et limitées, sinon elles multiplient la charge.
- **Idempotence** : une **clé** unique pour qu'une demande répétée ne s'exécute qu'une fois.
- **Asynchrone** : une **file de messages** absorbe la lenteur ; le résultat arrive plus tard.

Comment fonctionnent ces files, et quand préférer un journal d'événements : [Files de messages et journaux d'événements](https://byte-layers.com/fr/bits/queues-and-event-logs).

```ack
J'ai compris
```
