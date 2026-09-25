"""
CyberMind AI - Customer Support Email Service
Handles dispatching support tickets to admin and auto-acknowledgement emails to users via Gmail SMTP.
"""

from __future__ import annotations
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import uuid
from typing import Any
from pathlib import Path
from dotenv import load_dotenv

from core.logger import logger

# Ensure fresh environment variables
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)


def get_smtp_config() -> dict[str, Any]:
    """Retrieve SMTP configuration from environment."""
    raw_pwd = os.environ.get("SMTP_PASSWORD", "kvpv uelu eoyj zemq")
    clean_pwd = raw_pwd.strip().replace(" ", "")
    
    return {
        "host": os.environ.get("SMTP_HOST", "smtp.gmail.com").strip(),
        "port": int(os.environ.get("SMTP_PORT", "587")),
        "user": os.environ.get("SMTP_USER", os.environ.get("SMTP_EMAIL", "cybermindxai@gmail.com")).strip(),
        "password": clean_pwd,
        "admin_email": os.environ.get("SUPPORT_ADMIN_EMAIL", os.environ.get("ADMIN_SUPPORT_EMAIL", "cybermindxai@gmail.com")).strip(),
    }


def _create_smtp_connection(config: dict[str, Any]) -> smtplib.SMTP:
    """Establish and authenticate SMTP connection with TLS or SSL fallback."""
    host = config["host"]
    port = config["port"]
    user = config["user"]
    password = config["password"]

    # Try STARTTLS on specified port (default 587)
    try:
        server = smtplib.SMTP(host, port, timeout=20)
        server.ehlo()
        context = ssl.create_default_context()
        server.starttls(context=context)
        server.ehlo()
        server.login(user, password)
        return server
    except Exception as exc1:
        logger.warning("SMTP STARTTLS port %s failed: %s, attempting SSL port 465...", port, exc1)
        # Fallback to SSL on 465
        try:
            context = ssl.create_default_context()
            server_ssl = smtplib.SMTP_SSL(host, 465, context=context, timeout=20)
            server_ssl.login(user, password)
            return server_ssl
        except Exception as exc2:
            logger.error("SMTP SSL connection also failed: %s", exc2)
            raise exc2


