#!/usr/bin/env python
# coding: utf-8

import os
import numpy as np
import pandas as pd
from surprise import Reader
from surprise import Dataset
from surprise.model_selection import train_test_split
from surprise import KNNBasic
from surprise import accuracy
import random

if __name__ == "__main__":

	#Carga de los datos
	list_habits=pd.read_csv('/home/lc.ruales/taller1/lastfm-dataset-1K/userid-timestamp-artid-artname-traid-traname.tsv', sep = '\t', names = ['userid', 'timestamp', 'musicbrainz-artist-id', 'artist-name', 'musicbrainz-track-id', 'track-name'] )
	print(list_habits.head(10))

	#Para garantizar reproducibilidad en resultados
	seed = 10
	random.seed(seed)
	np.random.seed(seed)

	#Cantidad de veces que ha escuchado canciones
	t_usuario = list_habits.groupby(['userid'])['track-name'].agg({'count'})
	t_usuario = t_usuario.rename(columns={'count':'canciones_usuario'})

	#Cantidad de veces que ha escuchado a un artista
	t_artista = list_habits.groupby(['userid', 'artist-id'])['track-name'].agg({'count'})
	t_artista = t_artista.rename(columns={'count':'canciones_artista'})

	#Creación de matriz usuario-item-rating
	t_artista.join(t_usuario, how='left', on='userid')
	t_dataset =  t_artista.join(t_usuario, how='left', on='userid')
	t_dataset['rating'] = (t_dataset['canciones_artista'] / t_dataset['canciones_usuario'])*100
	t_dataset.sort_values(by='rating', ascending=False)
	ratings = t_dataset[t_dataset['rating']>=0.5]
	del ratings['canciones_artista']
	del ratings['canciones_usuario']
	ratings = ratings.reset_index()
	ratings.sort_values(by='rating', ascending=True)


	#Creación del dataset de entrenamiento y test a partir del dataframe de ratings
	reader = Reader( rating_scale = ( 0, 100 ) )
	surprise_dataset = Dataset.load_from_df( ratings[ [ 'userid', 'artist-id', 'rating' ] ], reader )
	train_set, test_set =  train_test_split(surprise_dataset, test_size=.2)

	#-------- Modelo usuario-usuario --------

	# se crea un modelo knnbasic usuario-usuario con similitud coseno 
	sim_options = {'name': 'cosine', 'user_based': True}
	algo = KNNBasic(k=25, min_k=2, sim_options=sim_options)
	algo.fit(trainset=train_set)
	test_predictions=algo.test(test_set)
	rmse_coseno_usuarios = accuracy.rmse(test_predictions, verbose = True)

	# se crea un modelo knnbasic usuario-usuario con similitud jaccard 
	sim_options = {'name': 'msd', 'user_based': True} 
	algo = KNNBasic(k=25, min_k=2, sim_options=sim_options)
	algo.fit(trainset=train_set)
	test_predictions=algo.test(test_set)
	rmse_jaccard_usuarios = accuracy.rmse( test_predictions, verbose = True)

	# se crea un modelo knnbasic usuario-usuario con similitud pearson 
	sim_options = {'name': 'pearson', 'user_based': True}
	algo = KNNBasic(k=25, min_k=2, sim_options=sim_options)
	algo.fit(trainset=train_set)
	test_predictions=algo.test(test_set)
	rmse_pearson_usuarios = accuracy.rmse( test_predictions, verbose = True)

	#-------- Modelo item-item --------

	# se crea un modelo knnbasic item-item con similitud coseno 
	sim_options = {'name': 'cosine', 'user_based': False} 
	algo = KNNBasic(k=25, min_k=2, sim_options=sim_options)
	algo.fit(trainset=train_set)
	test_predictions=algo.test(test_set)
	rmse_coseno_items = accuracy.rmse( test_predictions, verbose = True)

	# se crea un modelo knnbasic item-item con similitud jaccard 
	sim_options = {'name': 'msd', 'user_based': False}
	algo = KNNBasic(k=25, min_k=2, sim_options=sim_options)
	algo.fit(trainset=train_set)
	test_predictions=algo.test(test_set)
	rmse_jaccard_items = accuracy.rmse( test_predictions, verbose = True)

	# se crea un modelo knnbasic item-item con similitud pearson 
	sim_options = {'name': 'pearson', 'user_based': False}
	algo = KNNBasic(k=25, min_k=2, sim_options=sim_options)
	algo.fit(trainset=train_set)
	test_predictions=algo.test(test_set)
	rmse_pearson_items = accuracy.rmse( test_predictions, verbose = True)


	#Resultado de medida RMSE
	print("RMSE Filtro basado en usuarios, medida de similitud coseno: " , rmse_coseno_usuarios)
	print("RMSE Filtro basado en usuarios, medida de similitud jaccard: " , rmse_jaccard_usuarios)
	print("RMSE Filtro basado en usuarios, medida de similitud pearson: " , rmse_pearson_usuarios)
	print("RMSE Filtro basado en items, medida de similitud coseno: " , rmse_coseno_items)
	print("RMSE Filtro basado en items, medida de similitud jaccard: " , rmse_jaccard_items)
	print("RMSE Filtro basado en items, medida de similitud pearson: " , rmse_pearson_items)

