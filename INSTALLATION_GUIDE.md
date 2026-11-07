# INSTALLATION_GUIDE.md — تثبيت Ansible على Ubuntu Server (المرحلة 1)

> **النطاق:** تثبيت + تحقق فقط. لا تكامل، لا Playbooks إنتاجية، لا Collections تكامل، لا Docker/Traefik/Jenkins.  
> **مهم:** نفّذ مباشرة على Ubuntu. راجع كل خطوة. لا تحذف ملفات/إعدادات. لا تدّعِ نجاح اختبار لم يُنفذ.

## 0) وضع المشروع على الهدف
```bash
# نسخ منظم إلى /opt دون استبدال هدف موجود
sudo bash /path/to/InstallingAnsibleDeployment/01-Installation/scripts/deploy-to-opt.sh /opt/InstallingAnsibleDeployment
cd /opt/InstallingAnsibleDeployment
chmod +x VERIFY_INSTALLATION.sh 01-Installation/scripts/*.sh
```

## 1) فحص النظام (قبل أي تثبيت)
سجّل النتائج كما هي (الاحتفاظ بالإصدارات/الإعدادات الحالية):
```bash
bash 01-Installation/scripts/preflight.sh
# أو يدويًا:
lsb_release -a || cat /etc/os-release
python3 --version
ansible --version || echo "(not installed)"
pipx --version || echo "(pipx not found)"
git --version; ssh -V
id; groups
echo "$PATH"
```
إذا كان Ansible مثبتًا مسبقًا: **لا تزل/تستبدل** دون مراجعة؛ وثّق الإصدار الحالي في `VERSION_INFO.md`/`INSTALLATION_REPORT.md`.

## 2) تثبيت المتطلبات الناقصة فقط (apt)
```bash
sudo apt update
# sudo apt upgrade -y   # اختياري/بعد مراجعة أثره؛ ليس مطلوبًا ضمن تثبيت Ansible الأساسي
sudo apt install -y python3 python3-pip python3-venv pipx git openssh-client sshpass ca-certificates curl
```

## 3) تثبيت Ansible عبر `pipx` (موصى به، بيئة مستقلة)
> **لا تستخدم `sudo` مع `pipx install`** (pipx تثبيت مستخدم).

```bash
pipx ensurepath
# SSH: أعد فتح الجلسة أو:
source ~/.bashrc
pipx install --include-deps ansible
# إن كان مثبتًا بالفعل وتريد تحديثًا مدروسًا (اختياري): pipx upgrade --include-deps ansible
```
تحقق من `PATH` (عادة `~/.local/bin`): `command -v ansible`.

## 4) بديل (اختياري) — apt من مستودعات Ubuntu
```bash
sudo apt install -y software-properties-common python3-yaml
sudo apt install -y ansible
```
وثّق الطريقة المستخدمة في التقرير.

## 5) اختبارات التحقق (إلزامية)
```bash
ansible --version
ansible-playbook --version
ansible-galaxy --version
python3 --version
ansible localhost -i localhost, -c local -m ping
# المتوقع: localhost | SUCCESS => { "changed": false, "ping": "pong" }
```
أو:
```bash
cd /opt/InstallingAnsibleDeployment
./VERIFY_INSTALLATION.sh   # يحفظ verify-output.txt
```

## 6) توثيق وإغلاق المرحلة 1
- حدّث `VERSION_INFO.md` بالإصدارات **الفعلية**.
- حدّث `INSTALLATION_REPORT.md` بنتائج فعلية + أدلة (مرفق `verify-output.txt`). علّم PASS فقط عند نجاح كل الاختبارات.
- **توقف هنا.** لا تكامل Jenkins/Docker/Traefik/Odoo ولا Playbooks تكامل ولا Collections تكامل حتى طلب مستقل وبعد PASS.