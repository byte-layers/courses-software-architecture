---
title: "Architecture orientée événements et CQRS"
description: "Des services qui réagissent à ce qui s'est passé plutôt que de s'appeler : publier un événement, s'abonner sans toucher à l'émetteur, ce que coûte un enchaînement que personne ne voit en entier (saga, compensation, traces), puis CQRS, qui sépare le modèle d'écriture et une vue de lecture tenue à jour par les événements. Et l'event sourcing, en une phrase."
tags:
  - bit
  - architecture
  - messaging
  - system-design
difficulty: advanced
duration: 14
requires: "0.8.0"
---

Quand une action en déclenche plusieurs autres, le service qui la reçoit peut **appeler** chacun des autres, ou **annoncer** ce qui s'est passé et laisser chacun réagir. La seconde façon s'appelle l'**architecture orientée événements**. Vous verrez ce qu'elle apporte, ce qu'elle coûte, et une idée qui l'accompagne souvent : **CQRS**, un modèle pour écrire et un autre pour lire. L'exemple suivi : une librairie en ligne.

**Prérequis** : [Files de messages et journaux d'événements](https://byte-layers.com/fr/bits/queues-and-event-logs), pour le journal, les abonnés et leur position.

# Événements et CQRS

## Appels directs : commandes doit connaître tout le monde

Une commande de livre déclenche trois traitements : réserver le stock, facturer, envoyer la confirmation.

```scene
lesson: assets/events.scene.json
step: appels-directs
```

Le service des commandes **appelle** chacun des trois. Il doit donc connaître leurs adresses, décider quoi faire quand l'un est en panne, et être **modifié** chaque fois qu'un nouveau traitement s'ajoute. Les services sont **couplés** : un changement chez l'un oblige à toucher l'autre.

## Publier un événement : ce qui s'est passé

Commandes cesse d'appeler. Il annonce.

```scene
lesson: assets/events.scene.json
step: evenements
```

Commandes publie un **événement**, « commande passée » : un **fait**, au passé, avec les données utiles. Il ne sait pas qui l'écoute. Chaque **abonné** lit l'événement dans le journal et fait son travail. Un nouveau traitement **s'abonne** sans qu'on touche à commandes, et un abonné en panne rattrape son retard en revenant.

> 💡 **Remarque.** Un **événement** dit ce qui s'est passé (« commande passée ») ; une **commande** demande à quelqu'un de faire quelque chose (« réserve ce livre »). L'émetteur d'un événement n'attend rien de personne.

## Le prix : un enchaînement que personne ne voit en entier

Le stock n'a plus le livre, et la facture est déjà partie.

```scene
lesson: assets/events.scene.json
step: prix
```

Il n'y a pas d'annulation globale entre services. Le stock publie à son tour « réservation échouée » ; la facturation rembourse, les e-mails préviennent. C'est une **saga** : une suite d'étapes locales, avec pour chacune une **action de compensation**. Le prix : l'enchaînement complet n'est écrit **nulle part**, et pendant un moment le système est **incohérent**. Les **traces** et les identifiants de corrélation deviennent indispensables.

## CQRS : un modèle pour écrire, un autre pour lire

La page « mes commandes » assemble six tables à chaque affichage.

```scene
lesson: assets/events.scene.json
step: cqrs
```

Écrire juste et lire vite sont deux besoins différents. **CQRS** (*Command Query Responsibility Segregation*) les sépare : un **côté écriture** reçoit les ordres, applique les règles et publie un événement à chaque changement ; un **côté lecture** tient une **vue déjà assemblée** pour l'écran, mise à jour par ces événements. La page se lit d'un coup. Le prix : la vue a un léger **retard**, et il y a deux modèles à maintenir.

> 💡 **Remarque.** L'**event sourcing** va plus loin : on n'enregistre plus l'état, seulement la suite des événements, et l'état se recalcule en les rejouant. Puissant pour l'historique et l'audit, coûteux à faire évoluer. CQRS ne l'impose pas.

## À toi : événements, CQRS, ou rien de tout ça ?

Les événements valent leur prix quand **plusieurs réactions** suivent une même action, gérées par des **équipes différentes**, et qu'un léger décalage est acceptable. CQRS se justifie quand lectures et écritures ont des besoins **très différents**. Pour une application simple, un appel direct et une seule base restent le meilleur choix. Trois situations : choisis.

```quiz
title: "Événements, CQRS, ou rien ?"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Une petite application de prise de notes : on écrit une note, on la relit. Une équipe de deux."
    answers:
      - "Une seule base, des appels directs"
      - "CQRS avec event sourcing"
      - "Un journal d'événements entre chaque écran"
    correct: 1
    explanation: "Rien ne justifie deux modèles ni un journal : ils n'ajouteraient que du retard et du code."
  - prompt: "Chaque nouvel abonnement à une salle de sport doit déclencher : badge, facture, e-mail de bienvenue, statistiques. Quatre équipes."
    answers:
      - "Le service abonnements appelle les quatre, l'un après l'autre"
      - "Publier « abonnement souscrit », chaque équipe s'abonne"
      - "Une seule équipe fait tout dans un seul service"
    correct: 2
    explanation: "Plusieurs réactions, plusieurs équipes, un décalage acceptable : c'est le cas d'école des événements."
  - prompt: "Un tableau de bord lit des millions de fois par jour des chiffres agrégés, alors que les écritures sont des opérations unitaires avec beaucoup de règles."
    answers:
      - "Recalculer les agrégats à chaque affichage"
      - "Supprimer les règles pour écrire plus vite"
      - "CQRS : une vue de lecture agrégée, tenue à jour par les événements"
    correct: 3
    explanation: "Lectures et écritures ont des besoins opposés : deux modèles, chacun taillé pour le sien."
```

> 📖 [What do you mean by "Event-Driven"? (Martin Fowler, en anglais)](https://martinfowler.com/articles/201701-event-driven.html) · [CQRS (Martin Fowler, en anglais)](https://martinfowler.com/bliki/CQRS.html) · [Pattern : Saga (microservices.io, en anglais)](https://microservices.io/patterns/data/saga.html)

## Quatre questions pour vérifier ce que vous avez retenu

```quiz
title: "Événements et CQRS"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Quelle est la différence entre un événement et une commande ?"
    answers:
      - "Un événement dit ce qui s'est passé ; une commande demande de faire quelque chose"
      - "Aucune, ce sont deux mots pour un message"
      - "Une commande est toujours asynchrone"
    correct: 1
    explanation: "« Commande passée » est un fait ; « réserve ce livre » est une demande. L'émetteur d'un événement n'attend rien."
  - prompt: "Une nouvelle équipe veut réagir à chaque commande. En architecture orientée événements, que faut-il modifier dans le service des commandes ?"
    answers:
      - "Ajouter un appel vers la nouvelle équipe"
      - "Rien : la nouvelle équipe s'abonne à l'événement"
      - "Le redéployer avec la nouvelle adresse"
    correct: 2
    explanation: "L'émetteur ne connaît pas ses abonnés. C'est le découplage que cherchent les événements."
  - prompt: "Qu'est-ce qu'une saga ?"
    answers:
      - "Un journal d'événements très long"
      - "Une transaction qui verrouille tous les services"
      - "Une suite d'étapes locales, avec une action de compensation pour annuler chacune"
    correct: 3
    explanation: "Sans transaction globale entre services, on annule étape par étape : rembourser, prévenir, remettre en stock."
  - prompt: "Que sépare CQRS ?"
    answers:
      - "Le front et le back"
      - "Le modèle qui écrit et applique les règles, et le modèle qui sert les lectures"
      - "Les données de chaque client"
    correct: 2
    explanation: "Le côté écriture garde les données justes ; le côté lecture tient des vues prêtes à afficher, avec un léger retard."
```

## Récap

- **Appels directs** : l'émetteur connaît chaque destinataire et doit changer quand ils changent.
- **Événement** : un **fait** publié ; les **abonnés** réagissent ; on en ajoute sans toucher à l'émetteur.
- Le prix : un enchaînement écrit nulle part, des **sagas** et leurs **compensations**, une incohérence temporaire, des **traces** indispensables.
- **CQRS** : un **côté écriture** et un **côté lecture** avec des **vues** tenues à jour par les événements, au prix d'un léger retard.
- **Event sourcing** : enregistrer les événements plutôt que l'état ; CQRS ne l'impose pas.

Ces choix replacés dans des organisations réelles : [Six organisations, six architectures](https://byte-layers.com/fr/bits/architecture-case-studies).

```ack
J'ai compris
```
