from app.core import config

def test_settings_load():
    settings = config.get_settings()
    assert settings is not None
