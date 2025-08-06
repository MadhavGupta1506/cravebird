from mangum import Mangum
from app.main import app  # Import your main FastAPI app

handler = Mangum(app)  # AWS Lambda-compatible handler
