"""Tests for authentication testing utilities."""

from ulfblk_testing.auth import create_jwt_manager, create_test_token, generate_rsa_keys


class TestGenerateRSAKeys:
    def test_returns_pem_tuple(self):
        private_pem, public_pem = generate_rsa_keys()
        assert isinstance(private_pem, str)
        assert isinstance(public_pem, str)

    def test_private_key_is_valid_pem(self):
        private_pem, _ = generate_rsa_keys()
        assert private_pem.startswith("-----BEGIN PRIVATE KEY-----")

    def test_public_key_is_valid_pem(self):
        _, public_pem = generate_rsa_keys()
        assert public_pem.startswith("-----BEGIN PUBLIC KEY-----")

    def test_custom_key_size(self):
        private_pem, public_pem = generate_rsa_keys(key_size=4096)
        assert len(private_pem) > 1000


class TestCreateJWTManager:
    def test_creates_manager_with_provided_keys(self):
        private_pem, public_pem = generate_rsa_keys()
        manager = create_jwt_manager(private_pem=private_pem, public_pem=public_pem)
        assert manager.private_key == private_pem
        assert manager.public_key == public_pem

    def test_creates_manager_with_auto_generated_keys(self):
        manager = create_jwt_manager()
        assert manager.private_key is not None
        assert manager.public_key is not None


class TestCreateTestToken:
    def test_creates_decodable_token(self):
        manager = create_jwt_manager()
        token = create_test_token(manager, user_id="u-1", tenant_id="t-1")
        data = manager.decode_token(token)
        assert data.user_id == "u-1"
        assert data.tenant_id == "t-1"
        assert data.token_type == "access"
