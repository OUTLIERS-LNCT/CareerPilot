from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_async_session

app = FastAPI(title="My FastAPI Backend", version="0.1.0")

@app.get("/")
def read_root():
    return {"message": "Backend Is working falwlessly now test someting else"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/db-check")
async def check_database(session: AsyncSession = Depends(get_async_session)):
    """Test endpoint to verify PostgreSQL connectivity."""
    try:
        result = await session.execute(text("SELECT 1"))
        db_version = result.scalar()
        return {"status": "success", "database_connected": True, "result": db_version}
    except Exception as e:
        return {"status": "error", "database_connected": False, "details": str(e)}


def main():
    import uvicorn

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()