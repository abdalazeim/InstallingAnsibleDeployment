# VERSION_INFO.md — Ansible (المرحلة 1)

> حدّث هذا الملف **بعد التنفيذ الفعلي على Ubuntu الهدف**. لا تضع قيماً مفترضة.

| المكوّن | القيمة المرصودة (قبل) | القيمة المرصودة (بعد/الحالية) | ملاحظات |
|---|---|---|---|
| Ubuntu | لم يُرصد | لم يُرصد | `lsb_release -a` / `/etc/os-release` |
| Kernel | — | لم يُرصد | `uname -a` |
| Python 3 | لم يُرصد | لم يُرصد | `python3 --version` |
| Ansible (ansible-core) | لم يُرصد/قد يكون موجودًا | لم يُرصد | `ansible --version` — احتفظ بالإصدار الحالي قبل أي تغيير |
| ansible-playbook | — | لم يُرصد | `ansible-playbook --version` |
| ansible-galaxy | — | لم يُرصد | `ansible-galaxy --version` |
| طريقة التثبيت | — | لم يُحدد | `pipx` (موصى به، بدون `sudo pipx install`) أو `apt` |
| pipx | لم يُرصد | لم يُرصد | `pipx --version` |
| Git | لم يُرصد | لم يُرصد | `git --version` |
| SSH client | لم يُرصد | لم يُرصد | `ssh -V` |
| PATH يحتوي `~/.local/bin`؟ | — | لم يُتحقق | بعد `pipx ensurepath` + إعادة الجلسة |

## ملاحظات توافق/حفظ الحالة
- لا إزالة/استبدال Ansible أو إعدادات النظام الحالية دون مراجعة. وثّق أي تحديث اختياري (مثل `apt upgrade`) وتأثيره.