def _build_user_confirmation_html(ticket_id: str, name: str, email: str, subject: str, message: str, timestamp: str) -> str:
    """Dark cyber themed HTML email matching the exact CyberMind AI enterprise mockup design."""
    logo_url = "https://github.com/VASANI007/CyberMind-AI/blob/main/static/logo.png?raw=true"
    poster_url = "https://github.com/VASANI007/CyberMind-AI/blob/main/cyber.png?raw=true"
    
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Support Request Received - CyberMind AI</title>
</head>
<body style="margin:0; padding:0; background-color:#050811; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color:#CBD5E1;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#050811; padding:30px 10px;">
    <tr>
      <td align="center">
        <!-- Main Wrapper Card -->
        <table role="presentation" width="100%" style="max-width:620px; background:#0A0F1D; border:1px solid rgba(0, 210, 255, 0.2); border-radius:16px; overflow:hidden; box-shadow:0 25px 60px rgba(0,0,0,0.85);">
          <!-- TOP HEADER BAR -->
          <tr>
            <td style="padding:24px 28px 18px 28px; border-bottom:1px solid rgba(255,255,255,0.06);">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                <tr>
                  <!-- Left: Brand Logo & Title -->
                  <td style="vertical-align:middle;">
                    <table role="presentation" cellspacing="0" cellpadding="0">
                      <tr>
                        <td style="vertical-align:middle; padding-right:12px;">
                          <img src="{logo_url}" width="38" height="38" alt="CyberMind AI Logo" style="display:block; object-fit:contain;">
                        </td>
                        <td style="vertical-align:middle;">
                          <div style="font-size:21px; font-weight:800; color:#FFFFFF; letter-spacing:-0.5px; line-height:1.1;">CyberMind<span style="color:#00D2FF;">AI</span></div>
                          <div style="font-size:9px; font-weight:700; color:#64748B; letter-spacing:1.5px; text-transform:uppercase; margin-top:3px;">SECURE TODAY, SAFER TOMORROW</div>
                        </td>
                      </tr>
                    </table>
                  </td>
                  <!-- Right: Subtitle / Platform Tag -->
                  <td align="right" style="vertical-align:middle;">
                    <div style="font-size:8.5px; font-weight:700; color:#64748B; letter-spacing:1px; line-height:1.4; text-transform:uppercase; text-align:right;">
                      AI POWERED<br>
                      THREAT INTELLIGENCE<br>
                      <span style="border-bottom:1px solid #00D2FF; padding-bottom:1px; color:#94A3B8;">&amp; SECURITY PLATFORM</span>
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- HERO POSTER SECTION: Poster Background with Shield safely separated from Text -->
          <tr>
            <td background="{poster_url}" style="background-color:#080E1C; background-image:url('{poster_url}'); background-size:cover; background-position:center right; background-repeat:no-repeat; padding:32px 28px 28px 28px; border-bottom:1px solid rgba(0, 210, 255, 0.2);">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                <tr>
                  <!-- Left: Confined to 50% width so text NEVER overlaps the shield -->
                  <td style="width:50%; vertical-align:middle; padding-right:12px;">
                    <div style="display:inline-block; font-size:10px; font-weight:800; color:#C084FC; letter-spacing:1.6px; text-transform:uppercase; margin-bottom:8px; background:rgba(168,85,247,0.22); border:1px solid rgba(168,85,247,0.45); border-radius:20px; padding:3px 10px; text-shadow:0 1px 4px rgba(0,0,0,0.9);">
                      CUSTOMER SUPPORT
                    </div>
                    <h1 style="margin:0 0 8px 0; font-size:23px; font-weight:800; color:#FFFFFF; line-height:1.2; text-shadow:0 2px 8px rgba(0,0,0,0.95);">
                      Support Request<br><span style="color:#00D2FF;">Received</span>
                    </h1>
                    <p style="margin:0; font-size:12px; color:#E2E8F0; line-height:1.5; text-shadow:0 1px 5px rgba(0,0,0,0.95);">
                      Thank you for contacting CyberMind AI Support. We have successfully logged your inquiry.
                    </p>
                  </td>
                  <!-- Right: Reserved exclusively for the glowing shield in poster background -->
                  <td style="width:50%; vertical-align:middle;">
                    &nbsp;
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- MAIN CONTENT BODY -->
          <tr>
            <td style="padding:16px 28px 24px 28px;">
              <!-- CARD 1: User Greeting Card -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#0D1424; border:1px solid rgba(255,255,255,0.07); border-radius:12px; margin-bottom:18px;">
                <tr>
                  <td style="padding:16px 18px;">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                      <tr>
                        <td style="width:38px; vertical-align:top; padding-right:12px;">
                          <div style="width:36px; height:36px; border-radius:50%; background:#162036; border:1px solid rgba(0, 210, 255, 0.35); text-align:center; line-height:36px;">
                            <img src="https://cdn-icons-png.flaticon.com/512/9131/9131529.png" width="16" height="16" style="vertical-align:middle; display:inline-block;" alt="" />
                          </div>
                        </td>
                        <td style="vertical-align:middle;">
                          <div style="font-size:14.5px; color:#F8FAFC; line-height:1.5;">Hello <b style="color:#00D2FF;">{name}</b>,</div>
                          <div style="font-size:12.5px; color:#94A3B8; margin-top:3px; line-height:1.5;">
                            Thank you for contacting CyberMind AI. Our support team has received your request and is reviewing it. We will get back to you as soon as possible.
                          </div>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
              <!-- CARD 2: Response Timeline Notice -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:rgba(0, 210, 255, 0.04); border:1px solid rgba(0, 210, 255, 0.25); border-left:4px solid #00D2FF; border-radius:10px; margin-bottom:20px;">
                <tr>
                  <td style="padding:16px 18px;">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-bottom:8px;">
                      <tr>
                        <td style="width:28px; vertical-align:middle; padding-right:8px;">
                          <div style="width:26px; height:26px; border-radius:50%; background:rgba(0, 210, 255, 0.15); border:1px solid rgba(0, 210, 255, 0.4); text-align:center; line-height:26px;">
                            <img src="https://cdn-icons-png.flaticon.com/512/10473/10473481.png" width="14" height="14" style="vertical-align:middle; display:inline-block;" alt="" />
                          </div>
                        </td>
                        <td style="vertical-align:middle;">
                          <span style="font-size:11.5px; font-weight:800; color:#00D2FF; letter-spacing:0.8px; text-transform:uppercase;">RESPONSE TIMELINE NOTICE</span>
                        </td>
                      </tr>
                    </table>
                    <div style="font-size:13.5px; font-weight:600; color:#FFFFFF; line-height:1.55; margin-bottom:4px;">
                      Our dedicated cybersecurity support team is actively reviewing your request and will contact you via email within <span style="color:#00D2FF; font-weight:800;">24 to 25 hours</span>.
                    </div>
                    <div style="font-size:11.5px; color:#94A3B8; line-height:1.4;">
                      (Our support engineering team is actively investigating your request and will reach out to you within 24–25 hours.)
                    </div>
                  </td>
                </tr>
              </table>
              <!-- CARD 3: Ticket Details Card -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#0D1424; border:1px solid rgba(255,255,255,0.07); border-radius:12px; margin-bottom:18px;">
                <tr>
                  <td style="padding:18px 20px;">
                    <!-- Title -->
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-bottom:14px;">
                      <tr>
                        <td style="font-size:13px; font-weight:800; color:#FFFFFF; letter-spacing:0.6px; text-transform:uppercase;">
                          <img src="https://cdn-icons-png.flaticon.com/512/16782/16782995.png" width="15" height="15" style="vertical-align:middle; display:inline-block; margin-right:6px;" alt="" /> YOUR TICKET DETAILS
                        </td>
                      </tr>
                    </table>
                    <!-- Table Rows -->
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;">
                      <!-- Row 1: Ticket ID -->
                      <tr>
                        <td style="padding:9px 0; border-bottom:1px solid rgba(255,255,255,0.05); width:32px; vertical-align:middle;">
                          <span style="display:inline-block; width:22px; height:22px; border-radius:5px; background:rgba(168, 85, 247, 0.15); border:1px solid rgba(168, 85, 247, 0.4); color:#A855F7; text-align:center; line-height:22px; font-size:11px; font-weight:800;">#</span>
                        </td>
                        <td style="padding:9px 8px; border-bottom:1px solid rgba(255,255,255,0.05); font-size:12.5px; color:#94A3B8; width:34%; vertical-align:middle;">
                          Ticket ID:
                        </td>
                        <td style="padding:9px 0; border-bottom:1px solid rgba(255,255,255,0.05); font-size:13px; color:#00D2FF; font-weight:700; font-family:'Courier New', Courier, monospace; letter-spacing:0.5px; vertical-align:middle;">
                          {ticket_id}
                        </td>
                      </tr>
                      <!-- Row 2: Subject -->
                      <tr>
                        <td style="padding:9px 0; border-bottom:1px solid rgba(255,255,255,0.05); vertical-align:middle;">
                          <span style="display:inline-block; width:22px; height:22px; border-radius:5px; background:rgba(59, 130, 246, 0.15); border:1px solid rgba(59, 130, 246, 0.4); text-align:center; line-height:22px;"><img src="https://cdn-icons-png.flaticon.com/512/2210/2210197.png" width="12" height="12" style="vertical-align:middle; display:inline-block;" alt="" /></span>
                        </td>
                        <td style="padding:9px 8px; border-bottom:1px solid rgba(255,255,255,0.05); font-size:12.5px; color:#94A3B8; vertical-align:middle;">
                          Subject:
                        </td>
                        <td style="padding:9px 0; border-bottom:1px solid rgba(255,255,255,0.05); font-size:13px; color:#FFFFFF; font-weight:600; vertical-align:middle;">
                          {subject}
                        </td>
                      </tr>
                      <!-- Row 3: Submitted Email -->
                      <tr>
                        <td style="padding:9px 0; border-bottom:1px solid rgba(255,255,255,0.05); vertical-align:middle;">
                          <span style="display:inline-block; width:22px; height:22px; border-radius:5px; background:rgba(6, 182, 212, 0.15); border:1px solid rgba(6, 182, 212, 0.4); text-align:center; line-height:22px;"><img src="https://cdn-icons-png.flaticon.com/512/888/888853.png" width="12" height="12" style="vertical-align:middle; display:inline-block;" alt="" /></span>
                        </td>
                        <td style="padding:9px 8px; border-bottom:1px solid rgba(255,255,255,0.05); font-size:12.5px; color:#94A3B8; vertical-align:middle;">
                          Submitted Email:
                        </td>
                        <td style="padding:9px 0; border-bottom:1px solid rgba(255,255,255,0.05); font-size:13px; color:#38BDF8; font-weight:500; vertical-align:middle;">
                          <a href="mailto:{email}" style="color:#38BDF8; text-decoration:none;">{email}</a>
                        </td>
                      </tr>
                      <!-- Row 4: Submission Time -->
                      <tr>
                        <td style="padding:9px 0; border-bottom:1px solid rgba(255,255,255,0.05); vertical-align:middle;">
                          <span style="display:inline-block; width:22px; height:22px; border-radius:5px; background:rgba(236, 72, 153, 0.15); border:1px solid rgba(236, 72, 153, 0.4); text-align:center; line-height:22px;"><img src="https://cdn-icons-png.flaticon.com/512/10692/10692035.png" width="12" height="12" style="vertical-align:middle; display:inline-block;" alt="" /></span>
                        </td>
                        <td style="padding:9px 8px; border-bottom:1px solid rgba(255,255,255,0.05); font-size:12.5px; color:#94A3B8; vertical-align:middle;">
                          Submission Time:
                        </td>
                        <td style="padding:9px 0; border-bottom:1px solid rgba(255,255,255,0.05); font-size:13px; color:#CBD5E1; vertical-align:middle;">
                          {timestamp}
                        </td>
                      </tr>
                      <!-- Row 5: Your Message -->
                      <tr>
                        <td style="padding:10px 0 4px 0; vertical-align:top;">
                          <span style="display:inline-block; width:22px; height:22px; border-radius:5px; background:rgba(139, 92, 246, 0.15); border:1px solid rgba(139, 92, 246, 0.4); text-align:center; line-height:22px;"><img src="https://cdn-icons-png.flaticon.com/512/3790/3790214.png" width="12" height="12" style="vertical-align:middle; display:inline-block;" alt="" /></span>
                        </td>
                        <td style="padding:10px 8px 4px 8px; font-size:12.5px; color:#94A3B8; vertical-align:top;">
                          Your Message:
                        </td>
                        <td style="padding:10px 0 4px 0; font-size:13px; color:#F1F5F9; line-height:1.55; vertical-align:top; white-space:pre-wrap;">
                          {message}
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
              <!-- CARD 4: Helpful Reply Note -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#0D1424; border:1px solid rgba(255,255,255,0.06); border-radius:10px; margin-bottom:22px;">
                <tr>
                  <td style="padding:12px 16px;">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                      <tr>
                        <td style="width:28px; vertical-align:middle; padding-right:10px;">
                          <div style="width:24px; height:24px; border-radius:50%; background:rgba(59, 130, 246, 0.15); border:1px solid rgba(59, 130, 246, 0.4); text-align:center; line-height:24px; font-size:12px; color:#38BDF8;">
                            ℹ️
                          </div>
                        </td>
                        <td style="font-size:12px; color:#94A3B8; line-height:1.5; vertical-align:middle;">
                          If you need to provide additional details, log files, or screenshots regarding this inquiry, simply reply directly to this email.
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
              <!-- SIGN-OFF -->
              <div style="font-size:13.5px; color:#CBD5E1; margin-bottom:24px; line-height:1.6;">
                Warm Regards,<br>
                <strong style="color:#00D2FF; font-size:14.5px;">CyberMind AI Support Operations</strong><br>
                <span style="font-size:12px; color:#64748B;">Automated Threat Intelligence &amp; Security Platform</span>
              </div>
              <!-- 4 PILLARS FEATURE BADGES ROW -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-bottom:24px;">
                <tr>
                  <!-- Pillar 1 -->
                  <td width="23%" align="center" style="background:#0D1424; border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:12px 6px;">
                    <div style="width:28px; height:28px; border-radius:50%; background:rgba(0, 210, 255, 0.12); border:1px solid rgba(0, 210, 255, 0.35); text-align:center; line-height:28px; margin:0 auto 6px auto;"><img src="https://cdn-icons-png.flaticon.com/512/6071/6071531.png" width="14" height="14" style="vertical-align:middle; display:inline-block;" alt="" /></div>
                    <div style="font-size:9px; font-weight:800; color:#CBD5E1; letter-spacing:0.5px; line-height:1.2; text-transform:uppercase;">DETECT<br><span style="color:#64748B;">THREATS</span></div>
                  </td>
                  <td width="2.6%"></td>
                  <!-- Pillar 2 -->
                  <td width="23%" align="center" style="background:#0D1424; border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:12px 6px;">
                    <div style="width:28px; height:28px; border-radius:50%; background:rgba(168, 85, 247, 0.12); border:1px solid rgba(168, 85, 247, 0.35); text-align:center; line-height:28px; margin:0 auto 6px auto;"><img src="https://cdn-icons-png.flaticon.com/512/404/404621.png" width="14" height="14" style="vertical-align:middle; display:inline-block;" alt="" /></div>
                    <div style="font-size:9px; font-weight:800; color:#CBD5E1; letter-spacing:0.5px; line-height:1.2; text-transform:uppercase;">ANALYZE<br><span style="color:#64748B;">RISKS</span></div>
                  </td>
                  <td width="2.6%"></td>
                  <!-- Pillar 3 -->
                  <td width="23%" align="center" style="background:#0D1424; border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:12px 6px;">
                    <div style="width:28px; height:28px; border-radius:50%; background:rgba(59, 130, 246, 0.12); border:1px solid rgba(59, 130, 246, 0.35); text-align:center; line-height:28px; margin:0 auto 6px auto;"><img src="https://cdn-icons-png.flaticon.com/512/4870/4870942.png" width="14" height="14" style="vertical-align:middle; display:inline-block;" alt="" /></div>
                    <div style="font-size:9px; font-weight:800; color:#CBD5E1; letter-spacing:0.5px; line-height:1.2; text-transform:uppercase;">STAY<br><span style="color:#64748B;">PROTECTED</span></div>
                  </td>
                  <td width="2.6%"></td>
                  <!-- Pillar 4 -->
                  <td width="23%" align="center" style="background:#0D1424; border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:12px 6px;">
                    <div style="width:28px; height:28px; border-radius:50%; background:rgba(34, 197, 94, 0.12); border:1px solid rgba(34, 197, 94, 0.35); text-align:center; line-height:28px; margin:0 auto 6px auto;"><img src="https://cdn-icons-png.flaticon.com/512/921/921347.png" width="14" height="14" style="vertical-align:middle; display:inline-block;" alt="" /></div>
                    <div style="font-size:9px; font-weight:800; color:#CBD5E1; letter-spacing:0.5px; line-height:1.2; text-transform:uppercase;">SECURE<br><span style="color:#64748B;">TOGETHER</span></div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- FOOTER -->
          <tr>
            <td style="background:#070B16; padding:22px 28px; border-top:1px solid rgba(255,255,255,0.06);">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                <!-- Top Row: Brand & Tagline -->
                <tr>
                  <td style="vertical-align:middle;">
                    <div style="font-size:16px; font-weight:800; color:#FFFFFF; letter-spacing:-0.3px;">
                      CyberMind<span style="color:#00D2FF;">AI</span>
                    </div>
                  </td>
                  <td align="right" style="vertical-align:middle; font-size:9.5px; font-weight:700; color:#475569; letter-spacing:1px; text-transform:uppercase;">
                    SECURITY &bull; INTELLIGENCE &bull; A SAFER TOMORROW
                  </td>
                </tr>
                <!-- Bottom Row: Copyright -->
                <tr>
                  <td colspan="2" style="padding-top:12px; font-size:11px; color:#64748B; vertical-align:middle;">
                    &copy; 2026 CyberMind AI. All rights reserved. &bull; Enterprise Cyber Threat Intelligence
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _build_admin_notification_html(ticket_id: str, name: str, email: str, subject: str, message: str, timestamp: str) -> str:
    """Dark cyber themed HTML email sent to admin (cybermindxai@gmail.com) matching enterprise mockup."""
    logo_url = "https://github.com/VASANI007/CyberMind-AI/blob/main/static/logo.png?raw=true"
    poster_url = "https://github.com/VASANI007/CyberMind-AI/blob/main/cyber.png?raw=true"
    
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>New Customer Support Ticket - CyberMind AI</title>
</head>
<body style="margin:0; padding:0; background-color:#050811; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color:#CBD5E1;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#050811; padding:30px 10px;">
    <tr>
      <td align="center">
        <!-- Main Card -->
        <table role="presentation" width="100%" style="max-width:620px; background:#0A0F1D; border:1px solid rgba(0, 210, 255, 0.28); border-radius:16px; overflow:hidden; box-shadow:0 25px 60px rgba(0,0,0,0.85);">
          <!-- TOP HEADER BAR -->
          <tr>
            <td style="padding:24px 28px 18px 28px; border-bottom:1px solid rgba(255,255,255,0.06);">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="vertical-align:middle;">
                    <table role="presentation" cellspacing="0" cellpadding="0">
                      <tr>
                        <td style="vertical-align:middle; padding-right:12px;">
                          <img src="{logo_url}" width="42" height="42" alt="CyberMind AI Logo" style="display:block; object-fit:contain; filter:drop-shadow(0 0 10px rgba(0,210,255,0.45));">
                        </td>
                        <td style="vertical-align:middle;">
                          <div style="font-size:22px; font-weight:800; color:#FFFFFF; letter-spacing:-0.5px; line-height:1.1;">CyberMind<span style="color:#00D2FF;">AI</span></div>
                          <div style="font-size:8.5px; font-weight:700; color:#64748B; letter-spacing:1.4px; text-transform:uppercase; margin-top:3px;">ADVANCED CYBERSECURITY THREAT DETECTION PLATFORM</div>
                        </td>
                      </tr>
                    </table>
                  </td>
                  <td align="right" style="vertical-align:middle;">
                    <!-- Admin Notification Badge -->
                    <table role="presentation" cellspacing="0" cellpadding="0" style="display:inline-table; background:rgba(239, 68, 68, 0.12); border:1px solid rgba(239, 68, 68, 0.35); border-radius:8px; padding:6px 12px;">
                      <tr>
                        <td style="vertical-align:middle; padding-right:8px; line-height:1;"><img src="https://cdn-icons-png.flaticon.com/512/18421/18421884.png" width="14" height="14" style="vertical-align:middle; display:inline-block;" alt="" /></td>
                        <td style="vertical-align:middle; text-align:left;">
                          <div style="font-size:9.5px; font-weight:800; color:#EF4444; letter-spacing:0.8px; text-transform:uppercase; line-height:1.2;">ADMIN NOTIFICATION</div>
                          <div style="font-size:8px; font-weight:700; color:#F87171; letter-spacing:0.6px; text-transform:uppercase; line-height:1.2; margin-top:2px;">PRIORITY INQUIRY</div>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- HERO POSTER SECTION: Poster Background with Shield safely separated from Text -->
          <tr>
            <td background="{poster_url}" style="background-color:#080E1C; background-image:url('{poster_url}'); background-size:cover; background-position:center right; background-repeat:no-repeat; padding:32px 28px 28px 28px; border-bottom:1px solid rgba(0, 210, 255, 0.18);">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                <tr>
                  <!-- Left: Confined to 50% width so text NEVER overlaps the shield -->
                  <td style="width:50%; vertical-align:middle; padding-right:12px;">
                    <h1 style="margin:0 0 8px 0; font-size:23px; font-weight:800; color:#FFFFFF; line-height:1.2; text-shadow:0 2px 8px rgba(0,0,0,0.95);">
                      New Support<br><span style="color:#00D2FF;">Inquiry</span>
                    </h1>
                    <p style="margin:0; font-size:12px; color:#E2E8F0; line-height:1.5; text-shadow:0 1px 5px rgba(0,0,0,0.95);">
                      A customer has submitted a new inquiry requiring review within <b style="color:#00D2FF;">24&ndash;25 hours</b>.
                    </p>
                  </td>
                  <!-- Right: Reserved exclusively for the glowing shield in poster background -->
                  <td style="width:50%; vertical-align:middle;">
                    &nbsp;
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Content Body -->
          <tr>
            <td style="padding:20px 28px 24px 28px;">
              <!-- CARD 1: USER INFORMATION & METADATA -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#0B132B; border:1px solid rgba(0, 210, 255, 0.22); border-radius:12px; margin-bottom:16px;">
                <tr>
                  <td style="padding:18px 20px;">
                    <div style="margin-bottom:12px;">
                      <div style="display:inline-block; width:24px; height:24px; border-radius:6px; background:#1D4ED8; text-align:center; line-height:24px; vertical-align:middle; margin-right:8px;"><img src="https://cdn-icons-png.flaticon.com/512/9131/9131529.png" width="13" height="13" style="vertical-align:middle; display:inline-block;" alt="" /></div>
                      <span style="font-size:11.5px; font-weight:800; color:#E2E8F0; letter-spacing:1px; text-transform:uppercase; vertical-align:middle;">USER INFORMATION &amp; METADATA</span>
                    </div>
                    <table role="presentation" width="100%" style="border-collapse:collapse;">
                      <tr>
                        <td style="padding:8px 0; font-size:13px; color:#94A3B8; width:36%; border-bottom:1px solid rgba(255,255,255,0.05); vertical-align:middle;">
                          <span style="display:inline-block; width:20px; vertical-align:middle;"><img src="https://cdn-icons-png.flaticon.com/512/9131/9131529.png" width="13" height="13" style="vertical-align:middle; display:inline-block;" alt="" /></span> User Name:
                        </td>
                        <td style="padding:8px 0; font-size:13px; color:#FFFFFF; font-weight:700; border-bottom:1px solid rgba(255,255,255,0.05); vertical-align:middle;">
                          {name}
                        </td>
                      </tr>
                      <tr>
                        <td style="padding:8px 0; font-size:13px; color:#94A3B8; border-bottom:1px solid rgba(255,255,255,0.05); vertical-align:middle;">
                          <span style="display:inline-block; width:20px; vertical-align:middle;"><img src="https://cdn-icons-png.flaticon.com/512/888/888853.png" width="13" height="13" style="vertical-align:middle; display:inline-block;" alt="" /></span> User Email:
                        </td>
                        <td style="padding:8px 0; font-size:13px; color:#00D2FF; font-weight:600; border-bottom:1px solid rgba(255,255,255,0.05); vertical-align:middle;">
                          <a href="mailto:{email}" style="color:#00D2FF; text-decoration:none;">{email}</a>
                        </td>
                      </tr>
                      <tr>
                        <td style="padding:8px 0; font-size:13px; color:#94A3B8; border-bottom:1px solid rgba(255,255,255,0.05); vertical-align:middle;">
                          <span style="display:inline-block; width:20px; vertical-align:middle;"><img src="https://cdn-icons-png.flaticon.com/512/2210/2210197.png" width="13" height="13" style="vertical-align:middle; display:inline-block;" alt="" /></span> Subject:
                        </td>
                        <td style="padding:8px 0; font-size:13px; color:#F1F5F9; font-weight:600; border-bottom:1px solid rgba(255,255,255,0.05); vertical-align:middle;">
                          {subject}
                        </td>
                      </tr>
                      <tr>
                        <td style="padding:8px 0; font-size:13px; color:#94A3B8; border-bottom:1px solid rgba(255,255,255,0.05); vertical-align:middle;">
                          <span style="display:inline-block; width:20px; vertical-align:middle;"><img src="https://cdn-icons-png.flaticon.com/512/16782/16782995.png" width="13" height="13" style="vertical-align:middle; display:inline-block;" alt="" /></span> Ticket ID:
                        </td>
                        <td style="padding:8px 0; font-size:13px; color:#00D2FF; font-family:'Courier New', monospace; font-weight:700; border-bottom:1px solid rgba(255,255,255,0.05); vertical-align:middle;">
                          <span style="background:rgba(0,210,255,0.1); border:1px solid rgba(0,210,255,0.3); border-radius:4px; padding:2px 8px;">{ticket_id}</span>
                        </td>
                      </tr>
                      <tr>
                        <td style="padding:8px 0; font-size:13px; color:#94A3B8; vertical-align:middle;">
                          <span style="display:inline-block; width:20px; vertical-align:middle;"><img src="https://cdn-icons-png.flaticon.com/512/10692/10692035.png" width="13" height="13" style="vertical-align:middle; display:inline-block;" alt="" /></span> Submitted Time:
                        </td>
                        <td style="padding:8px 0; font-size:13px; color:#94A3B8; vertical-align:middle;">
                          {timestamp}
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              <!-- CARD 2: USER PROBLEM DESCRIPTION -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#0B132B; border:1px solid rgba(0, 210, 255, 0.22); border-radius:12px; margin-bottom:16px;">
                <tr>
                  <td style="padding:18px 20px;">
                    <div style="margin-bottom:12px;">
                      <div style="display:inline-block; width:24px; height:24px; border-radius:6px; background:#2563EB; text-align:center; line-height:24px; vertical-align:middle; margin-right:8px;"><img src="https://cdn-icons-png.flaticon.com/512/3790/3790214.png" width="13" height="13" style="vertical-align:middle; display:inline-block;" alt="" /></div>
                      <span style="font-size:11.5px; font-weight:800; color:#E2E8F0; letter-spacing:1px; text-transform:uppercase; vertical-align:middle;">USER PROBLEM DESCRIPTION</span>
                    </div>
                    <div style="background:linear-gradient(180deg, #070B18 0%, #060914 100%); border:1px solid rgba(59, 130, 246, 0.35); border-radius:10px; padding:16px 18px;">
                      <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                        <tr>
                          <td style="width:34px; vertical-align:top; padding-right:12px;">
                            <div style="width:30px; height:30px; border-radius:50%; background:#132147; border:1px solid #2563EB; text-align:center; line-height:30px;">
                              <img src="https://cdn-icons-png.flaticon.com/512/3790/3790214.png" width="14" height="14" style="vertical-align:middle; display:inline-block;" alt="" />
                            </div>
                          </td>
                          <td style="color:#F8FAFC; font-size:14px; line-height:1.6; white-space:pre-wrap; vertical-align:middle;">
{message}
                          </td>
                        </tr>
                      </table>
                    </div>
                  </td>
                </tr>
              </table>

              <!-- CARD 3: RESPONSE GUIDELINE -->
              <div style="background:rgba(0, 210, 255, 0.04); border:1px solid rgba(0, 210, 255, 0.25); border-radius:10px; padding:14px 18px; margin-bottom:20px;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                  <tr>
                    <td style="width:38px; vertical-align:middle; padding-right:12px;">
                      <div style="width:34px; height:34px; border-radius:50%; background:rgba(0, 210, 255, 0.12); border:1px solid #00D2FF; text-align:center; line-height:34px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/2055/2055768.png" width="16" height="16" style="vertical-align:middle; display:inline-block;" alt="" />
                      </div>
                    </td>
                    <td style="vertical-align:middle;">
                      <div style="font-size:10.5px; font-weight:800; color:#00D2FF; letter-spacing:1px; text-transform:uppercase;">RESPONSE GUIDELINE</div>
                      <div style="font-size:12.5px; color:#94A3B8; margin-top:3px; line-height:1.45;">
                        Please review this inquiry and respond to the user within <b style="color:#00D2FF;">24&ndash;25 hours</b> to ensure timely support.
                      </div>
                    </td>
                  </tr>
                </table>
              </div>

              <!-- Direct Reply Action Button -->
              <div style="text-align:center; margin-bottom:22px;">
                <a href="mailto:{email}?subject=Re: [CyberMind Support {ticket_id}] {subject}" 
                   style="display:inline-block; background:linear-gradient(90deg, #6366F1 0%, #00D2FF 100%); color:#FFFFFF; font-weight:700; font-size:14px; text-decoration:none; padding:14px 32px; border-radius:10px; box-shadow:0 6px 20px rgba(0, 210, 255, 0.35); letter-spacing:0.2px;">
                  <img src="https://cdn-icons-png.flaticon.com/512/888/888853.png" width="14" height="14" style="vertical-align:middle; display:inline-block;" alt="" /> &nbsp; Reply Directly to {name} <span style="opacity:0.85; font-size:12px; font-weight:400;">({email})</span> &nbsp; &rarr;
                </a>
              </div>

              <!-- 4 Feature Pillars -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-top:1px solid rgba(255,255,255,0.06); padding-top:18px;">
                <tr>
                  <td align="center" style="width:25%; padding:4px 6px; vertical-align:middle;">
                    <img src="https://cdn-icons-png.flaticon.com/512/6071/6071531.png" width="16" height="16" style="vertical-align:middle; display:inline-block;" alt="" />
                    <div style="font-size:9px; font-weight:700; color:#64748B; letter-spacing:0.8px; text-transform:uppercase; margin-top:4px;">DETECT THREATS</div>
                  </td>
                  <td align="center" style="width:25%; padding:4px 6px; vertical-align:middle;">
                    <img src="https://cdn-icons-png.flaticon.com/512/404/404621.png" width="16" height="16" style="vertical-align:middle; display:inline-block;" alt="" />
                    <div style="font-size:9px; font-weight:700; color:#64748B; letter-spacing:0.8px; text-transform:uppercase; margin-top:4px;">ANALYZE RISKS</div>
                  </td>
                  <td align="center" style="width:25%; padding:4px 6px; vertical-align:middle;">
                    <img src="https://cdn-icons-png.flaticon.com/512/4870/4870942.png" width="16" height="16" style="vertical-align:middle; display:inline-block;" alt="" />
                    <div style="font-size:9px; font-weight:700; color:#64748B; letter-spacing:0.8px; text-transform:uppercase; margin-top:4px;">STAY PROTECTED</div>
                  </td>
                  <td align="center" style="width:25%; padding:4px 6px; vertical-align:middle;">
                    <img src="https://cdn-icons-png.flaticon.com/512/921/921347.png" width="16" height="16" style="vertical-align:middle; display:inline-block;" alt="" />
                    <div style="font-size:9px; font-weight:700; color:#64748B; letter-spacing:0.8px; text-transform:uppercase; margin-top:4px;">SECURE TOGETHER</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- FOOTER (Without Round Buttons) -->
          <tr>
            <td style="background:#070B16; padding:22px 28px; border-top:1px solid rgba(255,255,255,0.06);">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="vertical-align:middle;">
                    <div style="font-size:16px; font-weight:800; color:#FFFFFF; letter-spacing:-0.3px;">
                      CyberMind<span style="color:#00D2FF;">AI</span>
                    </div>
                    <div style="font-size:8.5px; font-weight:700; color:#64748B; letter-spacing:1.4px; text-transform:uppercase; margin-top:3px;">
                      SECURE TODAY, SAFER TOMORROW
                    </div>
                  </td>
                  <td align="right" style="vertical-align:middle; font-size:11px; color:#64748B;">
                    &copy; 2026 CyberMind AI. All rights reserved.
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _save_ticket_to_db(ticket_id: str, name: str, email: str, subject: str, message: str) -> None:
    """Stores the support ticket locally in SQLite database."""
    try:
        from database.db import db
        # Ensure table exists
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS support_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT DEFAULT 'Open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        db.execute(
            """
            INSERT INTO support_tickets (ticket_id, name, email, subject, message, status)
            VALUES (?, ?, ?, ?, ?, 'Open')
            """,
            (ticket_id, name, email, subject, message)
        )
    except Exception as exc:
        logger.warning("Could not save support ticket to local DB: %s", exc)


