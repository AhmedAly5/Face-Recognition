# -*- coding: utf-8 -*-
"""
Original file is located at
    https://colab.research.google.com/drive/1Psnp1hCeFGCaQ-23pfR1fZVnzDyrNT1U
"""

import os, sys
from os import listdir
from matplotlib import image
import numpy as np
from zipfile import ZipFile
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics
from numpy import linalg
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

import matplotlib.image as mpimg
from google.colab import files
from IPython.display import Image

"""#Data Handling"""

#1) A)


with ZipFile('/content/Dataset.zip', 'r') as zipObj:
   # Extract all the contents of zip file in different directory
   zipObj.extractall('/content/dataset/')

#1) B)

# load all images in a directory
loaded_images = list()

for folder in listdir('/content/dataset/'):
  if folder == '.ipynb_checkpoints':
    pass
  else:
    for k,filename in enumerate(listdir('/content/dataset/'+folder+'/')):
      img_data = image.imread('/content/dataset/'+folder+'/' + filename)
      loaded_images.append(img_data)

#2) A)
vectors = []
for x in range(400):
  vectors.append(loaded_images[x].flatten())

#2) B)
D = np.matrix(vectors).reshape(-1, 10304)
y = []
i = 0
f = 0
while i < 400:
  if i%10==0:
    f+=1
  y.append(f)
  i+=1
print(D.shape)

#3) A & B)

#odd rows for training
x_train = D[::2]
y_train = y[::2]

#even rows for test
x_test = D[1::2]
y_test = y[1::2]

y_train=np.array(y_train)
x_train=np.array(x_train)
x_test=np.array(x_test)
y_test=np.array(y_test)

"""# PCA"""

#Project the training set, and test sets separately using the same projection matrix.
#using a function for reuse
def Proj(projmat,train,test):
    proj_train = np.dot(train, projmat.T)
    proj_test = np.dot(test, projmat.T)
    return proj_train, proj_test

#counting eiganvalues needed
def get_projection_matrix(pca_eganval,pca_eganvec,alpha):
    # total summation for all eigenvalues
    total = sum(pca_eganval)
    current_sum = 0
    i=0
    # to get minimum number of eigenvectors which are good enough 
    for x in range(len(pca_eganval)):
      if current_sum/total < alpha:
        current_sum += pca_eganval[x]
        i += 1
    U = pca_eganvec[:, 0 : i]
    return U.T

#KNN algorithm for first neighbour


def KnnClassifier(k,xtrain,ytrain,xtest,ytest,alpha):
  knn = KNeighborsClassifier(n_neighbors=k)
  modelfit = knn.fit(xtrain, ytrain)
  y_pred = knn.predict(xtest)
  accuracy = metrics.accuracy_score(ytest, y_pred)
  print('For alpha =',alpha,'at K = ',k,'accuracy =',accuracy)
  return accuracy

#4

def PCA(D_train,D_test,ytrain,ytest):
  alpha = np.array([0.8,0.85,0.9,0.95])
  #pca algorithm training set
  mean = np.mean(D_train, axis=0)
  centered_data = D_train - mean
  covmat = (centered_data.T.dot(centered_data))/ len(D_train)
  #Egan values and vectors for training set
  pca_eganval , pca_eganvec = linalg.eigh(covmat)
  #sorting
  index = np.argsort(pca_eganval)[::-1]
  pca_eganval = pca_eganval[index]
  pca_eganvec = pca_eganvec[:,index]
  #All 4 projection matrices for each alpha 
  projMat80 = get_projection_matrix(pca_eganval,pca_eganvec,alpha[0])
  projMat85 = get_projection_matrix(pca_eganval,pca_eganvec,alpha[1])
  projMat90 = get_projection_matrix(pca_eganval,pca_eganvec,alpha[2])
  projMat95 = get_projection_matrix(pca_eganval,pca_eganvec,alpha[3])

  print('Projection matrix shape for 0.8 alpha is ',projMat80.shape)
  print('Projection matrix shape for 0.95 alpha is ',projMat95.shape)

