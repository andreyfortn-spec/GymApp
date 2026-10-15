import os


def run(db_path, port):
    os.environ["GYM_DB"] = db_path
    import uvicorn
    from main import app
    config = uvicorn.Config(app, host="127.0.0.1", port=int(port),
                            log_level="warning", loop="asyncio", http="h11")
    uvicorn.Server(config).run()
