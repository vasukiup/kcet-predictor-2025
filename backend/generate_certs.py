import datetime
import os
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

def generate_self_signed_cert():
    print("Generating RSA private key...")
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"kcet-predictor.local"),
    ])

    print("Building X.509 certificate with CA trust constraints...")
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(u"kcet-predictor.local")]),
        critical=False,
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None),
        critical=True,
    ).sign(key, hashes.SHA256())

    os.makedirs("certs", exist_ok=True)

    print("Saving private key to certs/kcet-predictor.local.key...")
    with open("certs/kcet-predictor.local.key", "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    print("Saving certificate to certs/kcet-predictor.local.crt...")
    with open("certs/kcet-predictor.local.crt", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("Success: Generated self-signed SSL certificates in certs/ directory!")

if __name__ == "__main__":
    generate_self_signed_cert()
