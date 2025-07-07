"""
共通例外クラス定義

アプリケーション全体で使用する例外クラスを定義します。
"""

from typing import Any, Dict, Optional


class BaseApplicationError(Exception):
    """アプリケーション基底例外クラス"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """例外情報を辞書形式で返す"""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details
            }
        }


class DatabaseConnectionError(BaseApplicationError):
    """データベース接続エラー"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_CONNECTION_ERROR",
            details=details
        )


class ValidationError(BaseApplicationError):
    """バリデーションエラー"""
    
    def __init__(self, message: str, field: str = None, details: Optional[Dict[str, Any]] = None):
        if field:
            details = details or {}
            details["field"] = field
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details
        )


class AuthenticationError(BaseApplicationError):
    """認証エラー"""
    
    def __init__(self, message: str = "認証に失敗しました", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationError(BaseApplicationError):
    """認可エラー"""
    
    def __init__(self, message: str = "アクセス権限がありません", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class NotFoundError(BaseApplicationError):
    """リソース未発見エラー"""
    
    def __init__(self, message: str = "リソースが見つかりません", resource_type: str = None, details: Optional[Dict[str, Any]] = None):
        if resource_type:
            details = details or {}
            details["resource_type"] = resource_type
        
        super().__init__(
            message=message,
            error_code="NOT_FOUND_ERROR",
            details=details
        )


class BusinessLogicError(BaseApplicationError):
    """ビジネスロジックエラー"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            details=details
        )


class ExternalServiceError(BaseApplicationError):
    """外部サービスエラー"""
    
    def __init__(self, message: str, service_name: str = None, details: Optional[Dict[str, Any]] = None):
        if service_name:
            details = details or {}
            details["service_name"] = service_name
        
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details
        ) 