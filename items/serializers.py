from reflex_django.serializers import ReflexDjangoModelSerializer

from items.models import Transaction


class TransactionSerializer(ReflexDjangoModelSerializer):
    class Meta:
        model = Transaction
        fields = ("id", "name", "payment", "date", "status")
        read_only_fields = ("id",)
