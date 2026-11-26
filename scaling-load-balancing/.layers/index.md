---
title: "Tenir la charge : vertical, horizontal, répartiteur et services sans état"
description: "Quand le trafic d'une application dépasse ce que sa machine sait servir : mesurer la charge, la mise à l'échelle verticale (une machine plus grosse) et ses limites, la mise à l'échelle horizontale (des copies derrière un répartiteur de charge), le reverse proxy, et pourquoi les copies doivent être sans état. Avec un playground pour piloter soi-même le répartiteur."
tags:
  - bit
  - architecture
  - system-design
  - scaling
difficulty: intermediate
duration: 14
requires: "0.11.0"
---

Une application qui marche bien pour cent personnes peut s'effondrer quand dix mille arrivent en même temps. Vous verrez comment on la fait tenir : grossir la machine, ou la copier et répartir le trafic. Vous saurez ce que font un répartiteur de charge et un reverse proxy, et pourquoi les copies ne doivent rien garder pour elles. L'exemple suivi : la billetterie en ligne d'un festival, le jour où la vente ouvre.

**Prérequis** : [Les architectures d'un programme, du poste seul au n tiers](https://byte-layers.com/fr/bits/program-architectures), pour le client-serveur et les tiers.

# Tenir la charge

## Une machine, et la vente qui ouvre

La billetterie tourne sur un seul serveur d'application. À 10 h, la vente des billets ouvre, et tout le monde se connecte à la même minute.

```scene
lesson: assets/scaling.scene.json
step: une-machine
```

Trois chiffres disent l'état d'un service : le **trafic** (les requêtes par seconde), le **temps de réponse** et la part des requêtes en **échec**. Chaque machine a une **capacité** : au-delà, les requêtes attendent, puis échouent. Pour tenir, il faut plus de capacité. Deux façons de l'obtenir : **grossir** la machine, ou **multiplier** les machines.

## Une machine plus grosse

Première idée, la plus simple : garder la même application et la poser sur une machine plus puissante.

```scene
lesson: assets/scaling.scene.json
step: vertical
```

C'est la **mise à l'échelle verticale** (*scale up*). Rien à changer dans le code, et c'est souvent le bon premier geste. Mais une machine a un **plafond**, son prix grimpe plus vite que sa puissance, et le changement demande souvent un arrêt. Surtout, elle reste **seule** : si elle tombe, tout le site tombe.

## Des copies et un répartiteur

Deuxième idée : faire tourner plusieurs **copies identiques** de l'application, et mettre une seule adresse devant.

```scene
lesson: assets/scaling.scene.json
step: horizontal
```

C'est la **mise à l'échelle horizontale** (*scale out*). Devant les copies, un **répartiteur de charge** (*load balancer*) reçoit toutes les requêtes et les distribue, ici à tour de rôle. On ajoute des copies sans arrêter le site, et une copie qui tombe ne coupe pas tout. Les copies forment toujours **un seul tiers** : on compte les niveaux de machines, pas les exemplaires.

## Répartiteur et reverse proxy

La machine placée devant les copies fait souvent plus que répartir. On l'appelle alors un **reverse proxy**.

```scene
lesson: assets/scaling.scene.json
step: reverse-proxy
```

Un **reverse proxy** reçoit les requêtes **à la place** des serveurs, qui restent cachés derrière lui. Il peut **aiguiller** selon l'adresse demandée, porter le **chiffrement HTTPS**, compresser ou garder en mémoire des réponses. Répartir entre des copies est l'une de ses fonctions. Nginx, HAProxy ou Traefik font les deux. Un répartiteur peut aussi travailler plus bas, sans lire les requêtes HTTP : il distribue alors les connexions.

## Des copies sans état

Les copies doivent être interchangeables. Voici ce qui arrive quand l'une d'elles garde quelque chose pour elle.

```scene
lesson: assets/scaling.scene.json
step: sans-etat
```

Ce qu'une copie garde en mémoire entre deux requêtes est son **état** : un panier, une connexion. Si la requête suivante tombe sur une autre copie, cet état est perdu. Le remède : ranger l'état **hors des copies**, dans un **magasin de sessions** partagé ou dans la base. Les copies deviennent **sans état** (*stateless*) : n'importe laquelle sert n'importe qui.

> 💡 **Remarque.** Une autre parade consiste à renvoyer chaque utilisateur vers la même copie (*sticky sessions*). Elle dépanne, mais une copie qui tombe emporte les paniers de ses utilisateurs, et la charge se répartit moins bien.

## À toi : tenir la vente

Le même schéma, mais c'est toi qui pilotes : monte le trafic, ajoute des copies, fais-en tomber une. Le mode **guidé**, dans la barre de la scène, te donne quatre consignes.

```scene
lesson: assets/scaling.scene.json
step: playground
```

> 📖 [Répartition de charge (Wikipédia)](https://fr.wikipedia.org/wiki/R%C3%A9partition_de_charge) · [Reverse proxy (documentation Nginx, en anglais)](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)

## Quatre questions pour vérifier ce que vous avez retenu

```quiz
title: "Tenir la charge"
tracksProgress: false
showNotice: false
place: stage
questions:
  - prompt: "On remplace la machine d'un site par une machine quatre fois plus puissante. De quoi s'agit-il ?"
    answers:
      - "De mise à l'échelle verticale"
      - "De mise à l'échelle horizontale"
      - "De répartition de charge"
    correct: 1
    explanation: "Grossir une machine, c'est la mise à l'échelle verticale. L'horizontale ajoute des copies, derrière un répartiteur."
  - prompt: "Quel risque la mise à l'échelle horizontale réduit-elle, et pas la verticale ?"
    answers:
      - "Le coût du développement"
      - "La panne d'une seule machine qui coupe tout le site"
      - "Le temps de réponse de la base de données"
    correct: 2
    explanation: "Avec plusieurs copies, celle qui tombe est retirée par le répartiteur et les autres prennent sa part. Une seule machine, même grosse, reste un point unique de panne."
  - prompt: "Un utilisateur perd son panier dès que sa requête tombe sur une autre copie. Quelle est la cause ?"
    answers:
      - "Le répartiteur répartit mal le trafic"
      - "Les copies gardent le panier dans leur mémoire : elles ne sont pas sans état"
      - "Il n'y a pas assez de copies"
    correct: 2
    explanation: "Le panier est un état. Rangé dans la mémoire d'une copie, il n'existe pas pour les autres. Il faut le ranger hors des copies, dans un magasin partagé."
  - prompt: "Que fait un reverse proxy, en plus de répartir entre des copies ?"
    answers:
      - "Il remplace la base de données"
      - "Il reçoit les requêtes à la place des serveurs, les aiguille, et porte souvent le chiffrement HTTPS"
      - "Il installe les nouvelles versions de l'application"
    correct: 2
    explanation: "Le reverse proxy est l'unique porte d'entrée : il cache les serveurs, aiguille selon l'adresse, chiffre, compresse. La répartition est l'une de ses fonctions."
```

## Récap

- Trois chiffres disent si un service tient : **trafic**, **temps de réponse**, **échecs** ; chaque machine a une **capacité**.
- **Verticale** : une machine plus grosse ; simple, mais un plafond, un coût qui grimpe, et une machine seule.
- **Horizontale** : des copies identiques derrière un **répartiteur de charge** ; on ajoute des copies sans arrêter, et les copies restent un seul tiers.
- Le **reverse proxy** reçoit les requêtes à la place des serveurs : il aiguille, chiffre, répartit.
- Des copies **sans état** : l'état (session, panier) est rangé hors d'elles, dans un magasin partagé.

Quand les copies tiennent mais que la même page est demandée des milliers de fois : [Répondre plus vite : cache et CDN](https://byte-layers.com/fr/bits/cache-and-cdn). Quand une panne ne doit rien couper : [Rester en service : SPOF, redondance, failover](https://byte-layers.com/fr/bits/high-availability).

```ack
J'ai compris
```
