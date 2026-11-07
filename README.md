# InstallingAnsibleDeployment — تثبيت Ansible على Ubuntu Server (المرحلة 1 فقط)

> **المهمة:** تثبيت Ansible **مباشرة على Ubuntu Server** وتجهيز بيئة تشغيل أساسية ومستقرة. **Ansible ليس داخل Docker** ولا يعمل كخدمة خلفية.  
> **النطاق:** هذه المرحلة **تثبيت + تحقق + توثيق فقط**. **لا تكامل** مع Jenkins/Docker/Traefik/Odoo ولا Playbooks إنتاجية ولا Collections تكامل.  
> **تنظيم فقط:** لا حذف لملفات/مجلدات. الملفات الأصلية (كانت فارغة) محفوظة في `legacy/`. لا تدّعِ نجاح اختبار لم يُنفذ.

## المسار
`InstallingAnsibleDeployment/` (الموصى به على الهدف: `/opt/InstallingAnsibleDeployment`)

## الملفات المطلوبة (هذه المرحلة)
| الملف | الغرض |
|---|---|
| `README.md` | نظرة عامة، النطاق، القواعد، طريقة التشغيل السريع |
| `INSTALLATION_GUIDE.md` | خطوات التثبيت والتحقق التفصيلية (pipx موصى به) |
| `INSTALLATION_REPORT.md` | تقرير نتائج **فعلية** (بوابة الانتقال — لا Phase 2 قبل PASS) |
| `VERSION_INFO.md` | الإصدارات الفعلية المرصودة/المسجلة (يُحدَّث بعد التنفيذ على الهدف) |
| `VERIFY_INSTALLATION.sh` | سكربت تحقق يحفظ الدليل (ينفذ على Ubuntu) |
| `InstallingAnsibleCommand.md` | مرجع أوامر عربي مختصر/كامل |
| `01-Installation/` | سكربتات مساعدة (preflight/install/verify) + docs |
| `02-Integration/` | **لاحقًا فقط** بعد PASS — هيكل فارغ/بوابات (Jenkins, Docker, Traefik, Odoo, Playbooks) |
| `legacy/` | حفظ النسخ الأصلية القديمة (بدون حذف) |

## قواعد التنفيذ (إلزامية)
- التثبيت Native على Ubuntu؛ **لا** Ansible داخل Docker.
- فحص النظام أولًا والاحتفاظ بالإصدارات/الإعدادات الحالية قبل أي تحديث. تثبيت المتطلبات **الناقصة فقط**.
- تثبيت Ansible عبر **pipx** بصورة مستقلة؛ **لا تستخدم `sudo` مع `pipx install`**. تحقق من `PATH` وتوافق Python.
- لا تثبّت Jenkins/Docker/خدمات أخرى ضمن هذه المرحلة. لا تعدّل Docker/Traefik. لا تنظيف/إزالة غير مطلوب.
- سجّل الأوامر والنتائج الفعلية. التوقف بعد نجاح التثبيت وإنشاء التقرير النهائي. **لا انتقال للتكامل إلا بطلب مستقل وبعد PASS موثق.**