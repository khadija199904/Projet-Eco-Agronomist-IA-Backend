from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Optional
import json
import base64

from src.api.v1.dependencies.db import get_db
from src.api.v1.dependencies.user import get_current_user
from src.api.v1.schemas.diagnostic_schema import (
    PlantDiagnosticCreate, PlantDiagnosticResponse, 
    DiagnosticProductCreate, DiagnosticProductResponse
)
from src.api.v1.crud import diagnostic_crud
from src.api.v1.services import diagnostic_service
from src.database.models.users import User
from src.database.models.enums import UserRole
from src.core.security import verify_token

router = APIRouter(prefix="/diagnostics", tags=["IA Diagnostic"])

@router.post("/upload", summary="Analyser une image (Plante ou Produit)")
async def upload_and_diagnose(
    diag_type: str = Form(..., description="Type de diagnostic : 'plante' ou 'produit'"),
    lot_recolte_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Analyse une image via IA. 
    """
    authorized_roles = [UserRole.AGRICULTEUR, UserRole.QUALITE, UserRole.ADMIN]
    if user.role not in authorized_roles:
        raise HTTPException(status_code=403, detail="Accès non autorisé.")

    if diag_type == "plante":
        if user.role != UserRole.AGRICULTEUR:
            raise HTTPException(status_code=403, detail="Réservé aux agriculteurs.")
        
        try:
            image_path = await diagnostic_service.save_upload_file(file)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur sauvegarde : {e}")

        disease, severity, advice, detection_details = diagnostic_service.run_prediction(image_path)
        
        diag_create = PlantDiagnosticCreate(
            lot_recolte_id=lot_recolte_id,
            disease_detected=disease,
            severity_level=severity,
            treatment_advice=advice,
            detection_details=detection_details
        )
        return diagnostic_crud.create_plant_diagnostic(db, diag_create)

    elif diag_type == "produit":
        if user.role not in [UserRole.QUALITE, UserRole.ADMIN]:
            raise HTTPException(status_code=403, detail="Réservé aux contrôleurs qualité.")
        
        try:
            image_path = await diagnostic_service.save_upload_file(file, sub_dir="valorisation")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur sauvegarde : {e}")

        defects, score, taux, decision, detection_details = diagnostic_service.run_valorisation_prediction(image_path)
        
        diag_create = DiagnosticProductCreate(
            lot_recolte_id=lot_recolte_id,
            image_url=image_path,
            visual_defects=defects,
            healthy_score=score,
            taux_defauts_visuels=taux,
            decision_flux=decision,
            detection_details=detection_details
        )
        return diagnostic_crud.create_diagnostic_product(db, diag_create)
    
    else:
        raise HTTPException(status_code=400, detail="diag_type invalide. Utilisez 'plante' ou 'valorisation'.")


# @router.websocket("/stream")
# async def stream_live_diagnosis(
#     websocket: WebSocket,
#     token: str
# ):
#     """
#     WebSocket — Diagnostic en temps réel sur flux vidéo.
#     Protocole :
#     - Client envoie : JSON { "frame": "base64(jpeg)" }
#     - Serveur répond : JSON { label, confidence, boxes, status }
#     """
#     await websocket.accept()

#     # Vérification Token
#     try:
#         payload = verify_token(token)
#         if not payload:
#             raise Exception("Invalid token")
#     except Exception:
#         await websocket.send_text(json.dumps({"error": "Token invalide"}))
#         await websocket.close()
#         return

#     try:
#         while True:
#             # Réception frame base64
#             data = await websocket.receive_text()
#             msg = json.loads(data)
#             frame_b64 = msg.get("frame")

#             if not frame_b64:
#                 continue

#             frame_bytes = base64.b64decode(frame_b64)

#             # Inférence rapide YOLO
#             result = await diagnostic_service.analyze_frame(frame_bytes)

#             # Envoi résultat
#             await websocket.send_text(json.dumps({
#                 "label": result.get("label", "Aucune détection"),
#                 "confidence": result.get("confidence", 0.0),
#                 "boxes": result.get("boxes", []),
#                 "status": "detected" if result.get("confidence", 0) >= 0.80 else "scanning",
#             }))

#     except WebSocketDisconnect:
#         pass
#     except Exception as e:
#         await websocket.send_text(json.dumps({"error": str(e)}))
#         await websocket.close()


# @router.get("/history")
# def get_history(
#     diag_type: Optional[str] = None,
#     lot_id: Optional[int] = None,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user)
# ):
#     """Historique unifié des diagnostics."""
#     authorized_roles = [UserRole.AGRICULTEUR, UserRole.QUALITE, UserRole.ADMIN]
#     if user.role not in authorized_roles:
#         raise HTTPException(status_code=403, detail="Accès non autorisé.")

#     history = []
#     from src.api.v1.schemas.diagnostic_schema import DiagnosticHistoryItem
    
#     # Récupération Plante
#     if not diag_type or diag_type == "plante":
#         from src.database.models.diagnostics import PlantDiagnostic
#         query = db.query(PlantDiagnostic)
#         if lot_id: query = query.filter(PlantDiagnostic.lot_recolte_id == lot_id)
        
#         for d in query.all():
#             history.append(DiagnosticHistoryItem(
#                 id=d.id,
#                 diag_type="plante",
#                 label=d.disease_detected or "Sain",
#                 confidence=0.9, # Placeholder
#                 lot_recolte_id=d.lot_recolte_id,
#                 created_at=d.created_at
#             ))

#     # Récupération Produit
#     if not diag_type or diag_type == "valorisation":
#         from src.database.models.diagnostics import DiagnosticProduct
#         query = db.query(DiagnosticProduct)
#         if lot_id: query = query.filter(DiagnosticProduct.lot_recolte_id == lot_id)
        
#         for d in query.all():
#             history.append(DiagnosticHistoryItem(
#                 id=d.id,
#                 diag_type="valorisation",
#                 label="Qualité" if d.healthy_score > 0.8 else "Défaut",
#                 confidence=d.healthy_score or 0.0,
#                 lot_recolte_id=d.lot_recolte_id,
#                 created_at=d.created_at
#             ))

#     history.sort(key=lambda x: x.created_at, reverse=True)
#     return DiagnosticListResponse(total=len(history), diagnostics=history)


# @router.get("/{diag_type}/{diagnostic_id}")
# def get_diagnostic_detail(
#     diag_type: str,
#     diagnostic_id: int,
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user)
# ):
#     """Détail d'un diagnostic spécifique."""
#     authorized_roles = [UserRole.AGRICULTEUR, UserRole.QUALITE, UserRole.ADMIN]
#     if user.role not in authorized_roles:
#         raise HTTPException(status_code=403, detail="Accès non autorisé.")

#     if diag_type == "plante":
#         res = diagnostic_crud.get_plant_diagnostic_by_id(db, diagnostic_id)
#     elif diag_type == "valorisation":
#         res = diagnostic_crud.get_product_diagnostic_by_id(db, diagnostic_id)
#     else:
#         raise HTTPException(status_code=400, detail="Type invalide")

#     if not res:
#         raise HTTPException(status_code=404, detail="Diagnostic introuvable")
#     return res
