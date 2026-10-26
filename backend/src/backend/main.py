from fastapi import FastAPI

app = FastAPI(title="My FastAPI Backend", version="0.1.0")


@app.get("/")
def read_root():
    return {"message": "Welcome to your FastAPI backend powered by uv!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


def main():
    """Run the application using uvicorn when `uv run backend` is called."""
    import uvicorn

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()