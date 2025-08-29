import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.apis.main_api_router import api_router

logger = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def setup_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=["*"],
        expose_headers=["*"]
    )


def setup_routes(app: FastAPI):
    app.include_router(api_router)


def main():
    app = FastAPI(title="Auth Service", version="1.0.0")
    setup_logging()
    setup_middleware(app)
    setup_routes(app)

    uvicorn.run(app, host="0.0.0.0", port=8946)

if __name__ == '__main__':
    main()
