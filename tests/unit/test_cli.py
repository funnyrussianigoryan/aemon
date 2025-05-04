import logging

from aemon.cli import main


def test_main_logs_message(caplog):
    with caplog.at_level(logging.INFO):
        main()
    assert "Test message" in caplog.text
