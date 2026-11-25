# courses-software-architecture

Les contenus byte_layers sur l'architecture logicielle et le system design, pour qui connaît déjà le client-serveur et le trois tiers ([Les architectures d'un programme](https://byte-layers.com/fr/bits/program-architectures)). Un dossier par contenu, à plat, chacun avec son `.layers/`. Chaque bit se lit seul : il pose son propre exemple et ne cite que ses prérequis.

| Dossier | Contenu | Type |
|---|---|---|
| `tiers-layers-mvc/` | Tiers, couches et MVC : trois notions à ne pas mélanger | bit |
| `scaling-load-balancing/` | Tenir la charge : vertical, horizontal, répartiteur et services sans état | bit, playground |
| `monolith-to-microservices/` | Monolithe, monolithe modulaire, micro-services : ce qui se déploie ensemble | bit |

Chaque contenu a son tag, de la forme `<dossier>/vN`. Les bits avec un playground (étape `sim`) demandent l'extension 0.11.0 ; les autres, 0.8.0.

## Régénérer un schéma animé

Les fichiers `.layers/assets/*.scene.json` sont écrits par des scripts Python, rangés dans le dossier `scenes/` du contenu (hors de `.layers/`, donc non publiés). On corrige le script, jamais le JSON à la main, puis on le relance depuis la racine du dépôt, par exemple `python3 tiers-layers-mvc/scenes/tlm.py`. Les scripts importent `tools/scenes/scene_kit.py` (copie du kit de la skill byte-layers-scenes) et `tools/scenes/paths.py` ; avec `BL_SCENES` pointant sur `packages/scenes` d'un worktree du monorepo, la scène est aussi écrite dans `lessons/zz-<id>/` pour la valider et la capturer.

Licence : CC BY-NC-SA 4.0.
