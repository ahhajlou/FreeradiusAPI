import uvicorn
from app import app


if __name__ == "__main__":
    try:
        uvicorn.run(
            "main:app",
            host='0.0.0.0',
            port=8000,
            reload=False
        )
    except (KeyboardInterrupt, KeyError):
        pass
