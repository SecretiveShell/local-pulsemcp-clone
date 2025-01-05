from fastapi import FastAPI
from download import router as download_router
from endpoints import router as endpoints_router

app = FastAPI()

app.include_router(download_router)
app.include_router(endpoints_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7890)