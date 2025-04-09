# Bot de Trading Haute Fréquence (HFT_OB_BOT)

Ce document décrit l'architecture, les objectifs et la logique du bot de trading haute fréquence (HFT) basé sur l'order book et les déséquilibres. Il est conçu pour exploiter les micromouvements sur les marchés crypto (paire solusdt futures sur binance) en utilisant une stratégie de données d'ordre book et imbalances  , avec une amélioration continue via l'apprentissage machine.

## Objectifs
- **Winrate** : Atteindre un taux de succès (winrate) ≥ 50 % pour garantir une stratégie rentable.
- **Stratégie** : Exploiter les déséquilibres du carnet d'ordres (order book imbalances) pour scalping ou market making adaptatif.
- **Auto-apprentissage** : Utiliser le machine learning pour ajuster dynamiquement les décisions et améliorer les performances au fil du temps.
- **Performance** : Minimiser la latence et maximiser la fiabilité pour répondre aux exigences du trading haute fréquence.

## Logique Générale
1. **Récupération des données** : Les données de l'order book sont récupérées en temps réel ou historiquement via une API (ex. Binance).
2. **Analyse et décision** : Les déséquilibres (bid/ask volume) et les prédictions ML déterminent les actions (achat, vente, hold).
3. **Exécution** : Les ordres sont passés via l'API de l'échange avec une gestion stricte des risques.
4. **Feedback** : Les performances sont enregistrées, et les modèles ML sont retrainés périodiquement pour s'adapter aux conditions de marché.
5. **Validation** : Les stratégies sont testées via backtesting pour confirmer leur rentabilité avant déploiement.

## Architecture du Projet
Le projet est organisé en plusieurs dossiers, chacun avec un rôle spécifique. Voici l'arborescence complète :
hft_ob_bot/
├── core/                        # Logique principale du bot (exécution, gestion, stratégie)
│   ├── main.py                  # Point d'entrée : orchestre les modules
│   ├── ml_strategy.py           # Définit la stratégie basée sur l'order book et ML
│   ├── order_executor.py        # Gère l'exécution des ordres via API
│   ├── risk_manager.py          # Contrôle les risques (ex. limites de perte)
│   └── logger.py                # Enregistre les trades et performances
│
├── machine_learning/            # Modules pour l'apprentissage machine
│   ├── model_trainer.py         # Entraîne les modèles ML
│   ├── model_predictor.py       # Prédit les micromouvements à partir de l'order book
│   ├── auto_retrain.py          # Retraine automatiquement les modèles
│   └── models/                  # Dossier pour stocker les modèles entraînés (ex. rf_model.pkl)
│
├── backtest/                    # Outils pour tester la stratégie
│   ├── backtest_runner.py       # Simule la stratégie sur données historiques
│   ├── metrics.py               # Calcule les métriques (winrate, Sharpe ratio)
│   ├── visualizer.py            # Génère des graphiques de performance
│   └── reports/                 # Dossier pour stocker les rapports de backtesting
│
├── data/                        # Gestion des données brutes et traitées
│   ├── data_fetcher.py          # Récupère les données d'order book
│   ├── data_cleaner.py          # Nettoie et prépare les données pour le ML
│   ├── datasets/                # Dossier pour les données brutes
│   └── features/                # Dossier pour les features extraites
│
├── config/                      # Configurations et paramètres
│   ├── .env                     # Variables d'environnement (ex. clés API)
│   ├── config.py                # Paramètres globaux (ex. seuils d'imbalance)
│
└── requirements.txt             # Dépendances Python nécessaires


### Détails des Dossiers et Fichiers
- **core/** : Contient la logique principale. `main.py` coordonne les appels entre `data_fetcher.py`, `ml_strategy.py`, `order_executor.py`, et `risk_manager.py`. Les logs sont gérés par `logger.py`.
- **machine_learning/** : Gère l'entraînement (`model_trainer.py`), la prédiction (`model_predictor.py`), et le retraining automatique (`auto_retrain.py`) des modèles ML stockés dans `models/`.
- **backtest/** : Permet de tester la stratégie avec `backtest_runner.py`, d’évaluer les performances (`metrics.py`), et de visualiser les résultats (`visualizer.py`).
- **data/** : Récupère (`data_fetcher.py`) et prépare (`data_cleaner.py`) les données, stockées dans `datasets/` et transformées en features dans `features/`.
- **config/** : Centralise les paramètres et les clés API pour une configuration facile.

### Flux de Travail
1. `data_fetcher.py` récupère l'order book → passe à `ml_strategy.py`.
2. `ml_strategy.py` utilise `model_predictor.py` pour analyser et décider → passe à `order_executor.py`.
3. `order_executor.py` exécute les trades si `risk_manager.py` approuve → résultats logués par `logger.py`.
4. `auto_retrain.py` ajuste les modèles en fonction des performances mesurées par `backtest_runner.py`.

### Remarques
- Les chemins relatifs (ex. `machine_learning/models/`) sont utilisés pour stocker les fichiers générés.
- Les agents IA doivent comprendre cette structure pour suggérer des améliorations cohérentes.