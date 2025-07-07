"""
メール送信サービス

Magic Link認証用のメール送信機能を提供
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional
import logging

from ..config.auth_config import AuthConfig

logger = logging.getLogger(__name__)

class EmailService:
    """メール送信サービスクラス"""

    def __init__(self):
        self.environment = os.getenv("APP_ENV", "development")
        
        # 環境別のSMTP設定
        if self.environment == "development":
            # 開発環境（MailHog）
            self.smtp_host = "localhost"
            self.smtp_port = 1025
            self.smtp_user = None
            self.smtp_password = None
            self.use_ssl = False
            self.from_email = "noreply@myou-kou.com"
        else:
            # 本番環境（ConoHa）
            self.smtp_host = os.getenv("SMTP_HOST", "mail1006.conoha.ne.jp")
            self.smtp_port = int(os.getenv("SMTP_PORT", "465"))
            self.smtp_user = os.getenv("SMTP_USER", "kobuchi1106@myou-kou.com")
            self.smtp_password = os.getenv("SMTP_PASSWORD", "kobuchi123!")
            self.use_ssl = True
            self.from_email = self.smtp_user

    async def send_magic_link(self, to_email: str, magic_link_url: str) -> bool:
        """
        Magic Linkメールを送信

        Args:
            to_email: 送信先メールアドレス
            magic_link_url: Magic Link URL

        Returns:
            bool: 送信成功フラグ
        """
        template = AuthConfig.MAIL_TEMPLATES["magic_link"]
        subject = template["subject"]
        body = template["template"].format(magic_link_url=magic_link_url)

        message = MIMEMultipart()
        message["From"] = self.from_email
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain", "utf-8"))

        try:
            if self.environment == "development":
                # 開発環境ではログ出力のみ
                logger.info(f"[DEV] メール送信シミュレーション:")
                logger.info(f"To: {to_email}")
                logger.info(f"Subject: {subject}")
                logger.info(f"Body: {body}")
                return True

            # 本番環境での送信
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_ssl=self.use_ssl,
                validate_certs=False  # 自己署名証明書対応
            )
            logger.info(f"メール送信成功: {to_email}")
            return True

        except aiosmtplib.SMTPException as e:
            logger.error(f"SMTP送信エラー: {str(e)}")
            logger.error(f"設定: host={self.smtp_host}, port={self.smtp_port}, user={self.smtp_user}")
            return False

        except Exception as e:
            logger.error(f"予期せぬエラー: {str(e)}")
            return False

    async def test_connection(self) -> Optional[str]:
        """
        SMTP接続テスト

        Returns:
            Optional[str]: エラーメッセージ（成功時はNone）
        """
        try:
            smtp = aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_ssl=self.use_ssl,
                validate_certs=False
            )
            await smtp.connect()
            if self.smtp_user and self.smtp_password:
                await smtp.login(self.smtp_user, self.smtp_password)
            await smtp.quit()
            return None
        except Exception as e:
            return str(e)


# シングルトンインスタンス
email_service = EmailService() 