"""
Unit tests for cleaning functions (Phase 2.1).
"""

import pytest
from src.cleaners import clean_cuisines, clean_price, clean_rating


class TestCleanPrice:
    def test_comma_separated(self):
        assert clean_price("1,500") == 1500
        assert clean_price("2,000") == 2000

    def test_currency_symbols(self):
        assert clean_price("₹1,500") == 1500
        assert clean_price("$100") == 100
        assert clean_price("  500  ") == 500

    def test_plain_integer_string(self):
        assert clean_price("1500") == 1500
        assert clean_price("0") == 0

    def test_int_and_float_input(self):
        assert clean_price(1500) == 1500
        assert clean_price(100.0) == 100

    def test_none_and_empty(self):
        assert clean_price(None) is None
        assert clean_price("") is None
        assert clean_price("   ") is None

    def test_invalid_returns_none(self):
        assert clean_price("abc") is None
        assert clean_price("12.34.56") is None  # multiple decimals
        assert clean_price("1.5") is None  # decimal not allowed for price (integer only)

    def test_negative_returns_none(self):
        assert clean_price(-100) is None
        assert clean_price("-500") is None


class TestCleanRating:
    def test_slash_five_format(self):
        assert clean_rating("4.1/5") == 4.1
        assert clean_rating("4.5/5") == 4.5
        assert clean_rating("3/5") == 3.0

    def test_plain_number(self):
        assert clean_rating("4.5") == 4.5
        assert clean_rating("3") == 3.0
        assert clean_rating("0") == 0.0

    def test_numeric_input(self):
        assert clean_rating(4.1) == 4.1
        assert clean_rating(5) == 5.0

    def test_none_and_empty(self):
        assert clean_rating(None) is None
        assert clean_rating("") is None
        assert clean_rating("   ") is None

    def test_invalid_returns_none(self):
        assert clean_rating("abc") is None
        assert clean_rating("10/5") is None  # out of range
        assert clean_rating("-1") is None
        assert clean_rating("5.1") is None  # > 5

    def test_whitespace_around_slash(self):
        assert clean_rating("4.1 / 5") == 4.1

    def test_new_returns_zero(self):
        """Zomato uses 'NEW' for unrated restaurants; we retain as 0.0."""
        assert clean_rating("NEW") == 0.0
        assert clean_rating("new") == 0.0


class TestCleanCuisines:
    def test_comma_delimited(self):
        assert clean_cuisines("North Indian, Chinese") == ["North Indian", "Chinese"]
        assert clean_cuisines("Cafe, Bakery, Fast Food") == ["Cafe", "Bakery", "Fast Food"]

    def test_pipe_delimited(self):
        assert clean_cuisines("Cafe | Bakery") == ["Cafe", "Bakery"]

    def test_none_and_empty(self):
        assert clean_cuisines(None) == []
        assert clean_cuisines("") == []
        assert clean_cuisines("   ") == []

    def test_list_input(self):
        assert clean_cuisines(["North Indian", "Chinese"]) == ["North Indian", "Chinese"]
        assert clean_cuisines(["A", " ", "B"]) == ["A", "B"]

    def test_trimmed(self):
        assert clean_cuisines("  A  ,  B  ") == ["A", "B"]

    def test_single_cuisine(self):
        assert clean_cuisines("North Indian") == ["North Indian"]
