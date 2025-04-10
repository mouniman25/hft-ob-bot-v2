import torch
import numpy as np
import os

class MLPredictor:
    def __init__(self):
        self.model_path = "machine_learning/models/hft_model"
        self.model = self.load_or_create_model()

    def load_or_create_model(self):
        if os.path.exists(self.model_path):
            return tf.keras.models.load_model(self.model_path)
        return self.create_new_model()

    def create_new_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(4,)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy')
        return model

    async def predict(self, features):
        return float(self.model.predict(features)[0][0])

    def save_model(self):
        self.model.save(self.model_path)