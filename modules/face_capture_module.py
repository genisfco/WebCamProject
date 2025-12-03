"""
Módulo de captura de faces refatorado
"""
import cv2
import numpy as np
import os
import re
import time
import winsound
from typing import Optional, Callable, Tuple
from helper_functions import resize_video


class FaceCaptureModule:
    """Módulo para captura de faces via webcam"""
    
    def __init__(self, detector_type: str = "haarcascade", max_width: int = 800):
        """
        Inicializa o módulo de captura
        
        Args:
            detector_type: Tipo de detector ('ssd' ou 'haarcascade')
            max_width: Largura máxima do vídeo
        """
        self.detector_type = detector_type
        self.max_width = max_width
        
        # Carrega detector
        if detector_type == "ssd":
            self.network = cv2.dnn.readNetFromCaffe(
                "deploy.prototxt.txt",
                "res10_300x300_ssd_iter_140000.caffemodel"
            )
            self.face_detector = None
        else:
            self.face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
            self.network = None
        
        self.camera: Optional[cv2.VideoCapture] = None
        self.is_capturing = False
        self.frame_callback: Optional[Callable[[np.ndarray], None]] = None
    
    def set_frame_callback(self, callback: Callable[[np.ndarray], None]):
        """Define callback para frames"""
        self.frame_callback = callback
    
    def parse_name(self, name: str) -> str:
        """Normaliza o nome para uso em arquivos"""
        name = re.sub(r"[^\w\s]", '', name)
        name = re.sub(r"\s+", '_', name)
        return name
    
    def detect_face_haarcascade(self, frame: np.ndarray) -> Tuple[Optional[np.ndarray], np.ndarray]:
        """Detecta face usando Haar Cascade"""
        processed_frame = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(gray, 1.1, 5)
        
        face_roi = None
        for (x, y, w, h) in faces:
            cv2.rectangle(processed_frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
            face_roi = frame[y:y + h, x:x + w]
            face_roi = cv2.resize(face_roi, (140, 140))
        
        return face_roi, processed_frame
    
    def detect_face_ssd(self, frame: np.ndarray) -> Tuple[Optional[np.ndarray], np.ndarray]:
        """Detecta face usando SSD"""
        processed_frame = frame.copy()
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)), 
            1.0,
            (300, 300), 
            (104.0, 117.0, 123.0)
        )
        self.network.setInput(blob)
        detections = self.network.forward()
        
        face_roi = None
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.7:
                bbox = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (start_x, start_y, end_x, end_y) = bbox.astype("int")
                
                if (start_x < 0 or start_y < 0 or end_x > w or end_y > h):
                    continue
                
                face_roi = frame[start_y:end_y, start_x:end_x]
                face_roi = cv2.resize(face_roi, (90, 120))
                
                cv2.rectangle(processed_frame, (start_x, start_y), 
                            (end_x, end_y), (0, 255, 0), 2)
                text_conf = "{:.2f}%".format(confidence * 100)
                cv2.putText(processed_frame, text_conf, (start_x, start_y - 10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return face_roi, processed_frame
    
    def capture_faces(self, person_name: str, output_path: str, 
                     output_path_full: str, max_samples: int = 10,
                     capture_interval: float = 1.0,
                     progress_callback: Optional[Callable[[int, int], None]] = None) -> int:
        """
        Captura faces da webcam
        
        Args:
            person_name: Nome da pessoa (será normalizado)
            output_path: Caminho para salvar faces recortadas
            output_path_full: Caminho para salvar frames completos
            max_samples: Número máximo de amostras
            capture_interval: Intervalo entre capturas (segundos)
            progress_callback: Callback(amostra_atual, total)
        
        Returns:
            Número de amostras capturadas
        """
        person_name = self.parse_name(person_name)
        
        # Cria diretórios
        os.makedirs(output_path, exist_ok=True)
        os.makedirs(output_path_full, exist_ok=True)
        
        self.camera = cv2.VideoCapture(0)
        
        if not self.camera.isOpened():
            raise RuntimeError("Não foi possível abrir a câmera")
        
        self.is_capturing = True
        sample = 0
        last_capture_time = time.time()
        
        try:
            while sample < max_samples and self.is_capturing:
                ret, frame = self.camera.read()
                
                if not ret:
                    continue
                
                # Redimensiona se necessário
                if self.max_width is not None:
                    video_width, video_height = resize_video(
                        frame.shape[1], frame.shape[0], self.max_width
                    )
                    frame = cv2.resize(frame, (video_width, video_height))
                
                # Detecta face
                if self.detector_type == "ssd":
                    face_roi, processed_frame = self.detect_face_ssd(frame)
                else:
                    face_roi, processed_frame = self.detect_face_haarcascade(frame)
                
                # Callback do frame
                if self.frame_callback:
                    self.frame_callback(processed_frame)
                
                # Captura automática
                if face_roi is not None and (time.time() - last_capture_time) >= capture_interval:
                    sample += 1
                    image_name = f"{person_name}.{sample}.jpg"
                    
                    # Garante que os diretórios existem
                    os.makedirs(output_path, exist_ok=True)
                    os.makedirs(output_path_full, exist_ok=True)
                    
                    # Salva as imagens
                    face_path = os.path.join(output_path, image_name)
                    full_path = os.path.join(output_path_full, image_name)
                    
                    success_face = cv2.imwrite(face_path, face_roi)
                    success_full = cv2.imwrite(full_path, frame)
                    
                    if not success_face or not success_full:
                        print(f"⚠ Aviso: Erro ao salvar imagem {image_name}")
                    
                    # REMOVIDO: Beep durante captura (será apenas no final)
                    
                    # Callback de progresso
                    if progress_callback:
                        progress_callback(sample, max_samples)
                    
                    last_capture_time = time.time()
        
        finally:
            self.camera.release()
            self.is_capturing = False
            
            # Beep final quando todas as capturas terminarem
            if sample >= max_samples:
                try:
                    winsound.Beep(1000, 300)  # Beep mais longo e agudo no final
                except Exception:
                    pass
        
        return sample
    
    def stop_capture(self):
        """Para a captura"""
        self.is_capturing = False
        if self.camera:
            self.camera.release()

