"""Configuração centralizada de logs estruturados usando Loguru."""

import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    """Redireciona logs do módulo `logging` padrão para o Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())


def setup_logger(debug: bool = False) -> None:
    """
    Configura o logger do sistema.

    Args:
        debug: Se True, define nível para DEBUG, senão INFO.
    """
    logger.remove()

    level = "DEBUG" if debug else "INFO"

    # Console (stderr junto com uvicorn)
    logger.add(
        sys.stderr,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        level=level,
    )

    # Arquivo (JSON serializado)
    logger.add(
        "logs/app.log",
        rotation="500 MB",
        retention="10 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        serialize=True,
    )

    # Intercepta logs do módulo `logging` padrão (FastAPI, uvicorn, etc.)
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    logger.info("Logging configurado com sucesso!")


# Exportar o logger para uso global
log = logger
