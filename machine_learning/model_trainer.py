import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
from sklearn.preprocessing import LabelEncoder

class ModelTrainer:
    def __init__(self, config):
        self.config = config
        self.model = RandomForestClassifier(n_estimators=100)
        self.encoders = {}  # Pour stocker les encodeurs de catégories

    def load_data(self, file_path):
        data = pd.read_csv(file_path)
        return data

    def preprocess_data(self, data):
        """Prétraitement des données avant l'entraînement"""
        # 1. Suppression des colonnes non numériques inutiles
        if 'timestamp' in data.columns:
            data = data.drop('timestamp', axis=1)
        
        # 2. Conversion des colonnes catégorielles
        for col in data.select_dtypes(include=['object']).columns:
            if col != 'target':  # Ne pas encoder la cible
                le = LabelEncoder()
                data[col] = le.fit_transform(data[col])
                self.encoders[col] = le  # Sauvegarde l'encodeur
        
        # 3. Vérification de la colonne cible
        if 'target' not in data.columns:
            raise KeyError("Colonne 'target' manquante")
            
        return data

    def train_model(self, data):
        data = self.preprocess_data(data)
        
        X = data.drop('target', axis=1)
        y = data['target']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        print(f"Précision du modèle: {accuracy:.2%}")
        
        # Sauvegarde du modèle et des encodeurs
        model_dir = 'model'
        os.makedirs(model_dir, exist_ok=True)
        
        joblib.dump(self.model, os.path.join(model_dir, 'model.pkl'))
        joblib.dump(self.encoders, os.path.join(model_dir, 'encoders.pkl'))

if __name__ == "__main__":
    config = {}
    trainer = ModelTrainer(config)
    
    try:
        data = trainer.load_data('data/solusdt_historical_data.csv')
        trainer.train_model(data)
    except Exception as e:
        print(f"Erreur: {str(e)}")
        print("Colonnes disponibles:", data.columns.tolist())
        print("3 premières lignes:\n", data.head(3))