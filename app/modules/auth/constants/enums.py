from enum import Enum


class TokenTypeEnum(str, Enum):
    BEARER = "bearer"
    ACCESS = "access"
    REFRESH = "refresh"


class VerificationTypeEnum(str, Enum):
    EMAIL_SIGNUP = "email_signup"  # Verify email during registration
    EMAIL_LOGIN = "email_login"  # 2FA during login
    EMAIL_RECOVERY = "email_recovery"  # Password recovery
    SMS_SIGNUP = "sms_signup"  # Verify phone during registration
    SMS_LOGIN = "sms_login"  # 2FA during login
    SMS_RECOVERY = "sms_recovery"  # Password recovery via SMS
    MFA_TOTP = "mfa_totp"  # Time-based OTP (Google Authenticator)
    MFA_BACKUP = "mfa_backup"  # Backup codes for MFA
