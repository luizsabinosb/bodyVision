"""
Módulo com funções auxiliares para desenho de interface moderna
"""
import cv2


def draw_modern_panel(img, x, y, width, height, bg_color=(20, 20, 20), border_color=(100, 100, 100), alpha=0.85, shadow=True):
    """Desenha um painel moderno com fundo semi-transparente, borda e sombra"""
    pt1 = (x, y)
    pt2 = (x + width, y + height)
    
    # Efeito de sombra
    if shadow:
        shadow_offset = 3
        shadow_pt1 = (x + shadow_offset, y + shadow_offset)
        shadow_pt2 = (x + width + shadow_offset, y + height + shadow_offset)
        shadow_overlay = img.copy()
        cv2.rectangle(shadow_overlay, shadow_pt1, shadow_pt2, (0, 0, 0), -1)
        cv2.addWeighted(shadow_overlay, 0.3, img, 0.7, 0, img)
    
    # Fundo do painel
    overlay = img.copy()
    cv2.rectangle(overlay, pt1, pt2, bg_color, -1)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    
    # Borda com gradiente (simulado com borda dupla)
    cv2.rectangle(img, pt1, pt2, (border_color[0]//2, border_color[1]//2, border_color[2]//2), 1)
    cv2.rectangle(img, (x+1, y+1), (x + width - 1, y + height - 1), border_color, 2)


def draw_status_badge(img, x, y, text, status_color, bg_color=(30, 30, 30), alpha=0.9, icon=""):
    """Desenha um badge de status moderno com ícone opcional"""
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    padding = 15
    icon_space = 25 if icon else 0
    badge_width = text_width + padding * 2 + icon_space
    badge_height = text_height + padding * 2
    
    # Desenha fundo do badge
    overlay = img.copy()
    cv2.rectangle(overlay, (x, y), (x + badge_width, y + badge_height), bg_color, -1)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    
    # Desenha borda colorida
    cv2.rectangle(img, (x, y), (x + badge_width, y + badge_height), status_color, 2)
    
    # Desenha texto
    text_x = x + padding + icon_space
    cv2.putText(img, text, (text_x, y + text_height + padding // 2), 
                font, font_scale, status_color, thickness)
    
    return badge_width, badge_height


def draw_gradient_rect(img, x, y, width, height, color1, color2, alpha=0.7, vertical=True):
    """Desenha um retângulo com gradiente"""
    overlay = img.copy()
    if vertical:
        for i in range(height):
            ratio = i / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            cv2.line(overlay, (x, y + i), (x + width, y + i), (b, g, r), 1)
    else:
        for i in range(width):
            ratio = i / width
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            cv2.line(overlay, (x + i, y), (x + i, y + height), (b, g, r), 1)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)


def draw_progress_bar(img, x, y, width, height, progress, color, bg_color=(50, 50, 50)):
    """Desenha uma barra de progresso moderna"""
    # Fundo
    cv2.rectangle(img, (x, y), (x + width, y + height), bg_color, -1)
    # Barra de progresso
    progress_width = int(width * progress / 100)
    if progress_width > 0:
        cv2.rectangle(img, (x, y), (x + progress_width, y + height), color, -1)
    # Borda
    cv2.rectangle(img, (x, y), (x + width, y + height), (200, 200, 200), 2)


def draw_separator(img, x, y, length, color=(150, 150, 150), thickness=1):
    """Desenha uma linha separadora moderna"""
    cv2.line(img, (x, y), (x + length, y), color, thickness)

