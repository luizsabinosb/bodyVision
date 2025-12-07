"""
Módulo responsável pela renderização da interface do usuário
"""
import cv2
from ui_helpers import draw_gradient_rect, draw_separator, draw_progress_bar
from text_renderer import put_text_utf8, put_text_with_shadow, get_text_size_utf8


def render_feedback_panel(frame, pose_quality, camera_width, camera_height, offset_x=0, offset_y=0):
    """Renderiza o painel de feedback principal no topo (apenas na área da câmera)"""
    # Layout responsivo
    scale_factor = camera_width / 1280.0
    
    # Quebra de linha do texto
    lines = []
    max_chars = int(50 * scale_factor)  # Reduzido para caber na área da câmera
    pose_quality_temp = pose_quality
    while len(pose_quality_temp) > max_chars:
        split_index = pose_quality_temp.rfind(';', 0, max_chars)
        if split_index == -1:
            split_index = max_chars
        lines.append(pose_quality_temp[:split_index + 1].strip())
        pose_quality_temp = pose_quality_temp[split_index + 1:].strip()
    lines.append(pose_quality_temp)

    # Painel de feedback (ajustado para área da câmera)
    panel_y = offset_y + int(15 * scale_factor)
    panel_height = len(lines) * int(45 * scale_factor) + int(30 * scale_factor)
    panel_width = min(camera_width - int(40 * scale_factor), int(750 * scale_factor))
    panel_x = offset_x + (camera_width - panel_width) // 2
    
    # Cores baseadas no status
    if pose_quality.startswith("Posicao correta") or "centralizado" in pose_quality.lower():
        bg_color = (15, 50, 15)
        bg_color2 = (25, 80, 25)
        border_color = (0, 255, 100)
        icon_color = (0, 255, 0)
        text_color = (0, 255, 0)
    else:
        bg_color = (50, 15, 15)
        bg_color2 = (80, 25, 25)
        border_color = (255, 100, 0)
        icon_color = (0, 0, 255)
        text_color = (0, 0, 255)
    
    # Gradiente do painel
    draw_gradient_rect(frame, panel_x, panel_y, panel_width, panel_height, 
                      bg_color, bg_color2, alpha=0.92, vertical=True)
    
    # Borda
    cv2.rectangle(frame, (panel_x, panel_y), (panel_x + panel_width, panel_y + panel_height), 
                 border_color, 3)
    cv2.rectangle(frame, (panel_x + 3, panel_y + 3), 
                 (panel_x + panel_width - 3, panel_y + panel_height - 3), 
                 (border_color[0]//2, border_color[1]//2, border_color[2]//2), 1)
    
    # Ícone de status
    icon_x = panel_x + 15
    icon_y = panel_y + panel_height // 2
    cv2.circle(frame, (icon_x, icon_y), 8, icon_color, -1)
    cv2.circle(frame, (icon_x, icon_y), 12, icon_color, 2)
    
    # Texto do feedback
    y = panel_y + int(40 * scale_factor)
    font_scale = 0.8 * scale_factor
    line_spacing = int(50 * scale_factor)
    for line in lines:
        text_width, text_height = get_text_size_utf8(line, font_scale)
        x_center = panel_x + (panel_width - text_width) // 2
        # Texto com sombra usando UTF-8
        put_text_with_shadow(frame, line, (x_center, y), font_scale, text_color, 
                            thickness=2, shadow_color=(0, 0, 0))
        y += line_spacing


def render_info_panel(frame, mode_display, fps, camera_width, camera_height, offset_x=0, offset_y=0):
    """Renderiza apenas o FPS no canto superior esquerdo"""
    # Layout responsivo baseado na largura da câmera
    scale_factor = camera_width / 1280.0  # Fator de escala baseado em 1280px
    fps_x = offset_x + int(20 * scale_factor)
    fps_y = offset_y + int(30 * scale_factor)
    font_scale_fps = 0.7 * scale_factor
    
    # FPS com cor baseada na performance
    fps_color = (0, 255, 0) if fps >= 20 else (0, 165, 255) if fps >= 10 else (0, 0, 255)
    fps_text = f"FPS: {int(fps)}"
    
    # Renderiza FPS com sombra para melhor legibilidade
    put_text_with_shadow(frame, fps_text, (fps_x, fps_y), 
                        font_scale_fps, fps_color, thickness=2)


def render_instructions_panel(frame, camera_width, camera_height, offset_x=0, offset_y=0):
    """Renderiza o painel de instruções na parte inferior (apenas na área da câmera)"""
    scale_factor = camera_width / 1280.0
    instruction_panel_height = int(75 * scale_factor)
    instruction_panel_y = offset_y + camera_height - instruction_panel_height - int(15 * scale_factor)
    instruction_panel_width = camera_width - int(40 * scale_factor)
    instruction_panel_x = offset_x + int(20 * scale_factor)
    
    # Gradiente escuro
    draw_gradient_rect(frame, instruction_panel_x, instruction_panel_y, 
                      instruction_panel_width, instruction_panel_height,
                      (15, 15, 15), (30, 30, 30), alpha=0.92, vertical=True)
    
    # Borda
    cv2.rectangle(frame, (instruction_panel_x, instruction_panel_y), 
                 (instruction_panel_x + instruction_panel_width, instruction_panel_y + instruction_panel_height), 
                 (150, 150, 150), 3)
    
    # Título
    font_scale_title = 0.55 * scale_factor
    put_text_with_shadow(frame, "CONTROLES", 
                        (instruction_panel_x + int(15 * scale_factor), 
                         instruction_panel_y + int(25 * scale_factor)), 
                        font_scale_title, (200, 200, 200), thickness=2)
    
    # Separador
    draw_separator(frame, instruction_panel_x + int(10 * scale_factor), 
                  instruction_panel_y + int(30 * scale_factor), 
                  instruction_panel_width - int(20 * scale_factor), 
                  (120, 120, 120), 1)
    
    # Instruções
    instruction_scale = 0.5 * scale_factor
    instruction_y = instruction_panel_y + int(50 * scale_factor)
    
    # Instruções simplificadas (menu está no sidebar)
    controls_text = "Use as teclas 1-5 ou clique no menu lateral para mudar de pose"
    text_width1, _ = get_text_size_utf8(controls_text, instruction_scale)
    x1 = instruction_panel_x + (instruction_panel_width - text_width1) // 2
    put_text_with_shadow(frame, controls_text, (x1, instruction_y), 
                        instruction_scale, (240, 240, 240), thickness=1)


def render_sidebar_menu(frame, current_mode, mode_names, camera_width, h):
    """Renderiza o menu lateral moderno à direita da câmera"""
    # Menu responsivo baseado na altura
    # Calcula sidebar_width baseado no frame atual (já tem o tamanho certo)
    sidebar_x = camera_width
    sidebar_width = frame.shape[1] - camera_width
    
    # Calcula scale_factor baseado na altura
    scale_factor = h / 720.0  # Baseado em 720px de altura
    
    # Fundo do sidebar com gradiente
    draw_gradient_rect(frame, sidebar_x, 0, sidebar_width, h,
                      (20, 20, 30), (15, 15, 25), alpha=1.0, vertical=True)
    
    # Linha separadora entre câmera e menu
    cv2.line(frame, (sidebar_x, 0), (sidebar_x, h), (80, 80, 100), 3)
    cv2.line(frame, (sidebar_x + 1, 0), (sidebar_x + 1, h), (50, 50, 70), 1)
    
    # Cabeçalho do menu
    header_height = int(120 * scale_factor)
    header_y = 0
    draw_gradient_rect(frame, sidebar_x, header_y, sidebar_width, header_height,
                      (30, 30, 50), (25, 25, 45), alpha=1.0, vertical=True)
    
    # Título do menu
    title_text = "BODYVISION"
    title_scale = 1.0 * scale_factor
    title_width, _ = get_text_size_utf8(title_text, title_scale)
    title_x = sidebar_x + (sidebar_width - title_width) // 2
    title_y = int(50 * scale_factor)
    
    # Título com sombra
    put_text_with_shadow(frame, title_text, (title_x, title_y), 
                        title_scale, (100, 200, 255), thickness=3)
    
    # Subtítulo
    subtitle_text = "Sistema de Análise de Poses"
    subtitle_scale = 0.45 * scale_factor
    subtitle_width, _ = get_text_size_utf8(subtitle_text, subtitle_scale)
    subtitle_x = sidebar_x + (sidebar_width - subtitle_width) // 2
    put_text_utf8(frame, subtitle_text, (subtitle_x, title_y + int(35 * scale_factor)), 
                 subtitle_scale, (150, 150, 180), thickness=1)
    
    # Separador após header
    separator_y = header_height + int(10 * scale_factor)
    draw_separator(frame, sidebar_x + int(20 * scale_factor), separator_y, 
                  sidebar_width - int(40 * scale_factor), (80, 100, 130), 2)
    
    # Lista de poses
    poses_info = [
        ('enquadramento', '1', 'Enquadramento', 'Centralize-se na câmera'),
        ('double_biceps', '2', 'Duplo Bíceps', 'Braços elevados e contraídos'),
        ('back_double_biceps', '3', 'Duplo Bíceps Costas', 'Costas para a câmera'),
        ('side_chest', '4', 'Side Chest', 'Corpo de lado, braço contraído'),
        ('most_muscular', '5', 'Most Muscular', 'Braços abaixo dos ombros')
    ]
    
    # Calcula espaço disponível para itens (descontando header, separadores e footer)
    footer_height = int(100 * scale_factor)
    available_height = h - separator_y - footer_height - int(40 * scale_factor)
    num_items = len(poses_info)
    
    # Ajusta item_height e spacing para caber todos os itens
    min_item_height = int(90 * scale_factor)
    min_spacing = int(12 * scale_factor)
    
    # Calcula altura ideal dos itens
    total_spacing = min_spacing * (num_items - 1)
    item_height = max(min_item_height, int((available_height - total_spacing) / num_items))
    item_spacing = min_spacing
    
    start_y = separator_y + int(20 * scale_factor)
    
    for idx, (mode_key, key_num, display_name, description) in enumerate(poses_info):
        item_y = start_y + idx * (item_height + item_spacing)
        
        # Verifica se é a pose selecionada
        is_selected = (mode_key == current_mode)
        
        # Cores baseadas na seleção
        if is_selected:
            bg_color1 = (30, 60, 90)
            bg_color2 = (40, 80, 120)
            border_color = (100, 200, 255)
            text_color = (150, 230, 255)
            key_bg = (50, 150, 200)
        else:
            bg_color1 = (25, 25, 35)
            bg_color2 = (35, 35, 45)
            border_color = (60, 60, 80)
            text_color = (180, 180, 200)
            key_bg = (60, 60, 80)
        
        # Painel do item
        item_width = sidebar_width - int(30 * scale_factor)
        item_x = sidebar_x + int(15 * scale_factor)
        
        # Gradiente do item
        draw_gradient_rect(frame, item_x, item_y, item_width, item_height,
                          bg_color1, bg_color2, alpha=0.95, vertical=True)
        
        # Borda
        border_thickness = 3 if is_selected else 2
        cv2.rectangle(frame, (item_x, item_y), 
                     (item_x + item_width, item_y + item_height),
                     border_color, border_thickness)
        
        # Indicador de seleção (barra lateral)
        if is_selected:
            cv2.rectangle(frame, (item_x, item_y), 
                         (item_x + int(6 * scale_factor), item_y + item_height),
                         (100, 200, 255), -1)
        
        # Badge da tecla
        key_badge_size = int(35 * scale_factor)
        key_x = item_x + int(15 * scale_factor)
        key_y = item_y + int(25 * scale_factor)
        
        # Círculo do badge
        cv2.circle(frame, (key_x + key_badge_size // 2, key_y + key_badge_size // 2),
                  key_badge_size // 2 + 2, (0, 0, 0), -1)
        cv2.circle(frame, (key_x + key_badge_size // 2, key_y + key_badge_size // 2),
                  key_badge_size // 2, key_bg, -1)
        
        # Texto da tecla (sem acentuação, pode usar cv2)
        key_scale = 0.7 * scale_factor
        key_width, key_height = get_text_size_utf8(key_num, key_scale)
        key_text_x = key_x + (key_badge_size - key_width) // 2
        key_text_y = key_y + (key_badge_size + key_height) // 2
        put_text_utf8(frame, key_num, (key_text_x, key_text_y), 
                     key_scale, (255, 255, 255), thickness=2)
        
        # Nome da pose
        name_x = item_x + key_badge_size + int(20 * scale_factor)
        name_y = item_y + int(28 * scale_factor)
        name_scale = 0.6 * scale_factor
        put_text_utf8(frame, display_name, (name_x, name_y), 
                     name_scale, text_color, thickness=2)
        
        # Descrição (ajustada para caber no item)
        desc_y = name_y + int(22 * scale_factor)
        desc_scale = 0.38 * scale_factor
        desc_color = (text_color[0] - 50, text_color[1] - 50, text_color[2] - 50)
        
        # Trunca descrição se muito longa para caber
        max_desc_width = item_width - (name_x - item_x) - int(40 * scale_factor)
        desc_width, _ = get_text_size_utf8(description, desc_scale)
        if desc_width > max_desc_width:
            # Tenta truncar descrição
            truncated = description
            while desc_width > max_desc_width and len(truncated) > 10:
                truncated = truncated[:-1]
                desc_width, _ = get_text_size_utf8(truncated + "...", desc_scale)
            description = truncated + "..." if len(truncated) < len(description) else description
        
        put_text_utf8(frame, description, (name_x, desc_y), 
                     desc_scale, desc_color, thickness=1)
        
        # Ícone de seleção (se estiver selecionado)
        if is_selected:
            check_x = item_x + item_width - int(35 * scale_factor)
            check_y = item_y + int(25 * scale_factor)
            check_radius = int(12 * scale_factor)
            cv2.circle(frame, (check_x, check_y), check_radius, (0, 255, 100), -1)
            cv2.circle(frame, (check_x, check_y), check_radius + 2, (0, 200, 80), 2)
            # Checkmark
            cv2.line(frame, (check_x - int(5 * scale_factor), check_y), 
                    (check_x - int(2 * scale_factor), check_y + int(5 * scale_factor)), 
                    (255, 255, 255), 2)
            cv2.line(frame, (check_x - int(2 * scale_factor), check_y + int(5 * scale_factor)),
                    (check_x + int(5 * scale_factor), check_y - int(3 * scale_factor)), 
                    (255, 255, 255), 2)
    
    # Footer com instruções (já calculado acima)
    footer_y = h - footer_height
    draw_gradient_rect(frame, sidebar_x, footer_y, sidebar_width, footer_height,
                      (15, 15, 25), (20, 20, 30), alpha=0.95, vertical=True)
    
    footer_text = "Pressione [Q] para sair"
    footer_scale = 0.5 * scale_factor
    footer_width, _ = get_text_size_utf8(footer_text, footer_scale)
    footer_text_x = sidebar_x + (sidebar_width - footer_width) // 2
    footer_text_y = footer_y + int(40 * scale_factor)
    put_text_utf8(frame, footer_text, (footer_text_x, footer_text_y), 
                 footer_scale, (150, 150, 180), thickness=1)
    
    # Separador antes do footer
    draw_separator(frame, sidebar_x + int(20 * scale_factor), 
                  footer_y - int(10 * scale_factor), 
                  sidebar_width - int(40 * scale_factor), 
                  (80, 100, 130), 2)


def render_pose_skeleton(frame, points, angle_left, angle_right, angle_left_knee, angle_right_knee, pose_mode):
    """Renderiza o esqueleto da pose com linhas e ângulos"""
    font = cv2.FONT_HERSHEY_SIMPLEX
    arm_line_color = (0, 200, 255)
    arm_line_thickness = 4
    joint_radius = 6
    
    # Desenha braços
    for side in ["LEFT", "RIGHT"]:
        if f"{side}_SHOULDER" in points and f"{side}_ELBOW" in points and f"{side}_WRIST" in points:
            shoulder_pos = points[f"{side}_SHOULDER"]
            elbow_pos = points[f"{side}_ELBOW"]
            wrist_pos = points[f"{side}_WRIST"]
            
            # Linhas com efeito glow
            glow_color = (arm_line_color[0]//3, arm_line_color[1]//3, arm_line_color[2]//3)
            cv2.line(frame, shoulder_pos, elbow_pos, glow_color, arm_line_thickness + 2)
            cv2.line(frame, shoulder_pos, elbow_pos, arm_line_color, arm_line_thickness)
            cv2.line(frame, elbow_pos, wrist_pos, glow_color, arm_line_thickness + 2)
            cv2.line(frame, elbow_pos, wrist_pos, arm_line_color, arm_line_thickness)
            
            # Pontos nas articulações
            cv2.circle(frame, shoulder_pos, joint_radius + 2, (0, 0, 0), -1)
            cv2.circle(frame, shoulder_pos, joint_radius, (255, 255, 255), -1)
            cv2.circle(frame, elbow_pos, joint_radius + 2, (0, 0, 0), -1)
            cv2.circle(frame, elbow_pos, joint_radius, arm_line_color, -1)
            cv2.circle(frame, wrist_pos, joint_radius + 2, (0, 0, 0), -1)
            cv2.circle(frame, wrist_pos, joint_radius, (255, 255, 255), -1)
            
            # Badge do ângulo
            angle = angle_left if side == "LEFT" else angle_right
            angle_text = f"{int(angle)}°"
            angle_pos = elbow_pos
            text_size_angle, _ = cv2.getTextSize(angle_text, font, 0.65, 2)
            
            badge_x = angle_pos[0] - text_size_angle[0] // 2 - 8
            badge_y = angle_pos[1] - text_size_angle[1] - 25
            badge_w = text_size_angle[0] + 16
            badge_h = text_size_angle[1] + 12
            
            overlay = frame.copy()
            cv2.rectangle(overlay, (badge_x, badge_y), 
                         (badge_x + badge_w, badge_y + badge_h), (20, 20, 20), -1)
            cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
            cv2.rectangle(frame, (badge_x, badge_y), 
                         (badge_x + badge_w, badge_y + badge_h), arm_line_color, 2)
            cv2.putText(frame, angle_text, (badge_x + 8, badge_y + text_size_angle[1] + 6), 
                       font, 0.65, (255, 255, 255), 2)

    # Desenha pernas se necessário
    leg_line_color = (255, 100, 0)
    if pose_mode in ['side_chest', 'most_muscular']:
        for side in ["LEFT", "RIGHT"]:
            if (f"{side}_HIP" in points and f"{side}_KNEE" in points and 
                f"{side}_ANKLE" in points):
                hip_pos = points[f"{side}_HIP"]
                knee_pos = points[f"{side}_KNEE"]
                ankle_pos = points[f"{side}_ANKLE"]
                
                glow_color_leg = (leg_line_color[0]//3, leg_line_color[1]//3, leg_line_color[2]//3)
                cv2.line(frame, hip_pos, knee_pos, glow_color_leg, arm_line_thickness + 2)
                cv2.line(frame, hip_pos, knee_pos, leg_line_color, arm_line_thickness)
                cv2.line(frame, knee_pos, ankle_pos, glow_color_leg, arm_line_thickness + 2)
                cv2.line(frame, knee_pos, ankle_pos, leg_line_color, arm_line_thickness)
                
                cv2.circle(frame, hip_pos, joint_radius, (255, 255, 255), -1)
                cv2.circle(frame, knee_pos, joint_radius, leg_line_color, -1)
                cv2.circle(frame, ankle_pos, joint_radius, (255, 255, 255), -1)

