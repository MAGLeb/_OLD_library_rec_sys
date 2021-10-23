from typing import List

from turicreate.data_structures.sframe import SFrame

from backend.models.model import Model
from backend.database import Database


class Random(Model):
    """
    Recommendation model. Random predictions.
    """
    MODEL_PATH = 'random/'

    def __init__(self):
        self.db = Database()
        super().__init__(self.MODEL_PATH)

    def train(self, item_data: SFrame):
        pass

    def predict(self, user_id: int) -> List:
        predictions = self.db.random_books_ids()
        return predictions

    def load(self):
        pass

    def save(self):
        pass