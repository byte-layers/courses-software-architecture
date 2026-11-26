# courses-software-architecture

Les contenus byte_layers sur l'architecture logicielle et le system design, pour qui connaît déjà le client-serveur et le trois tiers ([Les architectures d'un programme](https://byte-layers.com/fr/bits/program-architectures)). Un dossier par contenu, à plat, chacun avec son `.layers/`. Chaque bit se lit seul : il pose son propre exemple et ne cite que ses prérequis.

| Dossier | Contenu | Type |
|---|---|---|
| `tiers-layers-mvc/` | Tiers, couches et MVC : trois notions à ne pas mélanger | bit |
| `hexagonal-architecture/` | L'architecture hexagonale : ports, adaptateurs, et la règle de dépendance | bit |
| `monolith-to-microservices/` | Monolithe, monolithe modulaire, micro-services : ce qui se déploie ensemble | bit |
| `microservices-costs/` | Le prix des micro-services : réseau, déploiements, observabilité | bit |
| `api-gateway-bff-microfrontends/` | Passerelle d'API, BFF et micro-frontends | bit |
| `sync-async-communication/` | Synchrone ou asynchrone : attendre la réponse, ou non | bit, playground |
| `communication-protocols/` | Les protocoles entre programmes : de TCP à gRPC | bit |
| `queues-and-event-logs/` | Files de messages et journaux d'événements | bit, playground |
| `event-driven-cqrs/` | Architecture orientée événements et CQRS | bit |
| `scaling-load-balancing/` | Tenir la charge : vertical, horizontal, répartiteur et services sans état | bit, playground |
| `cache-and-cdn/` | Répondre plus vite : cache et CDN | bit |
| `replication-sharding-cap/` | Réplication, partitionnement et théorème CAP | bit |
| `high-availability/` | Rester en service : SPOF, redondance, bascule | bit |
| `architecture-case-studies/` | Six organisations, six architectures | bit |

Quatre familles, lisibles dans cet ordre : organiser le code (les deux premiers), découper en services (les trois suivants), faire communiquer les programmes (quatre), tenir la charge et rester en service (quatre), puis les cas d'organisations. Chaque contenu a son tag, de la forme `<dossier>/vN`. Les bits avec un playground demandent l'extension 0.11.0 (`scaling-load-balancing`) ou 0.12.0 (`sync-async-communication`, `queues-and-event-logs`) ; les autres, 0.8.0.

## Régénérer un schéma animé

Les fichiers `.layers/assets/*.scene.json` sont écrits par des scripts Python, rangés dans le dossier `scenes/` du contenu (hors de `.layers/`, donc non publiés). On corrige le script, jamais le JSON à la main, puis on le relance depuis la racine du dépôt, par exemple `python3 tiers-layers-mvc/scenes/tlm.py`. Les scripts importent `tools/scenes/scene_kit.py` (copie du kit de la skill byte-layers-scenes) et `tools/scenes/paths.py` ; avec `BL_SCENES` pointant sur `packages/scenes` d'un worktree du monorepo, la scène est aussi écrite dans `lessons/zz-<id>/` pour la valider et la capturer.

Licence : CC BY-NC-SA 4.0.
