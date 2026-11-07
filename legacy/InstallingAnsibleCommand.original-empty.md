<div dir="rtl" align="right">

# InstallingAnsibleCommand.md — دليل أوامر Ansible (تثبيت مباشر على Ubuntu)
## تنظيم مرحلي، نفس الفكرة السابقة (تثبيت أولًا والتحقق فقط → تكامل/Playbooks لاحقًا)، مع الحفاظ على الملفات القديمة

> **قرار مهم:** يتم تثبيت **Ansible مباشرة على Ubuntu Server (Native)**، **وليس داخل Docker**. Ansible مسؤول عن إدارة السيرفر نفسه وتشغيل/تهيئة Docker والخدمات والحاويات. لا حاجة لتشغيل خدمة Ansible في الخلفية.  
> **تنظيم فقط (بدون حذف):** الملفات الأصلية (كانت فارغة) محفوظة في `legacy/`.  
> **قاعدة:** لا تدّعِ نجاح اختبار لم يُنفذ. سجّل النتائج الفعلية في `INSTALLATION_REPORT.md`. لا تبدأ المرحلة 2 قبل PASS المرحلة 1.

- الحزمة المنظمة: `InstallingAnsibleDeployment/`
- بوابة المرحلة 1: `INSTALLATION_REPORT.md`
- المسار الموصى به على Ubuntu: `/opt/InstallingAnsibleDeployment`

</div>

---

## تقسيم العمل (صارم)
| المرحلة | النطاق | ممنوع في هذه المرحلة |
|---|---|---|
| **1) تثبيت Ansible والتحقق من عمله فقط** | تثبيت Native على Ubuntu + أوامر تحقق + توثيق النتائج | ربط Jenkins/Docker/Traefik/Odoo، كتابة Playbooks إنتاجية، تثبيت Ansible داخل Docker |
| **2) التكامل وPlaybooks (لاحقًا)** | `02-Integration/` — Jenkins, Docker, Traefik, Odoo, Playbooks؛ كل جزء مستقل ومختبر وموثق | البدء قبل PASS المرحلة 1؛ تغييرات إنتاج دون موافقة + نسخة احتياطية قابلة للاستعادة |

---

## المرحلة الأولى: التثبيت على Ubuntu (Installation Only)

### المسار
- مجلد المشروع: `InstallingAnsibleDeployment/` (يُنصح بنسخه إلى `/opt/InstallingAnsibleDeployment`).
- أوامر التثبيت تنفذ **مباشرة على Ubuntu Server**.

### وضع الملفات تحت `/opt` (بدون استبدال هدف موجود)
```bash
# استنساخ/نسخ المجلد المنظم إلى /opt (عدّل المصدر حسب مكان المستودع)
sudo git clone <REPO_URL> /opt/InstallingAnsibleDeployment-src
sudo cp -a /opt/InstallingAnsibleDeployment-src/InstallingAnsibleDeployment /opt/InstallingAnsibleDeployment

# أو: سكربت آمن (يرفض الكتابة فوق هدف موجود)
sudo bash /path/to/InstallingAnsibleDeployment/01-Installation/scripts/deploy-to-opt.sh /opt/InstallingAnsibleDeployment

cd /opt/InstallingAnsibleDeployment/01-Installation
chmod +x scripts/*.sh
bash scripts/preflight.sh   # فحص OS/Python/Ansible الحالي/SSH — لا حذف
```

---

## الطريقة (أ): التثبيت الأساسي من مستودعات Ubuntu (apt)

> بسيطة ومباشرة. نفّذ الأوامر على الجهاز.

### 1. تحديث النظام
```bash
sudo apt update
sudo apt upgrade -y
```

### 2. تثبيت المتطلبات الأساسية
```bash
sudo apt install -y \
  software-properties-common \
  ca-certificates \
  curl \
  git \
  gnupg \
  python3 \
  python3-pip \
  python3-venv \
  python3-yaml \
  openssh-client
```

### 3. تثبيت Ansible من مستودعات Ubuntu
```bash
sudo apt install -y ansible
```

