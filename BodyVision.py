# Importa bibliotecas essenciais para visão computacional, matemática e tempo
import cv2
import mediapipe as mp
import math
import numpy as np
import time

# Classe responsável por detectar e avaliar poses humanas
class PoseDetector:
    def __init__(self, static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        # Inicializa os módulos do MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=static_image_mode,
                                      min_detection_confidence=min_detection_confidence,
                                      min_tracking_confidence=min_tracking_confidence)
        self.mp_drawing = mp.solutions.drawing_utils

    # Calcula o ângulo formado entre três pontos (por exemplo: ombro, cotovelo e pulso)
    @staticmethod
    def calculate_angle(a: list[float], b: list[float], c: list[float]) -> float:
        ba = [a[0] - b[0], a[1] - b[1]]
        bc = [c[0] - b[0], c[1] - b[1]]
        dot_product = ba[0] * bc[0] + ba[1] * bc[1]
        magnitude_ba = math.sqrt(ba[0]**2 + ba[1]**2)
        magnitude_bc = math.sqrt(bc[0]**2 + bc[1]**2)
        if magnitude_ba == 0 or magnitude_bc == 0:
            return 0
        angle_radians = math.acos(dot_product / (magnitude_ba * magnitude_bc))
        return math.degrees(angle_radians)

    # Avalia a postura "duplo bíceps" com base em altura dos cotovelos e ângulo dos braços
    @staticmethod
    def evaluate_double_biceps(left_angle, right_angle, left_elbow_height, right_elbow_height, left_shoulder_height, right_shoulder_height):
        errors = []
        if left_elbow_height > left_shoulder_height:
            errors.append("Cotovelo esquerdo muito baixo")
        if right_elbow_height > right_shoulder_height:
            errors.append("Cotovelo direito muito baixo")
        if not 45 <= left_angle <= 80:
            errors.append("Angulo do braco esquerdo fora do intervalo (45-80 graus)")
        if not 45 <= right_angle <= 80:
            errors.append("Angulo do braco direito fora do intervalo (45-80 graus)")
        if errors:
            return "Posicao incorreta - " + "; ".join(errors) + "."
        return "Posicao correta - Excelente postura!"

    # Verifica se o usuário está centralizado horizontalmente na imagem
    @staticmethod
    def evaluate_centered(shoulder_left_x, shoulder_right_x, width):
        center_x = width // 2
        body_center_x = (shoulder_left_x + shoulder_right_x) // 2
        offset = abs(center_x - body_center_x)
        threshold = width * 0.1
        if offset < threshold:
            return "Usuario bem centralizado na imagem."
        else:
            return "Centralize-se melhor na camera para avaliacao precisa."

    # Processa um frame individual e aplica a avaliação da pose
    def process_frame(self, frame, pose_mode='double_biceps'):
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)

        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            landmarks = results.pose_landmarks.landmark
            h, w, _ = frame.shape

            def get_pixel_point(landmark):
                return int(landmark.x * w), int(landmark.y * h)

            # Obtém pontos importantes dos dois braços
            points = {}
            for name in ["LEFT_SHOULDER", "LEFT_ELBOW", "LEFT_WRIST", "RIGHT_SHOULDER", "RIGHT_ELBOW", "RIGHT_WRIST"]:
                landmark_enum = getattr(self.mp_pose.PoseLandmark, name)
                points[name] = get_pixel_point(landmarks[landmark_enum.value])

            # Calcula os ângulos dos dois braços
            angle_left = self.calculate_angle(points["LEFT_SHOULDER"], points["LEFT_ELBOW"], points["LEFT_WRIST"])
            angle_right = self.calculate_angle(points["RIGHT_SHOULDER"], points["RIGHT_ELBOW"], points["RIGHT_WRIST"])

            # Avalia a pose de acordo com o modo
            if pose_mode == 'double_biceps':
                pose_quality = self.evaluate_double_biceps(
                    angle_left, angle_right,
                    points["LEFT_ELBOW"][1], points["RIGHT_ELBOW"][1],
                    points["LEFT_SHOULDER"][1], points["RIGHT_SHOULDER"][1]
                )
            elif pose_mode == 'enquadramento':
                pose_quality = self.evaluate_centered(
                    points["LEFT_SHOULDER"][0], points["RIGHT_SHOULDER"][0], w
                )
            else:
                pose_quality = f"Modo '{pose_mode}' ainda nao implementado"

            font = cv2.FONT_HERSHEY_SIMPLEX
            # Aplica cor verde para pose correta, vermelha para incorreta
            text_color = (0, 255, 0) if pose_quality.startswith("Posicao correta") or "centralizado" in pose_quality else (0, 0, 255)

            # Desenha as linhas dos braços e os ângulos
            for side in ["LEFT", "RIGHT"]:
                cv2.line(frame, points[f"{side}_SHOULDER"], points[f"{side}_ELBOW"], (255, 255, 0), 2)
                cv2.line(frame, points[f"{side}_ELBOW"], points[f"{side}_WRIST"], (255, 255, 0), 2)
                angle = angle_left if side == "LEFT" else angle_right
                cv2.putText(frame, f"{int(angle)}°", points[f"{side}_ELBOW"], font, 0.7, (139, 0, 0), 2)

            # Exibe texto centralizado indicando a qualidade da pose
            text_size, _ = cv2.getTextSize(pose_quality, font, 1.2, 2)
            x_center = (w - text_size[0]) // 2
            cv2.putText(frame, f"Qualidade: {pose_quality}", (x_center, 50), font, 1.2, text_color, 3)

        return frame

# Função principal que inicializa a câmera e exibe os resultados em tempo real
def main():
    detector = PoseDetector()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro ao acessar a camera.")
        return

    window_name = 'Pose Detection'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1920, 1080)

    prev_time = time.time()
    pose_mode = 'double_biceps'

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Erro ao capturar frame.")
            break

        frame = cv2.resize(frame, (1920, 1080))
        frame = detector.process_frame(frame, pose_mode)

        # Exibe FPS no canto superior esquerdo
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time
        cv2.putText(frame, f"FPS: {int(fps)}", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Instruções de uso no canto inferior direito
        instruction_text = "Pressione 'Q' para sair | '1': Biceps | '2': Enquadramento"
        text_size, _ = cv2.getTextSize(instruction_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.putText(frame, instruction_text, (1920 - text_size[0] - 30, 1080 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

        # Indica o modo atual no canto superior esquerdo
        cv2.putText(frame, f"Modo: {pose_mode}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 255, 255), 2)

        # Exibe o frame
        cv2.imshow(window_name, frame)

        # Alterna os modos com teclas 1 e 2
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('1'):
            pose_mode = 'double_biceps'
        elif key == ord('2'):
            pose_mode = 'enquadramento'

    cap.release()
    cv2.destroyAllWindows()

# Executa a função principal
if __name__ == "__main__":
    main()
