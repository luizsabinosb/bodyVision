"""
BodyVision - Sistema de Análise de Poses de Fisiculturismo
Arquivo principal do programa
"""
import cv2
import time
import numpy as np
from pose_evaluator import PoseDetector
from camera_utils import find_camera
from ui_renderer import (render_feedback_panel, render_info_panel, render_instructions_panel, 
                         render_pose_skeleton, render_sidebar_menu)


class BodyVisionApp:
    """Classe principal da aplicação BodyVision"""
    
    MODE_NAMES = {
        'double_biceps': 'Duplo Biceps (Frente)',
        'back_double_biceps': 'Duplo Biceps de Costas',
        'side_chest': 'Side Chest',
        'most_muscular': 'Most Muscular',
        'enquadramento': 'Enquadramento'
    }
    
    def __init__(self):
        """Inicializa a aplicação"""
        self.detector = PoseDetector()
        self.pose_mode = 'enquadramento'
        self.window_name = 'BodyVision - Detecção de Poses'
        self.cap = None
        # Valores serão ajustados dinamicamente baseados na resolução real
        self.camera_width = None
        self.camera_height = None
        self.sidebar_width_ratio = 0.24  # 24% da largura total para o menu
        self.sidebar_width = None
        self.total_width = None
        
    def process_frame(self, frame, pose_mode, camera_width):
        """Processa um frame e retorna o frame anotado e qualidade da pose"""
        pose_quality = None
        # MediaPipe espera RGB, mas podemos passar BGR direto em algumas versões
        # Para garantir compatibilidade, converte apenas uma vez
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.detector.pose.process(image_rgb)
        
        # Libera referência para ajudar GC
        del image_rgb

        if results.pose_landmarks:
            # Desenha landmarks de forma mais leve (sem preenchimento de conexões)
            self.detector.mp_drawing.draw_landmarks(
                frame, 
                results.pose_landmarks, 
                self.detector.mp_pose.POSE_CONNECTIONS,
                # Otimizações de desenho para melhor performance
                landmark_drawing_spec=self.detector.mp_drawing.DrawingSpec(
                    color=(0, 255, 0), thickness=2, circle_radius=2
                ),
                connection_drawing_spec=self.detector.mp_drawing.DrawingSpec(
                    color=(255, 255, 255), thickness=2
                )
            )
            landmarks = results.pose_landmarks.landmark
            h, w, _ = frame.shape

            # Obtém pontos importantes do corpo (otimizado - evita múltiplos getattr)
            points = {}
            
            # Cache dos enums para evitar getattr repetido
            landmark_enum = self.detector.mp_pose.PoseLandmark
            
            try:
                points["LEFT_SHOULDER"] = (int(landmarks[landmark_enum.LEFT_SHOULDER.value].x * camera_width), 
                                          int(landmarks[landmark_enum.LEFT_SHOULDER.value].y * h))
                points["LEFT_ELBOW"] = (int(landmarks[landmark_enum.LEFT_ELBOW.value].x * camera_width), 
                                       int(landmarks[landmark_enum.LEFT_ELBOW.value].y * h))
                points["LEFT_WRIST"] = (int(landmarks[landmark_enum.LEFT_WRIST.value].x * camera_width), 
                                       int(landmarks[landmark_enum.LEFT_WRIST.value].y * h))
                points["RIGHT_SHOULDER"] = (int(landmarks[landmark_enum.RIGHT_SHOULDER.value].x * camera_width), 
                                           int(landmarks[landmark_enum.RIGHT_SHOULDER.value].y * h))
                points["RIGHT_ELBOW"] = (int(landmarks[landmark_enum.RIGHT_ELBOW.value].x * camera_width), 
                                        int(landmarks[landmark_enum.RIGHT_ELBOW.value].y * h))
                points["RIGHT_WRIST"] = (int(landmarks[landmark_enum.RIGHT_WRIST.value].x * camera_width), 
                                        int(landmarks[landmark_enum.RIGHT_WRIST.value].y * h))
                points["LEFT_HIP"] = (int(landmarks[landmark_enum.LEFT_HIP.value].x * camera_width), 
                                     int(landmarks[landmark_enum.LEFT_HIP.value].y * h))
                points["RIGHT_HIP"] = (int(landmarks[landmark_enum.RIGHT_HIP.value].x * camera_width), 
                                      int(landmarks[landmark_enum.RIGHT_HIP.value].y * h))
                points["LEFT_KNEE"] = (int(landmarks[landmark_enum.LEFT_KNEE.value].x * camera_width), 
                                      int(landmarks[landmark_enum.LEFT_KNEE.value].y * h))
                points["RIGHT_KNEE"] = (int(landmarks[landmark_enum.RIGHT_KNEE.value].x * camera_width), 
                                       int(landmarks[landmark_enum.RIGHT_KNEE.value].y * h))
                points["LEFT_ANKLE"] = (int(landmarks[landmark_enum.LEFT_ANKLE.value].x * camera_width), 
                                       int(landmarks[landmark_enum.LEFT_ANKLE.value].y * h))
                points["RIGHT_ANKLE"] = (int(landmarks[landmark_enum.RIGHT_ANKLE.value].x * camera_width), 
                                        int(landmarks[landmark_enum.RIGHT_ANKLE.value].y * h))
            except (AttributeError, IndexError, KeyError):
                pass

            # Calcula ângulos
            angle_left = self.detector.calculate_angle(
                points.get("LEFT_SHOULDER", [0, 0]), 
                points.get("LEFT_ELBOW", [0, 0]), 
                points.get("LEFT_WRIST", [0, 0])
            )
            angle_right = self.detector.calculate_angle(
                points.get("RIGHT_SHOULDER", [0, 0]), 
                points.get("RIGHT_ELBOW", [0, 0]), 
                points.get("RIGHT_WRIST", [0, 0])
            )

            angle_left_knee = 0
            angle_right_knee = 0
            if all(key in points for key in ["LEFT_KNEE", "LEFT_HIP", "LEFT_ANKLE"]):
                angle_left_knee = self.detector.calculate_angle(
                    points["LEFT_HIP"], points["LEFT_KNEE"], points["LEFT_ANKLE"]
                )
            if all(key in points for key in ["RIGHT_KNEE", "RIGHT_HIP", "RIGHT_ANKLE"]):
                angle_right_knee = self.detector.calculate_angle(
                    points["RIGHT_HIP"], points["RIGHT_KNEE"], points["RIGHT_ANKLE"]
                )

            # Avalia a pose
            pose_quality = self._evaluate_pose(pose_mode, points, angle_left, angle_right, 
                                               angle_left_knee, angle_right_knee, camera_width)

            # Renderiza esqueleto da pose
            render_pose_skeleton(frame, points, angle_left, angle_right, 
                               angle_left_knee, angle_right_knee, pose_mode)

        return frame, pose_quality

    def _evaluate_pose(self, pose_mode, points, angle_left, angle_right, 
                      angle_left_knee, angle_right_knee, camera_width):
        """Avalia a pose de acordo com o modo selecionado"""
        if pose_mode == 'double_biceps':
            if all(key in points for key in ["LEFT_ELBOW", "RIGHT_ELBOW", "LEFT_SHOULDER", "RIGHT_SHOULDER"]):
                return self.detector.evaluate_double_biceps(
                    angle_left, angle_right,
                    points["LEFT_ELBOW"][1], points["RIGHT_ELBOW"][1],
                    points["LEFT_SHOULDER"][1], points["RIGHT_SHOULDER"][1]
                )
            return "Nao foi possivel detectar os pontos necessarios"
            
        elif pose_mode == 'back_double_biceps':
            if all(key in points for key in ["LEFT_ELBOW", "RIGHT_ELBOW", "LEFT_SHOULDER", 
                                             "RIGHT_SHOULDER", "LEFT_WRIST", "RIGHT_WRIST"]):
                return self.detector.evaluate_back_double_biceps(
                    angle_left, angle_right,
                    points["LEFT_ELBOW"][1], points["RIGHT_ELBOW"][1],
                    points["LEFT_SHOULDER"][1], points["RIGHT_SHOULDER"][1],
                    points["LEFT_SHOULDER"][0], points["RIGHT_SHOULDER"][0],
                    points["LEFT_WRIST"][1], points["RIGHT_WRIST"][1]
                )
            return "Nao foi possivel detectar os pontos necessarios"
            
        elif pose_mode == 'side_chest':
            if "LEFT_SHOULDER" not in points or "RIGHT_SHOULDER" not in points:
                return "Nao foi possivel detectar os ombros"
            
            # Determina qual lado está mais visível
            shoulder_center_x = (points["LEFT_SHOULDER"][0] + points["RIGHT_SHOULDER"][0]) / 2
            left_distance = abs(points["LEFT_SHOULDER"][0] - shoulder_center_x)
            right_distance = abs(points["RIGHT_SHOULDER"][0] - shoulder_center_x)
            
            if left_distance < right_distance:
                visible_arm_angle = angle_left
                visible_elbow_height = points.get("LEFT_ELBOW", [0, 0])[1]
                visible_shoulder_height = points["LEFT_SHOULDER"][1]
                visible_knee_angle = angle_left_knee if angle_left_knee > 0 else 170
                opposite_arm_angle = angle_right
            else:
                visible_arm_angle = angle_right
                visible_elbow_height = points.get("RIGHT_ELBOW", [0, 0])[1]
                visible_shoulder_height = points["RIGHT_SHOULDER"][1]
                visible_knee_angle = angle_right_knee if angle_right_knee > 0 else 170
                opposite_arm_angle = angle_left
            
            hip_rotation = 0
            if "LEFT_HIP" in points and "RIGHT_HIP" in points:
                hip_rotation = abs(points["LEFT_HIP"][0] - points["RIGHT_HIP"][0])
            
            return self.detector.evaluate_side_chest(
                visible_arm_angle, visible_elbow_height, visible_shoulder_height,
                hip_rotation, visible_knee_angle, opposite_arm_angle
            )
            
        elif pose_mode == 'most_muscular':
            if all(key in points for key in ["LEFT_ELBOW", "RIGHT_ELBOW", "LEFT_SHOULDER", 
                                             "RIGHT_SHOULDER", "LEFT_WRIST", "RIGHT_WRIST"]):
                shoulder_width = abs(points["RIGHT_SHOULDER"][0] - points["LEFT_SHOULDER"][0])
                
                torso_alignment = 0
                if all(key in points for key in ["LEFT_SHOULDER", "LEFT_HIP", "RIGHT_SHOULDER", "RIGHT_HIP"]):
                    torso_alignment = abs((points["LEFT_SHOULDER"][1] - points["LEFT_HIP"][1]) - 
                                         (points["RIGHT_SHOULDER"][1] - points["RIGHT_HIP"][1]))
                
                return self.detector.evaluate_most_muscular(
                    angle_left, angle_right,
                    points["LEFT_ELBOW"][1], points["RIGHT_ELBOW"][1],
                    points["LEFT_SHOULDER"][1], points["RIGHT_SHOULDER"][1],
                    shoulder_width,
                    angle_left_knee if angle_left_knee > 0 else 175,
                    angle_right_knee if angle_right_knee > 0 else 175,
                    torso_alignment,
                    points["LEFT_WRIST"][0], points["RIGHT_WRIST"][0],
                    points["LEFT_SHOULDER"][0], points["RIGHT_SHOULDER"][0]
                )
            return "Nao foi possivel detectar os pontos necessarios"
            
        elif pose_mode == 'enquadramento':
            if "LEFT_SHOULDER" in points and "RIGHT_SHOULDER" in points:
                return self.detector.evaluate_centered(
                    points["LEFT_SHOULDER"][0], points["RIGHT_SHOULDER"][0], camera_width
                )
            return "Nao foi possivel detectar os pontos necessarios"
        else:
            return f"Modo '{pose_mode}' ainda nao implementado"

    def run(self):
        """Executa o loop principal da aplicação"""
        # Tenta encontrar câmera
        self.cap, camera_index = find_camera()
        
        if self.cap is None or not self.cap.isOpened():
            print("❌ Erro: Não foi possível acessar nenhuma câmera.")
            print("💡 Dicas:")
            print("   - Verifique se a câmera está conectada")
            print("   - Feche outros aplicativos que possam estar usando a câmera")
            print("   - Verifique as permissões de câmera nas configurações do sistema")
            return

        # Obtém resolução real da câmera
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Se a câmera não retornou valores válidos, usa valores padrão
        if actual_width <= 0 or actual_height <= 0:
            actual_width = 1280
            actual_height = 720
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, actual_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, actual_height)
        
        # Define resoluções
        self.camera_width = actual_width
        self.camera_height = actual_height
        self.sidebar_width = int(actual_width * self.sidebar_width_ratio)
        self.total_width = actual_width + self.sidebar_width
        
        # Configura FPS da câmera para 30
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        # Propriedades adicionais para garantir 30 FPS
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduz buffer para minimizar latência
        # Tenta configurar formato para melhorar FPS
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        
        # Verifica FPS configurado
        configured_fps = self.cap.get(cv2.CAP_PROP_FPS)
        print(f"📹 FPS da câmera configurado: {configured_fps:.2f}")
        
        # Define FPS alvo para o loop
        self.target_fps = 30.0
        self.frame_time = 1.0 / self.target_fps
        
        # Configura janela para tela cheia
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        
        # Força janela para maximizar/tela cheia
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        # Aguarda um frame para garantir que a janela foi criada
        cv2.waitKey(1)
        
        # Obtém tamanho real da tela
        window_rect = cv2.getWindowImageRect(self.window_name)
        if window_rect[2] > 0 and window_rect[3] > 0:
            # Atualiza dimensões baseadas na tela cheia
            self.total_width = window_rect[2]
            self.camera_height = window_rect[3]
            actual_height = window_rect[3]
        else:
            # Fallback: usa valores grandes para simular tela cheia
            self.total_width = 1920
            self.camera_height = 1080
            actual_height = 1080

        prev_time = time.time()
        frame_error_count = 0
        max_frame_errors = 10
        last_frame_time = time.time()

        print("🎬 Iniciando detecção de poses...")
        print("💡 Controles:")
        print("   [Q] - Sair")
        print("   [F] - Alternar tela cheia")
        print("   [1-5] - Mudar de pose")

        while self.cap.isOpened():
            loop_start_time = time.time()
            
            ret, frame = self.cap.read()
            if not ret or frame is None:
                frame_error_count += 1
                if frame_error_count > max_frame_errors:
                    print(f"❌ Erro: Falha ao capturar frames consecutivos ({max_frame_errors} vezes)")
                    print("   Verifique se a câmera ainda está conectada e funcionando")
                    break
                time.sleep(0.1)
                continue

            frame_error_count = 0

            # Obtém tamanho atual da janela em tela cheia
            window_rect = cv2.getWindowImageRect(self.window_name)
            
            # Sempre usa o tamanho real da janela (que deve estar em tela cheia)
            if window_rect[2] > 0 and window_rect[3] > 0:
                window_width = window_rect[2]
                window_height = window_rect[3]
            else:
                # Se não conseguir detectar, força valores de tela cheia
                window_width = 1920
                window_height = 1080
            
            # Calcula dimensões responsivas baseadas no tamanho da janela
            # Menu lateral: 24% da largura total
            sidebar_width = max(int(window_width * self.sidebar_width_ratio), 300)  # Mínimo 300px
            camera_display_width = window_width - sidebar_width
            camera_display_height = window_height
            
            # Redimensiona frame da câmera MANTENDO ASPECT RATIO para evitar distorção
            frame_h, frame_w = frame.shape[:2]
            camera_aspect = frame_w / frame_h if frame_h > 0 else 16/9
            display_aspect = camera_display_width / camera_display_height if camera_display_height > 0 else 16/9
            
            # Calcula dimensões mantendo proporção (sem distorção)
            if camera_aspect > display_aspect:
                # Frame é mais largo - ajusta pela largura e corta em cima/baixo se necessário
                new_width = camera_display_width
                new_height = int(camera_display_width / camera_aspect)
            else:
                # Frame é mais alto - ajusta pela altura e corta nas laterais se necessário
                new_height = camera_display_height
                new_width = int(camera_display_height * camera_aspect)
            
            # Garante que não exceda os limites
            new_width = min(new_width, camera_display_width)
            new_height = min(new_height, camera_display_height)
            
            # Redimensiona frame da câmera mantendo aspect ratio (sem distorção)
            # Usa INTER_AREA para melhor performance em downscaling
            if new_width < frame_w or new_height < frame_h:
                interpolation = cv2.INTER_AREA  # Melhor para reduzir tamanho
            else:
                interpolation = cv2.INTER_LINEAR  # Melhor para aumentar tamanho
            frame_resized = cv2.resize(frame, (new_width, new_height), interpolation=interpolation)
            
            # Processa frame redimensionado e obtém feedback
            frame_resized, pose_quality = self.process_frame(frame_resized, self.pose_mode, new_width)

            # Calcula FPS real
            curr_time = time.time()
            elapsed = curr_time - prev_time
            if elapsed > 0:
                fps = 1.0 / elapsed
            else:
                fps = self.target_fps
            prev_time = curr_time
            
            # Controle de frame rate: só limita se estiver processando MUITO rápido
            # Não adiciona delay se já estiver lento (abaixo de 30 FPS)
            processing_time = time.time() - loop_start_time
            if processing_time < self.frame_time * 0.8:  # Só limita se processou em menos de 80% do tempo
                sleep_time = max(0, self.frame_time - processing_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)

            # Cria canvas combinado (câmera + menu) com tamanho exato da janela
            combined_frame = np.zeros((window_height, window_width, 3), dtype=np.uint8)
            combined_frame.fill(15)  # Fundo escuro preto
            
            # Centraliza frame redimensionado na área da câmera (mantém aspect ratio)
            camera_x_offset = max(0, (camera_display_width - new_width) // 2)
            camera_y_offset = max(0, (camera_display_height - new_height) // 2)
            
            # Copia frame redimensionado centralizado na área da câmera
            y1 = camera_y_offset
            y2 = min(camera_y_offset + new_height, window_height)
            x1 = camera_x_offset
            x2 = min(camera_x_offset + new_width, camera_display_width)
            
            # Ajusta dimensões se necessário
            frame_h_actual = y2 - y1
            frame_w_actual = x2 - x1
            
            if frame_h_actual > 0 and frame_w_actual > 0:
                combined_frame[y1:y2, x1:x2] = frame_resized[:frame_h_actual, :frame_w_actual]
            
            # Coordenadas para renderização dos painéis UI (relativas ao frame renderizado)
            
            mode_display = self.MODE_NAMES.get(self.pose_mode, self.pose_mode)
            
            # Renderiza painéis de UI sobre a área da câmera
            render_info_panel(combined_frame, mode_display, fps, 
                            frame_w_actual, frame_h_actual,
                            x1, y1)
            render_instructions_panel(combined_frame, frame_w_actual, frame_h_actual,
                                     x1, y1)
            
            # Renderiza painel de feedback
            if pose_quality:
                render_feedback_panel(combined_frame, pose_quality, frame_w_actual, frame_h_actual,
                                     x1, y1)
            
            # Renderiza menu lateral na posição correta
            render_sidebar_menu(combined_frame, self.pose_mode, self.MODE_NAMES, 
                               camera_display_width, window_height)
            
            cv2.imshow(self.window_name, combined_frame)

            # Verifica se janela foi fechada
            if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                print("Janela fechada pelo usuário.")
                break

            # Processa teclas
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                print("Encerrando programa...")
                break
            elif key == ord('f') or key == ord('F'):
                # Alterna tela cheia
                current_prop = cv2.getWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN)
                if current_prop == cv2.WINDOW_FULLSCREEN:
                    cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                    print("Modo janela")
                else:
                    cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                    print("Modo tela cheia")
            elif key == ord('1'):
                self.pose_mode = 'enquadramento'
                print("Modo: Enquadramento")
            elif key == ord('2'):
                self.pose_mode = 'double_biceps'
                print("Modo: Duplo Bíceps (Frente)")
            elif key == ord('3'):
                self.pose_mode = 'back_double_biceps'
                print("Modo: Duplo Bíceps de Costas")
            elif key == ord('4'):
                self.pose_mode = 'side_chest'
                print("Modo: Side Chest")
            elif key == ord('5'):
                self.pose_mode = 'most_muscular'
                print("Modo: Most Muscular")

        # Limpeza
        print("Liberando recursos...")
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        print("✅ Programa encerrado com sucesso!")


def main():
    """Função principal"""
    app = BodyVisionApp()
    app.run()


if __name__ == "__main__":
    main()
