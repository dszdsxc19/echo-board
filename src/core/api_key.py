"""API key validation and user feedback for Echo-Board."""

import os
import re
from typing import Optional, Tuple

import httpx

from .config import settings
from .logging import EchoBoardLogger

logger = EchoBoardLogger.get_logger("api_key")


class APIKeyValidator:
    """Validate API keys and provide user feedback."""

    @staticmethod
    def validate_gemini_api_key(api_key: Optional[str] = None) -> Tuple[bool, str]:
        """Validate Gemini API key.

        Args:
            api_key: API key to validate. If None, uses settings.

        Returns:
            Tuple of (is_valid, message)
        """
        key = api_key or settings.llm.api_key

        # Check if key exists
        if not key or key == "your_gemini_api_key_here":
            return False, "❌ API密钥未设置。请在.env文件中设置GEMINI_API_KEY"

        # Check key format
        if not APIKeyValidator._check_key_format(key, "gemini"):
            return False, "❌ API密钥格式不正确。Gemini密钥通常以AIza开头"

        # Test the key by making a simple API call
        try:
            is_valid = APIKeyValidator._test_gemini_key(key)
            if is_valid:
                return True, "✅ API密钥有效"
            else:
                return False, "❌ API密钥无效或已过期"

        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return False, f"❌ 验证API密钥时出错: {str(e)}"

    @staticmethod
    def _check_key_format(key: str, key_type: str) -> bool:
        """Check if API key format is valid.

        Args:
            key: API key to check
            key_type: Type of API key (gemini)

        Returns:
            True if format is valid
        """
        if key_type == "gemini":
            # Gemini API keys typically start with AIza
            return bool(re.match(r"^AIza[0-9A-Za-z\-_]{35}$", key))

        return False

    @staticmethod
    def _test_gemini_api_call(api_key: str) -> bool:
        """Test Gemini API with a simple call.

        Args:
            api_key: API key to test

        Returns:
            True if API call succeeds
        """
        url = "https://generativelanguage.googleapis.com/v1beta/models"
        params = {"key": api_key}

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, params=params)

        return response.status_code == 200

    @staticmethod
    def _test_gemini_key(key: str) -> bool:
        """Test if Gemini API key works.

        Args:
            key: API key to test

        Returns:
            True if key is valid
        """
        try:
            return APIKeyValidator._test_gemini_api_call(key)
        except Exception as e:
            logger.error(f"API test failed: {e}")
            return False

    @staticmethod
    def check_api_status() -> dict:
        """Check overall API status.

        Returns:
            Dictionary with status information
        """
        status = {
            "gemini_configured": False,
            "gemini_valid": False,
            "notes_directory_exists": False,
            "vector_store_initialized": False,
        }

        # Check Gemini API
        if settings.llm.api_key:
            is_valid, _ = APIKeyValidator.validate_gemini_api_key()
            status["gemini_configured"] = True
            status["gemini_valid"] = is_valid

        # Check notes directory
        if settings.notes.directory:
            status["notes_directory_exists"] = os.path.exists(settings.notes.directory)

        return status

    @staticmethod
    def get_setup_instructions() -> str:
        """Get instructions for setting up API keys.

        Returns:
            Setup instructions in Chinese
        """
        return """
## API密钥设置说明

### 步骤1: 获取Gemini API密钥

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 使用您的Google账号登录
3. 点击"Create API Key"创建新的API密钥
4. 复制生成的API密钥

### 步骤2: 配置环境变量

1. 复制 `.env.example` 为 `.env`:
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，添加您的API密钥:
   ```
   GEMINI_API_KEY=您复制的API密钥
   ```

3. 保存文件并重启应用程序

### 验证设置

启动应用程序后，系统会自动验证API密钥。如果看到"✅ API密钥有效"，说明配置成功。

### 故障排除

- 如果看到"❌ API密钥无效"，请检查密钥是否正确复制
- 如果看到"❌ 网络错误"，请检查您的网络连接
- 确保API密钥没有过期或被撤销
        """.strip()


# Helper functions
def validate_api_key_at_startup():
    """Validate API key at application startup.

    Returns:
        Tuple of (is_valid, message)
    """
    logger.info("Validating API key at startup...")
    return APIKeyValidator.validate_gemini_api_key()
