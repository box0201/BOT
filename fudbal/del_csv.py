import os
import glob

directory = '/content/'

def delete():
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            os.remove(file_path)
            
def delete_txt():
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            os.remove(file_path)
            
def func():
  lista = []
  for filename in os.listdir(directory):
    if filename.endswith('.csv'):
        file_path = os.path.join(directory, filename)
        lista.append(file_path)
  return lista

delete()