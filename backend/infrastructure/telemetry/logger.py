"""Configuração centralizada de logs estruturados usando Loguru."""
import sys
from loguru import logger


def setup_logger(debug: bool = False) -> None:
    """
    Configura o logger do sistema.

    Args:
        debug: Se True, define nível para DEBUG, senão INFO.
    """
    logger.remove()
    
    level = "DEBUG" if debug else "INFO"
    
    # Log estruturado no console
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
    )

    # Log em arquivo (opcional para produção)
    logger.add(
        "logs/app.log",
        rotation="500 MB",
        retention="10 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        serialize=True # JSON format para fácil processamento
    )

    logger.info("Logging configurado com sucesso!")


# Exportar o logger para uso global
log = logger