def send_support_ticket(name: str, email: str, subject: str, message: str) -> dict[str, Any]:
    """
    Submits a customer support ticket:
    1. Dispatches an alert email to Admin (cybermindxai@gmail.com).
    2. Dispatches an auto-acknowledgement email to the User with the 24-25h response guarantee.
    3. Saves ticket to database.

    Returns:
        dict: {"success": bool, "message": str, "ticket_id": str}
    """
    clean_name = (name or "").strip()
    clean_email = (email or "").strip()
    clean_sub = (subject or "").strip()
    clean_msg = (message or "").strip()

    if not clean_name:
        return {"success": False, "message": "Please enter your full name."}
    if not clean_email or "@" not in clean_email or "." not in clean_email:
        return {"success": False, "message": "Please enter a valid email address."}
    if not clean_sub:
        return {"success": False, "message": "Please enter a subject for your request."}
    if not clean_msg:
        return {"success": False, "message": "Please describe the problem or issue you are experiencing."}

    config = get_smtp_config()
    ticket_id = f"CM-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:5].upper()}"
    timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p (IST)")

    # ── 1. PERSIST TO DB UPFRONT (Ensures inquiry is never lost) ────
    _save_ticket_to_db(ticket_id, clean_name, clean_email, clean_sub, clean_msg)

    server = None
    try:
        server = _create_smtp_connection(config)
        sender_email = config["user"]
        admin_email = config["admin_email"]

        # ── 2. SEND EMAIL TO ADMIN ────────────────────────────────────
        msg_admin = MIMEMultipart("alternative")
        msg_admin["Subject"] = f"[Support Ticket {ticket_id}] {clean_sub} - From {clean_name}"
        msg_admin["From"] = f"CyberMind AI Support <{sender_email}>"
        msg_admin["To"] = admin_email
        msg_admin["Reply-To"] = clean_email

        html_admin = _build_admin_notification_html(ticket_id, clean_name, clean_email, clean_sub, clean_msg, timestamp)
        msg_admin.attach(MIMEText(html_admin, "html", "utf-8"))
        
        server.sendmail(sender_email, [admin_email], msg_admin.as_string())
        logger.info("Support ticket %s dispatched to admin (%s)", ticket_id, admin_email)

        # ── 3. SEND AUTO-ACKNOWLEDGEMENT EMAIL TO USER ────────────────
        msg_user = MIMEMultipart("alternative")
        msg_user["Subject"] = f"[CyberMind AI] We received your inquiry: {clean_sub} [{ticket_id}]"
        msg_user["From"] = f"CyberMind AI Customer Support <{sender_email}>"
        msg_user["To"] = clean_email
        msg_user["Reply-To"] = admin_email

        html_user = _build_user_confirmation_html(ticket_id, clean_name, clean_email, clean_sub, clean_msg, timestamp)
        msg_user.attach(MIMEText(html_user, "html", "utf-8"))

        server.sendmail(sender_email, [clean_email], msg_user.as_string())
        logger.info("Confirmation email for ticket %s dispatched to user (%s)", ticket_id, clean_email)

        return {
            "success": True,
            "ticket_id": ticket_id,
            "message": f"Your ticket ({ticket_id}) has been submitted successfully! A confirmation email has been dispatched to {clean_email}."
        }

    except Exception as exc:
        logger.error("Failed to send support ticket email: %s", exc, exc_info=True)
        err_str = str(exc)
        if "534" in err_str or "5.7.14" in err_str:
            err_msg = (
                f"Google Security Check (534): Gmail has temporarily paused automated SMTP for {config.get('user')}. "
                "Please visit https://accounts.google.com/DisplayUnlockCaptcha while logged in and click 'Continue', "
                "or generate a new App Password at https://myaccount.google.com/apppasswords and update SMTP_PASSWORD in .env."
            )
        elif "535" in err_str or "Authentication Credentials Invalid" in err_str:
            err_msg = (
                "Gmail Authentication Error: The App Password in .env is invalid. "
                "Please generate a fresh 16-character App Password at https://myaccount.google.com/apppasswords."
            )
        else:
            err_msg = f"Failed to send email via SMTP server: {err_str}"

        return {
            "success": False,
            "ticket_id": ticket_id,
            "message": err_msg
        }
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass
