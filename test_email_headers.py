"""Test email parser with various header configurations."""

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from email_worker.imap.parser import parse_email


def test_parse_headers():
    """Test parsing emails with different header combinations."""

    print("=" * 70)
    print("EMAIL PARSER HEADER TEST")
    print("=" * 70)

    # Test 1: Email with standard From header
    print("\n1. Standard email with From header:")
    email_with_from = b"""From: John Doe <john@example.com>
To: faizyaburrahman.king.gadoon@gmail.com
Subject: Test email
Message-ID: <test1@example.com>

This is a test email.
"""
    result = parse_email(email_with_from)
    if result:
        print(f"   ✓ Parsed successfully")
        print(f"   From: {result.from_address}")
        print(f"   Subject: {result.subject}")
    else:
        print("   ✗ Failed to parse")

    # Test 2: Email without From, but with Return-Path
    print("\n2. Email without From, with Return-Path:")
    email_with_return_path = b"""Return-Path: <sender@example.com>
To: faizyaburrahman.king.gadoon@gmail.com
Subject: No From header
Message-ID: <test2@example.com>

This email has no From header.
"""
    result = parse_email(email_with_return_path)
    if result:
        print(f"   ✓ Parsed successfully")
        print(f"   From: {result.from_address}")
        print(f"   Subject: {result.subject}")
    else:
        print("   ✗ Failed to parse")

    # Test 3: Email without From, with Reply-To
    print("\n3. Email without From, with Reply-To:")
    email_with_reply_to = b"""Reply-To: replyto@example.com
To: faizyaburrahman.king.gadoon@gmail.com
Subject: Only Reply-To
Message-ID: <test3@example.com>

This email only has Reply-To.
"""
    result = parse_email(email_with_reply_to)
    if result:
        print(f"   ✓ Parsed successfully")
        print(f"   From: {result.from_address}")
        print(f"   Subject: {result.subject}")
    else:
        print("   ✗ Failed to parse")

    # Test 4: Email with Received header (extract sender from trace)
    print("\n4. Email with only Received headers:")
    email_with_received = b"""Delivered-To: faizyaburrahman.king.gadoon@gmail.com
Received: from mail.example.com (mail.example.com [192.168.1.1])
    by gmail.com with SMTP id test
    for <helpdesk@example.com>; Mon, 30 Jun 2026 10:00:00 -0000
To: faizyaburrahman.king.gadoon@gmail.com
Subject: Only Received header
Message-ID: <test4@example.com>
X-Original-From: original@example.com

Extracted from Received header.
"""
    result = parse_email(email_with_received)
    if result:
        print(f"   ✓ Parsed successfully")
        print(f"   From: {result.from_address}")
        print(f"   Subject: {result.subject}")
    else:
        print("   ✗ Failed to parse")

    # Test 5: Gmail-style forwarded email
    print("\n5. Gmail forwarded email (like UID 130):")
    email_gmail_style = b"""Delivered-To: faizyaburrahman.king.gadoon@gmail.com
Received: by 2002:a05:6f02:310:b0:124:7ced:cb16 with SMTP id 16csp1047939rcf;
        Tue, 30 Jun 2026 13:43:58 -0700 (PDT)
Return-Path: <actualuser@gmail.com>
To: faizyaburrahman.king.gadoon@gmail.com
Subject: Help with laptop
Message-ID: <CABc123xyz@mail.gmail.com>

My laptop won't turn on, please help!
"""
    result = parse_email(email_gmail_style)
    if result:
        print(f"   ✓ Parsed successfully")
        print(f"   From: {result.from_address}")
        print(f"   Subject: {result.subject}")
    else:
        print("   ✗ Failed to parse")

    # Test 6: Completely missing sender info
    print("\n6. Email with NO sender information:")
    email_no_sender = b"""Delivered-To: faizyaburrahman.king.gadoon@gmail.com
To: faizyaburrahman.king.gadoon@gmail.com
Subject: No sender at all
Message-ID: <test6@example.com>

This should fail.
"""
    result = parse_email(email_no_sender)
    if result:
        print(f"   ✗ Should have failed but parsed:")
        print(f"   From: {result.from_address}")
    else:
        print("   ✓ Correctly rejected (no sender info)")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\nThe parser should handle cases 1-5 successfully and reject case 6.")
    print("If case 5 (Gmail-style) works, your Docker email issue is fixed!")


if __name__ == "__main__":
    test_parse_headers()
