# Projet Multi Tool Agent

## Description

Ce projet implémente un système multi-agents utilisant le Google Agent Development Kit (ADK) conçu pour gérer les interactions d'une page Facebook. Un `coordinator_agent` central orchestre plusieurs sous-agents spécialisés pour gérer des tâches telles que l'analyse de la page, la planification de contenu, la création de contenu, la publication de posts, la gestion des commentaires et l'analyse des performances.

Le système utilise les modèles Google Gemini pour ses capacités d'IA et interagit avec l'API Graph de Facebook.

## Structure du Projet

```
multi_tool_agent/
├── .env                  # Variables d'environnement pour les clés API et la configuration
├── agent.py              # Définition de l'agent coordinateur principal
├── config/               # Fichiers de configuration (ex: page_config.yaml)
├── data/                 # Fichiers de données utilisés ou générés par les agents (ex: strategy.json)
├── models/               # Modèles Pydantic pour les structures de données
├── prompt.py             # Configuration du prompt racine (si utilisé)
├── subs_agents/          # Répertoire contenant les sous-agents
│   ├── analytic/         # Agent pour l'analyse des performances
│   ├── marketing/        # Agent pour l'analyse de la page et la définition du persona
│   ├── publisher/        # Agent pour la publication des posts
│   ├── setter/           # Agent pour la gestion des commentaires
│   ├── strategy/         # Agent pour la planification de contenu
│   └── writer/           # Agent pour la création de contenu
├── tools/                # Outils personnalisés utilisés par les agents
├── __init__.py
└── README.md             # Ce fichier
```

## Installation

1.  **Cloner le dépôt (si applicable) :**
    ```bash
    git clone <votre-url-de-depot>
    cd multi_tool_agent
    ```
2.  **Configurer un environnement Python :**
    Il est recommandé d'utiliser un environnement virtuel :
    ```bash
    python -m venv venv
    # Activer l'environnement
    # Windows :
    .\venv\Scripts\activate
    # macOS/Linux :
    source venv/bin/activate
    ```
3.  **Installer les dépendances :**
    *(Hypothèse : Vous avez un fichier requirements.txt. Sinon, vous devrez en créer un basé sur les imports du projet, ex : `google-adk`, `google-generativeai`, `python-dotenv`, etc.)*
    ```bash
    pip install -r requirements.txt
    ```
    *(S'il n'y a pas de `requirements.txt`, vous devrez installer manuellement les paquets nécessaires comme `google-adk`, `python-dotenv`, potentiellement `google-cloud-aiplatform` si vous utilisez Vertex AI, et toutes les bibliothèques utilisées dans votre répertoire `tools/`.)*

## Configuration

1.  **Créez un fichier `.env`** dans le répertoire `multi_tool_agent/` en copiant l'exemple ou en en créant un nouveau.
2.  **Remplissez le fichier `.env`** avec vos identifiants :

    ```dotenv
    # --- Configuration Google Gemini ---
    # Mettre à "True" si vous utilisez Vertex AI, "False" si vous utilisez Google AI Studio
    GOOGLE_GENAI_USE_VERTEXAI="False"

    # Requis si GOOGLE_GENAI_USE_VERTEXAI est "False"
    GOOGLE_API_KEY="VOTRE_CLE_API_GOOGLE_AI_STUDIO"

    # --- Configuration Facebook ---
    FB_PAGE_ID="VOTRE_ID_PAGE_FACEBOOK"
    FB_PAGE_ACCESS_TOKEN="VOTRE_JETON_ACCES_PAGE_FACEBOOK"

    # --- Optionnel : Configuration Vertex AI (seulement si GOOGLE_GENAI_USE_VERTEXAI est "True") ---
    # GOOGLE_CLOUD_PROJECT="votre-id-projet-gcp"
    # GOOGLE_CLOUD_LOCATION="votre-localisation-gcp" # ex: us-central1
    ```

3.  **Configurez `config/page_config.yaml`** (si nécessaire) avec les paramètres spécifiques pour l'analyse de votre page Facebook ou d'autres configurations d'agent.

## Exécution de l'Agent

*(Hypothèse : La principale façon d'exécuter le système d'agents est via le script `agent.py` ou un point d'entrée qui l'utilise. Adaptez la commande si votre projet a un script principal différent.)*

Vous pouvez généralement interagir avec le système d'agents en exécutant le script de l'agent principal. La manière d'interagir peut dépendre de la configuration ADK (par exemple, en utilisant une commande CLI spécifique fournie par ADK ou en exécutant directement le script Python s'il inclut une logique d'interaction).

Exemple (conceptuel - à adapter en fonction de votre méthode d'exécution réelle) :
```bash

adk web agent.py
```

Une fois en cours d'exécution, vous pouvez interagir avec le `coordinator_agent` en utilisant des commandes comme :
*   "lancer l'analyse de la page"
*   "lancer le planning"
*   "les posts à faire pour la journée"
*   "publie mes posts"
*   "gère les commentaires et les posts"
*   "analyse les performances de la semaine"

## Fonctionnalités des Agents

*   **`coordinator_agent`**: L'orchestrateur central. Il reçoit les demandes de l'utilisateur et les délègue au sous-agent approprié.
*   **`marketing_agent`**: Analyse la page Facebook pour déterminer le persona cible.
*   **`strategy_agent`**: Crée un plan/calendrier de contenu hebdomadaire.
*   **`writer_agent`**: Génère le contenu des posts en fonction du calendrier quotidien.
*   **`publisher_agent`**: Publie les posts générés sur la page Facebook.
*   **`setter_agent`**: Gère les commentaires sur les posts Facebook.
*   **`analyst_agent`**: Analyse les métriques de performance hebdomadaires et génère des rapports.
