import httpx
import json
from sqlalchemy.orm import Session
import models
from ws_manager import manager

async def forward_webhook(endpoint_id: int, payload: str, destinations: list[models.Destination], req_meta: dict):
    # Note: normally we might run DB operations synchronously here, 
    # but since it's a background task in FastAPI, we should use a fresh DB session
    from database import SessionLocal
    db = SessionLocal()
    
    try:
        active_destinations = [d for d in destinations if d.is_active]
        
        log_dict = {
            "endpoint_id": endpoint_id,
            "destination_id": None,
            "status_code": 200,
            "payload": payload,
            "response_body": "No active destinations configured. Payload received successfully."
        }
        log_dict.update(req_meta)
        
        if active_destinations:
            responses = []
            async with httpx.AsyncClient(timeout=10.0) as client:
                for dest in active_destinations:
                    try:
                        # Forward the payload
                        res = await client.post(dest.url, content=payload.encode('utf-8') if isinstance(payload, str) else payload)
                        responses.append(f"[{dest.url}] HTTP {res.status_code}: {res.text[:200]}")
                        log_dict["status_code"] = res.status_code # Store the last status code (or could compute average/min/max)
                    except Exception as e:
                        responses.append(f"[{dest.url}] ERROR: {str(e)}")
                        log_dict["status_code"] = 500
            
            log_dict["response_body"] = "\n".join(responses)
            
        # Log the single delivery
        log_entry = models.DeliveryLog(**log_dict)
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        
        log_dict['id'] = log_entry.id
        await manager.broadcast_to_endpoint(endpoint_id, log_dict)
        
    except Exception as e:
        print(f"Error in forwarder: {e}")
    finally:
        db.close()
