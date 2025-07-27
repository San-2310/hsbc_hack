# HSBC Enterprise Dashboard - Setup Guide

This guide will help you set up the complete HSBC Enterprise Dashboard with both backend and frontend components.

## Prerequisites

- Python 3.9+
- Node.js 18+
- Firebase project
- Git

## 1. Firebase Setup

### Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project
3. Enable Authentication with Google provider
4. Create a Firestore database
5. Generate a service account key:
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Download the JSON file

### Configure Firebase

1. Copy the service account details to your backend environment
2. Add Firebase web app configuration to your frontend environment

## 2. Backend Setup

### Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Configuration

1. Copy `env.example` to `.env`
2. Update the Firebase configuration with your service account details
3. Set a secure `SECRET_KEY`

### Initialize Database

```bash
# The database will be automatically created on first run
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

### Run Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

## 3. Frontend Setup

### Install Dependencies

```bash
cd frontend
npm install
```

### Environment Configuration

1. Copy `env.example` to `.env`
2. Update the Firebase configuration with your web app details

### Run Frontend

```bash
npm start
```

The application will be available at `http://localhost:3000`

## 4. Project Structure

```
hsbc-dashboard/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   └── services/       # Business logic
│   ├── requirements.txt
│   └── env.example
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── context/        # React contexts
│   │   ├── pages/          # Page components
│   │   └── services/       # API services
│   ├── package.json
│   └── env.example
└── README.md
```

## 5. Features Overview

### Backend Features

- ✅ Firebase Authentication
- ✅ File upload and processing
- ✅ Data normalization
- ✅ Aggregation services
- ✅ Analytics generation
- ✅ Audit logging
- ✅ Role-based access control

### Frontend Features

- ✅ Modern React with TypeScript
- ✅ Firebase Authentication UI
- ✅ Responsive design with Tailwind CSS
- ✅ Dark/Light mode toggle
- ✅ Dashboard with metrics
- ✅ File upload interface
- ✅ Navigation and routing

### Security Features

- ✅ Firebase Authentication
- ✅ JWT token validation
- ✅ Role-based permissions
- ✅ Input validation
- ✅ CORS protection
- ✅ Audit trail

## 6. Development Workflow

### Backend Development

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm start
```

### Database Migrations

```bash
cd backend
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

## 7. Deployment

### Backend Deployment (Render/Railway)

1. Push code to repository
2. Set environment variables
3. Deploy with Python runtime
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend Deployment (Vercel/Netlify)

1. Push code to repository
2. Set environment variables
3. Deploy with Node.js runtime
4. Set build command: `npm run build`

## 8. Environment Variables

### Backend (.env)

```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY="your-private-key"
FIREBASE_CLIENT_EMAIL=your-service-account-email
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_CLIENT_X509_CERT_URL=your-cert-url

# Database
DATABASE_URL=your-database-url

# Security
SECRET_KEY=your-secret-key

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=104857600
```

### Frontend (.env)

```bash
# Firebase Configuration
REACT_APP_FIREBASE_API_KEY=your-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
REACT_APP_FIREBASE_APP_ID=your-app-id

# API
REACT_APP_API_URL=your-api-url
```

## 9. Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 10. Troubleshooting

### Common Issues

1. **Firebase Authentication Errors**

   - Verify service account credentials
   - Check Firebase project configuration
   - Ensure Authentication is enabled

2. **Database Connection Issues**

   - Verify DATABASE_URL
   - Check database permissions
   - Ensure database exists

3. **CORS Errors**

   - Update ALLOWED_ORIGINS in backend
   - Check frontend API URL configuration

4. **File Upload Issues**
   - Verify upload directory permissions
   - Check file size limits
   - Ensure supported file types

### Support

For issues and questions:

1. Check the logs for error messages
2. Verify environment configuration
3. Test API endpoints with Postman/curl
4. Check browser console for frontend errors

## 11. Next Steps

After successful setup:

1. **Customize the UI**: Modify colors, branding, and layout
2. **Add Features**: Implement additional data processing capabilities
3. **Enhance Security**: Add more granular permissions
4. **Scale**: Optimize for larger datasets and concurrent users
5. **Monitor**: Add logging and monitoring solutions

## 12. Production Checklist

- [ ] Set up production Firebase project
- [ ] Configure production database
- [ ] Set secure environment variables
- [ ] Enable HTTPS
- [ ] Set up monitoring and logging
- [ ] Configure backup strategies
- [ ] Test all features thoroughly
- [ ] Set up CI/CD pipeline
- [ ] Document deployment procedures
- [ ] Train users on the system

---

**Note**: This is a development setup. For production deployment, additional security measures, monitoring, and optimization should be implemented.
