import hashlib
import json
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from .models import MailboxInvestigation


class QMailUploadAndIngestionTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Set portal session auth so middleware permits access
        session = self.client.session
        session["portal_authenticated"] = True
        session.save()

    def test_initiate_upload_and_chunked_streaming(self):
        # 1. Test initiating upload
        init_url = reverse("q_mail:upload_initiate")
        payload = {
            "audit_ref": "AUD-TEST-2026-001",
            "audit_name": "Test Forensic Audit",
            "auditee_name": "John Doe",
            "auditee_email": "john.doe@enterprise.internal",
            "auditee_department": "Finance",
            "auditee_designation": "Director",
            "pst_file_name": "sample_evidence.pst",
            "file_size_bytes": 3000,
        }
        res = self.client.post(
            init_url,
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        mailbox_id = data["mailbox_id"]

        # Verify DB object
        inv = MailboxInvestigation.objects.get(id=mailbox_id)
        self.assertEqual(inv.audit_ref, "AUD-TEST-2026-001")
        self.assertEqual(inv.auditee_name, "John Doe")

        # 2. Test uploading file in 3 binary chunks
        chunk_url = reverse("q_mail:upload_chunk")
        full_content = b"PST_HEADER_DUMMY_BINARY_DATA_" * 100
        expected_sha256 = hashlib.sha256(full_content).hexdigest()

        chunk_size = len(full_content) // 3
        chunks = [
            full_content[:chunk_size],
            full_content[chunk_size : chunk_size * 2],
            full_content[chunk_size * 2 :],
        ]

        for idx, chunk_bytes in enumerate(chunks):
            chunk_file = SimpleUploadedFile(
                f"chunk_{idx}.bin", chunk_bytes, content_type="application/octet-stream"
            )
            chunk_res = self.client.post(
                chunk_url,
                data={
                    "mailbox_id": mailbox_id,
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                    "chunk": chunk_file,
                },
            )
            self.assertEqual(chunk_res.status_code, 200)
            chunk_data = chunk_res.json()
            self.assertTrue(chunk_data["success"])

            if idx == len(chunks) - 1:
                self.assertTrue(chunk_data["is_completed"])
                self.assertEqual(chunk_data["file_sha256"], expected_sha256)

        # 3. Verify file on disk
        inv.refresh_from_db()
        expected_path = Path(settings.MEDIA_ROOT) / "uploads" / "pst" / f"{mailbox_id}.pst"
        self.assertTrue(expected_path.exists())
        self.assertEqual(inv.file_sha256, expected_sha256)
        self.assertEqual(inv.file_size_bytes, len(full_content))

        # 4. Test progress API
        progress_url = reverse("q_mail:progress_api", kwargs={"mailbox_id": mailbox_id})
        prog_res = self.client.get(progress_url)
        self.assertEqual(prog_res.status_code, 200)
        self.assertEqual(prog_res.json()["audit_ref"], "AUD-TEST-2026-001")

        # 5. Test paginated messages API
        messages_url = reverse("q_mail:messages_api", kwargs={"mailbox_id": mailbox_id})
        msg_res = self.client.get(messages_url)
        self.assertEqual(msg_res.status_code, 200)
        self.assertIn("data", msg_res.json())
        self.assertIn("last_page", msg_res.json())

        # Cleanup test upload file
        if expected_path.exists():
            expected_path.unlink()
