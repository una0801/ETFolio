"""
로깅 설정
애플리케이션 전체에서 사용할 로거 설정
"""
import logging
import sys
from pathlib import Path

# 로그 디렉토리 생성
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 로그 포맷 설정
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 로거 설정 함수
def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    로거 생성 및 설정
    
    Args:
        name: 로거 이름 (보통 __name__ 사용)
        level: 로그 레벨
    
    Returns:
        설정된 로거
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 이미 핸들러가 있으면 추가하지 않음 (중복 방지)
    if logger.handlers:
        return logger
    
    # 포매터 생성
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # 콘솔 핸들러 (터미널 출력)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (파일에 저장)
    file_handler = logging.FileHandler(
        LOG_DIR / "etfolio.log",
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 에러 로그 별도 파일
    error_handler = logging.FileHandler(
        LOG_DIR / "error.log",
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger


# 기본 로거
app_logger = setup_logger("etfolio")

