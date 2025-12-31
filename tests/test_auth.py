"""Tests for authentication service."""
import pytest
from webapp.app.services.auth import hash_password, verify_password


class TestPasswordHashing:
    """Test password hashing functions."""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        password = "test_password_123"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_different_each_time(self):
        """Test that same password produces different hashes (salted)."""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2  # Should be different due to salt

    def test_verify_password_correct(self):
        """Test that verify_password returns True for correct password."""
        password = "correct_password"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test that verify_password returns False for wrong password."""
        password = "correct_password"
        hashed = hash_password(password)
        assert verify_password("wrong_password", hashed) is False

    def test_verify_password_empty(self):
        """Test handling of empty password."""
        hashed = hash_password("some_password")
        assert verify_password("", hashed) is False

    def test_hash_special_characters(self):
        """Test password with special characters."""
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_hash_unicode_password(self):
        """Test password with unicode characters."""
        password = "password_with_unicode_"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
