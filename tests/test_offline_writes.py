"""Isolated SQLite tests for the real offline mixin. Never load production settings."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from uuid import uuid4

from django.conf import settings

settings.configure(
    SECRET_KEY="offline-test-only", USE_TZ=True,
    INSTALLED_APPS=["django.contrib.auth", "django.contrib.contenttypes"],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    REST_FRAMEWORK={"DEFAULT_AUTHENTICATION_CLASSES": [], "DEFAULT_PERMISSION_CLASSES": []},
)
import django
django.setup()
from django.contrib.auth.models import User
from django.db import connection, models
from rest_framework import generics, mixins, serializers
from rest_framework.test import APIRequestFactory, force_authenticate


class Receipt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request_id = models.UUIDField()
    fingerprint = models.CharField(max_length=64)
    status = models.PositiveSmallIntegerField()
    response = models.JSONField(null=True)

    class Meta:
        app_label = "offline_test"
        constraints = [models.UniqueConstraint(fields=["user", "request_id"], name="test_unique_offline_id")]


class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)

    class Meta:
        app_label = "offline_test"


# Substitute only the model module, so the production mixin executes unchanged.
package = types.ModuleType("offline_test")
sys.modules["offline_test"] = package
models_module = types.ModuleType("offline_test.models")
models_module.OfflineReceipt = Receipt
sys.modules["offline_test.models"] = models_module
spec = importlib.util.spec_from_file_location("offline_test.offline", Path(__file__).parents[1] / "guide/offline.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ["id", "value"]


class EntryView(module.OfflineWriteMixin, mixins.CreateModelMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EntrySerializer

    def get_queryset(self):
        return Entry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class OfflineWriteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with connection.schema_editor() as editor:
            for model in [User, Receipt, Entry]:
                editor.create_model(model)
        cls.user = User.objects.create(username="offline-test")
        cls.other = User.objects.create(username="other-test")

    def setUp(self):
        Receipt.objects.all().delete()
        Entry.objects.all().delete()

    def send(self, method, body, pk=None, user=None):
        path = f"/api/logbook/{str(pk) + '/' if pk else ''}"
        request = getattr(APIRequestFactory(), method)(path, body, format="json")
        force_authenticate(request, user=user or self.user)
        return EntryView.as_view()(request, **({"pk": pk} if pk else {}))

    def test_retry_returns_same_entry_once(self):
        payload = {"value": "one", "_offline_request_id": str(uuid4())}
        first = self.send("post", payload)
        second = self.send("post", payload)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(first.data, second.data)
        self.assertEqual(Entry.objects.count(), 1)
        self.assertEqual(Receipt.objects.count(), 1)

    def test_id_cannot_be_reused_with_new_payload(self):
        key = str(uuid4())
        self.send("post", {"value": "one", "_offline_request_id": key})
        response = self.send("post", {"value": "two", "_offline_request_id": key})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(Entry.objects.get().value, "one")

    def test_conflict_preserves_server_value(self):
        entry = Entry.objects.create(user=self.user, value="newer")
        response = self.send("patch", {"value": "offline", "_offline_request_id": str(uuid4()), "_offline_base": {"value": "older"}}, entry.pk)
        self.assertEqual(response.status_code, 409)
        entry.refresh_from_db()
        self.assertEqual(entry.value, "newer")
        self.assertEqual(Receipt.objects.count(), 0)

    def test_matching_baseline_updates_and_retry_replays(self):
        entry = Entry.objects.create(user=self.user, value="old")
        payload = {"value": "new", "_offline_request_id": str(uuid4()), "_offline_base": {"value": "old"}}
        self.assertEqual(self.send("patch", payload, entry.pk).status_code, 200)
        self.assertEqual(self.send("patch", payload, entry.pk).status_code, 200)
        entry.refresh_from_db()
        self.assertEqual(entry.value, "new")

    def test_delete_retries_without_deleting_another_entry(self):
        entry = Entry.objects.create(user=self.user, value="old")
        payload = {"_offline_request_id": str(uuid4()), "_offline_base": {"id": entry.pk, "value": "old"}}
        self.assertEqual(self.send("delete", payload, entry.pk).status_code, 204)
        self.assertEqual(self.send("delete", payload, entry.pk).status_code, 204)
        self.assertEqual(Entry.objects.count(), 0)

    def test_user_cannot_edit_another_users_entry(self):
        entry = Entry.objects.create(user=self.other, value="private")
        response = self.send("patch", {"value": "bad", "_offline_request_id": str(uuid4()), "_offline_base": {"value": "private"}}, entry.pk)
        self.assertEqual(response.status_code, 404)

    def test_missing_baseline_and_invalid_key_rejected(self):
        entry = Entry.objects.create(user=self.user, value="old")
        for payload in [{"value": "new", "_offline_request_id": str(uuid4())}, {"value": "new", "_offline_request_id": "invalid"}]:
            self.assertEqual(self.send("patch", payload, entry.pk).status_code, 400)

    def test_normal_online_writes_still_work(self):
        self.assertEqual(self.send("post", {"value": "online"}).status_code, 201)
        self.assertEqual(Receipt.objects.count(), 0)


if __name__ == "__main__":
    unittest.main()
