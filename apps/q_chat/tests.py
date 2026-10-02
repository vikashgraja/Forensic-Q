"""
Unit & Integration Tests for Q-Chat Corporate Messaging Forensics Engine
"""

from django.test import TestCase
from django.urls import reverse

from .selectors import (
    get_chat_channel_by_id,
    get_chat_dashboard_metrics,
    get_chat_participants_summary,
    get_paginated_chat_messages,
)
from .services import ingest_chat_export_file


class QChatForensicTests(TestCase):
    def setUp(self):
        self.raw_whatsapp = (
            "24/04/2024, 10:15 - Arun Kumar: Good morning team, please check the quote for tender L1.\n"
            "24/04/2024, 10:16 - Rajesh M: Received. Can we discuss the commission cut off the record?\n"
            "24/04/2024, 10:17 - Arun Kumar: <Media omitted>\n"
            "24/04/2024, 10:18 - Rajesh M: You deleted this message\n"
            "24/04/2024, 10:20 - Arun Kumar: Send cash payment details on personal account please.\n"
        )
        self.channel = ingest_chat_export_file(
            file_obj_or_content=self.raw_whatsapp,
            filename="whatsapp_export.txt",
            platform="WHATSAPP",
            channel_name="Procurement Tender Chat",
            custodian_name="Arun Kumar",
        )

    def test_whatsapp_ingestion(self):
        self.assertEqual(self.channel.total_messages, 5)
        self.assertEqual(self.channel.participant_count, 2)
        self.assertTrue(self.channel.flagged_messages_count >= 2)

        # Check deleted message flag
        deleted_msg = self.channel.messages.filter(is_deleted=True).first()
        self.assertIsNotNone(deleted_msg)
        self.assertEqual(deleted_msg.sender_name, "Rajesh M")

        # Check media attachment flag
        media_msg = self.channel.messages.filter(has_media=True).first()
        self.assertIsNotNone(media_msg)
        self.assertEqual(media_msg.media_type, "IMAGE")

    def test_json_ingestion(self):
        json_content = (
            '{"messages": ['
            '{"sender_name": "Supplier Lead", "sent_at": "2024-05-01T12:00:00Z", "message_text": "Here is the revised tender proposal"},'
            '{"sender_name": "Buyer", "sent_at": "2024-05-01T12:05:00Z", "message_text": "Ensure we get 10% cash discount off the record"}'
            "]}"
        )
        ch2 = ingest_chat_export_file(
            file_obj_or_content=json_content,
            filename="teams_export.json",
            platform="TEAMS",
            channel_name="Supplier Teams Thread",
        )
        self.assertEqual(ch2.total_messages, 2)
        self.assertTrue(ch2.flagged_messages_count >= 1)

    def test_selectors(self):
        metrics = get_chat_dashboard_metrics()
        self.assertGreaterEqual(metrics["total_channels"], 1)
        self.assertGreaterEqual(metrics["total_messages"], 5)

        participants = get_chat_participants_summary(self.channel.id)
        self.assertEqual(len(participants), 2)

        paginated = get_paginated_chat_messages(self.channel.id, page=1, page_size=10)
        self.assertEqual(paginated["total_count"], 5)

    def test_views_and_endpoints(self):
        session = self.client.session
        session["portal_authenticated"] = True
        session.save()

        # Dashboard View
        r_dash = self.client.get(reverse("q_chat:dashboard"))
        self.assertEqual(r_dash.status_code, 200)

        # Channel Detail View
        r_detail = self.client.get(reverse("q_chat:channel_detail", args=[self.channel.id]))
        self.assertEqual(r_detail.status_code, 200)

        # Messages API View
        r_api = self.client.get(reverse("q_chat:messages_api", args=[self.channel.id]))
        self.assertEqual(r_api.status_code, 200)
        self.assertEqual(r_api.json()["total_count"], 5)

        # Delete Channel
        r_del = self.client.post(reverse("q_chat:delete_channel", args=[self.channel.id]))
        self.assertEqual(r_del.status_code, 302)
        self.assertIsNone(get_chat_channel_by_id(self.channel.id))

    def test_system_disclaimer_and_chat_order(self):
        """
        Tests that WhatsApp disclaimers are recognized as system messages and that
        senders maintain consistent left vs right side alignment across multiple messages.
        """
        chat_content = (
            "[03/02/2026, 11:22:22] Arshita Intern HMIL: Good morning, Sir.\n"
            "[03/02/2026, 11:37:19] Messages and calls are end-to-end encrypted. Only people in this chat can read, listen to, or share them.\n"
            "[03/02/2026, 11:37:19] Arshita Intern HMIL is a contact.\n"
            "[03/02/2026, 13:25:31] Vikash G: Will let you know\n"
            "[03/02/2026, 13:53:14] Arshita Intern HMIL: Sure, Thank you!\n"
            "[03/02/2026, 13:53:20] Arshita Intern HMIL: Please keep me updated.\n"
            "[06/02/2026, 17:54:32] Vikash G: Hi can you send me your resume\n"
            "[06/02/2026, 17:54:40] Vikash G: Also send your portfolio.\n"
        )
        ch = ingest_chat_export_file(
            file_obj_or_content=chat_content,
            filename="_chat.txt",
            platform="WHATSAPP",
            channel_name="Interview Followup",
        )

        # System messages must NOT count as human participants
        self.assertEqual(ch.participant_count, 2)
        self.assertIn("Arshita Intern HMIL", ch.participants)
        self.assertIn("Vikash G", ch.participants)
        self.assertNotIn("System", ch.participants)

        # Retrieve messages
        paginated = get_paginated_chat_messages(ch.id, page=1, page_size=20)
        messages = paginated["data"]
        self.assertEqual(len(messages), 8)

        # Verify system messages
        sys_msgs = [m for m in messages if m["is_system"]]
        self.assertEqual(len(sys_msgs), 2)
        self.assertEqual(sys_msgs[0]["sender_name"], "System")
        self.assertIn("end-to-end encrypted", sys_msgs[0]["message_text"])
        self.assertEqual(sys_msgs[1]["sender_name"], "System")
        self.assertIn("is a contact", sys_msgs[1]["message_text"])

        # Verify sender side consistency
        # Person 1 (Arshita) must ALWAYS be on the left (is_right_side == False)
        # Person 2 (Vikash) must ALWAYS be on the right (is_right_side == True)
        arshita_msgs = [m for m in messages if m["sender_name"] == "Arshita Intern HMIL"]
        self.assertEqual(len(arshita_msgs), 3)
        for m in arshita_msgs:
            self.assertFalse(
                m["is_right_side"],
                f"Expected Arshita's message '{m['message_text']}' to be on the left",
            )

        vikash_msgs = [m for m in messages if m["sender_name"] == "Vikash G"]
        self.assertEqual(len(vikash_msgs), 3)
        for m in vikash_msgs:
            self.assertTrue(
                m["is_right_side"],
                f"Expected Vikash's message '{m['message_text']}' to be on the right",
            )

    def test_human_messages_with_system_phrases_not_hijacked(self):
        """
        Tests that human messages containing words like 'is a contact' or 'left the group'
        are retained as human messages and NOT converted into system messages.
        """
        chat_content = (
            "[03/02/2026, 10:10:00] Alice: Mr. Sharma is a contact person for the vendor.\n"
            "[03/02/2026, 10:11:00] Bob: Why have they left the group?\n"
            "[03/02/2026, 10:12:00] Messages and calls are end-to-end encrypted. Only people in this chat can read, listen to, or share them.\n"
            "[03/02/2026, 10:13:00] Arshita Intern HMIL is a contact.\n"
        )
        ch = ingest_chat_export_file(
            file_obj_or_content=chat_content,
            filename="false_positives_test.txt",
            platform="WHATSAPP",
            channel_name="Contact Discussion",
        )

        paginated = get_paginated_chat_messages(ch.id, page=1, page_size=10)
        msgs = paginated["data"]
        self.assertEqual(len(msgs), 4)

        # Message 1 from Alice
        self.assertEqual(msgs[0]["sender_name"], "Alice")
        self.assertFalse(msgs[0]["is_system"])
        self.assertEqual(msgs[0]["message_text"], "Mr. Sharma is a contact person for the vendor.")

        # Message 2 from Bob
        self.assertEqual(msgs[1]["sender_name"], "Bob")
        self.assertFalse(msgs[1]["is_system"])
        self.assertEqual(msgs[1]["message_text"], "Why have they left the group?")

        # Message 3: real encryption notice
        self.assertEqual(msgs[2]["sender_name"], "System")
        self.assertTrue(msgs[2]["is_system"])

        # Message 4: real contact notice
        self.assertEqual(msgs[3]["sender_name"], "System")
        self.assertTrue(msgs[3]["is_system"])
