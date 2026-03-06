from pollen_monitor.monitor import check_threshold


class TestCheckThreshold:

    def test_above_threshold(self):
        assert check_threshold(4, limit=3) is True

    def test_at_threshold(self):
        assert check_threshold(3, limit=3) is True

    def test_below_threshold(self):
        assert check_threshold(2, limit=3) is False

    def test_zero_level(self):
        assert check_threshold(0) is False

    def test_custom_limit(self):
        assert check_threshold(2, limit=2) is True
        assert check_threshold(1, limit=2) is False
