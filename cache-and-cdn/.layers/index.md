---
title: "Répondre plus vite : cache et CDN"
description: "Ne pas refaire mille fois le même travail : le cache qui garde une copie des réponses (succès, défaut), la copie périmée et ses deux parades (durée de vie, invalidation), puis le CDN qui place des copies des fichiers près des lecteurs, partout dans le monde. Ce qu'on peut mettre en cache, et ce qu'on ne doit pas y mettre."
tags:
  - bit
  - architecture
  - performance
  - system-design
difficulty: intermediate
duration: 12
requires: "0.8.0"
---

Beaucoup de requêtes demandent exactement la même chose. Plutôt que de refaire le travail à chaque fois, on garde une **copie** de la réponse, au plus près de celui qui la demande. Vous verrez le **cache**, le problème des copies périmées, et le **CDN**, qui place ces copies partout dans le monde. L'exemple suivi : un site de recettes de cuisine, dont une recette est lue des milliers de fois.

**Prérequis** : [Tenir la charge : vertical, horizontal, répartiteur](https://byte-layers.com/fr/bits/scaling-load-balancing), pour l'application, ses copies et sa base.

# Cache et CDN

## Sans cache : la même recette, calculée mille fois

La recette de la tarte aux pommes passe à la télévision. Mille lecteurs par seconde l'ouvrent.

```scene
lesson: assets/cache.scene.json
step: sans-cache
```

Pour chaque lecteur, l'application **relit la base** et reconstruit la même page. Le résultat est identique à chaque fois, mais la base fait mille fois le travail. Elle sature, et le temps de réponse grimpe pour tout le monde. Ajouter des copies de l'application n'y change rien : c'est la base qui est le **goulot**.

## Le cache : garder une copie de la réponse

On place une mémoire rapide à côté de l'application.

```scene
lesson: assets/cache.scene.json
step: cache
```

Le **cache** garde une copie des réponses déjà calculées, en mémoire. L'application le consulte d'abord. S'il n'a pas la réponse, c'est un **défaut de cache** (*miss*) : elle lit la base, puis range la réponse. Les demandes suivantes sont des **succès de cache** (*hit*), servis en quelques millisecondes. Sur mille lectures, la base n'en voit plus qu'une.

## La copie périmée : durée de vie et invalidation

Une copie a un défaut : elle ne sait pas que l'original a changé.

```scene
lesson: assets/cache.scene.json
step: perime
```

La recette est corrigée dans la base, mais le cache sert toujours l'ancienne : sa copie est **périmée**. Deux parades, souvent combinées. Une **durée de vie** (*TTL*) : passé un délai, la copie est jetée et relue. Une **invalidation** : au moment d'écrire, l'application efface la copie concernée. Choisir la durée, c'est choisir combien de temps une information un peu ancienne reste acceptable.

> ⚠️ **Si une donnée doit toujours être exacte** (un solde, un stock au moment de payer), ne la servez pas depuis un cache : relisez la source.

## Le CDN : des copies près des lecteurs

Le site est hébergé à Paris ; une partie de ses lecteurs est au Canada.

```scene
lesson: assets/cache.scene.json
step: cdn
```

Chaque fichier qui traverse l'Atlantique paie la **distance**, à l'aller et au retour. Un **CDN** (*Content Delivery Network*) a des serveurs dans le monde entier, qui gardent des copies des fichiers. La première demande va jusqu'au **serveur d'origine** ; les suivantes sont servies **sur place**. Images, scripts, feuilles de style, et même des pages entières s'y prêtent. Le navigateur, lui aussi, garde des copies, selon l'en-tête HTTP `Cache-Control`.

## À toi : que mettre en cache ?

Une bonne question avant chaque copie : **combien de fois** cette réponse sera-t-elle redemandée, et **combien de temps** peut-elle être un peu ancienne sans gêner personne ? Beaucoup de lectures et un léger retard acceptable : le cache s'impose. Une donnée propre à chacun, ou qui doit être exacte à la seconde : on la laisse à la source. Quatre éléments du site de recettes : choisis.

```quiz
title: "Que mettre en cache ?"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "La photo d'une recette, qui ne change jamais."
    answers:
      - "Ne jamais la mettre en cache"
      - "Dans le CDN et le navigateur, avec une longue durée de vie"
      - "La recalculer à chaque demande"
    correct: 2
    explanation: "Un fichier qui ne change pas est le cas idéal : on le garde longtemps, au plus près du lecteur."
  - prompt: "La liste des dix recettes les plus lues, recalculée à partir de millions de visites."
    answers:
      - "Dans le cache, avec une durée de vie de quelques minutes"
      - "Recalculée à chaque affichage de la page d'accueil"
      - "Dans le navigateur de chaque lecteur, pour un an"
    correct: 1
    explanation: "Coûteuse à calculer, lue sans arrêt, et un classement vieux de cinq minutes ne gêne personne."
  - prompt: "Le carnet de recettes favorites d'un lecteur connecté."
    answers:
      - "Dans le CDN, partagé avec tous les lecteurs"
      - "Pas dans un cache partagé : c'est une donnée propre à chacun"
      - "Dans le cache, sans durée de vie"
    correct: 2
    explanation: "Une page personnelle mise en cache partagé risque d'être servie à un autre lecteur. On ne la partage jamais."
  - prompt: "Le stock d'un livre de recettes, vérifié au moment de payer."
    answers:
      - "Dans le cache, pour aller plus vite"
      - "Dans le CDN"
      - "Relu à la source à chaque paiement"
    correct: 3
    explanation: "Au moment de payer, une valeur périmée vendrait un livre qui n'existe plus."
```

> 📖 [Caching (MDN, en anglais)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching) · [Réseau de diffusion de contenu (Wikipédia)](https://fr.wikipedia.org/wiki/R%C3%A9seau_de_diffusion_de_contenu)

## Quatre questions pour vérifier ce que vous avez retenu

```quiz
title: "Cache et CDN"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "Qu'est-ce qu'un succès de cache (hit) ?"
    answers:
      - "Une réponse trouvée dans le cache, sans relire la source"
      - "Une réponse trouvée dans la base"
      - "Une erreur du cache"
    correct: 1
    explanation: "Succès : la copie est là. Défaut (miss) : il faut lire la source, puis ranger la copie."
  - prompt: "Une recette corrigée s'affiche encore dans son ancienne version. Pourquoi ?"
    answers:
      - "La base n'a pas enregistré la correction"
      - "Le cache sert une copie périmée"
      - "Le CDN est en panne"
    correct: 2
    explanation: "La copie ne sait pas que l'original a changé. D'où la durée de vie, et l'invalidation au moment de l'écriture."
  - prompt: "Que fait un CDN ?"
    answers:
      - "Il chiffre les échanges entre le site et la base"
      - "Il remplace la base de données"
      - "Il garde des copies des fichiers sur des serveurs proches des lecteurs"
    correct: 3
    explanation: "Les lecteurs sont servis par un serveur proche ; seules les premières demandes vont jusqu'à l'origine."
  - prompt: "Quelle donnée ne doit pas être servie depuis un cache ?"
    answers:
      - "Le logo du site"
      - "Le solde d'un compte au moment d'un paiement"
      - "La liste des recettes de la semaine"
    correct: 2
    explanation: "Une donnée qui doit être exacte au moment d'agir se relit à la source."
```

## Récap

- Beaucoup de demandes identiques : on garde une **copie** de la réponse plutôt que de refaire le travail.
- **Cache** : consulté d'abord ; **défaut** (*miss*) → on lit la source et on range ; **succès** (*hit*) → réponse immédiate.
- Une copie peut être **périmée** : **durée de vie** (*TTL*) et **invalidation** à l'écriture.
- **CDN** : des copies des fichiers près des lecteurs ; le **serveur d'origine** garde la référence.
- On ne met pas en cache partagé ce qui est **propre à chacun**, ni ce qui doit être **exact** au moment d'agir.

Quand une seule machine ne peut plus garder toutes les données : [Réplication, partitionnement et théorème CAP](https://byte-layers.com/fr/bits/replication-sharding-cap).

```ack
J'ai compris
```
