import httpx
import json
from sqlalchemy.orm import Session
import models
from ws_manager import manager

def get_system_setting(db: Session, key: str, default: str):
    setting = db.query(models.SystemSetting).filter(models.SystemSetting.key == key).first()
    if setting:
        return setting.value
    return default


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
                        elif auth_type == "query_param":
                            param_name = auth_config.get("param_name", "")
                            param_value = auth_config.get("param_value", "")
                            if param_name:
                                separator = "&" if "?" in dest.url else "?"
                                dest.url = f"{dest.url}{separator}{param_name}={param_value}"
                        elif auth_type == "hmac":
                            import hmac
                            import hashlib
                            header_name = auth_config.get("header_name", "X-Hub-Signature-256")
                            secret = auth_config.get("secret", "")
                            algorithm = auth_config.get("algorithm", "sha256")
                            
                            content_bytes = payload.encode('utf-8') if isinstance(payload, str) else payload
                            
                            if algorithm == "sha256":
                                signature = hmac.new(secret.encode(), content_bytes, hashlib.sha256).hexdigest()
                                dest_headers[header_name] = f"sha256={signature}"
                            elif algorithm == "sha1":
                                signature = hmac.new(secret.encode(), content_bytes, hashlib.sha1).hexdigest()
                                dest_headers[header_name] = f"sha1={signature}"

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
        
        # Enforce log limits
        try:
            max_logs = int(get_system_setting(db, "max_logs_per_endpoint", "1000"))
            log_count = db.query(models.DeliveryLog).filter(models.DeliveryLog.endpoint_id == endpoint_id).count()
            if log_count > max_logs:
                # Find IDs of oldest logs to delete
                logs_to_delete = log_count - max_logs
                oldest_logs = db.query(models.DeliveryLog.id).filter(
                    models.DeliveryLog.endpoint_id == endpoint_id
                ).order_by(models.DeliveryLog.created_at.asc()).limit(logs_to_delete).all()
                
                if oldest_logs:
                    old_ids = [log[0] for log in oldest_logs]
                    db.query(models.DeliveryLog).filter(models.DeliveryLog.id.in_(old_ids)).delete(synchronize_session=False)
                    db.commit()
        except Exception as e:
            print(f"Error enforcing log limits: {e}")
            db.rollback()
        
        log_dict['id'] = log_entry.id
        await manager.broadcast_to_endpoint(endpoint_id, log_dict)
        
    except Exception as e:
        print(f"Error in forwarder: {e}")
    finally:
        db.close()
