import os
import uuid
import cv2
import numpy as np

def save_diagnostic_image(im_array: np.ndarray) -> str:
    """
    Sauvegarde l'image annotée sur le disque et retourne le chemin relatif.
    
    """
    target_dir = os.path.join("uploads", "diagnostics")
    os.makedirs(target_dir, exist_ok=True)
    unique_filename = f"{uuid.uuid4().hex}.jpg"
    image_path = os.path.join(target_dir, unique_filename)
        
        
    image_annote = cv2.imwrite(image_path, im_array)
    
    if not image_annote:
        raise IOError(f"Impossible de sauvegarder l'image dans {image_path}")

    # On retourne le chemin relatif pour stockage en DB et accès via URL
    return image_path