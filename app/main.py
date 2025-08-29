import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.apis.main_router import main_router
from app.configs.app_config import config
from common.redis_infrastructure import infra

logger = logging.getLogger(__name__)


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    logging.getLogger("langchain").setLevel(logging.ERROR)
    logging.getLogger("langchain_core").setLevel(logging.ERROR)
    logging.getLogger("langchain_openai").setLevel(logging.ERROR)


def setup_infrastructure():
    """Setup all infrastructure components."""
    try:
        infra.setup()
        logger.info("Infrastructure setup completed successfully")
    except Exception as e:
        logger.error(f"Infrastructure setup failed: {e}")
        raise


def setup_middleware(app: FastAPI):
    """Setup application middleware."""
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    origins = config.allowed_origins()
    logger.info(f"Configured CORS origins: {origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )


def setup_routes(app: FastAPI):
    """Setup application routes."""
    app.include_router(main_router)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI()

    setup_logging()
    setup_infrastructure()
    setup_middleware(app)
    setup_routes(app)

    return app


def start_debugger():
    """Start debugger if configured."""
    if not config.DEBUGGER:
        return

    debugger = config.DEBUGGER.strip().lower()

    if debugger in {"pydev", "debugpy"}:
        try:
            import pydevd_pycharm

            pydevd_pycharm.settrace(
                host='host.docker.internal',
                port=config.DEBUGGER_PORT,
                stdoutToServer=True,
                stderrToServer=True,
                suspend=False
            )

            logger.info("PyCharm debugger attached.")
        except ImportError:
            logger.warning("pydevd_pycharm not installed.")
    elif debugger == "debugpy":
        try:
            import debugpy

            debugpy.listen(("0.0.0.0", config.DEBUGGER_PORT))

            logger.info(f"debugpy listening on {config.DEBUGGER_PORT}.")
        except ImportError:
            logger.warning("debugpy not installed.")


def main():
    """Main application entry point."""
    if config.ENV.upper() == "DEV" and config.DEBUGGER is not None:
        start_debugger()

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=config.PORT, reload=False)


def get_app():
    """Get the FastAPI app instance for WSGI servers."""
    return create_app()


app = create_app()


if __name__ == "__main__":
    main()
