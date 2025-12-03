"""
Módulo de treinamento de reconhecedores faciais
"""
import cv2
import numpy as np
import os
import pickle
from PIL import Image
from typing import Dict, Tuple


class TrainingModule:
    """Módulo para treinamento de reconhecedores faciais"""
    
    def __init__(self, training_path: str = 'dataset/'):
        """
        Inicializa o módulo de treinamento
        
        Args:
            training_path: Caminho para o dataset de treinamento
        """
        self.training_path = training_path
    
    def get_image_data(self, path_train: str) -> Tuple[np.ndarray, list, Dict[str, int]]:
        """
        Carrega dados de imagens do dataset
        
        Returns:
            Tupla (ids, faces, face_names)
        """
        subdirs = [os.path.join(path_train, f) for f in os.listdir(path_train) 
                   if os.path.isdir(os.path.join(path_train, f))]
        
        faces = []
        ids = []
        face_names = {}
        id_counter = 1
        
        print("Carregando faces do dataset...")
        
        for subdir in subdirs:
            name = os.path.split(subdir)[1]
            
            images_list = [os.path.join(subdir, f) for f in os.listdir(subdir)
                          if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            for path in images_list:
                try:
                    image = Image.open(path).convert('L')
                    face = np.array(image, 'uint8')
                    face = cv2.resize(face, (90, 120))
                    
                    ids.append(id_counter)
                    faces.append(face)
                    print(f"{id_counter} <-- {path}")
                except Exception as e:
                    print(f"Erro ao processar {path}: {e}")
                    continue
            
            if name not in face_names and images_list:
                face_names[name] = id_counter
                id_counter += 1
        
        return np.array(ids), faces, face_names
    
    def train_all_recognizers(self, show_progress: bool = False) -> Dict[str, bool]:
        """
        Treina todos os reconhecedores
        
        Args:
            show_progress: Se True, mostra progresso visual
        
        Returns:
            Dicionário com status de treinamento de cada reconhecedor
        """
        if not os.path.exists(self.training_path):
            raise FileNotFoundError(f"Diretório de treinamento não encontrado: {self.training_path}")
        
        ids, faces, face_names = self.get_image_data(self.training_path)
        
        if len(faces) == 0:
            raise ValueError("Nenhuma face encontrada no dataset")
        
        print(f"\nTotal de faces: {len(faces)}")
        print(f"Total de pessoas: {len(face_names)}")
        
        # Salva mapeamento de nomes
        with open("face_names.pickle", "wb") as f:
            pickle.dump(face_names, f)
        
        results = {}
        
        # Treina Eigenfaces
        try:
            print('\nTreinando reconhecedor Eigenface...')
            eigen_classifier = cv2.face.EigenFaceRecognizer_create()
            eigen_classifier.train(faces, ids)
            eigen_classifier.write('eigen_classifier.yml')
            results['eigenfaces'] = True
            print('... Concluído!\n')
        except Exception as e:
            print(f'Erro ao treinar Eigenface: {e}\n')
            results['eigenfaces'] = False
        
        # Treina Fisherfaces
        try:
            # Fisherface requer pelo menos 2 classes (pessoas diferentes)
            num_pessoas = len(face_names)
            if num_pessoas < 2:
                print('Treinando reconhecedor Fisherface...')
                print(f'⚠ Aviso: Fisherface requer pelo menos 2 pessoas cadastradas.')
                print(f'⚠ Atualmente há apenas {num_pessoas} pessoa(s). Pulando treinamento do Fisherface.\n')
                results['fisherfaces'] = False
            else:
                print('Treinando reconhecedor Fisherface...')
                fisher_classifier = cv2.face.FisherFaceRecognizer_create()
                fisher_classifier.train(faces, ids)
                fisher_classifier.write('fisher_classifier.yml')
                results['fisherfaces'] = True
                print('... Concluído!\n')
        except Exception as e:
            print(f'Erro ao treinar Fisherface: {e}\n')
            results['fisherfaces'] = False
        
        # Treina LBPH
        try:
            print('Treinando reconhecedor LBPH...')
            lbph_classifier = cv2.face.LBPHFaceRecognizer_create()
            lbph_classifier.train(faces, ids)
            lbph_classifier.write('lbph_classifier.yml')
            results['lbph'] = True
            print('... Concluído!\n')
        except Exception as e:
            print(f'Erro ao treinar LBPH: {e}\n')
            results['lbph'] = False
        
        return results
    
    def get_face_names(self) -> Dict[str, int]:
        """Carrega o mapeamento de nomes do arquivo pickle"""
        try:
            with open("face_names.pickle", "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {}

