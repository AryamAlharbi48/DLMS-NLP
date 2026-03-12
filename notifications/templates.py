# ================================================================
# DLMS Notification Templates
# ================================================================
# Each template has 3 versions:
#   - email_subject : the subject line of the email
#   - email_body    : full HTML email body
#   - sms_body      : short text for SMS
#   - inapp_body    : dictionary for in-app notification
#
# Each value is a lambda function that accepts a dictionary `d`
# containing the variables to inject into the message.
# ================================================================

TEMPLATES = {

    # ── 1. INACTIVITY WARNING — 90 days before threshold ─────────────
    "INACTIVITY_WARNING_90": {

        "email_subject": lambda d: (
            "تنبيه: حسابك غير نشط | DLMS Inactivity Warning"
        ),

        "email_body": lambda d: f"""
        <div dir="rtl" style="font-family:Arial,sans-serif;
                               max-width:600px; margin:auto; padding:24px;
                               border:1px solid #ddd; border-radius:8px;">

            <h2 style="color:#1B3A6B;">مرحباً {d['name']}</h2>

            <p>لاحظ نظام <strong>DLMS</strong> أن حسابك لم يُستخدم
               منذ <strong>{d['days_inactive']} يوماً</strong>.</p>

            <p>لديك <strong>{d['days_left']} يوماً</strong>
               قبل أن يبدأ النظام بإجراءات التحقق من الوفاة.</p>

            <p>إذا كنت بخير، يرجى الضغط على الزر أدناه لتأكيد نشاطك:</p>

            <div style="text-align:center; margin:32px 0;">
                <a href="{d['confirm_url']}"
                   style="background:#1B3A6B; color:white;
                          padding:14px 32px; border-radius:6px;
                          text-decoration:none; font-size:16px;">
                    ✅ أنا بخير — تأكيد النشاط
                </a>
            </div>

            <hr style="border:none; border-top:1px solid #eee;
                        margin:24px 0;"/>

            <p style="color:#888; font-size:12px;">
                Smart Digital Legacy Management System —
                Taif University, KSA
            </p>
        </div>
        """,

        "sms_body": lambda d: (
            f"DLMS: مرحباً {d['name']}، حسابك غير نشط منذ "
            f"{d['days_inactive']} يوم. "
            f"تبقى {d['days_left']} يوم. "
            f"تأكيد: {d['confirm_url']}"
        ),

        "inapp_body": lambda d: {
            "title": "تنبيه عدم النشاط",
            "message": (
                f"حسابك غير نشط منذ {d['days_inactive']} يوماً. "
                f"تبقى {d['days_left']} يوماً للتأكيد."
            ),
            "action_url": d["confirm_url"],
            "severity": "warning",
        },
    },

    # ── 2. INACTIVITY WARNING — 30 days before threshold ─────────────
    "INACTIVITY_WARNING_30": {

        "email_subject": lambda d: (
            "⚠️ تحذير مهم: تبقى 30 يوماً | DLMS Urgent Warning"
        ),

        "email_body": lambda d: f"""
        <div dir="rtl" style="font-family:Arial,sans-serif;
                               max-width:600px; margin:auto; padding:24px;
                               border:2px solid #C0392B; border-radius:8px;">

            <h2 style="color:#C0392B;">⚠️ تحذير عاجل — {d['name']}</h2>

            <p>حسابك في نظام DLMS غير نشط منذ
               <strong>{d['days_inactive']} يوماً</strong>.</p>

            <p style="color:#C0392B; font-weight:bold;">
                تبقى 30 يوماً فقط قبل أن يُفترض أنك متوفٍّ
                وتُنفَّذ تعليماتك الرقمية تلقائياً.
            </p>

            <div style="text-align:center; margin:32px 0;">
                <a href="{d['confirm_url']}"
                   style="background:#C0392B; color:white;
                          padding:14px 32px; border-radius:6px;
                          text-decoration:none; font-size:16px;">
                    ✅ تأكيد أنني بخير
                </a>
            </div>

            <p style="color:#888; font-size:12px;">
                Smart Digital Legacy Management System —
                Taif University, KSA
            </p>
        </div>
        """,

        "sms_body": lambda d: (
            f"DLMS تحذير: {d['name']}، تبقى 30 يوم فقط. "
            f"تأكيد نشاطك الآن: {d['confirm_url']}"
        ),

        "inapp_body": lambda d: {
            "title": "⚠️ تحذير عاجل",
            "message": (
                "تبقى 30 يوماً فقط قبل تنفيذ تعليماتك الرقمية. "
                "انقر للتأكيد الآن."
            ),
            "action_url": d["confirm_url"],
            "severity": "critical",
        },
    },

    # ── 3. INACTIVITY WARNING — 7 days before threshold ──────────────
    "INACTIVITY_WARNING_7": {

        "email_subject": lambda d: (
            "🚨 آخر تحذير: 7 أيام متبقية | DLMS Final Warning"
        ),

        "email_body": lambda d: f"""
        <div dir="rtl" style="font-family:Arial,sans-serif;
                               max-width:600px; margin:auto; padding:24px;
                               background:#FFF3CD;
                               border:2px solid #FF6B00;
                               border-radius:8px;">

            <h2 style="color:#FF6B00;">🚨 آخر تحذير — {d['name']}</h2>

            <p>تبقى <strong>7 أيام فقط</strong> قبل تفعيل
               التعليمات الرقمية الخاصة بك.</p>

            <p>إذا لم تستجب، سيقوم النظام بتنفيذ جميع
               التعليمات التي سجّلتها مسبقاً.</p>

            <div style="text-align:center; margin:32px 0;">
                <a href="{d['confirm_url']}"
                   style="background:#FF6B00; color:white;
                          padding:16px 36px; border-radius:6px;
                          text-decoration:none; font-size:18px;
                          font-weight:bold;">
                    🚨 اضغط هنا الآن للتأكيد
                </a>
            </div>

            <p style="color:#888; font-size:12px;">
                Smart Digital Legacy Management System —
                Taif University, KSA
            </p>
        </div>
        """,

        "sms_body": lambda d: (
            f"DLMS 🚨 آخر تحذير {d['name']}: "
            f"7 أيام فقط. تأكيد: {d['confirm_url']}"
        ),

        "inapp_body": lambda d: {
            "title": "🚨 آخر تحذير",
            "message": "7 أيام فقط. اضغط الآن لتأكيد نشاطك.",
            "action_url": d["confirm_url"],
            "severity": "critical",
        },
    },

    # ── 4. USER CONFIRMED ALIVE ───────────────────────────────────────
    "CONFIRMED_ALIVE": {

        "email_subject": lambda d: (
            "✅ تم تأكيد نشاطك | DLMS Activity Confirmed"
        ),

        "email_body": lambda d: f"""
        <div dir="rtl" style="font-family:Arial,sans-serif;
                               max-width:600px; margin:auto; padding:24px;
                               background:#D4EDDA;
                               border:1px solid #1E8449;
                               border-radius:8px;">

            <h2 style="color:#1E8449;">✅ تم التأكيد بنجاح</h2>

            <p>مرحباً <strong>{d['name']}</strong>،</p>

            <p>تم تأكيد نشاطك بنجاح. تمت إعادة تعيين
               عداد عدم النشاط.</p>

            <p>لن يتم إرسال أي تحذيرات إضافية حتى
               الفترة القادمة.</p>

            <p style="color:#888; font-size:12px;">
                Smart Digital Legacy Management System —
                Taif University, KSA
            </p>
        </div>
        """,

        "sms_body": lambda d: (
            f"DLMS ✅: تم تأكيد نشاطك يا {d['name']}. شكراً!"
        ),

        "inapp_body": lambda d: {
            "title": "✅ تم تأكيد نشاطك",
            "message": "تم إعادة تعيين عداد عدم النشاط بنجاح.",
            "action_url": None,
            "severity": "success",
        },
    },

    # ── 5. BENEFICIARY ACCESS GRANTED ────────────────────────────────
    "BENEFICIARY_ACCESS_GRANTED": {

        "email_subject": lambda d: (
            f"إشعار وصول — أصول {d['deceased_name']} الرقمية | DLMS"
        ),

        "email_body": lambda d: f"""
        <div dir="rtl" style="font-family:Arial,sans-serif;
                               max-width:600px; margin:auto; padding:24px;
                               border:1px solid #1B3A6B;
                               border-radius:8px;">

            <h2 style="color:#1B3A6B;">
                إشعار وصول للأصول الرقمية
            </h2>

            <p>مرحباً <strong>{d['beneficiary_name']}</strong>،</p>

            <p>تم تأكيد وفاة <strong>{d['deceased_name']}</strong>.
               وفقاً لتعليماته المسجلة مسبقاً، تم تخصيص
               الأصول الرقمية التالية لك:</p>

            <ul style="background:#f9f9f9; padding:16px;
                        border-radius:6px;">
                {''.join(f'<li style="margin:8px 0;">{a}</li>'
                         for a in d['assets'])}
            </ul>

            <p>رمز الوصول الخاص بك:</p>
            <div style="text-align:center; margin:16px 0;">
                <span style="font-size:28px; font-weight:bold;
                              color:#1B3A6B; letter-spacing:6px;">
                    {d['access_code']}
                </span>
            </div>

            <div style="text-align:center; margin:24px 0;">
                <a href="{d['access_url']}"
                   style="background:#1A7A74; color:white;
                          padding:14px 32px; border-radius:6px;
                          text-decoration:none; font-size:16px;">
                    الدخول للنظام
                </a>
            </div>

            <p style="color:#C0392B; font-size:13px;">
                ⚠️ هذا الرابط صالح لمدة 72 ساعة فقط.
            </p>

            <p style="color:#888; font-size:12px;">
                Smart Digital Legacy Management System —
                Taif University, KSA
            </p>
        </div>
        """,

        "sms_body": lambda d: (
            f"DLMS: تم منح وصولك لأصول {d['deceased_name']}. "
            f"رمزك: {d['access_code']} — {d['access_url']}"
        ),

        "inapp_body": lambda d: {
            "title": "تم منح الوصول للأصول الرقمية",
            "message": (
                f"يمكنك الآن الوصول للأصول الرقمية "
                f"المخصصة لك من {d['deceased_name']}."
            ),
            "action_url": d["access_url"],
            "severity": "info",
        },
    },

    # ── 6. DEATH ASSUMED — sent to admin ─────────────────────────────
    "DEATH_ASSUMED_ADMIN": {

        "email_subject": lambda d: (
            f"[ADMIN] تم افتراض وفاة المستخدم: {d['username']}"
        ),

        "email_body": lambda d: f"""
        <div style="font-family:Arial,sans-serif;
                    max-width:600px; margin:auto; padding:24px;
                    border:2px solid #C0392B; border-radius:8px;">

            <h2 style="color:#C0392B;">
                [ADMIN ALERT] Death Assumption Triggered
            </h2>

            <table style="width:100%; border-collapse:collapse;">
                <tr>
                    <td style="padding:8px; font-weight:bold;">
                        Username:
                    </td>
                    <td style="padding:8px;">{d['username']}</td>
                </tr>
                <tr style="background:#f9f9f9;">
                    <td style="padding:8px; font-weight:bold;">
                        User ID:
                    </td>
                    <td style="padding:8px;">{d['user_id']}</td>
                </tr>
                <tr>
                    <td style="padding:8px; font-weight:bold;">
                        Days Inactive:
                    </td>
                    <td style="padding:8px;">{d['days_inactive']}</td>
                </tr>
                <tr style="background:#f9f9f9;">
                    <td style="padding:8px; font-weight:bold;">
                        Triggered At:
                    </td>
                    <td style="padding:8px;">{d['triggered_at']}</td>
                </tr>
            </table>

            <p style="margin-top:16px;">
                Posthumous actions will be executed automatically.
                Log in to the admin panel to review or override.
            </p>
        </div>
        """,

        "sms_body": lambda d: (
            f"DLMS ADMIN: Death assumed for user "
            f"{d['username']} after {d['days_inactive']} inactive days."
        ),

        "inapp_body": lambda d: {
            "title": "[Admin] Death Assumption Triggered",
            "message": (
                f"User {d['username']} has been marked as "
                f"presumed deceased after "
                f"{d['days_inactive']} days of inactivity."
            ),
            "action_url": d.get("admin_url"),
            "severity": "critical",
        },
    },
}