import pytest
from unittest.mock import patch
from core.os.factory import get_os, _os_instance
import core.os.factory as factory

@pytest.fixture(autouse=True)
def reset_factory():
    """Reset the singleton instance before each test."""
    factory._os_instance = None
    yield
    factory._os_instance = None

def test_windows_os_detection():
    with patch('platform.system', return_value='Windows'):
        os_interface = get_os()
        assert os_interface.os_name == "Windows"
        assert os_interface.capabilities.supports_screen_capture is True

def test_linux_os_detection():
    with patch('platform.system', return_value='Linux'):
        os_interface = get_os()
        assert os_interface.os_name == "Linux"
        assert os_interface.capabilities.supports_screen_capture is True

def test_macos_os_detection():
    with patch('platform.system', return_value='Darwin'):
        os_interface = get_os()
        assert os_interface.os_name == "macOS"
        assert os_interface.capabilities.supports_global_hotkeys is False

def test_unsupported_os_fallback():
    with patch('platform.system', return_value='FreeBSD'):
        os_interface = get_os()
        assert os_interface.os_name == "Linux" # Fallback
