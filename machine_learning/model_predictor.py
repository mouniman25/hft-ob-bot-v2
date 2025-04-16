import torch
import torch.nn as nn
import torch.optim as optim
import os
import numpy as np

class MLPredictor(nn.Module):
    def __init__(self):
        super().__init__()
        self.model_path = "machine_learning/models/hft_model.pth"
        self.model = self.load_or_create_model()
        
        # Configuration de l'optimiseur et de la fonction de perte
        self.optimizer = optim.Adam(self.model.parameters())
        self.criterion = nn.BCELoss()  # Binary Cross Entropy Loss

    def load_or_create_model(self):
        model = self._create_model_architecture()
        if os.path.exists(self.model_path):
            try:
                model.load_state_dict(torch.load(self.model_path))
                model.eval()
                print("Modèle chargé depuis", self.model_path)
            except:
                print("Erreur lors du chargement, création d'un nouveau modèle")
                model = self._create_model_architecture()
        return model

    def _create_model_architecture(self):
        return nn.Sequential(
            nn.Linear(4, 64),    # input_shape=(4,) devient nn.Linear(4, 64)
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    async def predict(self, features):
        # Convertir les features en tensor
        if isinstance(features, np.ndarray):
            features = torch.from_numpy(features).float()
        elif not isinstance(features, torch.Tensor):
            features = torch.tensor(features, dtype=torch.float)
            
        with torch.no_grad():
            prediction = self.model(features)
        return prediction.item()

    def save_model(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        torch.save(self.model.state_dict(), self.model_path)
        print("Modèle sauvegardé dans", self.model_path)