import uvicorn
from app import app


if __name__ == "__main__":
    try:
        uvicorn.run(
            "main:app",
            host='127.0.0.1',
            port=8000,
            reload=True
        )
    except (KeyboardInterrupt, KeyError):
        pass
