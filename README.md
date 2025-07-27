# HSBC Enterprise Dashboard

**Enterprise-grade data processing and visualization platform for HSBC**

A comprehensive web platform that enables analysts, managers, and financial engineers to upload various datasets, normalize and aggregate them on-the-fly, and gain real-time visibility through an intuitive, interactive dashboard.

## Features

### **Input Flexibility**

- **Multiple File Types**: CSV, XLSX, XLS, JSON
- **API Integration**: Fetch data from external APIs with custom headers
- **URL Downloads**: Download files directly from URLs
- **Direct JSON**: Paste JSON data directly into the interface
- **Drag & Drop**: Intuitive file upload with progress tracking

### **Advanced Normalization (HSBC-Focused)**

- **Smart Schema Detection**: Automatic column type inference
- **HSBC-Specific Rules**:
  - Date standardization (ISO 8601 format)
  - Currency symbol removal and parsing
  - Transaction type mapping (CR/DR → Credit/Debit)
  - Account number standardization
- **Custom Rules**: User-defined column mappings and transformations
- **Data Quality Assessment**: Null detection, duplicate analysis, outlier identification

### **Advanced Aggregation**

- **Multiple Aggregation Types**:
  - Group By with multiple functions
  - Time Series analysis with various frequencies
  - Pivot tables
  - Summary statistics with financial metrics
- **HSBC Patterns**: Pre-built aggregation patterns for common use cases
- **Data Cleaning**: Handle missing values, outliers, and format inconsistencies
- **Real-time Processing**: Background task processing with progress tracking

### **Enterprise Security**

- **Firebase Authentication**: Google OAuth and email/password
- **Role-Based Access Control**: Analyst, Admin roles
- **JWT Token Validation**: Secure API access
- **Audit Logging**: Complete processing history
- **Data Isolation**: User-specific data access

### **Modern UI/UX**

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Mode**: Theme switching with HSBC branding
- **Real-time Notifications**: Toast messages for user feedback
- **Interactive Charts**: Recharts integration for data visualization
- **Keyboard Shortcuts**: Power user features

## Architecture

### **Backend (FastAPI)**

```
backend/
├── app/
│   ├── api/                    # API routes
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── upload.py          # Basic file upload
│   │   ├── enhanced_upload.py # Advanced upload (API, URL, JSON)
│   │   ├── processing.py      # Basic processing
│   │   ├── enhanced_processing.py # Advanced processing
│   │   └── dashboard.py       # Dashboard data
│   ├── core/                  # Core functionality
│   │   ├── config.py         # Application settings
│   │   ├── auth.py           # Firebase authentication
│   │   └── database.py       # Database configuration
│   ├── models/               # Database models
│   │   ├── file_upload.py    # File metadata
│   │   ├── processing_log.py # Processing history
│   │   └── user_session.py   # User sessions
│   └── services/             # Business logic
│       ├── enhanced_file_processor.py    # File processing
│       └── enhanced_aggregation_service.py # Data aggregation
```

### **Frontend (React + TypeScript)**

```
frontend/
├── src/
│   ├── components/           # Reusable components
│   │   ├── Layout/          # Layout components
│   │   ├── Upload/          # Upload components
│   │   ├── Aggregation/     # Aggregation components
│   │   └── UI/              # UI components
│   ├── pages/               # Page components
│   ├── context/             # React context
│   └── services/            # API services
```

## Database Schema

### **Tables**

#### 1. `file_uploads`

```sql
CREATE TABLE file_uploads (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_type VARCHAR NOT NULL,
    file_size INTEGER NOT NULL,
    status VARCHAR NOT NULL,
    total_rows INTEGER,
    total_columns INTEGER,
    schema_info TEXT,
    metadata TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);
```

#### 2. `processing_logs`

```sql
CREATE TABLE processing_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id VARCHAR NOT NULL,
    user_id VARCHAR NOT NULL,
    operation VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    details TEXT,
    created_at TIMESTAMP NOT NULL
);
```

#### 3. `user_sessions`

```sql
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR NOT NULL,
    session_token VARCHAR NOT NULL,
    ip_address VARCHAR,
    user_agent TEXT,
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL
);
```

## Setup Instructions

### **Prerequisites**

- Python 3.8+
- Node.js 16+
- Firebase project
- SQLite (development) or PostgreSQL (production)

### **1. Clone and Setup**

```bash
git clone <repository-url>
cd hsbc-dashboard
```

### **2. Backend Setup**

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### **3. Frontend Setup**

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
```

### **4. Firebase Configuration**

#### Create Firebase Project:

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create new project
3. Enable Authentication (Google, Email/Password)
4. Create Firestore database
5. Generate service account key

#### Configure Environment Variables:

**Backend (.env):**

```env
# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com

# Database
DATABASE_URL=sqlite:///./hsbc_dashboard.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=104857600

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:3001"]
```

**Frontend (.env):**

```env
# Firebase
REACT_APP_FIREBASE_API_KEY=your-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=123456789
REACT_APP_FIREBASE_APP_ID=1:123456789:web:abcdef

# Backend API
REACT_APP_API_URL=http://localhost:8000
```

### **5. Run the Application**

#### Start Backend:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Frontend:

```bash
cd frontend
npm start
```

### **6. Access the Application**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📊 API Endpoints

### **Authentication**

- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### **File Upload**

- `POST /api/enhanced-upload/file` - Upload file
- `POST /api/enhanced-upload/api` - Upload from API
- `POST /api/enhanced-upload/url` - Upload from URL
- `POST /api/enhanced-upload/json` - Upload JSON data
- `GET /api/enhanced-upload/schema/{file_id}` - Get file schema
- `GET /api/enhanced-upload/files` - List user files

### **Data Processing**

- `POST /api/enhanced-processing/normalize` - Normalize data
- `POST /api/enhanced-processing/aggregate` - Aggregate data
- `POST /api/enhanced-processing/export` - Export results
- `GET /api/enhanced-processing/suggestions/{file_id}` - Get suggestions
- `GET /api/enhanced-processing/logs/{file_id}` - Get processing logs

### **Dashboard**

- `GET /api/dashboard/overview` - Dashboard overview
- `GET /api/dashboard/analytics` - Analytics data
- `GET /api/dashboard/insights` - AI insights

## 🔧 Development

### **Running Tests**

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### **Code Formatting**

```bash
# Backend
cd backend
black app/
isort app/

# Frontend
cd frontend
npm run format
```

### **Database Migrations**

```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## 🚀 Deployment

### **Backend Deployment (Render/Railway)**

1. Connect your repository
2. Set environment variables
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### **Frontend Deployment (Vercel/Netlify)**

1. Connect your repository
2. Set environment variables
3. Build command: `npm run build`
4. Output directory: `build`

## 🔒 Security Features

- **Firebase Authentication**: Secure user authentication
- **JWT Tokens**: Stateless authentication
- **Role-Based Access**: User permissions
- **Input Validation**: Pydantic models
- **SQL Injection Protection**: SQLAlchemy ORM
- **CORS Protection**: Configured origins
- **File Upload Security**: Type and size validation
- **Audit Logging**: Complete activity tracking

## 📈 Performance Features

- **Async Processing**: Background tasks for heavy operations
- **Database Indexing**: Optimized queries
- **File Streaming**: Efficient file handling
- **Caching**: Redis integration (optional)
- **CDN Ready**: Static asset optimization
- **Lazy Loading**: Component-level code splitting

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Built with ❤️ for HSBC Enterprise Solutions**
