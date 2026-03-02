"""
unit tests — auth service + ml pricing engine.
"""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock

from app.services.auth import hash_password, verify_password, create_access_token, decode_token
from app.services.ml_engine import PricingEngine
from app.models.event import EventType


# auth tests
class TestAuth:
    def test_hash_and_verify(self):
        hashed = hash_password("mypassword")
        assert hashed != "mypassword"
        assert verify_password("mypassword", hashed)
        assert not verify_password("wrong", hashed)

    def test_create_and_decode_token(self):
        token = create_access_token("user-123")
        payload = decode_token(token)
        assert payload["sub"] == "user-123"
        assert payload["type"] == "access"

    def test_decode_invalid_token(self):
        with pytest.raises(ValueError):
            decode_token("invalid.token.here")


# pricing engine tests
class TestPricingEngine:
    def _make_event(self, **overrides):
        defaults = {
            "id": "evt-1",
            "event_type": EventType.CAMP,
            "base_price": 100.0,
            "current_price": 100.0,
            "capacity": 20,
            "booked_count": 10,
            "start_date": date.today() + timedelta(days=14),
        }
        defaults.update(overrides)
        mock = MagicMock(**defaults)
        # make enum accessible as attribute
        mock.event_type = defaults["event_type"]
        mock.base_price = defaults["base_price"]
        mock.current_price = defaults["current_price"]
        mock.capacity = defaults["capacity"]
        mock.booked_count = defaults["booked_count"]
        mock.start_date = defaults["start_date"]
        return mock

    def _make_booking(self, **overrides):
        defaults = {"status": MagicMock(value="confirmed"), "price_paid": 100.0}
        defaults.update(overrides)
        return MagicMock(**defaults)

    def test_recommendation_returns_required_fields(self):
        engine = PricingEngine()
        event = self._make_event()
        bookings = [self._make_booking() for _ in range(10)]

        rec = engine.generate_recommendation(event, bookings, competition_proxy=5.0)

        assert "suggested_price" in rec
        assert "confidence" in rec
        assert "explanation" in rec
        assert "price_change_pct" in rec
        assert "drivers" in rec
        assert isinstance(rec["suggested_price"], (int, float))
        assert 0 <= rec["confidence"] <= 100

    def test_high_demand_increases_price(self):
        engine = PricingEngine()
        event = self._make_event(booked_count=18, capacity=20)  # 90% fill
        bookings = [self._make_booking() for _ in range(18)]

        rec = engine.generate_recommendation(event, bookings, competition_proxy=3.0)
        assert rec["suggested_price"] >= event.current_price

    def test_low_demand_may_decrease_price(self):
        engine = PricingEngine()
        event = self._make_event(booked_count=3, capacity=20)  # 15% fill
        bookings = [self._make_booking() for _ in range(3)]

        rec = engine.generate_recommendation(event, bookings, competition_proxy=8.0)
        assert rec["suggested_price"] <= event.current_price

    def test_price_bounds_enforced(self):
        engine = PricingEngine()
        event = self._make_event(base_price=100.0, current_price=100.0)
        bookings = [self._make_booking() for _ in range(20)]

        rec = engine.generate_recommendation(event, bookings, competition_proxy=1.0)
        assert rec["suggested_price"] >= 50.0  # 50% floor
        assert rec["suggested_price"] <= 200.0  # 200% ceiling

    def test_private_event_type_premium(self):
        engine = PricingEngine()
        event_camp = self._make_event(event_type=EventType.CAMP, booked_count=10)
        event_private = self._make_event(event_type=EventType.PRIVATE, booked_count=10)
        bookings = [self._make_booking() for _ in range(10)]

        rec_camp = engine.generate_recommendation(event_camp, bookings, competition_proxy=5.0)
        rec_private = engine.generate_recommendation(event_private, bookings, competition_proxy=5.0)

        # private should generally have higher/equal pricing multiplier
        assert rec_private["suggested_price"] >= rec_camp["suggested_price"] - 10  # reasonable tolerance

    def test_what_if_simulator(self):
        engine = PricingEngine()
        event = self._make_event()
        bookings = [self._make_booking() for _ in range(10)]

        result = engine.what_if_simulate(event, bookings, competition_proxy=5.0, test_prices=[80, 100, 120, 140])

        assert len(result) == 4
        for point in result:
            assert "price" in point
            assert "projected_demand" in point
            assert "projected_revenue" in point