# Projecting the training set, and test sets separately for each alpha

  PJtrain80, PJtest80 = Proj(projMat80, D_train, D_test)
  PJtrain85, PJtest85 = Proj(projMat85, D_train, D_test)
  PJtrain90, PJtest90 = Proj(projMat90, D_train, D_test)
  PJtrain95, PJtest95 = Proj(projMat95, D_train, D_test)
  k = [1,3,5,7] 
  maxaccuracy=0
  print("PCA\n")
  for i in k :
    accuracy = []
    accuracy.append(KnnClassifier(i,PJtrain80, ytrain, PJtest80, ytest, alpha[0]))
    accuracy.append(KnnClassifier(i,PJtrain85, ytrain, PJtest85, ytest, alpha[1]))
    accuracy.append(KnnClassifier(i,PJtrain90, ytrain, PJtest90, ytest, alpha[2]))
    accuracy.append(KnnClassifier(i,PJtrain95, ytrain, PJtest95, ytest, alpha[3]))
    maxaccuracy=max(max(accuracy),maxaccuracy)
    print('\n')
    plt.plot(alpha,accuracy)
  #plotting the relation between alpha and accuracy
  plt.xlabel("alpha")  
  plt.ylabel("accuracy")
  plt.legend(["1","3","5","7"]) 
  plt.show()
  maxalpha=alpha[int(np.argmax(accuracy))]
  return maxaccuracy,maxalpha

maxaccuracy,maxalpha=PCA(x_train,x_test,y_train,y_test)
print (maxaccuracy)

"""# LDA"""

def LDA_KnnClassifier(k,xtrain,ytrain,xtest,ytest):
  knn = KNeighborsClassifier(n_neighbors=k)
  modelfit = knn.fit(xtrain, ytrain)
  y_pred = knn.predict(xtest)
  accuracy = metrics.accuracy_score(ytest, y_pred)
  return accuracy

def LDA(D_train,D_test,ytrain,ytest):
  nk=int(D_train.shape[0]/40)
  Arr=np.zeros((40,nk,10304))
  for i in range (40):
    Arr[i]=D_train[ytrain == i+1]
#LDA algorithm training set
  mean = np.mean(D_train, axis=0)
  meanArr = np.mean(Arr,axis=1)
  meanArr_expanded = np.expand_dims(meanArr, axis=1)
  sb=np.zeros((10304,10304))
  for i in range(40):
    M=meanArr_expanded[i]-mean
    sb+=nk*np.dot(M.T,M)
  Z = Arr - meanArr_expanded
  S = np.empty((10304,10304),float)
  for i in range(40):
    S+=np.dot(Z[i].T,Z[i])
  E_Val,E_Vec=np.linalg.eigh(np.dot(np.linalg.inv(S),(sb)))
  LDA_index=np.argsort(E_Val)[::-1]
  EigenVec = E_Vec[:,LDA_index]
  P=EigenVec[:,:39]
  W_train=np.dot(D_train,P)
  W_test=np.dot(D_test,P)
  k = [1,3,5,7] 
  print("LDA\n")
  accuracy2 = []
  for i in k :
    acc=LDA_KnnClassifier(i,W_train,ytrain,W_test,ytest)
    accuracy2.append(acc)
    print ('at K = ',i,'accuracy =',acc)
    print('\n')
  plt.plot(k,accuracy2)
  plt.xlabel("K")  
  plt.ylabel("accuracy")
  plt.show()
  return accuracy2[0]

accuracy=LDA(x_train,x_test,y_train,y_test)

if accuracy>maxaccuracy:
  print ("LDA is more accurate")
else:
  print ("PDA is more accurate Alpha= " + str(maxalpha))

"""# Bouns"""

