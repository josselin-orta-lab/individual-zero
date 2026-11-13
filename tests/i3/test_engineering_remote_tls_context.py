"""R2.10: TLS CAS-writer construction must fail closed, without World or motor.

These tests check **client configuration**, not a deployed, independently
administered M11 host, authenticated writer certificate or remote high-water.
"""
import ssl
import unittest
import warnings

from i3.runtime.engineering_remote_witness import RemoteEngineeringWitness


class RemoteCASTLSConfigurationTests(unittest.TestCase):
    AUTHORITY = "d" * 64
    KEY = bytes(range(32))
    HTTPS = "https://witness.example.com:8443"
    LOOPBACK = "http://127.0.0.1:8443"

    def client(self, origin=None, *, context=None, **extra):
        return RemoteEngineeringWitness(
            self.HTTPS if origin is None else origin,
            key=self.KEY, authority_id=self.AUTHORITY,
            tls_context=context, **extra)

    @staticmethod
    def strict_context():
        context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
        # Require an explicit minimum for an operator-supplied context.
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        return context

    def test_strict_custom_https_context_is_accepted_without_network(self):
        context = self.strict_context()
        client = self.client(context=context)
        self.assertEqual(client.authority_id, self.AUTHORITY)
        self.assertTrue(context.check_hostname)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        self.assertGreaterEqual(context.minimum_version, ssl.TLSVersion.TLSv1_2)

    def test_unverified_https_context_denied_before_network(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with self.assertRaisesRegex(ValueError, "TLS CAS writer"):
            self.client(context=context)

    def test_hostname_disabled_but_cert_required_is_still_denied(self):
        context = self.strict_context()
        context.check_hostname = False
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        with self.assertRaisesRegex(ValueError, "hostname verification"):
            self.client(context=context)

    def test_legacy_tls_minimum_denied_even_with_hostname_and_ca(self):
        context = self.strict_context()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            context.minimum_version = ssl.TLSVersion.TLSv1_1
        with self.assertRaisesRegex(ValueError, "TLS CAS writer"):
            self.client(context=context)

    def test_unbounded_default_minimum_requires_explicit_minimum_for_custom_context(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        # MINIMUM_SUPPORTED does not itself prove that TLS <= 1.1 is blocked.
        if context.minimum_version == ssl.TLSVersion.MINIMUM_SUPPORTED:
            with self.assertRaisesRegex(ValueError, "TLS CAS writer"):
                self.client(context=context)

    def test_tls_context_rejected_on_plain_loopback_http(self):
        with self.assertRaisesRegex(ValueError, "TLS context cannot secure"):
            self.client(self.LOOPBACK, context=self.strict_context(),
                        allow_test_loopback_http=True)

    def test_bad_tls_context_type_denied(self):
        with self.assertRaisesRegex(ValueError, "real TLS context"):
            self.client(context=object())

    def test_default_https_is_still_constructible_and_plain_http_is_test_only(self):
        self.assertEqual(self.client().authority_id, self.AUTHORITY)
        with self.assertRaisesRegex(ValueError, "HTTPS mandatory"):
            self.client(self.LOOPBACK)
        self.assertEqual(
            self.client(self.LOOPBACK, allow_test_loopback_http=True).authority_id,
            self.AUTHORITY)
        with self.assertRaises(ValueError):
            self.client("http://example.com:8443", allow_test_loopback_http=True)


if __name__ == "__main__":
    unittest.main()
