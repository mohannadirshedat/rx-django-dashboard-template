from decouple import config
import json


class SecretManager:
    """ Manages secrets.
        Secrets are cached in the secrets attribute and can be accessed with the get_secret method.

        When a secret is updated, the cache is NOT updated.
        This means that the application needs to be restarted to get the new value.
    """

    def __init__(self, with_external_provider=False):
        self.with_external_provider = with_external_provider
        self.setup()

        if self.with_external_provider:
            self.provider_secrets = self.get_all_provider_secrets()

        self.secrets = {}

    def setup(self):
        pass

    def get_secret(self, secret_name, default='RAISE_EXCEPTION'):
        """ Returns the value of a secret. Raises an exception if the secret is not found.
            If default is provided, it will be returned instead of raising an exception.

            The secret is first checked in the cache, then in the .env file, then in the external provider (if any)
        """

        if secret_name in self.secrets:
            return self.secrets[secret_name]
        else:
            secret = self.get_secret_from_env_file(secret_name)
            if secret is None and self.with_external_provider: secret = self.get_secret_from_provider(secret_name)
            if secret is None:
                if default != 'RAISE_EXCEPTION':
                    return default
                else:
                    raise Exception(f"Secret {secret_name} not found.")
            return secret

    def get_secret_from_env_file(self, secret_name):
        """ Returns the value of a secret from the .env file. """

        secret = config(secret_name, None)
        if secret is not None:
            self.secrets[secret_name] = self.parse_value(secret)
            return self.secrets[secret_name]

        return None

    def get_secret_from_provider(self, secret_name):
        """ Returns the value of a secret from Infisical. """

        if secret_name in self.provider_secrets:
            self.secrets[secret_name] = self.provider_secrets[secret_name]
            return self.secrets[secret_name]

        return None

    def get_all_provider_secrets(self):
        if self.with_external_provider:
            raise NotImplementedError("get_all_provider_secrets method must be implemented in the child class.")

    def parse_value(self, value):
        """ Parses a secret value. """

        # Check if value is a bool and return it.
        if value in ['True', 'true', 'False', 'false']:
            return value in ['True', 'true']

        # Check if value is an int and return it.
        try:
            return int(value)
        except ValueError:
            pass

        # Check if value is a float and return it.
        try:
            return float(value)
        except ValueError:
            pass

        # Check if value is a JSON string and return it.
        try:
            return json.loads(value)
        except ValueError:
            pass

        # If we couldn't parse the value, return it as is.
        return value


class EnvSecretManager(SecretManager):
    """ Manages secrets from env file.
        Secrets are cached in the secrets attribute and can be accessed with the get_secret method.

        When a secret is updated, the cache is NOT updated.
        This means that the application needs to be restarted to get the new value.
    """

secret_manager = EnvSecretManager()