---
title: "Réplication, partitionnement et théorème CAP"
description: "Quand une seule base ne suffit plus : la réplication pour répartir les lectures, le retard de réplication et la cohérence à terme, le partitionnement pour répartir les données et les écritures (clé, partition trop chaude), puis le théorème CAP énoncé correctement : pendant une coupure du réseau, un système réparti choisit entre réponses toujours justes et réponses toujours données."
tags:
  - bit
  - architecture
  - databases
  - system-design
difficulty: advanced
duration: 15
requires: "0.8.0"
---

Une base de données sur une seule machine a deux limites : le nombre de requêtes qu'elle sert, et la quantité de données qu'elle garde. Pour aller au-delà, on **copie** les données sur plusieurs machines, ou on les **coupe** en parts. Vous verrez les deux, ce que chacune coûte, et le théorème CAP, qui dit ce qu'on ne peut pas avoir quand le réseau entre ces machines se coupe. L'exemple suivi : un site de petites annonces entre particuliers.

**Prérequis** : [Tenir la charge : vertical, horizontal, répartiteur](https://byte-layers.com/fr/bits/scaling-load-balancing), pour les copies sans état devant une base.

# Réplication, partitionnement et CAP

## La réplication : des copies pour lire

Sur le site, on lit cent annonces pour une publiée. La base sature sous les lectures.

```scene
lesson: assets/data.scene.json
step: replication
```

On ajoute des **répliques** : des copies de la base, que la **principale** tient à jour en recopiant chaque écriture. C'est la **réplication**. Les **écritures** vont toujours à la principale ; les **lectures** se répartissent sur les répliques. La charge de chaque machine baisse, et une réplique peut prendre le relais si la principale tombe.

## Le retard de réplication : l'annonce introuvable

La recopie n'est pas instantanée. La plupart du temps, personne ne le remarque.

```scene
lesson: assets/data.scene.json
step: retard
```

Une visiteuse publie une annonce, recharge la page, et ne la voit pas : sa lecture est tombée sur une réplique **pas encore à jour**. Une fraction de seconde plus tard, tout concorde. C'est la **cohérence à terme** (*eventual consistency*) : sans nouvelle écriture, toutes les copies finissent par dire la même chose. Parade courante : juste après une écriture, **relire ses propres données** sur la principale.

> 💡 **Remarque.** Une recopie **synchrone**, où la principale attend qu'une réplique ait reçu l'écriture avant de confirmer, supprime ce retard pour cette réplique, au prix d'écritures plus lentes.

## Le partitionnement : couper les données en parts

80 millions d'annonces, et des écritures qui passent toutes par une seule principale.

```scene
lesson: assets/data.scene.json
step: partitionnement
```

Les répliques aident à lire, pas à écrire. On **partitionne** alors les données (*sharding*) : chaque **partition** garde une part des annonces, choisie par une **clé** (la région, un identifiant). Chacune reçoit ses écritures, et a ses propres répliques. Le prix : une requête qui porte sur tout doit interroger **toutes** les partitions, et une clé mal choisie crée une partition **trop chaude**.

## Le réseau se coupe : cohérence ou disponibilité

Deux nœuds, à Paris et à Lyon, gardent les mêmes annonces et se recopient. Un jour, le lien entre eux se coupe.

```scene
lesson: assets/data.scene.json
step: cap
```

C'est une **partition réseau** : chaque nœud marche, mais ils ne se parlent plus. Un prix change à Paris ; Lyon ne peut pas le savoir. Lyon a deux choix : **refuser** de répondre, pour ne jamais donner une valeur fausse (la **cohérence**), ou **répondre** avec ce qu'il a, au risque d'être périmé (la **disponibilité**). Pendant la coupure, il ne peut pas avoir les deux.

## Le théorème CAP, énoncé correctement

Le théorème CAP (Eric Brewer, 2000 ; démontré en 2002) parle de trois propriétés d'un système réparti.

| Lettre | Ce qu'elle garantit |
|---|---|
| **C**, cohérence | chaque lecture voit la dernière écriture, comme s'il n'y avait qu'une copie |
| **A**, disponibilité | chaque requête reçue par un nœud en marche obtient une réponse, pas une erreur |
| **P**, tolérance au partitionnement | le système continue de fonctionner quand des messages entre nœuds se perdent |

Les coupures de réseau arrivent toujours : **P n'est pas une option**. Le théorème dit donc : **pendant une partition réseau**, il faut choisir entre C et A. Hors coupure, rien n'empêche d'avoir les deux. Le slogan « deux sur trois » est trompeur.

```fill
place: stage
text: "Le théorème CAP, en une phrase : pendant une _____ réseau, un système réparti doit choisir entre la _____ et la disponibilité. Hors coupure, il peut avoir les _____."
blanks:
  - answers: ["partition", "coupure"]
    hint: "Les nœuds marchent, mais ne se parlent plus."
  - answers: ["cohérence", "coherence"]
    hint: "Chaque lecture voit la dernière écriture."
  - answers: ["deux", "2"]
    hint: "Le slogan « deux sur trois » est trompeur."
```

## À toi : cohérence ou disponibilité ?

Pendant une coupure, le bon choix dépend de ce qui fait le plus de tort : une réponse **fausse**, ou **pas de réponse**. Trois données du site et d'ailleurs : choisis.

```quiz
title: "Cohérence ou disponibilité ?"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Le nombre de vues affiché sous une annonce."
    answers:
      - "Cohérence : refuser d'afficher la page tant que le compteur n'est pas exact"
      - "Disponibilité : afficher un compteur un peu en retard"
      - "Aucun des deux"
    correct: 2
    explanation: "Un compteur de vues approximatif ne fait de tort à personne. Bloquer la page en ferait."
  - prompt: "Le solde d'un compte bancaire, au moment d'autoriser un retrait."
    answers:
      - "Disponibilité : autoriser le retrait avec le solde connu localement"
      - "Cohérence : refuser l'opération tant que le solde n'est pas certain"
      - "Afficher un solde estimé"
    correct: 2
    explanation: "Autoriser un retrait sur un solde périmé peut créer un découvert. Mieux vaut un refus temporaire."
  - prompt: "L'ajout d'un article au panier sur un site marchand."
    answers:
      - "Disponibilité : accepter l'ajout, et fusionner les paniers au retour du réseau"
      - "Cohérence : refuser tout ajout pendant la coupure"
      - "Vider le panier"
    correct: 1
    explanation: "Refuser un ajout fait perdre une vente ; fusionner deux versions du panier plus tard est acceptable."
```

> 📖 [Théorème CAP (Wikipédia)](https://fr.wikipedia.org/wiki/Th%C3%A9or%C3%A8me_CAP) · [CAP Twelve Years Later (Eric Brewer, en anglais)](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/)

## Quatre questions pour vérifier ce que vous avez retenu

```quiz
title: "Réplication, partitionnement et CAP"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "À quoi servent surtout des répliques en lecture ?"
    answers:
      - "À répartir les lectures sur plusieurs machines"
      - "À répartir les écritures"
      - "À chiffrer les données"
    correct: 1
    explanation: "Les écritures passent toujours par la principale. Pour répartir les écritures, il faut partitionner."
  - prompt: "Une visiteuse publie une annonce et ne la voit pas en rechargeant. Pourquoi ?"
    answers:
      - "L'annonce a été perdue"
      - "Sa lecture est tombée sur une réplique pas encore à jour"
      - "La principale est en panne"
    correct: 2
    explanation: "C'est le retard de réplication. La cohérence à terme garantit que la réplique finira par l'avoir."
  - prompt: "Qu'est-ce qu'une partition trop chaude ?"
    answers:
      - "Une machine mal refroidie"
      - "Une partition qui reçoit beaucoup plus de requêtes que les autres, à cause de la clé choisie"
      - "Une partition sans répliques"
    correct: 2
    explanation: "Si la clé répartit mal les données ou les requêtes, une partition porte presque toute la charge."
  - prompt: "Que dit le théorème CAP ?"
    answers:
      - "Un système réparti a toujours au plus deux propriétés sur trois"
      - "Les coupures de réseau peuvent être évitées"
      - "Pendant une partition réseau, un système réparti doit choisir entre cohérence et disponibilité"
    correct: 3
    explanation: "Les partitions arrivent toujours. Pendant l'une d'elles, on choisit : réponses toujours justes, ou réponses toujours données. Hors coupure, on peut avoir les deux."
```

## Récap

- **Réplication** : des **répliques** tenues à jour par la **principale** ; elles répartissent les **lectures**.
- La recopie a un **retard** : **cohérence à terme** ; parade, relire ses propres écritures sur la principale.
- **Partitionnement** : couper les données selon une **clé** pour répartir les **écritures** ; attention aux requêtes sur tout et aux partitions **trop chaudes**.
- **Partition réseau** : les nœuds marchent mais ne se parlent plus.
- **CAP** : pendant une partition réseau, choisir entre **cohérence** (refuser plutôt que se tromper) et **disponibilité** (répondre, quitte à être périmé). Pas « deux sur trois ».

Ces choix appliqués à des organisations différentes : [Six organisations, six architectures](https://byte-layers.com/fr/bits/architecture-case-studies).

```ack
J'ai compris
```
