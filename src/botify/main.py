from fastapi import FastAPI
def create_app():
    app = FastAPI()
    return app


if __name__=="__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8860, log_level="debug", reload=True)