---
title: "Découper une application de VTC"
description: "Un défi en quatre décisions sur Hopla, une application de VTC encore monolithique : les modules qui méritent de devenir des services, où vivent leurs données, comment ils se parlent, et comment encaisser la panne du prestataire de paiement un vendredi soir. Vos décisions sont vérifiées."
tags:
  - challenge
  - architecture
  - system-design
difficulty: advanced
duration: 30
introTitle: "Le défi"
requires: "0.8.0"
options:
  allowManualProgress: false
  autoCompleteOnNext: unverifiable
---

Ce challenge vous permet de prouver que vous savez découper une application en services **pour de bonnes raisons**, et choisir pour chacun sa base et sa façon de communiquer. L'application à découper est **Hopla**, une application de VTC inventée. Il n'y a **aucune commande à recopier** : chaque tâche pose une question d'architecture, et vous inscrivez votre décision dans un fichier. Un bouton vérifie ce fichier.

Si vous êtes bloqué, les **indices** se dévoilent un par un, et la **solution** reste en dernier recours. Les utiliser ne coûte rien : seule la vérification compte.

## Avant de commencer

- **Ce qu'il faut savoir** : ce qu'enseignent [Monolithe, monolithe modulaire, micro-services](https://byte-layers.com/fr/bits/monolith-to-microservices), [Le prix des micro-services](https://byte-layers.com/fr/bits/microservices-costs), [Synchrone ou asynchrone](https://byte-layers.com/fr/bits/sync-async-communication), [Les protocoles entre programmes](https://byte-layers.com/fr/bits/communication-protocols) et [Six organisations, six architectures](https://byte-layers.com/fr/bits/architecture-case-studies).
- **Ce qu'il faut avoir** : un terminal (Git Bash sous Windows) et un éditeur de texte.
- **Le fichier de décisions** : `~/byte-layers/architecture/ride-hailing/decisions.txt` est créé pour vous à l'ouverture. Il contient une ligne `clé=` par décision, à compléter après le signe `=`. Les majuscules et les espaces sont ignorés. Les lignes qui commencent par `#` sont des commentaires. Supprimez le dossier `~/byte-layers/architecture/ride-hailing` quand vous n'en avez plus besoin.

> Hopla est inventée et simplifiée : une vraie décision pèse aussi le budget, les compétences de l'équipe et l'existant. Les chiffres sont des ordres de grandeur.

# Tâche 1 : les modules qui deviennent des services

## Hopla aujourd'hui

```setup
D=~/byte-layers/architecture/ride-hailing
if [ ! -f "$D/decisions.txt" ]; then
  mkdir -p "$D"
  cat > "$D/decisions.txt" <<'FIN'
# Tâche 1 : les lettres des modules à sortir du monolithe, par exemple a,f
extraire=
# Tâche 2 : une lettre pour les factures, une lettre pour les positions
factures=
positions=
# Tâche 3 : une lettre par échange
demande=
suivi=
fin=
prix=
# Tâche 4 : les lettres des trois mesures à retenir, par exemple a,c,f
panne=
FIN
fi
```

**Hopla** met en relation des passagers et des chauffeurs dans dix villes. Toute l'application est un **monolithe modulaire** : un seul programme, une seule base, des modules bien séparés dans le code, déployé toutes les deux semaines. Quarante développeurs, en quatre équipes. Le monolithe commence à gêner, et la direction demande « des micro-services ».

| Lettre | Module | Ce qu'il fait | Charge | Équipe, rythme | Contraintes |
|---|---|---|---|---|---|
| a | passagers | comptes, profils, moyens de paiement enregistrés | faible | Produit, toutes les deux semaines | aucune particulière |
| b | chauffeurs | comptes, documents (permis, assurance), validation | faible | Produit, toutes les deux semaines | aucune particulière |
| c | courses en direct | reçoit la position de 20 000 chauffeurs toutes les 4 secondes, trouve le chauffeur le plus proche, suit la course | 5 000 positions par seconde le samedi soir, presque rien à 4 h du matin | Temps réel, veut déployer chaque jour | doit répondre en moins d'une seconde |
| d | tarification | calcule le prix, applique la majoration quand la demande dépasse l'offre | une fois par demande de course | Tarifs, change ses règles **plusieurs fois par semaine** | aucune particulière |
| e | paiement | débite la carte par un prestataire, rembourse | une fois par course | Paiement, toutes les deux semaines | audits de sécurité, accès au code et aux données réservé à cette équipe |
| f | factures | produit la facture PDF de chaque course et le relevé mensuel | faible, en fin de mois | Produit, toutes les deux semaines | aucune particulière |
| g | notifications | envoie les SMS et notifications « votre chauffeur arrive » | quelques messages par course | Produit, toutes les deux semaines | aucune particulière |

Complétez `extraire=` avec les lettres des modules qui ont une **vraie raison** de devenir un service à part. Les autres restent des modules du monolithe.

**Critères :**

- chaque module extrait a au moins une raison propre : une charge très différente des autres, une équipe qui veut livrer à un autre rythme, ou des contraintes que le reste n'a pas ;
- aucun module n'est extrait sans raison : chaque service de plus a un prix.

```hint
Un service de plus, c'est un déploiement, une base, une surveillance et des appels réseau qui peuvent échouer de plus. Pour chaque module, cherchez dans le tableau une raison qui le distingue des autres. « Faible, Produit, toutes les deux semaines, aucune particulière » n'en est pas une.
```

```hint
Il y a trois raisons possibles, et chacune désigne un module différent : la charge qui varie énormément, l'équipe qui change ses règles plusieurs fois par semaine, et les audits avec accès réservé.
```

```verify
F=~/byte-layers/architecture/ride-hailing/decisions.txt
[ -f "$F" ] || { echo "Le fichier $F n'existe pas. Rechargez la page du challenge pour le recréer."; exit 1; }
v() { tr 'A-Z' 'a-z' < "$F" | sed -n "s/^[[:space:]]*$1[[:space:]]*=//p" | tail -1 | tr -d '[:space:]"'; }
R=$(v extraire)
[ -n "$R" ] || { echo "La ligne extraire= est vide."; exit 1; }
echo "$R" | grep -qE '^[a-g](,[a-g])*$' || { echo "Écrivez des lettres de a à g séparées par des virgules, par exemple a,f."; exit 1; }
L=$(echo "$R" | tr -cd 'a-g' | fold -w1 | sort -u | tr -d '\n')
M=""
for x in a b f g; do
  case "$L" in *$x*) M="$M
- $x : faible charge, équipe Produit, même rythme, aucune contrainte propre. En faire un service ajouterait un déploiement, une base et des appels réseau, sans rien gagner.";; esac
done
case "$L" in *c*) ;; *) M="$M
- il manque le module dont la charge varie énormément : en service à part, on ajoute des copies le samedi soir sans copier tout le monolithe.";; esac
case "$L" in *d*) ;; *) M="$M
- il manque le module dont l'équipe change les règles plusieurs fois par semaine : aujourd'hui elle attend le déploiement commun toutes les deux semaines.";; esac
case "$L" in *e*) ;; *) M="$M
- il manque le module audité, dont l'accès doit être réservé à une équipe : à part, son code et sa base sont isolés du reste.";; esac
[ -z "$M" ] || { echo "Votre choix ($L) n'est pas encore le bon :$M"; exit 1; }
echo "Trois services : courses en direct (la charge), tarification (le rythme), paiement (les contraintes). Le reste reste un monolithe modulaire."
```

````solution
```text
extraire=c,d,e
```

| Lettre | Verdict |
|---|---|
| c | extrait : sa charge passe de presque rien à 5 000 positions par seconde ; en service, on ajoute des copies de ce seul service |
| d | extrait : l'équipe Tarifs livre ses règles plusieurs fois par semaine sans attendre les autres |
| e | extrait : un code et une base isolés, auditables, accessibles à une seule équipe |
| a, b, f, g | restent des modules du monolithe : rien ne les distingue, et chaque service de plus a un prix |

Le résultat n'est pas « des micro-services partout » : c'est **un monolithe modulaire et trois services**. On en sortira d'autres le jour où une vraie raison apparaîtra.
````

# Tâche 2 : à qui appartiennent les données

## Une base par service

Chaque service extrait a **sa propre base** : personne d'autre n'y lit ni n'y écrit. Deux questions en découlent.

**Les factures.** Le module factures, resté dans le monolithe, a besoin pour chaque course terminée de la distance, du prix et du passager. Ces informations naissent dans le service courses en direct.

| Lettre | Proposition |
|---|---|
| a | le monolithe se connecte à la base du service courses en direct et y lit ce qu'il lui faut |
| b | le service courses en direct publie un événement « course terminée » avec ces informations ; le monolithe s'y abonne et garde sa copie |
| c | on remet toutes les données dans une seule base partagée par tous |

**Les positions.** Le service courses en direct reçoit 5 000 positions par seconde. Pour trouver le chauffeur le plus proche, il n'a besoin que de la **dernière** position de chaque chauffeur ; une position de plus de 30 secondes ne sert plus à rien.

| Lettre | Proposition |
|---|---|
| a | une base relationnelle qui garde chaque position, avec une transaction par écriture |
| b | un stockage clé-valeur en mémoire (un chauffeur, sa dernière position), répliqué, où chaque position expire après 30 secondes |
| c | un fichier par chauffeur, réécrit à chaque position |

Complétez `factures=` et `positions=` avec une lettre chacun.

**Critères :**

- aucun service ne lit la base d'un autre ;
- le stockage des positions tient la charge et ne garde que ce qui sert.

```hint
Si le monolithe lit la base du service courses en direct, que se passe-t-il le jour où l'équipe Temps réel renomme une colonne ? Et si tout revient dans une seule base, qu'a-t-on gagné à découper ?
```

```hint
Pour les positions : il faut écrire très vite, lire très vite, et oublier ce qui a plus de 30 secondes. Lequel des trois stockages est fait pour ça ?
```

```verify
F=~/byte-layers/architecture/ride-hailing/decisions.txt
[ -f "$F" ] || { echo "Le fichier $F n'existe pas. Rechargez la page du challenge pour le recréer."; exit 1; }
v() { tr 'A-Z' 'a-z' < "$F" | sed -n "s/^[[:space:]]*$1[[:space:]]*=//p" | tail -1 | tr -d '[:space:]"'; }
case "$(v factures)" in
  b) ;;
  "") echo "La ligne factures= est vide."; exit 1 ;;
  a) echo "factures : lire la base d'un autre service le lie à ses tables. Le jour où l'équipe Temps réel change une colonne, les factures cassent, et elle ne peut plus changer sa base seule."; exit 1 ;;
  c) echo "factures : une seule base partagée, c'est revenir au couplage du monolithe ; aucun service ne pourrait plus changer ses données seul."; exit 1 ;;
  *) echo "factures : écrivez une seule lettre, a, b ou c."; exit 1 ;;
esac
case "$(v positions)" in
  b) ;;
  "") echo "La ligne positions= est vide."; exit 1 ;;
  a) echo "positions : une transaction et une ligne gardée pour chaque position, 5 000 fois par seconde, pour n'en lire que la dernière. Il faut un stockage plus rapide qui oublie de lui-même."; exit 1 ;;
  c) echo "positions : 20 000 fichiers réécrits toutes les 4 secondes sur une seule machine, sans copie ni expiration. Cherchez un stockage en mémoire, répliqué."; exit 1 ;;
  *) echo "positions : écrivez une seule lettre, a, b ou c."; exit 1 ;;
esac
echo "Les factures reçoivent un événement et gardent leur copie ; les positions vivent en mémoire et expirent d'elles-mêmes."
```

````solution
```text
factures=b
positions=b
```

- **factures=b** : l'événement « course terminée » donne au monolithe tout ce qu'il lui faut, sans qu'il connaisse la base du service. Le prix : sa copie arrive avec un léger retard, sans gravité pour une facture.
- **positions=b** : un stockage clé-valeur en mémoire (Redis, par exemple) écrit et lit en une fraction de milliseconde, et la durée de vie efface les positions périmées. Répliqué, il survit à la panne d'une machine ; perdre quelques positions n'est pas grave, la suivante arrive dans 4 secondes.
````

# Tâche 3 : comment ils se parlent

## Quatre échanges

| Lettre | Façon de communiquer |
|---|---|
| a | requête HTTP vers une API REST, réponse attendue |
| b | WebSocket : une connexion qui reste ouverte, le serveur envoie quand il veut |
| c | événement déposé dans un journal d'événements, lu par les abonnés à leur rythme |
| d | appel gRPC : appel synchrone entre services, contrat typé, format binaire compact |

Une lettre par échange, dans `decisions.txt` :

- `demande=` : l'application du passager demande une course, et attend un numéro de course en retour ;
- `suivi=` : l'application du passager affiche la voiture qui approche, mise à jour toutes les 4 secondes ;
- `fin=` : la course se termine ; les factures, les notifications et le paiement doivent chacun réagir ;
- `prix=` : pendant la demande, le service courses en direct demande le prix au service tarification, des centaines de fois par seconde, et ne peut rien proposer sans lui.

**Critères :**

- un échange qui attend une réponse est synchrone ; un échange que plusieurs services traitent à leur rythme est asynchrone ;
- quand c'est le serveur qui a des nouvelles à donner, la connexion reste ouverte ;
- un appel interne à fort volume utilise un format compact et un contrat strict.

```hint
Pour `suivi=` : faut-il que l'application redemande toutes les 4 secondes « où est la voiture ? », ou que le serveur le lui dise ?
```

```hint
Pour `fin=` : trois services réagissent, et le passager n'a pas à attendre la facture pour sortir de la voiture. Pour `prix=` : les deux bouts sont des services internes, et le volume est élevé.
```

```verify
F=~/byte-layers/architecture/ride-hailing/decisions.txt
[ -f "$F" ] || { echo "Le fichier $F n'existe pas. Rechargez la page du challenge pour le recréer."; exit 1; }
v() { tr 'A-Z' 'a-z' < "$F" | sed -n "s/^[[:space:]]*$1[[:space:]]*=//p" | tail -1 | tr -d '[:space:]"'; }
M=""
case "$(v demande)" in
  a) ;;
  "") M="$M
- demande= est vide.";;
  *) M="$M
- demande : l'application pose une question et attend une réponse, le numéro de course. C'est le cas le plus simple : une requête HTTP vers une API REST.";;
esac
case "$(v suivi)" in
  b) ;;
  "") M="$M
- suivi= est vide.";;
  a) M="$M
- suivi : redemander toutes les 4 secondes, c'est une requête presque toujours inutile par passager. Ici, c'est le serveur qui a des nouvelles : une connexion qui reste ouverte.";;
  *) M="$M
- suivi : c'est le serveur qui envoie une nouvelle position toutes les 4 secondes à l'application, sur une connexion qui reste ouverte.";;
esac
case "$(v fin)" in
  c) ;;
  "") M="$M
- fin= est vide.";;
  *) M="$M
- fin : trois services réagissent, chacun à son rythme, et la course ne doit pas attendre la facture. Un événement publié une fois, lu par chaque abonné.";;
esac
case "$(v prix)" in
  d) ;;
  "") M="$M
- prix= est vide.";;
  a) M="$M
- prix : REST fonctionnerait, mais pour un appel interne des centaines de fois par seconde, un format binaire compact et un contrat typé coûtent moins et cassent moins. Lequel ?";;
  c) M="$M
- prix : le service courses en direct ne peut rien proposer sans le prix ; il doit attendre la réponse. Un événement ne répond pas.";;
  *) M="$M
- prix : un appel synchrone interne, à fort volume, avec un contrat strict.";;
esac
[ -z "$M" ] || { echo "Pas encore :$M"; exit 1; }
echo "REST pour la demande, WebSocket pour le suivi, un événement pour la fin de course, gRPC pour le prix."
```

````solution
```text
demande=a
suivi=b
fin=c
prix=d
```

| Échange | Choix | Pourquoi |
|---|---|---|
| demande | REST | une question, une réponse, depuis une application mobile, à travers la passerelle d'API |
| suivi | WebSocket | le serveur pousse la position toutes les 4 secondes, sans que l'application redemande |
| fin | événement | trois abonnés, chacun à son rythme ; on en ajoute un sans toucher au service des courses |
| prix | gRPC | appel interne synchrone, très fréquent : format compact, contrat partagé par les deux équipes |

REST conviendrait aussi pour le prix : c'est un choix de confort et de volume, pas une obligation.
````

# Tâche 4 : le vendredi soir où le paiement ralentit

## Le prestataire répond en 20 secondes

Vendredi, 23 h. Le prestataire de paiement répond en **20 secondes** au lieu d'une demi-seconde. Aujourd'hui, le service courses en direct demande au service paiement de débiter la carte **avant** de chercher un chauffeur : les demandes s'accumulent, et plus aucune course ne part.

| Lettre | Proposition |
|---|---|
| a | augmenter le délai d'attente du service paiement à 60 secondes, pour ne plus avoir d'échec |
| b | accepter la course sans attendre le débit ; le débit part en fin de course, déposé dans une file, et le service paiement le traite à son rythme |
| c | réessayer immédiatement cinq fois chaque débit qui échoue |
| d | joindre à chaque débit une clé d'idempotence, l'identifiant de la course, que le service paiement transmet au prestataire |
| e | un disjoncteur : après une série d'échecs, le service paiement cesse quelques instants d'appeler le prestataire, et les débits attendent dans la file |
| f | remettre le paiement dans le monolithe |

Complétez `panne=` avec les lettres des **trois** propositions à retenir.

**Critères :**

- les courses partent même quand le prestataire est lent ;
- aucune proposition retenue n'aggrave la charge sur le prestataire ;
- aucun passager n'est débité deux fois.

```hint
Deux propositions aggravent la situation : l'une garde chaque demande bloquée plus longtemps, l'autre multiplie les appels vers un prestataire déjà saturé. Une troisième ne change rien au problème, qui est l'attente.
```

```hint
Une fois le débit dans une file, il sera retenté. Que faut-il pour qu'un débit retenté ne débite pas une seconde fois ? Et pour ne pas marteler le prestataire pendant qu'il est malade ?
```

```verify
F=~/byte-layers/architecture/ride-hailing/decisions.txt
[ -f "$F" ] || { echo "Le fichier $F n'existe pas. Rechargez la page du challenge pour le recréer."; exit 1; }
v() { tr 'A-Z' 'a-z' < "$F" | sed -n "s/^[[:space:]]*$1[[:space:]]*=//p" | tail -1 | tr -d '[:space:]"'; }
R=$(v panne)
[ -n "$R" ] || { echo "La ligne panne= est vide."; exit 1; }
echo "$R" | grep -qE '^[a-f](,[a-f])*$' || { echo "Écrivez des lettres de a à f séparées par des virgules, par exemple a,c,f."; exit 1; }
L=$(echo "$R" | tr -cd 'a-f' | fold -w1 | sort -u | tr -d '\n')
M=""
case "$L" in *a*) M="$M
- a : un délai plus long garde chaque demande bloquée plus longtemps ; les places du service se remplissent plus vite. C'est la panne en cascade.";; esac
case "$L" in *c*) M="$M
- c : cinq nouvelles tentatives immédiates multiplient par six les appels vers un prestataire déjà saturé.";; esac
case "$L" in *f*) M="$M
- f : dans le monolithe, l'appel au prestataire attend tout autant ; la lenteur bloquerait alors tout le monolithe.";; esac
case "$L" in *b*) ;; *) M="$M
- il manque la mesure qui fait partir les courses sans attendre le prestataire.";; esac
case "$L" in *d*) ;; *) M="$M
- il manque la mesure qui empêche un débit retenté de débiter deux fois.";; esac
case "$L" in *e*) ;; *) M="$M
- il manque la mesure qui laisse le prestataire se remettre au lieu de l'appeler sans arrêt.";; esac
[ -z "$M" ] || { echo "Votre choix ($L) n'est pas encore le bon :$M"; exit 1; }
echo "Asynchrone, idempotent, protégé par un disjoncteur : les courses partent, et personne ne paie deux fois."
```

````solution
```text
panne=b,d,e
```

| Lettre | Verdict |
|---|---|
| a | écarté : plus d'attente, plus de places occupées, panne en cascade plus rapide |
| b | retenu : la course ne dépend plus du prestataire ; le débit attend dans la file |
| c | écarté : multiplie la charge au pire moment |
| d | retenu : un débit retenté avec la même clé est reconnu par le prestataire, et n'est pas exécuté deux fois |
| e | retenu : on cesse d'appeler un prestataire malade, le temps qu'il se remette ; la file garde les débits |
| f | écarté : ne change rien à l'attente, et la propage à tout le monolithe |

Le prix de la mesure **b** : un débit peut échouer après la course. Hopla l'accepte, comme beaucoup de services de ce type : la carte est vérifiée à l'enregistrement, et un débit refusé se traite après coup (nouvelle tentative, autre carte, compte suspendu).
````

## Ce que vous avez construit

| Partie | Base | Reçoit | Publie ou appelle |
|---|---|---|---|
| monolithe modulaire (passagers, chauffeurs, factures, notifications) | relationnelle | REST depuis les applications, l'événement « course terminée » | — |
| courses en direct | clé-valeur en mémoire, plus un historique des courses | REST (demande), positions des chauffeurs | WebSocket vers le passager, gRPC vers la tarification, l'événement « course terminée » |
| tarification | ses règles de prix | gRPC | — |
| paiement | ses débits, avec leur clé d'idempotence | l'événement « course terminée », via sa file | le prestataire, derrière un disjoncteur |

Pour aller plus loin, dessinez ce schéma sur [Excalidraw](https://excalidraw.com/) ou en [Mermaid](https://mermaid.js.org/), avec la passerelle d'API devant les applications. Puis comparez avec un cas réel : [l'architecture micro-services d'Uber (en anglais)](https://www.uber.com/en-FR/blog/microservice-architecture/) et [l'évolution de sa couche d'API, en schémas (ByteByteGo, en anglais)](https://bytebytego.com/guides/evolution-of-ubers-api-layer/). Uber est allé jusqu'à des milliers de services, puis les a regroupés en domaines : la bonne taille d'un service se rediscute avec la croissance.