xtrain1,xtest1,ytrain1,ytest1 = train_test_split(D,y, test_size=0.3, random_state=42 ,stratify=y)
ytrain1=np.array(ytrain1)
xtrain1=np.array(xtrain1)
xtest1=np.array(xtest1)
ytest1=np.array(ytest1)

PCA(xtrain1,xtest1,ytrain1,ytest1)

LDA(xtrain1,xtest1,ytrain1,ytest1)

"""# Compare faces and non faces

"""

with ZipFile('/content/Nonfaces.zip', 'r') as zipObj:
   zipObj.extractall('/content/dataset2/')

loaded_images2 = list()
for k,filename in enumerate(listdir('/content/dataset2/Nonfaces/')):
  img_data = image.imread('/content/dataset2/Nonfaces/'+ filename)
  loaded_images2.append(img_data)

vectors2 = []
# adding both faces and non faces datasets together
for x in range(400):
  vectors2.append(loaded_images2[x].flatten())
for x in range(400):
  vectors2.append(loaded_images[x].flatten())

D2 = np.matrix(vectors2).reshape(-1, 10304)
y2 = []
i = 0
f = 0
while i < 800:
  if i==400:
    f+=1
  y2.append(f)
  i+=1
Accuracy = []

def showSuccessAndFailure(k,xtrain,ytrain,xtest,ytest,x):
  knn = KNeighborsClassifier(n_neighbors=k)
  modelfit = knn.fit(xtrain, ytrain)
  y_pred = knn.predict(xtest)
  print(y_pred)
  for i in range(len(y_pred)):
    if i <= x :
      if y_pred[i]!= 0 :
           
            imgplot = plt.imshow(loaded_images[i])
            plt.show()
    else :
      if y_pred[i]!= 1 :

            imgplot = plt.imshow(loaded_images2[i-x])
            plt.show()






   

  return 0

def CompareLda(nonfacesnumber):
  
  x_train2=np.concatenate((D2[0:nonfacesnumber],D2[400:600]))
  y_train2=y2[0:nonfacesnumber] + y2[400:600]
  x_test2 =np.concatenate( (D2[nonfacesnumber:400],D2[600:800]))
  y_test2 = y2[nonfacesnumber:400] +y2[600:800]


  x_train2_nonface= D2[0:nonfacesnumber]
  x_train2_face=D2[400:600]

  mean_nonface = np.mean(x_train2_nonface, axis=0)
  mean_face = np.mean(x_train2_face,axis=0)

  B = np.dot((mean_face-mean_nonface).T,(mean_face-mean_nonface))

  Z1 = x_train2_nonface - mean_nonface
  Z2 = x_train2_face - mean_face

  S1 = np.dot(Z1.T,Z1)
  S2 = np.dot(Z2.T,Z2)
  S = S1+S2

  E_Val,E_Vec=np.linalg.eigh(np.dot(np.linalg.inv(S),(B)))

  index=np.argsort(E_Val)[::-1]
  EigenVal = E_Val[index]
  EigenVec = E_Vec[:,index]
  np.abs(EigenVal)
  P=EigenVec[:,:120]
  W_train2=np.dot(x_train2,P)
  W_test2=np.dot(x_test2,P)


  accuracy = (LDA_KnnClassifier(1,W_train2,y_train2,W_test2,y_test2))
  print(accuracy)

  return W_train2,y_train2,W_test2,y_test2

W_train2,y_train2,W_test2,y_test2 =CompareLda(150)

showSuccessAndFailure(1,W_train2,y_train2,W_test2,y_test2,400-150)

Accuracyout = [0.92222 ,0.92307 ,0.942 ,0.95, 0.968, 0.9675, 0.9675, 0.9657 ,0.9657 ,0.9696, 0.96666 ,0.971 ,0.968]
nonfacesused = [60 ,80 ,100 ,120 ,150 ,170 ,200 ,220 ,250 ,270 ,300 ,320 ,350]

plt.plot(nonfacesused,Accuracyout)
plt.xlabel("NonFacesNumbers")  
plt.ylabel("Accuracy")
plt.show()
