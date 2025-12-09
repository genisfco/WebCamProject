"""
Módulo de reconhecimento facial refatorado com integração ao banco de dados
"""
import cv2
import numpy as np
import pickle
import threading
import time
import os
from typing import Optional, Callable, Dict
from database.db_manager import DatabaseManager
from utils.permissions import PermissionChecker
from utils.notifications import NotificationManager
from helper_functions import resize_video


class FaceRecognitionModule:
    """Módulo de reconhecimento facial com integração ao banco de dados"""
    
    def __init__(self, db_manager: DatabaseManager, 
                 recognizer_type: str = "lbph",
                 threshold: float = 10e5,
                 max_width: int = 800):
        """
        Inicializa o módulo de reconhecimento
        
        Args:
            db_manager: Gerenciador do banco de dados
            recognizer_type: Tipo de reconhecedor ('eigenfaces', 'fisherfaces', 'lbph')
            threshold: Threshold de confiança (10e5 = sempre retorna predição)
            max_width: Largura máxima do vídeo
        """
        self.db_manager = db_manager
        self.permission_checker = PermissionChecker(db_manager)
        self.notification_manager = NotificationManager()
        
        self.recognizer_type = recognizer_type
        self.threshold = threshold
        self.max_width = max_width
        
        # Carrega o reconhecedor
        self.face_classifier = self._load_recognizer(recognizer_type)
        
        # Carrega mapeamento de nomes
        self.face_names = self._load_face_names()
        
        # Carrega detector SSD
        self.network = cv2.dnn.readNetFromCaffe(
            "deploy.prototxt.txt",
            "res10_300x300_ssd_iter_140000.caffemodel"
        )
        
        # Estado do reconhecimento
        self.is_running = False
        self.video_thread: Optional[threading.Thread] = None
        self.camera: Optional[cv2.VideoCapture] = None
        
        # Callbacks
        self.frame_callback: Optional[Callable[[np.ndarray], None]] = None
        self.access_callback: Optional[Callable[[Dict], None]] = None
        
        # Controle de rate limiting para evitar spam de notificações
        self.last_recognition_time = {}
        self.recognition_cooldown = 5.0  # segundos entre reconhecimentos do mesmo usuário
    
    def _load_recognizer(self, option: str):
        """Carrega o reconhecedor facial"""
        training_files = {
            "eigenfaces": "eigen_classifier.yml",
            "fisherfaces": "fisher_classifier.yml",
            "lbph": "lbph_classifier.yml"
        }
        
        training_data = training_files.get(option, "lbph_classifier.yml")
        
        if option == "eigenfaces":
            face_classifier = cv2.face.EigenFaceRecognizer_create()
        elif option == "fisherfaces":
            face_classifier = cv2.face.FisherFaceRecognizer_create()
        elif option == "lbph":
            face_classifier = cv2.face.LBPHFaceRecognizer_create()
        else:
            raise ValueError(f"Algoritmo inválido: {option}")
        
        # Verifica se o arquivo existe antes de tentar ler
        if os.path.exists(training_data):
            try:
                face_classifier.read(training_data)
            except Exception as e:
                print(f"⚠ Aviso: Erro ao carregar {training_data}: {e}")
                print("⚠ O classificador será inicializado vazio. Treine novos usuários para usar o reconhecimento.")
        else:
            print(f"⚠ Arquivo {training_data} não encontrado.")
            print("⚠ O classificador será inicializado vazio. Cadastre e treine usuários para usar o reconhecimento.")
        
        return face_classifier
    
    def _load_face_names(self) -> Dict[int, str]:
        """Carrega o mapeamento de IDs para nomes"""
        try:
            with open("face_names.pickle", "rb") as f:
                original_labels = pickle.load(f)
                # Inverte chave e valor para acesso por ID
                return {v: k for k, v in original_labels.items()}
        except FileNotFoundError:
            return {}
    
    def set_frame_callback(self, callback: Callable[[np.ndarray], None]):
        """Define callback para frames processados"""
        self.frame_callback = callback
    
    def set_access_callback(self, callback: Callable[[Dict], None]):
        """Define callback para eventos de acesso"""
        self.access_callback = callback
    
    def set_log_callback(self, callback: Callable[[str], None]):
        """Define callback para logs"""
        self.notification_manager.set_log_callback(callback)
    
    def recognize_faces(self, frame: np.ndarray) -> np.ndarray:
        """
        Reconhece faces em um frame
        
        Args:
            frame: Frame de vídeo
        
        Returns:
            Frame processado com anotações
        """
        processed_frame = frame.copy()
        
        # Desenha notificação visual ativa se houver
        self.notification_manager.draw_active_notification(processed_frame)
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        (h, w) = frame.shape[:2]
        
        # Detecta faces usando SSD
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)), 
            1.0, 
            (300, 300), 
            (104.0, 117.0, 123.0)
        )
        self.network.setInput(blob)
        detections = self.network.forward()
        
        face_detected = False
        
        # Verifica se há faces cadastradas para reconhecer
        if not self.face_names:
            # Sem faces cadastradas, apenas detecta mas não reconhece
            for i in range(0, detections.shape[2]):
                confidence_detection = detections[0, 0, i, 2]
                
                if confidence_detection > 0.7:
                    # Rate limiting para notificação
                    current_time = time.time()
                    if 'nenhum_usuario' not in self.last_recognition_time:
                        self.last_recognition_time['nenhum_usuario'] = 0
                    
                    if current_time - self.last_recognition_time['nenhum_usuario'] >= self.recognition_cooldown:
                        self.notification_manager.nenhum_usuario_cadastrado()
                        self.last_recognition_time['nenhum_usuario'] = current_time
                    break  # Apenas uma notificação por frame
            return processed_frame
        
        for i in range(0, detections.shape[2]):
            confidence_detection = detections[0, 0, i, 2]
            
            if confidence_detection > 0.7:  # Threshold de detecção
                bbox = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (start_x, start_y, end_x, end_y) = bbox.astype("int")
                
                # Validação de limites
                if (start_x < 0 or start_y < 0 or end_x > w or end_y > h):
                    continue
                
                face_detected = True
                
                # Extrai ROI da face
                face_roi = gray[start_y:end_y, start_x:end_x]
                face_roi = cv2.resize(face_roi, (90, 120))
                
                # Reconhece a face
                try:
                    prediction, conf = self.face_classifier.predict(face_roi)
                    
                    # Processa reconhecimento
                    if conf <= self.threshold and prediction in self.face_names:
                        nome_face = self.face_names[prediction]
                        self._process_recognition(nome_face, conf, prediction, 
                                                start_x, start_y, end_x, end_y, processed_frame)
                    # Face não identificada - não desenha nada, apenas processa silenciosamente
                except Exception as e:
                    # Erro ao reconhecer (classificador vazio ou corrompido) - não desenha nada
                    pass
        
        if not face_detected:
            # Nenhuma face detectada
            pass
        
        return processed_frame
    
    def _process_recognition(self, nome_face: str, conf: float, face_id: int,
                           start_x: int, start_y: int, end_x: int, end_y: int,
                           frame: np.ndarray):
        """
        Processa um reconhecimento de face
        
        Args:
            nome_face: Nome da face reconhecida
            conf: Nível de confiança
            face_id: ID da face
            start_x, start_y, end_x, end_y: Coordenadas do bounding box
            frame: Frame para desenhar
        """
        # Rate limiting - evita spam de notificações
        current_time = time.time()
        if nome_face in self.last_recognition_time:
            if current_time - self.last_recognition_time[nome_face] < self.recognition_cooldown:
                # Ainda em cooldown, não faz nada (não desenha nada)
                return
        
        self.last_recognition_time[nome_face] = current_time
        
        # Busca usuário no banco de dados
        usuario = self.db_manager.buscar_usuario_por_face_id(face_id)
        
        if not usuario:
            # Face reconhecida mas não cadastrada no banco
            self.notification_manager.acesso_negado("Usuário não cadastrado no sistema", nome_face)
            self.db_manager.registrar_acesso(None, "entrada", "negado", conf, 
                                            "Usuário não cadastrado no sistema")
            return
        
        usuario_id = usuario['id']
        
        # Verifica permissões
        permitido, motivo = self.permission_checker.verificar_acesso(usuario_id)
        
        if permitido:
            # Acesso liberado - apenas notificação visual, sem desenhar ao redor do rosto
            self.notification_manager.acesso_liberado(usuario['nome'], conf)
            self.db_manager.registrar_acesso(usuario_id, "entrada", "liberado", conf)
            
            # Callback de acesso
            if self.access_callback:
                self.access_callback({
                    'usuario_id': usuario_id,
                    'nome': usuario['nome'],
                    'numero_identificacao': usuario.get('numero_identificacao', usuario.get('ra', '')),
                    'tipo_identificacao': usuario.get('tipo_identificacao', 'RA'),
                    'status': 'liberado',
                    'confianca': conf
                })
        else:
            # Acesso negado - apenas notificação visual, sem desenhar ao redor do rosto
            self.notification_manager.acesso_negado(motivo, usuario['nome'])
            self.db_manager.registrar_acesso(usuario_id, "entrada", "negado", conf, motivo)
            
            # Callback de acesso
            if self.access_callback:
                self.access_callback({
                    'usuario_id': usuario_id,
                    'nome': usuario['nome'],
                    'numero_identificacao': usuario.get('numero_identificacao', usuario.get('ra', '')),
                    'tipo_identificacao': usuario.get('tipo_identificacao', 'RA'),
                    'status': 'negado',
                    'confianca': conf,
                    'motivo': motivo
                })
    
    def _video_loop(self):
        """Loop principal de processamento de vídeo (executa em thread separada)"""
        self.camera = cv2.VideoCapture(0)
        
        if not self.camera.isOpened():
            self.notification_manager.erro_reconhecimento("Não foi possível abrir a câmera")
            self.is_running = False
            return
        
        while self.is_running:
            ret, frame = self.camera.read()
            
            if not ret:
                continue
            
            # Redimensiona se necessário
            if self.max_width is not None:
                video_width, video_height = resize_video(
                    frame.shape[1], frame.shape[0], self.max_width
                )
                frame = cv2.resize(frame, (video_width, video_height))
            
            # Processa reconhecimento
            processed_frame = self.recognize_faces(frame)
            
            # Callback do frame processado
            if self.frame_callback:
                self.frame_callback(processed_frame)
        
        # Libera a câmera
        if self.camera:
            self.camera.release()
    
    def start_recognition(self):
        """Inicia o reconhecimento facial"""
        if self.is_running:
            return
        
        self.is_running = True
        self.video_thread = threading.Thread(target=self._video_loop, daemon=True)
        self.video_thread.start()
        self.notification_manager.info("Reconhecimento facial iniciado")
    
    def stop_recognition(self):
        """Para o reconhecimento facial"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.video_thread:
            self.video_thread.join(timeout=2.0)
        
        self.notification_manager.info("Reconhecimento facial parado")
    
    def reload_recognizer(self):
        """Recarrega o reconhecedor e o mapeamento de nomes"""
        try:
            self.face_classifier = self._load_recognizer(self.recognizer_type)
            self.face_names = self._load_face_names()
            self.notification_manager.info("Reconhecedor recarregado")
        except Exception as e:
            print(f"⚠ Erro ao recarregar reconhecedor: {e}")
            self.notification_manager.info("Reconhecedor não pôde ser recarregado. Treine novos usuários.")

