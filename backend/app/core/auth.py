import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin import firestore
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Dict, Any
import json
import os
from app.core.config import settings

def initialize_firebase():
    try:
        firebase_admin.get_app()
        print(f"Using Firebase Project ID: {settings.FIREBASE_PROJECT_ID}")
    except ValueError:
        cred = credentials.Certificate("/Users/san_23/Desktop/hsbc_hack/backend/hsbc-api-98ff3-firebase-adminsdk-fbsvc-ec5ffd6656.json")
        firebase_admin.initialize_app(cred)

initialize_firebase()

class User:
    def __init__(self, uid: str, email: str, display_name: Optional[str] = None, role: str = "analyst"):
        self.uid = uid
        self.email = email
        self.display_name = display_name
        self.role = role

async def verify_firebase_token(token: str) -> User:
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        display_name = decoded_token.get('name', '')
        role = get_user_role(uid)
        return User(uid=uid, email=email, display_name=display_name, role=role)
    except Exception as e:
        raise ValueError(f"Invalid token: {str(e)}")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        return await verify_firebase_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_user_role(uid: str) -> str:
    try:
        db = firestore.client()
        user_doc = db.collection('users').document(uid).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            return user_data.get('role', 'analyst')
        else:
            create_user_document(uid, 'analyst')
            return 'analyst'
    except Exception as e:
        return 'analyst'

def create_user_document(uid: str, role: str = 'analyst'):
    try:
        db = firestore.client()
        user_data = {
            'uid': uid,
            'role': role,
            'created_at': firestore.SERVER_TIMESTAMP,
            'last_login': firestore.SERVER_TIMESTAMP
        }
        db.collection('users').document(uid).set(user_data)
    except Exception as e:
        print(f"Error creating user document: {e}")

def update_user_last_login(uid: str):
    try:
        db = firestore.client()
        db.collection('users').document(uid).update({
            'last_login': firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        print(f"Error updating last login: {e}")

# --- Permissions ---
def get_user_permissions(role: str) -> Dict[str, bool]:
    permissions = {
        'analyst': {
            'upload_files': True,
            'view_dashboards': True,
            'create_aggregations': True,
            'export_data': True,
            'delete_own_files': True,
            'admin_access': False,
            'manage_users': False
        },
        'admin': {
            'upload_files': True,
            'view_dashboards': True,
            'create_aggregations': True,
            'export_data': True,
            'delete_own_files': True,
            'admin_access': True,
            'manage_users': True
        }
    }
    return permissions.get(role, permissions['analyst'])

async def check_permission(user: User, permission: str) -> bool:
    permissions = get_user_permissions(user.role)
    return permissions.get(permission, False)