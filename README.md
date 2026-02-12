🚀 Development & Testing Guide
1️⃣ Clone the Repository
git clone https://github.com/sachinchoudharyy/voice-verification.git
cd voice-verification

2️⃣ Backend Setup (FastAPI)
Create virtual environment
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Mac/Linux

Install dependencies
pip install -r requirements.txt


If no requirements.txt exists:

pip install fastapi uvicorn python-multipart

3️⃣ Frontend Setup (React - Development Mode)
cd ../frontend
npm install
npm start


Frontend will run at:

http://localhost:3000

4️⃣ Run Backend (Development Mode)

From backend folder:

uvicorn app.main:app --reload


Backend runs at:

http://localhost:8000


Swagger docs:

http://localhost:8000/docs

📱 Testing On Mobile (Using ngrok)
Step 1 – Stop React dev server (if running)

We test using production build.

Step 2 – Build React
cd frontend
npm run build


Copy the generated build folder into:

backend/app/


Ensure structure:

backend/app/build/index.html
backend/app/build/static/

Step 3 – Run Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000


Test locally:

http://localhost:8000

Step 4 – Start ngrok

In a new terminal:

ngrok http 8000


Copy the HTTPS forwarding URL.

Step 5 – Open On Mobile

Open this URL on your mobile browser:

https://your-ngrok-url.ngrok-free.dev

🔄 After Making Frontend Changes

Whenever you modify React code:

cd frontend
npm run build


Replace old backend/app/build folder with new one.

Restart backend.
