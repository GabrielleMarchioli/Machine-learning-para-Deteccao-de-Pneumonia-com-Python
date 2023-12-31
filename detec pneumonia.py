# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KlmtR4j_8dKBFiG5779l6fRuUqYvR_pQ

# Projeto de Aprendizado de Máquina para Detecção de Pneumonia com Python/Machine Learning Project for Pneumonia Detection with Python
## Utilizando a Biblioteca Fastai/Using the Fastai Library


Projeto de Machine Learning para a detecção de pneumonia, utilizando a linguagem de programação Python e a biblioteca Fastai./Machine Learning project for pneumonia detection, using the Python programming language and the Fastai library.
![download](https://github.com/GabrielleMarchioli/Aprendizado-de-M-quina-para-Detec-o-de-Pneumonia-com-Python/assets/109180231/f4fa9413-abc4-44b2-bc1a-549cf195a9a3)
<br>
feito por: Gabrielle Marchioli/
made by: Gabrielle Marchioli

# Bibliotecas usadas/Libraries used:
"""

import pandas as pd
import numpy as np
import os
import keras
import matplotlib.pyplot as plt
from keras.layers import Dense,GlobalAveragePooling2D
from keras.applications import MobileNet
from keras.preprocessing import image
from keras.applications.mobilenet import preprocess_input
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Model
from keras.optimizers import Adam
from google.colab import files

"""#Importando o dataset/Importing the dataset:"""

from google.colab import files

!pip install -U -q kaggle
!mkdir /root/.kaggle

files.upload()
!cp kaggle.json /root/.kaggle
!chmod 600 /root/.kaggle/kaggle.json

!kaggle datasets download -d paultimothymooney/chest-xray-pneumonia

"""#Importing the dataset/Importing the dataset:"""

import os

# instala a ferramenta pv, que é um utilitário para exibir o progresso de dados através de um pipeline./installs the pv tool, which is a utility for displaying data progress through a pipeline.
!apt install pv
!unzip -o /content/chest-xray-pneumonia.zip | pv -l >/dev/null
#O pv -l está sendo usado para exibir o progresso da extração./pv -l is being used to display the extraction progress.
#O >/dev/null redireciona a saída para o null para evitar a exibição na tela./>/dev/null redirects output to null to avoid displaying it on the screen.
os.remove('chest-xray-pneumonia.zip')

"""# Fazendo o Modelo/Make Model:"""

base_model=MobileNet(weights='imagenet',include_top=False) #importa o modelo mobilenet e descarta a última camada de 1.000 neurônios./imports the mobilenet model and discards the last 1000 neuron layer.

x=base_model.output
x=GlobalAveragePooling2D()(x)
x=Dense(1024,activation='relu')(x) #adicionamos camadas densas para que o modelo possa aprender funções mais complexas e classificar para obter melhores resultados./we add dense layers so that the model can learn more complex functions and classify for better results.
x=Dense(1024,activation='relu')(x) #dense layer 2
x=Dense(512,activation='relu')(x) #dense layer 3
preds=Dense(2,activation='softmax')(x) #camada final com ativação softmax./final layer with softmax activation.

#criaçao de um novo modelo combinando a MobileNet com as camadas adicionais./creation of a new model combining MobileNet with additional layers.
model = Model(inputs=base_model.input, outputs=preds)

#congelar as 20 primeiras camadas para não serem treinadas novamente./freeze the first 20 layers so they cannot be trained again.
for layer in model.layers[:20]:
  layer.trainable = False

#Descongelar as camadas apos a vigésima para serem treinadas./Thaw the layers after the twentieth to be trained.
for layer in model.layers[20:]:
  layer.trainable = True

"""#Treinando o modelo/Training the model:"""

train_datagen=ImageDataGenerator(preprocessing_function=preprocess_input)

train_generator = train_datagen.flow_from_directory('/content/chest_xray/test/',
                                                    target_size=(224,224),
                                                    color_mode='rgb',
                                                    batch_size=32,
                                                    class_mode='categorical', shuffle=True)
model.compile(optimizer='Adam',loss='categorical_crossentropy',metrics=['accuracy'])
step_size_train=train_generator.n//train_generator.batch_size
model.fit_generator(generator=train_generator,
                    steps_per_epoch=step_size_train,
                    epochs=5)

#Salvar os pesos/Save the weights:
model.save('chest-xray-pneumonia.h5') #o método save do Keras é usado para salvar todo o modelo, incluindo a arquitetura, configuração e os pesos, em um arquivo H5./The Keras save method is used to save the entire model, including the architecture, configuration and weights, into an H5 file.
!zip -r model.zip 'chest-xray-pneumonia.h5' #compacta o modelo./compact the model.

"""#Implementação/Implementation:"""

from keras.models import load_model
new_model = load_model("/content/chest-xray-pneumonia.h5")

def get_rez(pic):
  img = image.load_img(pic, target_size=(224,224))
  x=image.img_to_array(img)
  x=np.expand_dims(x, axis=0)
  x = preprocess_input(x)
  p_good,p_ill = np.around(new_model.predict(x), decimals=2)[0]
  return{'p_good' :p_good, 'p_ill' :p_ill}

from IPython.display import Image, display
# Carregando a imagem e realizando pré-processamento./Loading the image and performing preprocessing.
def get_rez(pic):
    img = image.load_img(pic, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)

    # Fazendo previsões usando o modelo./Making predictions using the model.
    predictions = new_model.predict(x)
    p_good, p_ill = predictions[0]

     # Retornando um dicionário com as previsões e as probabilidades associadas./Returning a dictionary with the predictions and associated probabilities.
    return {'p_good': p_good, 'p_ill': p_ill, 'probabilities': predictions}

# Diretórios das imagens de teste./Test image directories.
ill_path = "/content/chest_xray/test/PNEUMONIA/"
good_path = "/content/chest_xray/test/NORMAL/"

# Lista das primeiras 5 imagens em cada diretório./List of the first 5 images in each directory.
ill_images = [ill_path + img for img in os.listdir(ill_path)[:5]]
good_images = [good_path + img for img in os.listdir(good_path)[:5]]

# Exibe e analisa as previsões para imagens com pneumonia./Display and analyze predictions for images with pneumonia.
for ill_pic in ill_images:
    display(Image(filename=ill_pic, width=224, height=224))
    predictions = get_rez(ill_pic)
    print(f"Predição para {ill_pic}:")
    print(f" - Pneumonia: {predictions['p_ill']:.2%}")
    print(f" - Normal: {predictions['p_good']:.2%}")
    print("")

# Exibe e analisa as previsões para imagens sem pneumonia./Displays and analyzes predictions for pneumonia-free images.
for good_pic in good_images:
    display(Image(filename=good_pic, width=224, height=224))
    predictions = get_rez(good_pic)
    print(f"Predição para {good_pic}:")
    print(f" - Pneumonia: {predictions['p_ill']:.2%}")
    print(f" - Normal: {predictions['p_good']:.2%}")
    print("")