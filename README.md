diff --git a/README.md b/README.md
new file mode 100644
index 0000000000000000000000000000000000000000..645cd7002acb4184caedeb253176e6bd694a1a23
--- /dev/null
+++ b/README.md
@@ -0,0 +1,60 @@
+# CreditNavigator Backend (Local Setup)
+
+This project uses a FastAPI backend in `backend/`.
+
+## 1) Go to backend folder
+
+```bash
+cd backend
+```
+
+## 2) Create and activate virtual environment
+
+```bash
+python -m venv .venv
+source .venv/bin/activate
+```
+
+> Windows (PowerShell):
+>
+> ```powershell
+> .venv\Scripts\Activate.ps1
+> ```
+
+## 3) Install dependencies
+
+```bash
+pip install -r requirements.txt
+```
+
+## 4) Create `.env`
+
+Create `backend/.env` with your Vertex AI values:
+
+```env
+VERTEX_PROJECT_ID=your-gcp-project-id
+VERTEX_LOCATION=us-central1
+VERTEX_ENDPOINT_ID=your-vertex-endpoint-id
+```
+
+Optional (if your frontend runs on a different URL):
+
+```env
+FRONTEND_URL=http://localhost:5173
+```
+
+## 5) Run backend locally
+
+```bash
+uvicorn main:app --reload --host 0.0.0.0 --port 8000
+```
+
+Backend will be available at:
+- API root: `http://localhost:8000`
+- Swagger docs: `http://localhost:8000/docs`
+
+## Quick health check
+
+```bash
+curl http://localhost:8000/docs
+```
