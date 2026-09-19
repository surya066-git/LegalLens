from app.config import Settings


def test_settings_defaults() -> None:
    settings = Settings()

    assert settings.app_name == "LegalLens AI"
    assert settings.app_env == "development"
    assert settings.cors_origins == ["http://localhost:3000"]


def test_cors_origins_can_be_comma_separated() -> None:
    settings = Settings(CORS_ORIGINS="http://localhost:3000,http://127.0.0.1:3000")

    assert settings.cors_origins == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