### 4. التحقق من التثبيت
```bash
ansible --version
ansible-playbook --version
ansible-galaxy --version
```

### 5. التحقق من Python
```bash
python3 --version
```

### 6. التحقق من Ansible Collections الأساسية
```bash
ansible-galaxy collection list
```

### 7. اختبار Ansible محليًا (مطلوب)
```bash
ansible localhost -i localhost, -c local -m ping
```

**النتيجة المتوقعة:**
```text
localhost | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

**ملاحظة:** هذا تثبيت أساسي من مستودعات Ubuntu. **لا يحتاج** تثبيت Ansible داخل Docker أو إعداد Jenkins في هذه المرحلة.

---

## الطريقة (ب) الموصى بها: التثبيت عبر `pipx` (بيئة Python مستقلة)

> موصى بها لتثبيت Ansible في بيئة Python مستقلة بدل بيئة نظام Python (نهج موثق رسميًا). لا تثبّت Ansible داخل Docker ولا تشغّل خدمة Ansible في الخلفية.

### 1. تثبيت المتطلبات
```bash
sudo apt update
sudo apt install -y \
  python3 \
  python3-pip \
  python3-venv \
  pipx \
  git \
  openssh-client \
  sshpass
```

### 2. تجهيز `pipx`
```bash
pipx ensurepath
# إذا كنت على SSH: أعد فتح الجلسة أو نفّذ:
source ~/.bashrc
```

### 3. تثبيت Ansible
```bash
pipx install --include-deps ansible
```

### 4. التحقق
```bash
ansible --version
ansible-playbook --version
ansible-galaxy --version
```

### 5. إنشاء/استخدام مجلد المشروع
```bash
mkdir -p ~/InstallingAnsibleDeployment
cd ~/InstallingAnsibleDeployment
# أو استخدم المسار المنظم: /opt/InstallingAnsibleDeployment
```

### 6. اختبار التشغيل المحلي (مطلوب)
```bash
ansible localhost -i localhost, -c local -m ping
```

---

## سكربتات مساعدة (داخل `01-Installation/scripts/`)
> السكربتات للتسهيل فقط؛ نفّذها بعد المراجعة وسجّل النتائج الفعلية.

```bash
cd /opt/InstallingAnsibleDeployment/01-Installation
bash scripts/preflight.sh                 # فحص — بدون حذف
bash scripts/install-ubuntu.sh pipx       # موصى به (أو: apt)
bash scripts/verify.sh                    # يحفظ verify-output.txt
```

---

## بوابة المرحلة 1 (إلزامية)
حدّث `/opt/InstallingAnsibleDeployment/INSTALLATION_REPORT.md` بنتائج **فعلية** (أوامر + خرج/`verify-output.txt`). **لا تبدأ المرحلة 2** إلا بعد PASS لكل البنود:
- [ ] `ansible`, `ansible-playbook`, `ansible-galaxy` تعمل (`--version`).
- [ ] `python3 --version` متاح.
- [ ] `ansible localhost -i localhost, -c local -m ping` يعيد `pong/SUCCESS`.
- [ ] لا أخطاء حرجة.
- [ ] الدليل موثق.

عند الفشل: أصلح وأعد الاختبار وتوقف عن التكامل.

---

## المرحلة 2 — التكامل وPlaybooks (لاحقًا، بعد PASS فقط)
داخل `02-Integration/` وبشكل مستقل ومختبر: `jenkins/`, `docker/`, `traefik/`, `odoo/`, `playbooks/`.  
كل جزء يحتاج: فحص متطلبات → ملفات مستقلة → توثيق → اختبار آمن → `TEST_REPORT.md` بنتائج فعلية. لا أسرار في Git. لا تغييرات إنتاج دون موافقة صريحة + نسخة احتياطية قابلة للاستعادة.

## حفظ القديم (تنظيم فقط)
`legacy/` يحتوي الملفات الأصلية المحفوظة (كانت فارغة): `README.original-empty.md`, `InstallingAnsibleCommand.original-empty.md`. **لم يُحذف شيء.**