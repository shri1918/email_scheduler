import uvicorn
from config import settings
from api import app

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    ) 