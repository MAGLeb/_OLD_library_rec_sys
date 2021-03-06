import os
from typing import List
from datetime import datetime

import pandas as pd

from turicreate import SFrame, load_model
from turicreate.toolkits.recommender.item_similarity_recommender import create

from backend.core.models.model import Model
from backend.utils.utils import NUMBER_ITEMS_TO_RETURN


class ItemSimilarity(Model):
    """
    Find the most similar (the nearest) book to the book for which you want to predict.

    This model first computes the similarity between items using the observations of users who have interacted with
    both items. Given a similarity between item i and j, S(i,j), it scores an item j for user u using a weighted
    average of the user’s previous observations Iu.

    There are three choices of similarity metrics to use: ‘jaccard’, ‘cosine’ and ‘pearson’.

    Jaccard similarity is used to measure the similarity between two set of elements. In the context of
    recommendation, the Jaccard similarity between two items is computed as:

                                                     |U_i ∩ U_j|
                                            JS(i,j)= -----------
                                                     |U_i ∪ U_j|

    Recommendation model imported from Open-Source framework from Apple 'Turicreate'.
    https://github.com/apple/turicreate
    """
    MODEL_PATH = 'data/models/item_similarity/'

    def __init__(self, database):
        super().__init__(self.MODEL_PATH, database)

    def train(self):
        data = self._database.interactions
        data.drop(inplace=True, columns=['dt'], axis=1)
        data = SFrame(data)

        self._model = create(observation_data=data, user_id='user_id', item_id='book_id',
                             verbose=True, seed_item_set_size=0)

    def predict(self, user_id: int, books_ids: list = None, k: int = NUMBER_ITEMS_TO_RETURN) -> List:
        if self._model is None:
            self.load()

        if books_ids is None:
            predictions = self._model.recommend(users=[user_id], k=k, exclude_known=True, random_seed=42)
        else:
            data = self._database.interactions.copy()
            new_observation_data = pd.DataFrame({'book_id': list(map(int, books_ids)),
                                                 'user_id': list([int(user_id)] * len(books_ids)),
                                                 'dt': list([datetime.now().strftime('%Y-%m-%d')] * len(books_ids))})
            data = pd.concat([data, new_observation_data]).reset_index(drop=True)
            data = data.drop(columns=['dt'], axis=1)
            data = SFrame(data)

            model = create(observation_data=data, user_id='user_id', item_id='book_id',
                           verbose=True, seed_item_set_size=0)
            predictions = model.recommend(users=[user_id], k=k, exclude_known=True, random_seed=42)

        return list(predictions['book_id'])[:NUMBER_ITEMS_TO_RETURN]

    def load(self):
        if os.path.exists(self._local_model_path):
            self._model = load_model(self._local_model_path)

    def save(self):
        self._model.save(self._local_model_path)
