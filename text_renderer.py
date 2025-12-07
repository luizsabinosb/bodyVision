"""
Módulo para renderização de texto com suporte a acentuação UTF-8
Otimizado para performance com cache de fontes e renderização híbrida
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import re

# Cache global de fontes
_font_cache = {}
_cached_font_path = None


def _has_accent(text):
    """Verifica se o texto contém caracteres acentuados"""
    return bool(re.search(r'[àáâãäèéêëìíîïòóôõöùúûüÀÁÂÃÄÈÉÊËÌÍÎÏÒÓÔÕÖÙÚÛÜçÇ]', text))


def get_font_path():
    """Tenta encontrar uma fonte adequada no sistema (com cache)"""
    global _cached_font_path
    
    if _cached_font_path is not None:
        return _cached_font_path
    
    # Lista de fontes comuns no sistema
    font_paths = [
        # macOS
        '/System/Library/Fonts/Helvetica.ttc',
        '/System/Library/Fonts/Arial.ttf',
        '/Library/Fonts/Arial.ttf',
        # Linux
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        # Windows
        'C:/Windows/Fonts/arial.ttf',
        'C:/Windows/Fonts/calibri.ttf',
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            _cached_font_path = path
            return path
    
    _cached_font_path = None
    return None


def _get_cached_font(font_size, font_path=None):
    """Obtém fonte do cache ou cria nova"""
    if font_path is None:
        font_path = get_font_path()
    
    cache_key = (font_path, font_size)
    
    if cache_key in _font_cache:
        return _font_cache[cache_key]
    
    try:
        if font_path and os.path.exists(font_path):
            if font_path.endswith('.ttc'):
                font = ImageFont.truetype(font_path, font_size, index=0)
            else:
                font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
    
    _font_cache[cache_key] = font
    return font


def put_text_utf8(img, text, position, font_scale, color, thickness=2, font_path=None):
    """
    Renderiza texto com suporte a acentuação UTF-8 usando PIL
    Otimizado com cache de fontes e renderização parcial
    """
    # Se não tem acento, usa cv2 (muito mais rápido)
    if not _has_accent(text):
        font = cv2.FONT_HERSHEY_SIMPLEX
        # Usa LINE_AA apenas para texto grande (melhor performance)
        line_type = cv2.LINE_AA if font_scale > 0.6 else cv2.LINE_8
        cv2.putText(img, text, position, font, font_scale, color, thickness, line_type)
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        return text_size[0], text_size[1]
    
    # Renderização com PIL apenas para texto com acentos
    if font_path is None:
        font_path = get_font_path()
    
    # Usa cache de fonte
    base_font_size = max(10, int(font_scale * 30))
    font = _get_cached_font(base_font_size, font_path)
    
    # Renderiza apenas na região necessária do texto (otimização)
    # Estima tamanho do texto (usando imagem menor para medição)
    img_temp = Image.new('RGBA', (1000, 100), (0, 0, 0, 0))
    draw_temp = ImageDraw.Draw(img_temp)
    bbox = draw_temp.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x, y = position
    padding = 3  # Reduzido para melhor performance
    
    # Limita tamanho máximo da imagem de texto para melhor performance
    max_text_w = min(text_width + padding * 2, 800)
    max_text_h = min(text_height + padding * 2, 200)
    
    # Cria imagem apenas para o texto com padding
    text_img = Image.new('RGBA', (max_text_w, max_text_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_img)
    
    # Converte cor BGR para RGB
    color_rgb = (color[2], color[1], color[0])
    
    # Desenha texto
    draw.text((padding, padding), text, fill=color_rgb, font=font)
    
    # Converte para numpy (mais rápido)
    text_array = np.asarray(text_img, dtype=np.uint8)
    
    # Calcula região de interesse na imagem principal
    roi_y1 = max(0, y - padding)
    roi_y2 = min(img.shape[0], y + text_height + padding * 2)
    roi_x1 = max(0, x)
    roi_x2 = min(img.shape[1], x + text_width + padding * 2)
    
    if roi_y2 > roi_y1 and roi_x2 > roi_x1:
        roi_h = roi_y2 - roi_y1
        roi_w = roi_x2 - roi_x1
        
        # Ajusta tamanho do texto renderizado para corresponder ao ROI
        text_roi_h = min(max_text_h, roi_h)
        text_roi_w = min(max_text_w, roi_w)
        
        # Extrai região do texto
        text_roi = text_array[:text_roi_h, :text_roi_w]
        
        # Extrai ROI da imagem
        roi = img[roi_y1:roi_y1+text_roi_h, roi_x1:roi_x1+text_roi_w].copy()
        
        # Alpha blending otimizado
        if text_roi.shape[2] == 4:  # RGBA
            # Garante que as dimensões sejam compatíveis
            if roi.shape[:2] == text_roi.shape[:2]:
                alpha = text_roi[:, :, 3:4].astype(np.float32) / 255.0
                text_rgb = text_roi[:, :, :3].astype(np.float32)
                text_bgr = text_rgb[:, :, ::-1]  # RGB para BGR
                roi_float = roi.astype(np.float32)
                
                # Composição alpha (broadcasting seguro)
                result = (1 - alpha) * roi_float + alpha * text_bgr
                img[roi_y1:roi_y1+text_roi_h, roi_x1:roi_x1+text_roi_w] = result.astype(np.uint8)
            else:
                # Dimensões incompatíveis - composição simples sem alpha
                img[roi_y1:roi_y1+min(roi.shape[0], text_roi.shape[0]), 
                    roi_x1:roi_x1+min(roi.shape[1], text_roi.shape[1])] = \
                    text_roi[:min(roi.shape[0], text_roi.shape[0]), 
                            :min(roi.shape[1], text_roi.shape[1]), :3][:, :, ::-1]
        else:
            # Sem alpha, composição direta
            if roi.shape == text_roi[:, :, ::-1].shape:
                img[roi_y1:roi_y1+text_roi_h, roi_x1:roi_x1+text_roi_w] = text_roi[:, :, ::-1]
            else:
                # Ajusta tamanhos se necessário
                h_min = min(roi.shape[0], text_roi.shape[0])
                w_min = min(roi.shape[1], text_roi.shape[1])
                img[roi_y1:roi_y1+h_min, roi_x1:roi_x1+w_min] = text_roi[:h_min, :w_min, ::-1]
    
    return text_width, text_height


def get_text_size_utf8(text, font_scale, font_path=None):
    """Retorna o tamanho que o texto ocuparia (otimizado)"""
    # Se não tem acento, usa cv2 (muito mais rápido)
    if not _has_accent(text):
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size, _ = cv2.getTextSize(text, font, font_scale, 2)
        return text_size[0], text_size[1]
    
    # Para texto com acentos, usa cache de fonte
    base_font_size = max(10, int(font_scale * 30))
    font = _get_cached_font(base_font_size, font_path)
    
    # Cria imagem temporária mínima para medir
    img_temp = Image.new('RGB', (100, 100), (0, 0, 0))
    draw = ImageDraw.Draw(img_temp)
    bbox = draw.textbbox((0, 0), text, font=font)
    
    return (bbox[2] - bbox[0], bbox[3] - bbox[1])


def put_text_with_shadow(img, text, position, font_scale, color, thickness=2, 
                         shadow_offset=(2, 2), shadow_color=(0, 0, 0), font_path=None):
    """Renderiza texto com sombra usando UTF-8 (otimizado)"""
    x, y = position
    shadow_x = x + shadow_offset[0]
    shadow_y = y + shadow_offset[1]
    
    # Desenha sombra primeiro
    put_text_utf8(img, text, (shadow_x, shadow_y), font_scale, shadow_color, thickness, font_path)
    
    # Desenha texto principal
    text_width, text_height = put_text_utf8(img, text, position, font_scale, color, thickness, font_path)
    
    return text_width, text_height
