---
title: "Rester en service : SPOF, redondance, bascule"
description: "Ce qui garde un service debout quand une machine tombe : repérer les points uniques de défaillance, doubler chaque élément (redondance, réplication de la base, répartiteur de secours), basculer sur la réplique quand la principale tombe, répartir dans deux centres de données. Ce que veulent dire 99,9 % ou 99,99 % de disponibilité, et ce que chaque neuf coûte."
tags:
  - bit
  - architecture
  - reliability
  - system-design
difficulty: intermediate
duration: 13
requires: "0.8.0"
---

Une machine finit toujours par tomber : un disque qui lâche, une mise à jour ratée, une coupure de courant. La **haute disponibilité**, c'est organiser un système pour qu'il reste en service malgré ces pannes. Vous verrez comment repérer ce qui peut tout arrêter, le doubler, basculer quand il tombe, et ce que coûte chaque pas de plus. L'exemple suivi : une épicerie en ligne qui prend des commandes jour et nuit.

**Prérequis** : [Tenir la charge : vertical, horizontal, répartiteur](https://byte-layers.com/fr/bits/scaling-load-balancing), pour le répartiteur, les copies et les contrôles de santé.

# Rester en service

## Trouver les points uniques de défaillance

L'épicerie fait déjà tourner trois copies de son application derrière un répartiteur.

```scene
lesson: assets/ha.scene.json
step: spof
```

Quand une copie tombe, les autres prennent le relais : c'est déjà de la redondance. Mais il n'y a qu'**un** répartiteur et qu'**une** base. Si l'un des deux tombe, tout s'arrête. Un tel élément s'appelle un **point unique de défaillance** (*SPOF*, *single point of failure*). Le premier travail est de les **lister**, en suivant le chemin d'une requête du client jusqu'aux données.

## La redondance : un second exemplaire de chaque élément

Pour chaque SPOF, on prévoit un second exemplaire prêt à servir.

```scene
lesson: assets/ha.scene.json
step: redondance
```

La base reçoit une **réplique** : une copie que la base principale tient à jour en continu, c'est la **réplication**. Le répartiteur reçoit un jumeau, prêt à reprendre son adresse. C'est la **redondance**. Elle a un prix évident, deux fois plus de machines, et un prix moins visible : il faut **tester** que le second exemplaire marche vraiment, sinon on le découvre le jour de la panne.

## La bascule : la réplique prend le relais

Un soir, la base principale tombe.

```scene
lesson: assets/ha.scene.json
step: bascule
```

Des **contrôles de santé** constatent la panne, plusieurs fois de suite pour ne pas réagir à un simple raté. La réplique est alors **promue** : elle devient la principale, et l'application s'y connecte. C'est la **bascule** (*failover*). Elle n'est pas instantanée : quelques secondes à quelques minutes de coupure. Et si la recopie avait du retard, les toutes dernières écritures peuvent manquer.

> 💡 **Remarque.** Deux chiffres résument une bascule : le **temps de reprise** (*RTO*), combien de temps le service est coupé, et la **perte de données admise** (*RPO*), combien d'écritures récentes on accepte de perdre. Une recopie qui attend la réplique avant de confirmer réduit la perte, au prix d'écritures plus lentes.

## Deux centres de données : survivre à une panne de site

Tout est en double. Mais tout est au même endroit.

```scene
lesson: assets/ha.scene.json
step: zones
```

Une coupure de courant, un incendie ou une erreur de réseau emporte **tout un centre de données**, avec les deux exemplaires. On répartit donc les exemplaires dans **plusieurs centres**, éloignés l'un de l'autre. Les hébergeurs en nuage appellent ces centres des **zones de disponibilité**. Quand un centre tombe, l'autre prend tout : il doit donc pouvoir porter **seul** toute la charge.

## À toi : combien de neufs ?

On exprime la disponibilité en pourcentage du temps où le service répond.

| Disponibilité | Arrêt possible par an |
|---|---|
| 99 % | environ 3,7 jours |
| 99,9 % | environ 8 h 45 |
| 99,99 % | environ 53 minutes |
| 99,999 % | environ 5 minutes |

Chaque **neuf** de plus divise l'arrêt permis par dix, et coûte bien plus que le précédent : plus de machines, de centres, de tests, de personnes d'astreinte. Trois situations : choisis l'objectif raisonnable.

```quiz
title: "Combien de neufs ?"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "L'outil interne qui sert à poser ses congés, utilisé en journée par 200 salariés."
    answers:
      - "99,999 %, dans trois centres de données"
      - "Autour de 99 % : quelques heures d'arrêt par an ne gênent personne"
      - "Aucun objectif, même s'il est coupé une semaine"
    correct: 2
    explanation: "Un arrêt d'une heure se rattrape le lendemain. Doubler chaque élément coûterait plus que la gêne."
  - prompt: "Le site de l'épicerie en ligne, où chaque heure d'arrêt fait perdre des commandes."
    answers:
      - "99,9 % à 99,99 % : redondance de chaque élément, bascule automatique"
      - "99 % suffit, les clients reviendront"
      - "100 %, garanti"
    correct: 1
    explanation: "La perte se compte en commandes : la redondance et la bascule automatique se rentabilisent."
  - prompt: "Un fournisseur promet « 100 % de disponibilité ». Qu'en penser ?"
    answers:
      - "C'est possible avec assez de machines"
      - "C'est la norme pour un service en ligne"
      - "Aucun système ne le garantit : on réduit la probabilité et la durée des pannes, on ne les supprime pas"
    correct: 3
    explanation: "Une erreur humaine, une mise à jour ou une panne de réseau peuvent toujours tout arrêter. On vise un nombre de neufs, et on prépare la reprise."
```

> 📖 [Haute disponibilité (Wikipédia)](https://fr.wikipedia.org/wiki/Haute_disponibilit%C3%A9) · [Point unique de défaillance (Wikipédia)](https://fr.wikipedia.org/wiki/Point_individuel_de_d%C3%A9faillance)

## Quatre questions pour vérifier ce que vous avez retenu

```quiz
title: "Rester en service"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Qu'est-ce qu'un point unique de défaillance ?"
    answers:
      - "Un élément dont la panne arrête tout le système"
      - "Un élément qui tombe souvent"
      - "Le point d'entrée d'un site"
    correct: 1
    explanation: "Il n'a pas de second exemplaire. La redondance commence par les lister."
  - prompt: "Que se passe-t-il pendant une bascule de base de données ?"
    answers:
      - "Rien de visible, c'est instantané"
      - "La panne est constatée, la réplique est promue principale, l'application s'y reconnecte ; une courte coupure est possible"
      - "La base principale est réparée automatiquement"
    correct: 2
    explanation: "Il faut constater la panne avec certitude, promouvoir, puis rediriger. D'où quelques secondes à quelques minutes de coupure."
  - prompt: "Pourquoi répartir les exemplaires dans deux centres de données ?"
    answers:
      - "Pour aller plus vite"
      - "Pour payer moins cher"
      - "Parce qu'une panne de site (courant, incendie, réseau) emporte tout ce qu'il contient"
    correct: 3
    explanation: "Deux exemplaires dans le même centre tombent ensemble. Chaque centre doit pouvoir porter seul la charge."
  - prompt: "Passer de 99,9 % à 99,99 % de disponibilité, c'est :"
    answers:
      - "Diviser par dix l'arrêt permis, d'environ 8 h 45 à environ 53 minutes par an"
      - "Gagner 0,09 %, presque rien"
      - "Doubler l'arrêt permis"
    correct: 1
    explanation: "Chaque neuf divise l'arrêt permis par dix, et coûte nettement plus que le précédent."
```

## Récap

- Lister les **points uniques de défaillance** en suivant une requête du client aux données.
- **Redondance** : un second exemplaire de chaque élément ; **réplication** de la base vers une **réplique**.
- **Bascule** (*failover*) : la réplique est promue ; **temps de reprise** (RTO) et **perte de données admise** (RPO).
- **Plusieurs centres de données** pour survivre à une panne de site ; chacun doit porter seul la charge.
- La disponibilité se compte en **neufs** ; chaque neuf divise l'arrêt par dix et coûte plus que le précédent.

Quand les données elles-mêmes sont copiées sur plusieurs machines, et ce qu'on perd quand le réseau se coupe : [Réplication, partitionnement et théorème CAP](https://byte-layers.com/fr/bits/replication-sharding-cap).

```ack
J'ai compris
```
