"""
Módulo responsável pela detecção e avaliação de poses de fisiculturismo
"""
import cv2
import mediapipe as mp
import math


class PoseDetector:
    def __init__(self, static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """Inicializa os módulos do MediaPipe Pose"""
        self.mp_pose = mp.solutions.pose
        # Usa model_complexity=1 (modelo já instalado, evita download)
        # smooth_landmarks=True para suavização (melhor UX)
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=1,  # 1 = médio (modelo já instalado), evita erro de SSL
            smooth_landmarks=True,
            enable_segmentation=False,  # Desabilita segmentação para melhor performance
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils

    @staticmethod
    def calculate_angle(a: list[float], b: list[float], c: list[float]) -> float:
        """Calcula o ângulo formado entre três pontos (por exemplo: ombro, cotovelo e pulso)"""
        ba = [a[0] - b[0], a[1] - b[1]]
        bc = [c[0] - b[0], c[1] - b[1]]
        dot_product = ba[0] * bc[0] + ba[1] * bc[1]
        magnitude_ba = math.sqrt(ba[0]**2 + ba[1]**2)
        magnitude_bc = math.sqrt(bc[0]**2 + bc[1]**2)
        if magnitude_ba == 0 or magnitude_bc == 0:
            return 0
        
        # Normaliza o valor para evitar erro de domínio em math.acos
        cos_angle = dot_product / (magnitude_ba * magnitude_bc)
        cos_angle = max(-1.0, min(1.0, cos_angle))  # Limita entre -1 e 1
        
        angle_radians = math.acos(cos_angle)
        return math.degrees(angle_radians)

    @staticmethod
    def evaluate_double_biceps(left_angle, right_angle, left_elbow_height, right_elbow_height, 
                               left_shoulder_height, right_shoulder_height):
        """Avalia a postura 'duplo bíceps' com base em altura dos cotovelos e ângulo dos braços"""
        errors = []
        if left_elbow_height > left_shoulder_height:
            errors.append("Cotovelo esquerdo muito baixo")
        if right_elbow_height > right_shoulder_height:
            errors.append("Cotovelo direito muito baixo")
        if not 30 <= left_angle <= 80:
            errors.append("Angulo do braco esquerdo fora do intervalo (30-80 graus)")
        if not 30 <= right_angle <= 80:
            errors.append("Angulo do braco direito fora do intervalo (30-80 graus)")
        if errors:
            return "Posicao incorreta - " + "; ".join(errors) + "."
        return "Posicao correta - Excelente postura!"

    @staticmethod
    def evaluate_centered(shoulder_left_x, shoulder_right_x, width):
        """Verifica se o usuário está centralizado horizontalmente na imagem"""
        center_x = width // 2
        body_center_x = (shoulder_left_x + shoulder_right_x) // 2
        offset = abs(center_x - body_center_x)
        threshold = width * 0.1
        if offset < threshold:
            return "Usuario bem centralizado na imagem."
        else:
            return "Centralize-se melhor na camera para avaliacao precisa."

    @staticmethod
    def evaluate_back_double_biceps(left_angle, right_angle, left_elbow_height, right_elbow_height, 
                                     left_shoulder_height, right_shoulder_height, left_shoulder_x, right_shoulder_x,
                                     left_wrist_height, right_wrist_height):
        """Avalia a postura 'duplo bíceps de costas' - cotovelo acima do ombro, ângulo 30-80 graus"""
        errors = []
        
        # Métrica principal: cotovelo acima do ombro
        if left_elbow_height > left_shoulder_height:
            errors.append("Cotovelo esquerdo muito baixo - eleve acima do ombro")
        if right_elbow_height > right_shoulder_height:
            errors.append("Cotovelo direito muito baixo - eleve acima do ombro")
        
        # Métrica principal: braço fazendo ângulo de 30-80 graus
        if not 30 <= left_angle <= 80:
            errors.append("Angulo do braco esquerdo incorreto (30-80 graus)")
        if not 30 <= right_angle <= 80:
            errors.append("Angulo do braco direito incorreto (30-80 graus)")
        
        if errors:
            return "Posicao incorreta - " + "; ".join(errors) + "."
        return "Posicao correta - Excelente duplo biceps de costas!"

    @staticmethod
    def evaluate_side_chest(visible_arm_angle, visible_elbow_height, visible_shoulder_height, 
                            hip_rotation, visible_knee_angle, opposite_arm_angle):
        """Avalia a postura 'side chest' - corpo de lado, braço visível contraído em 75-90 graus"""
        errors = []
        
        # Métrica principal: braço virado para a câmera deve estar contraído em 75-90 graus
        if not 75 <= visible_arm_angle <= 90:
            errors.append("Braco visivel deve estar contraido (75-90 graus)")
        
        if errors:
            return "Posicao incorreta - " + "; ".join(errors) + "."
        return "Posicao correta - Excelente side chest!"

    @staticmethod
    def evaluate_most_muscular(left_arm_angle, right_arm_angle, left_elbow_height, right_elbow_height,
                               left_shoulder_height, right_shoulder_height, shoulder_width, 
                               left_knee_angle, right_knee_angle, torso_alignment,
                               left_wrist_x, right_wrist_x, left_shoulder_x, right_shoulder_x):
        """Avalia a postura 'most muscular' - cotovelos abaixo dos ombros, braços contraídos um contra o outro"""
        errors = []
        
        # Métrica principal: cotovelos devem estar ABAIXO dos ombros
        if left_elbow_height <= left_shoulder_height + 10:
            errors.append("Cotovelo esquerdo deve estar abaixo do ombro")
        if right_elbow_height <= right_shoulder_height + 10:
            errors.append("Cotovelo direito deve estar abaixo do ombro")
        
        # Métrica principal: braços devem estar contraídos um contra o outro
        wrist_distance = abs(left_wrist_x - right_wrist_x)
        shoulder_width_actual = abs(right_shoulder_x - left_shoulder_x)
        
        # Os punhos devem estar próximos (máximo 50% da largura dos ombros)
        if shoulder_width_actual > 0 and wrist_distance > shoulder_width_actual * 0.5:
            errors.append("Bracos devem estar contraidos um contra o outro - aproxime as maos")
        
        if errors:
            return "Posicao incorreta - " + "; ".join(errors) + "."
        return "Posicao correta - Excelente most muscular!"

