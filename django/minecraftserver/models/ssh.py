from io import StringIO

from paramiko.rsakey import RSAKey
from django.db import models


class KeyPair(models.Model):
    public_key = models.TextField()
    private_key = models.TextField()
    digitalocean_id = models.PositiveIntegerField(blank=True, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-generated_at']

    @classmethod
    def generate_rsa_keypair(cls: type):
        new_key = RSAKey.generate(4096)
        private_key = StringIO()
        new_key.write_private_key(private_key)

        return cls.objects.create(
            public_key=' '.join([new_key.get_name(), new_key.get_base64()]),
            private_key=private_key.getvalue()
        )

    @classmethod
    def get_default_keypair(cls: type):
        """
        Either return the earliest created keypair or create a new one if no
        keypair objects exist
        """

        try:
            return cls.objects.all()[0]
        except IndexError:
            return cls.generate_rsa_keypair()

    def as_pkey(self: 'KeyPair'):
        private_key = StringIO(self.private_key)
        return RSAKey.from_private_key(private_key)
