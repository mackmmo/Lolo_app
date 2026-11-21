"""Retry-safe personal writes. No credentials or tokens are stored in receipts."""
import hashlib
import json
from uuid import UUID

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework.response import Response

from .models import OfflineReceipt


class OfflineWriteMixin:
    def create(self, request, *args, **kwargs):
        return self._offline_write(request, lambda: super(OfflineWriteMixin, self).create(request, *args, **kwargs))

    def update(self, request, *args, **kwargs):
        return self._offline_write(request, lambda: super(OfflineWriteMixin, self).update(request, *args, **kwargs))

    def destroy(self, request, *args, **kwargs):
        return self._offline_write(request, lambda: super(OfflineWriteMixin, self).destroy(request, *args, **kwargs))

    def _offline_write(self, request, operation):
        key = request.data.get("_offline_request_id")
        if not key:
            with transaction.atomic():
                get_user_model().objects.select_for_update().get(pk=request.user.pk)
                return operation()
        try:
            key = str(UUID(str(key)))
        except (ValueError, TypeError):
            return Response({"detail": "Invalid offline request ID."}, status=400)
        fingerprint = hashlib.sha256(json.dumps(
            [request.method, request.path, request.data], sort_keys=True, separators=(",", ":")
        ).encode()).hexdigest()
        data = request.data.copy()
        data.pop("_offline_request_id", None)
        baseline = data.pop("_offline_base", None)
        request._full_data = data
        with transaction.atomic():
            # Serialize this user's sync requests, including the first attempt.
            get_user_model().objects.select_for_update().get(pk=request.user.pk)
            receipt = OfflineReceipt.objects.filter(user=request.user, request_id=key).first()
            if receipt:
                if receipt.fingerprint != fingerprint:
                    return Response({"detail": "Offline request ID reused with different data."}, status=409)
                return Response(receipt.response, status=receipt.status)
            if request.method in ("PATCH", "DELETE"):
                instance = self.get_object()
                # Require the original values for every field an offline edit overwrites.
                required = set(data) if request.method == "PATCH" else set(self.get_serializer(instance).data)
                if not isinstance(baseline, dict) or not required.issubset(baseline):
                    return Response({"detail": "Original values required for offline changes."}, status=400)
                current = self.get_serializer(instance).data
                conflicts = [field for field in required if current.get(field) != baseline[field]]
                if conflicts:
                    return Response({"detail": "This entry changed on another device. Resolve before syncing.", "fields": conflicts}, status=409)
            try:
                with transaction.atomic():
                    response = operation()
            except IntegrityError:
                return Response({"detail": "An entry already exists or changed. Resolve before syncing."}, status=409)
            if response.status_code < 400:
                OfflineReceipt.objects.create(user=request.user, request_id=key,
                    fingerprint=fingerprint, status=response.status_code, response=response.data)
            return response
