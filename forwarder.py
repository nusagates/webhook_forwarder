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
            
            # Extract method and headers, remove problematic headers
            method = req_meta.get("http_method", "POST").upper()
            
            # Default to POST if GET is received (since we want to forward the payload)
            if method == "GET":
                method = "POST"
                
            headers = {}
            try:
                original_headers = json.loads(req_meta.get("headers", "{}"))
                for k, v in original_headers.items():
                    # Skip hop-by-hop headers and host
                    if k.lower() not in ['host', 'content-length', 'connection', 'keep-alive', 'transfer-encoding', 'upgrade']:
                        headers[k] = v
            except:
                pass
                
            async with httpx.AsyncClient(timeout=10.0) as client:
                for dest in active_destinations:
                    try:
                        import base64
                        dest_headers = headers.copy()
                        auth_type = dest.auth_type
                        auth_config_str = dest.auth_config or "{}"
                        
                        try:
                            auth_config = json.loads(auth_config_str)
                        except:
                            auth_config = {}
                            
                        if auth_type == "basic":
                            username = auth_config.get("username", "")
                            password = auth_config.get("password", "")
                            auth_str = base64.b64encode(f"{username}:{password}".encode()).decode()
                            dest_headers["Authorization"] = f"Basic {auth_str}"
                        elif auth_type == "bearer":
                            token = auth_config.get("token", "")
                            dest_headers["Authorization"] = f"Bearer {token}"
                        elif auth_type == "custom_header":
                            header_name = auth_config.get("header_name", "")
                            header_value = auth_config.get("header_value", "")
                            if header_name:
                                dest_headers[header_name] = header_value

                        # Forward the payload with original headers and method
                        res = await client.request(
                            method, 
                            dest.url, 
                            content=payload.encode('utf-8') if isinstance(payload, str) else payload,
                            headers=dest_headers
                        )
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
