"""
Módulo com utilitários para gerenciamento de câmera
"""
import cv2
import time


def find_camera():
    """Tenta encontrar uma câmera disponível testando diferentes índices"""
    print("🔍 Procurando câmera disponível...")
    
    for i in range(5):  # Testa índices de 0 a 4
        try:
            test_cap = cv2.VideoCapture(i)
            if test_cap.isOpened():
                # Configura propriedades para melhor performance
                test_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                test_cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                
                # Tenta ler um frame para confirmar que funciona
                ret, test_frame = test_cap.read()
                if ret and test_frame is not None and test_frame.size > 0:
                    # Aguarda um pouco para estabilizar
                    time.sleep(0.05)  # Reduzido
                    ret2, test_frame2 = test_cap.read()
                    if ret2 and test_frame2 is not None:
                        print(f"✅ Câmera encontrada e funcionando no índice {i}")
                        return test_cap, i
                test_cap.release()
        except Exception as e:
            print(f"⚠️  Erro ao testar câmera índice {i}: {str(e)}")
            continue
    
    return None, None

