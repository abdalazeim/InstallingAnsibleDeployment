# المرحلة 2 — تكامل مشروع Ansible (مُقيّد: لا تُنفّذ قبل نجاح المرحلة 1)

> **الحالة:** غير منفّذة. هذا المجلد **هيكل أساسي** للعبوات التكاملية (playbooks) التي سيتم تنفيذها **فقط بعد** تسجيل نجاح المرحلة 1 الحقيقي في ملف `../INSTALLATION_REPORT.md` (تثبيت Ansible والتحقق منه على Ubuntu).
> **مهم:** يظل Ansible مثبتاً **أصلياً على Ubuntu (وليس Docker)**. لا تُعيد تثبيت Ansible إذا كان مثبتاً ويعمل بالفعل.

---

## بوابة الدخول (إلزامية)
- [ ] نجاح المرحلة 1 مع أدلة حقيقية في `../INSTALLATION_REPORT.md` و `../VERSION_INFO.md`.
- [ ] لا مزاعم غير مُتحقّق منها. توقّف عند أي فشل حرج.

---

## النطاق (بعد البوابة)
فحص بيئة Ansible (الإصدار/Python، المجموعات، SSH، صلاحيات المستخدم، اتصال الهدف، حالة Docker/Traefik/Jenkins/Odoo حسب الحاجة) **قبل** إجراء أي تغييرات. ثم تنفيذ مكونات مختبرة بشكل مستقل:

- **إعداد مشروع Ansible:** `ansible.cfg`، المخازن (development/staging/production)، `group_vars`/`host_vars`، الأدوار (roles)، متطلبات المجموعات (collections requirements)، القوالب (templates)، المعالجات (handlers)، الملفات (files)، Vault.
- **التكاملات (منفصلة، مُساوية للذات idempotent):**
  - **Docker** (المحرك/compose/الشبكات/الحاويات/الأحجام/الصور/النشر/الصحة/السجلات)
  - **Traefik** (فحص التكوين الحالي ونسخه احتياطياً قبل التغييرات؛ التوجيه/TLS/Let's Encrypt/تحدي Cloudflare DNS حسب الحاجة)
  - **Odoo** (إصدار 17/19 **مفصولين تماماً** تكوينات/قواعد بيانات/أحجام/متغيرات بيئة؛ النشر، Postgres، النسخ الاحتياطي/الاستعادة، فحوصات الصحة؛ **لا ترقيات لقاعدة بيانات/وحدات الإنتاج دون موافقة صريحة + نسخة احتياطية قابلة للاستعادة**)
  - **Jenkins** (تشغيل اللعبات مع SSH/بيانات اعتماد، متغيرات/مخزون/اختيار بيئة، تسجيل/معالجة الأخطاء/التوقف عند الفشل؛ أقل امتيازات — لا root/منفذ Docker غير ضروري)

---

## اللعبات المستقلة (إنشاء/اختبار بشكل منفصل؛ لا كيان واحد موحد)
`system_preparation.yml`، `docker_installation.yml`، `docker_configuration.yml`، `traefik_configuration.yml`، `odoo17_deployment.yml`، `odoo19_deployment.yml`، `postgresql_management.yml`، `backup.yml`، `restore.yml`، `health_check.yml`، `maintenance.yml`.

---

## الاختبار (يُسجّل في `docs/IMPLEMENTATION_REPORT.md` / تقارير لكل مكون)
التحقق من بناء الجملة والمخزون، SSH/`ansible` ping، تشغيل اللعبات، **المُساواة للذات (idempotency)**، صحة Docker/Odoo/Postgres، إجراءات النسخ الاحتياطي/الاستعادة. الاختبار في البيئة التجريبية (staging) أولاً؛ لا انتقال للإنتاج قبل التحقق من النتائج.

---

## الأمان
مفاتيح SSH، Ansible Vault، أقل امتيازات/sudo، لا أسرار في Git، حماية المخزون/السجلات، نسخ احتياطي للتكوينات قبل التعديل.

---

## البنية (الهيكل الأساسي)
`inventories/{development,staging,production}/`، `playbooks/`، `roles/`، `collections/`، `templates/`، `handlers/`، `files/`، `vault/`، `docs/`، `scripts/`. الحفاظ على القابلية لإعادة الاستخدام والتوسع.

---

# دليل شامل باللغة العربية: جميع الفوائد، طريقة الاستخدام، التثبيت، وكل شيء

## 1. ما هو Ansible ولماذا نستخدمه؟

### الفوائد الرئيسية:
| الفائدة | الوصف |
|-----------|-------|
| **بلا وكيل (Agentless)** | لا يحتاج تثبيت برامج على الخوادم المستهدفة، يعمل عبر SSH |
| **إعلاني (Declarative)** | تصف *النتيجة المطلوبة* وليس *خطوات التنفيذ* |
| **مُساوي للذات (Idempotent)** | إعادة التشغيل لا تغيّر الحالة إذا كانت مطابقة للمطلوب |
| **بسيط وقابل للقراءة** | يستخدم YAML، سهل التعلم والصيانة |
| **قوي وقابل للتوسع** | يدعم الأدوار، المجموعات، الإضافات، والقوالب |
| **إدارة التكوين كما كود (IaC)** | كل شيء في Git، قابل للمراجعة والإصدار |

---

## 2. المتطلبات المسبقة (قبل البدء)

### على جهاز التحكم (Control Node - حيث تشغّل Ansible):
- **نظام تشغيل:** Linux (Ubuntu 22.04/24.04 مستحسن) أو macOS أو WSL2 على Windows
- **Python:** ≥ 3.9
- **SSH Client:** OpenSSH
- **Git:** لإدارة الكود

### على الخوادم المستهدفة (Managed Nodes):
- **نظام تشغيل:** Ubuntu 22.04/24.04 LTS
- **Python:** ≥ 3.9 (مثبت افتراضياً)
- **SSH Server:** مفتوح ومنضبط
- **مستخدم sudo:** بصلاحية `NOPASSWD` أو بكلمة مرور

---

## 3. التثبيت (المرحلة 1 — ملخص سريع)

> **تنبيه:** هذا ملخص فقط. التفاصيل الكاملة في `../INSTALLATION_REPORT.md` و `../01-Prerequisites/`.

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت المتطلبات
sudo apt install -y python3 python3-pip python3-venv sshpass git curl wget

# إنشاء بيئة افتراضية (مستحسن)
python3 -m venv ~/.ansible-venv
source ~/.ansible-venv/bin/activate

# تثبيت Ansible
pip install --upgrade pip
pip install ansible-core==2.17.*  # أو أحدث إصدار مستقر

# التحقق
ansible --version
ansible localhost -m ping
```

**ملاحظة هامة:** في هذا المشروع، Ansible يثبت **أصلياً على Ubuntu** وليس داخل Docker.

---

## 4. هيكل المشروع (بعد التكامل)

```
02-Integration/
├── ansible.cfg                 # إعدادات Ansible الرئيسية
├── inventories/                # مخازن البيئات
│   ├── development/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   ├── staging/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   └── production/
│       ├── hosts.yml
│       └── group_vars/
├── playbooks/                  # اللعبات الرئيسية
│   ├── system_preparation.yml
│   ├── docker_installation.yml
│   ├── docker_configuration.yml
│   ├── traefik_configuration.yml
│   ├── odoo17_deployment.yml
│   ├── odoo19_deployment.yml
│   ├── postgresql_management.yml
│   ├── backup.yml
│   ├── restore.yml
│   ├── health_check.yml
│   └── maintenance.yml
├── roles/                      # الأدوار القابلة لإعادة الاستخدام
│   ├── common/
│   ├── docker/
│   ├── traefik/
│   ├── odoo17/
│   ├── odoo19/
│   ├── postgresql/
│   └── backup/
├── collections/                # متطلبات المجموعات الخارجية
│   └── requirements.yml
├── templates/                  # قوالب Jinja2
├── handlers/                   # معالجات الأحداث
├── files/                      # ملفات ثابتة
├── vault/                      # أسرار مشفرة (Ansible Vault)
├── docs/                       # توثيق إضافي
│   └── IMPLEMENTATION_REPORT.md
└── scripts/                    # سكريبتات مساعدة
```

---

## 5. الإعداد الأساسي: `ansible.cfg`

```ini
[defaults]
inventory = ./inventories/development/hosts.yml
remote_user = ansible
become = true
become_method = sudo
become_ask_pass = false
host_key_checking = false
retry_files_enabled = false
stdout_callback = yaml
callback_whitelist = timer, profile_tasks
collections_paths = ./collections
roles_path = ./roles
library = ./library
module_utils = ./module_utils
filter_plugins = ./filter_plugins
action_plugins = ./action_plugins
callback_plugins = ./callback_plugins
lookup_plugins = ./lookup_plugins
vars_plugins = ./vars_plugins
strategy_plugins = ./strategy_plugins
cache_plugins = ./cache_plugins
terminal_plugins = ./terminal_plugins
cliconf_plugins = ./cliconf_plugins
httpapi_plugins = ./httpapi_plugins
netconf_plugins = ./netconf_plugins

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no
pipelining = true
control_path = %(directory)s/%%h-%%r
transfer_method = smart

[privilege_escalation]
become = true
become_method = sudo
become_user = root
become_ask_pass = false

[galaxy]
server_list = release_galaxy

[galaxy_server.release_galaxy]
url = https://galaxy.ansible.com/
token = 
```

---

## 6. المخزون (Inventory) — مثال للبيئة التجريبية

**`inventories/staging/hosts.yml`:**
```yaml
all:
  children:
    docker_hosts:
      hosts:
        staging-server-01:
          ansible_host: 10.0.1.10
          ansible_user: ansible
          ansible_ssh_private_key_file: ~/.ssh/id_rsa_staging
    traefik_hosts:
      hosts:
        staging-server-01:
    odoo17_hosts:
      hosts:
        staging-server-01:
          odoo_version: "17.0"
          odoo_port: 8069
          odoo_longpolling_port: 8072
    odoo19_hosts:
      hosts:
        staging-server-01:
          odoo_version: "19.0"
          odoo_port: 18069
          odoo_longpolling_port: 18072
    postgresql_hosts:
      hosts:
        staging-server-01:
          pg_version: "16"
          pg_port: 5432
    jenkins_controller:
      hosts:
        jenkins-controller:
          ansible_host: 10.0.1.5
          ansible_user: jenkins
  vars:
    environment: staging
    docker_network_name: odoo_net_staging
    traefik_domain: staging.example.com
    letsencrypt_email: admin@example.com
```

**`inventories/staging/group_vars/all.yml`:**
```yaml
# متغيرات مشتركة لجميع المضيفين
timezone: "Africa/Casablanca"
locale: "en_US.UTF-8"

# Docker
docker_version: "27.0.*"
docker_compose_version: "v2.28.*"
docker_storage_driver: "overlay2"
docker_log_driver: "json-file"
docker_log_opts:
  max-size: "10m"
  max-file: "3"

# Traefik
traefik_version: "v3.0"
traefik_network: "traefik_net"
traefik_dashboard_enabled: true
traefik_dashboard_auth: "{{ vault_traefik_dashboard_auth }}"

# Odoo مشترك
odoo_db_user: "odoo"
odoo_db_password: "{{ vault_odoo_db_password }}"
odoo_admin_password: "{{ vault_odoo_admin_password }}"
odoo_master_password: "{{ vault_odoo_master_password }}"

# PostgreSQL
postgresql_version: "16"
postgresql_max_connections: 200
postgresql_shared_buffers: "256MB"
postgresql_effective_cache_size: "768MB"
postgresql_work_mem: "16MB"
postgresql_maintenance_work_mem: "128MB"

# النسخ الاحتياطي
backup_schedule: "0 2 * * *"
backup_retention_days: 30
backup_storage_path: "/mnt/backups"
backup_s3_enabled: false
```

---

## 7. المجموعات المطلوبة (Collections)

**`collections/requirements.yml`:**
```yaml
collections:
  - name: community.docker
    version: ">=3.10.0"
  - name: community.general
    version: ">=8.0.0"
  - name: ansible.posix
    version: ">=1.5.0"
  - name: community.postgresql
    version: ">=2.5.0"
  - name: geerlingguy.docker
    version: ">=3.0.0"
  - name: nginxinc.nginx
    version: ">=1.0.0"

roles: []
```

**التثبيت:**
```bash
ansible-galaxy collection install -r collections/requirements.yml -p ./collections
```

---

## 8. اللعبات الرئيسية — أمثلة عملية

### 8.1 إعداد النظام (`system_preparation.yml`)
```yaml
---
- name: System Preparation | Configure base system
  hosts: all
  become: true
  gather_facts: true
  tags: [system, preparation]
  
  pre_tasks:
    - name: Update apt cache
      apt:
        update_cache: true
        cache_valid_time: 3600
      tags: [packages]
  
  roles:
    - role: common
      tags: [common]
  
  tasks:
    - name: Install essential packages
      apt:
        name:
          - curl
          - wget
          - gnupg2
          - software-properties-common
          - apt-transport-https
          - ca-certificates
          - lsb-release
          - ufw
          - fail2ban
          - htop
          - net-tools
          - vim
          - git
        state: present
      tags: [packages]
  
    - name: Configure timezone
      timezone:
        name: "{{ timezone }}"
      tags: [timezone]
  
    - name: Configure locale
      locale_gen:
        name: "{{ locale }}"
        state: present
      tags: [locale]
  
    - name: Set default locale
      copy:
        dest: /etc/default/locale
        content: |
          LANG={{ locale }}
          LC_ALL={{ locale }}
      tags: [locale]
  
    - name: Configure UFW firewall
      ufw:
        rule: allow
        port: "{{ item }}"
        proto: tcp
      loop:
        - "22"      # SSH
        - "80"      # HTTP
        - "443"     # HTTPS
        - "8080"    # Traefik Dashboard
      tags: [firewall]
  
    - name: Enable UFW
      ufw:
        state: enabled
        policy: deny
      tags: [firewall]
  
    - name: Configure fail2ban
      copy:
        dest: /etc/fail2ban/jail.local
        content: |
          [DEFAULT]
          bantime = 3600
          findtime = 600
          maxretry = 5
          
          [sshd]
          enabled = true
          port = ssh
          filter = sshd
          logpath = /var/log/auth.log
          maxretry = 3
      notify: restart fail2ban
      tags: [security]
  
  handlers:
    - name: restart fail2ban
      service:
        name: fail2ban
        state: restarted
```

### 8.2 تثبيت Docker (`docker_installation.yml`)
```yaml
---
- name: Docker Installation | Install Docker Engine and Compose
  hosts: docker_hosts
  become: true
  gather_facts: true
  tags: [docker, installation]
  
  roles:
    - role: geerlingguy.docker
      tags: [docker]
  
  vars:
    docker_edition: "ce"
    docker_package: "docker-ce={{ docker_version }}~ubuntu.{{ ansible_distribution_release }}~{{ ansible_architecture }}"
    docker_compose_package: "docker-compose-plugin={{ docker_compose_version }}"
    docker_users:
      - "{{ ansible_user }}"
    docker_daemon_options:
      log-driver: "{{ docker_log_driver }}"
      log-opts:
        max-size: "{{ docker_log_opts.max-size }}"
        max-file: "{{ docker_log_opts.max-file }}"
      storage-driver: "{{ docker_storage_driver }}"
      iptables: true
      ipv6: false
      live-restore: true
      userland-proxy: false
      experimental: false
      metrics-addr: "127.0.0.1:9323"
    docker_networks:
      - name: "{{ docker_network_name }}"
        driver: bridge
        attachable: true
        internal: false
        enable_ipv6: false
      - name: "{{ traefik_network }}"
        driver: bridge
        attachable: true
        internal: false
        enable_ipv6: false
  
  tasks:
    - name: Verify Docker installation
      command: docker --version
      register: docker_version_output
      changed_when: false
      tags: [verify]
  
    - name: Verify Docker Compose installation
      command: docker compose version
      register: compose_version_output
      changed_when: false
      tags: [verify]
  
    - name: Display versions
      debug:
        msg:
          - "Docker: {{ docker_version_output.stdout }}"
          - "Compose: {{ compose_version_output.stdout }}"
      tags: [verify]
```

### 8.3 نشر Odoo 17 (`odoo17_deployment.yml`)
```yaml
---
- name: Odoo 17 Deployment | Deploy Odoo 17 with PostgreSQL
  hosts: odoo17_hosts
  become: true
  gather_facts: true
  tags: [odoo, odoo17, deployment]
  
  vars:
    odoo_container_name: "odoo17_{{ environment }}"
    odoo_image: "odoo:17.0"
    odoo_port: "{{ odoo_port | default(8069) }}"
    odoo_longpolling_port: "{{ odoo_longpolling_port | default(8072) }}"
    odoo_data_dir: "/opt/odoo17/data"
    odoo_config_dir: "/opt/odoo17/config"
    odoo_addons_dir: "/opt/odoo17/addons"
    odoo_log_dir: "/var/log/odoo17"
    pg_container_name: "postgres16_odoo17_{{ environment }}"
    pg_image: "postgres:16-alpine"
    pg_data_dir: "/opt/postgres16/odoo17/data"
  
  pre_tasks:
    - name: Create required directories
      file:
        path: "{{ item }}"
        state: directory
        mode: "0755"
        owner: "{{ ansible_user }}"
        group: "{{ ansible_user }}"
      loop:
        - "{{ odoo_data_dir }}"
        - "{{ odoo_config_dir }}"
        - "{{ odoo_addons_dir }}"
        - "{{ odoo_log_dir }}"
        - "{{ pg_data_dir }}"
      tags: [directories]
  
    - name: Generate Odoo configuration
      template:
        src: odoo17/odoo.conf.j2
        dest: "{{ odoo_config_dir }}/odoo.conf"
        mode: "0640"
        owner: "{{ ansible_user }}"
        group: "{{ ansible_user }}"
      tags: [config]
  
  roles:
    - role: docker
      tags: [docker]
    - role: postgresql
      tags: [postgresql]
    - role: odoo17
      tags: [odoo17]
  
  tasks:
    - name: Deploy PostgreSQL container
      community.docker.docker_container:
        name: "{{ pg_container_name }}"
        image: "{{ pg_image }}"
        state: started
        restart_policy: unless-stopped
        networks:
          - name: "{{ docker_network_name }}"
        env:
          POSTGRES_DB: "postgres"
          POSTGRES_USER: "{{ odoo_db_user }}"
          POSTGRES_PASSWORD: "{{ odoo_db_password }}"
        volumes:
          - "{{ pg_data_dir }}:/var/lib/postgresql/data"
        healthcheck:
          test: ["CMD-SHELL", "pg_isready -U {{ odoo_db_user }}"]
          interval: 10s
          timeout: 5s
          retries: 5
          start_period: 30s
        labels:
          traefik.enable: "false"
      tags: [postgresql]
  
    - name: Wait for PostgreSQL to be ready
      wait_for:
        host: "{{ pg_container_name }}"
        port: 5432
        timeout: 60
      delegate_to: localhost
      tags: [postgresql]
  
    - name: Deploy Odoo 17 container
      community.docker.docker_container:
        name: "{{ odoo_container_name }}"
        image: "{{ odoo_image }}"
        state: started
        restart_policy: unless-stopped
        networks:
          - name: "{{ docker_network_name }}"
          - name: "{{ traefik_network }}"
        ports:
          - "{{ odoo_port }}:8069"
          - "{{ odoo_longpolling_port }}:8072"
        env:
          HOST: "{{ pg_container_name }}"
          PORT: "5432"
          USER: "{{ odoo_db_user }}"
          PASSWORD: "{{ odoo_db_password }}"
          DATABASE: "odoo17_{{ environment }}"
        volumes:
          - "{{ odoo_data_dir }}:/var/lib/odoo"
          - "{{ odoo_config_dir }}/odoo.conf:/etc/odoo/odoo.conf:ro"
          - "{{ odoo_addons_dir }}:/mnt/extra-addons"
          - "{{ odoo_log_dir }}:/var/log/odoo"
        healthcheck:
          test: ["CMD", "curl", "-f", "http://localhost:8069/web/health"]
          interval: 30s
          timeout: 10s
          retries: 3
          start_period: 60s
        labels:
          traefik.enable: "true"
          traefik.http.routers.odoo17.rule: "Host(`odoo17.{{ traefik_domain }}`)"
          traefik.http.routers.odoo17.entrypoints: "websecure"
          traefik.http.routers.odoo17.tls.certresolver: "letsencrypt"
          traefik.http.services.odoo17.loadbalancer.server.port: "8069"
      tags: [odoo17]
  
    - name: Verify Odoo 17 health
      uri:
        url: "http://localhost:{{ odoo_port }}/web/health"
        method: GET
        status_code: 200
        timeout: 10
      register: odoo_health
      retries: 10
      delay: 10
      until: odoo_health.status == 200
      tags: [verify, health]
  
    - name: Display Odoo access info
      debug:
        msg: "Odoo 17 available at: https://odoo17.{{ traefik_domain }}"
      tags: [verify]
```

---

## 9. قوالب (Templates) — أمثلة

### 9.1 `templates/odoo17/odoo.conf.j2`
```ini
[options]
; This is the password that allows database operations:
admin_passwd = {{ odoo_master_password }}
db_host = {{ hostvars[groups['postgresql_hosts'][0]].ansible_host | default('postgres16_odoo17_' ~ environment) }}
db_port = 5432
db_user = {{ odoo_db_user }}
db_password = {{ odoo_db_password }}
db_name = odoo17_{{ environment }}

; Data directory
data_dir = /var/lib/odoo

; Addons paths
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons

; Logging
logfile = /var/log/odoo/odoo-server.log
log_level = info
log_handler = [':INFO', ':WARNING', ':ERROR']
logrotate = True
max_log_size = 10000000
max_log_count = 10

; Performance
workers = {{ ansible_processor_vcpus | default(2) * 2 }}
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200

; Security
list_db = False
db_maxconn = 64
proxy_mode = True

; Email (configure as needed)
email_from = False
smtp_server = False
smtp_port = 25
smtp_user = False
smtp_password = False
smtp_ssl = False

; Web interface
dbfilter = ^odoo17_{{ environment }}$

; Longpolling
longpolling_port = 8072

; Sessions
session_max_age = 3600
session_timeout = 3600
```

### 9.2 `templates/traefik/traefik.yml.j2`
```yaml
global:
  checkNewVersion: true
  sendAnonymousUsage: false

api:
  dashboard: {{ traefik_dashboard_enabled | lower }}
  insecure: false

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
          permanent: true
  websecure:
    address: ":443"
    http:
      tls:
        certResolver: letsencrypt
      middlewares:
        - securityHeaders@file

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
    network: "{{ traefik_network }}"
    watch: true
  file:
    filename: /etc/traefik/dynamic.yml
    watch: true

certificatesResolvers:
  letsencrypt:
    acme:
      email: "{{ letsencrypt_email }}"
      storage: /etc/traefik/acme.json
      dnsChallenge:
        provider: cloudflare
        delayBeforeCheck: 10
        # Or use HTTP challenge:
        # httpChallenge:
        #   entryPoint: web

log:
  level: INFO
  format: json

accessLog:
  format: json
  filePath: /var/log/traefik/access.log
```

---

## 10. Ansible Vault — إدارة الأسرار

### إنشاء ملف Vault:
```bash
# إنشاء ملف vault مشفر
ansible-vault create vault/staging.yml

# أو تحرير ملف موجود
ansible-vault edit vault/staging.yml

# عرض محتوى الملف
ansible-vault view vault/staging.yml

# فك التشفير (للقراءة فقط)
ansible-vault decrypt vault/staging.yml
```

### مثال محتوى `vault/staging.yml`:
```yaml
vault_odoo_db_password: "super_secure_db_password_123"
vault_odoo_admin_password: "admin_secure_password_456"
vault_odoo_master_password: "master_secure_password_789"
vault_traefik_dashboard_auth: "admin:$apr1$hash..."
vault_postgresql_password: "postgres_super_password"
vault_cloudflare_api_token: "cf_api_token_xxxxx"
vault_s3_access_key: "s3_access_key"
vault_s3_secret_key: "s3_secret_key"
vault_github_token: "ghp_xxxxxxxxxxxx"
vault_ssh_private_key: |
  -----BEGIN OPENSSH PRIVATE KEY-----
  xxxxxxxxxxxx
  -----END OPENSSH PRIVATE KEY-----
```

### تشغيل اللعبات مع Vault:
```bash
# طلب كلمة المرور تفاعلياً
ansible-playbook -i inventories/staging/hosts.yml playbooks/odoo17_deployment.yml --ask-vault-pass

# أو استخدام ملف كلمة مرور (غير مستحسن للإنتاج)
ansible-playbook -i inventories/staging/hosts.yml playbooks/odoo17_deployment.yml --vault-password-file ~/.vault_pass
```

---

## 11. التشغيل والاستخدام اليومي

### 11.1 فحص الاتصال والبنية:
```bash
# اختبار الاتصال بجميع المضيفين
ansible all -i inventories/staging/hosts.yml -m ping

# اختبار اتصال مجموعة محددة
ansible odoo17_hosts -i inventories/staging/hosts.yml -m ping

# جمع الحقائق (facts)
ansible all -i inventories/staging/hosts.yml -m setup

# التحقق من بناء الجملة
ansible-playbook -i inventories/staging/hosts.yml playbooks/odoo17_deployment.yml --syntax-check
```

### 11.2 تشغيل اللعبات (Dry-run أولاً):
```bash
# تشغيل تجريبي (لا يغيّر شيئاً)
ansible-playbook -i inventories/staging/hosts.yml playbooks/odoo17_deployment.yml --check --diff

# تشغيل فعلي
ansible-playbook -i inventories/staging/hosts.yml playbooks/odoo17_deployment.yml

# تشغيل مع علامات محددة
ansible-playbook -i inventories/staging/hosts.yml playbooks/odoo17_deployment.yml --tags "config,verify"

# تجاهل علامات معينة
ansible-playbook -i inventories/staging/hosts.yml playbooks/odoo17_deployment.yml --skip-tags "packages"

# تشغيل بدءاً من مهمة محددة
ansible-playbook -i inventories/staging/hosts.yml playbooks/odoo17_deployment.yml --start-at-task "Deploy Odoo 17 container"
```

### 11.3 تشغيل لعبات محددة:
```bash
# إعداد النظام
ansible-playbook -i inventories/staging/hosts.yml playbooks/system_preparation.yml

# تثبيت Docker
ansible-playbook -i inventories/staging/hosts.yml playbooks/docker_installation.yml

# تكوين Docker
ansible-playbook -i inventories/staging/hosts.yml playbooks/docker_configuration.yml

# تكوين Traefik
ansible-playbook -i inventories/staging/hosts.yml playbooks/traefik_configuration.yml

# نشر Odoo 17
ansible-playbook -i inventories/staging/hosts.yml playbooks/odoo17_deployment.yml

# نشر Odoo 19
ansible-playbook -i inventories/staging/hosts.yml playbooks/odoo19_deployment.yml

# إدارة PostgreSQL
ansible-playbook -i inventories/staging/hosts.yml playbooks/postgresql_management.yml

# النسخ الاحتياطي
ansible-playbook -i inventories/staging/hosts.yml playbooks/backup.yml

# الاستعادة
ansible-playbook -i inventories/staging/hosts.yml playbooks/restore.yml -e "restore_date=2024-01-15"

# فحص الصحة
ansible-playbook -i inventories/staging/hosts.yml playbooks/health_check.yml

# الصيانة
ansible-playbook -i inventories/staging/hosts.yml playbooks/maintenance.yml
```

---

## 12. التكامل مع Jenkins

### 12.1 Jenkins Pipeline مثال (`scripts/jenkins/Jenkinsfile`):
```groovy
pipeline {
    agent any
    
    environment {
        ANSIBLE_HOST_KEY_CHECKING = 'false'
        ANSIBLE_STDOUT_CALLBACK = 'yaml'
        VAULT_PASSWORD_FILE = credentials('ansible-vault-password')
    }
    
    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['development', 'staging', 'production'],
            description: 'Target environment'
        )
        choice(
            name: 'PLAYBOOK',
            choices: [
                'system_preparation.yml',
                'docker_installation.yml',
                'docker_configuration.yml',
                'traefik_configuration.yml',
                'odoo17_deployment.yml',
                'odoo19_deployment.yml',
                'postgresql_management.yml',
                'backup.yml',
                'restore.yml',
                'health_check.yml',
                'maintenance.yml'
            ],
            description: 'Playbook to execute'
        )
        booleanParam(
            name: 'DRY_RUN',
            defaultValue: true,
            description: 'Run in check mode (dry-run)'
        )
        string(
            name: 'EXTRA_VARS',
            defaultValue: '',
            description: 'Extra vars (JSON format)'
        )
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Validate') {
            steps {
                sh '''
                    cd 02-Integration
                    ansible-playbook -i inventories/${ENVIRONMENT}/hosts.yml playbooks/${PLAYBOOK} --syntax-check
                '''
            }
        }
        
        stage('Dry Run') {
            when { expression { params.DRY_RUN == true } }
            steps {
                sh '''
                    cd 02-Integration
                    ansible-playbook -i inventories/${ENVIRONMENT}/hosts.yml playbooks/${PLAYBOOK} \
                        --check --diff \
                        --vault-password-file ${VAULT_PASSWORD_FILE} \
                        ${EXTRA_VARS}
                '''
            }
        }
        
        stage('Deploy') {
            when { expression { params.DRY_RUN == false } }
            steps {
                input message: "Confirm deployment to ${ENVIRONMENT}?", ok: 'Deploy'
                sh '''
                    cd 02-Integration
                    ansible-playbook -i inventories/${ENVIRONMENT}/hosts.yml playbooks/${PLAYBOOK} \
                        --vault-password-file ${VAULT_PASSWORD_FILE} \
                        ${EXTRA_VARS}
                '''
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: '02-Integration/logs/*.log', allowEmptyArchive: true
        }
        failure {
            emailext (
                subject: "Ansible Deployment Failed: ${ENVIRONMENT}/${PLAYBOOK}",
                body: "Build ${BUILD_NUMBER} failed. Check Jenkins console.",
                to: '${CHANGES_AUTHOR_EMAIL}'
            )
        }
    }
}
```

### 12.2 بيانات اعتماد Jenkins المطلوبة:
| المعرف (ID) | النوع | الوصف |
|-------------|-------|---------|
| `ansible-vault-password` | Secret text | كلمة مرور Ansible Vault |
| `ansible-ssh-key` | SSH Username with private key | مفتاح SSH للخوادم المستهدفة |
| `cloudflare-api-token` | Secret text | رمز Cloudflare API لـ DNS challenge |
| `s3-credentials` | AWS Credentials | بيانات اعتماد S3 للنسخ الاحتياطي |

---

## 13. النسخ الاحتياطي والاستعادة

### 13.1 استراتيجية النسخ الاحتياطي:
| النوع | التكرار | الاحتفاظ | المكان |
|------|---------|----------|--------|
| قاعدة بيانات PostgreSQL | يومي (02:00) | 30 يوم | محلي + S3 |
| ملفات Odoo (filestore) | يومي (02:30) | 30 يوم | محلي + S3 |
| تكوينات النظام | أسبوعي | 12 أسبوع | Git + محلي |
| صور Docker | عند كل نشر | 5 صور | Registry |

### 13.2 أمر النسخ الاحتياطي اليدوي:
```bash
# تشغيل النسخ الاحتياطي
ansible-playbook -i inventories/staging/hosts.yml playbooks/backup.yml

# مع متغيرات إضافية
ansible-playbook -i inventories/staging/hosts.yml playbooks/backup.yml \
    -e "backup_type=full backup_destination=s3"
```

### 13.3 الاستعادة:
```bash
# استعادة أحدث نسخة
ansible-playbook -i inventories/staging/hosts.yml playbooks/restore.yml

# استعادة نسخة محددة
ansible-playbook -i inventories/staging/hosts.yml playbooks/restore.yml \
    -e "restore_date=2024-01-15 restore_type=database"

# استعادة ملفات Odoo فقط
ansible-playbook -i inventories/staging/hosts.yml playbooks/restore.yml \
    -e "restore_type=filestore restore_date=2024-01-15"
```

---

## 14. فحوصات الصحة (Health Checks)

### 14.1 تشغيل فحص الصحة:
```bash
# فحص شامل
ansible-playbook -i inventories/staging/hosts.yml playbooks/health_check.yml

# فحص خدمة محددة
ansible-playbook -i inventories/staging/hosts.yml playbooks/health_check.yml \
    -e "check_services=docker,traefik,odoo17,postgresql"
```

### 14.2 ما يفحصه `health_check.yml`:
- ✅ حالة Docker (Engine, Compose, Networks, Containers)
- ✅ حالة Traefik (Dashboard, Routers, Certificates, TLS)
- ✅ حالة Odoo 17/19 (Web interface, Longpolling, Database connection)
- ✅ حالة PostgreSQL (Connections, Replication, Disk space, Backups)
- ✅ موارد النظام (CPU, Memory, Disk, Inodes)
- ✅ شهادات SSL (انتهاء الصلاحية، التجديد التلقائي)
- ✅ النسخ الاحتياطية (آخر نسخة، سلامة الملفات، حجم)
- ✅ السجلات (أخطاء حديثة، مساحة القرص)

---

## 15. الصيانة الدورية (`maintenance.yml`)

### 15.1 مهام الصيانة:
```bash
# تشغيل الصيانة الكاملة
ansible-playbook -i inventories/staging/hosts.yml playbooks/maintenance.yml

# مهام محددة
ansible-playbook -i inventories/staging/hosts.yml playbooks/maintenance.yml \
    --tags "cleanup,update,security"
```

### 15.2 ما تتضمنه الصيانة:
| المهمة | الوصف |
|--------|-------|
| `cleanup` | تنظيف صور Docker غير المستخدمة، سجلات قديمة، ملفات مؤقتة |
| `update` | تحديث حزم النظام، صور Docker الأساسية (باستثناء الإنتاج) |
| `security` | فحص الثغرات (Trivy، Lynis)، تحديث قواعد fail2ban |
| `certificates` | التحقق من تجديد شهادات Let's Encrypt |
| `backups` | التحقق من سلامة النسخ الاحتياطية، اختبار استعادة عشوائي |
| `logs` | تدوير السجلات، أرشفة، تنبيهات على الأخطاء المتكررة |

---

## 16. أفضل الممارسات والنصائح

### 16.1 الأمان:
- ✅ استخدم **Ansible Vault** لكل الأسرار
- ✅ لا تضع كلمات مرور في Git أبداً
- ✅ استخدم مفاتيح SSH مع `ssh-agent`
- ✅ حدّد `become` بأقل امتيازات مطلوبة
- ✅ فعّل `host_key_checking` في الإنتاج
- ✅ دوّر مفاتيح SSH وكلمات المرور دورياً

### 16.2 الموثوقية:
- ✅ اختبر دائماً في `staging` أولاً
- ✅ استخدم `--check --diff` قبل كل تشغيل إنتاج
- ✅ اجعل اللعبات **مُساوية للذات (idempotent)**
- ✅ استخدم `handlers` للخدمات بدلاً من `service` مباشر
- ✅ أضف `healthcheck` لكل حاوية
- ✅ وثّق كل تغيير في `CHANGELOG.md`

### 16.3 الأداء:
- ✅ فعّل `pipelining = true` في `ansible.cfg`
- ✅ استخدم `mitogen` لتسريع التنفيذ:
  ```bash
  pip install mitogen
  # في ansible.cfg:
  # strategy_plugins = /path/to/mitogen/ansible_mitogen/plugins/strategy
  # strategy = mitogen_linear
  ```
- ✅ اجمع المهام المتشابهة في `loop`
- ✅ استخدم `gather_facts: false` عندما لا تحتاج حقائق

### 16.4 التنظيم:
- ✅ استخدم **الأدوار (roles)** للكود القابل لإعادة الاستخدام
- ✅ فصل المتغيرات حسب البيئة في `group_vars/`
- ✅ استخدم **العلامات (tags)** للتشغيل الانتقائي
- ✅ نوّع اللعبات: واحدة لكل مكون رئيسي
- ✅ استخدم `import_playbook` للتركيب عند الحاجة

---

## 17. استكشاف الأخطاء الشائعة

| المشكلة | السبب المحتمل | الحل |
|----------|---------------|-------|
| `UNREACHABLE!` | SSH key/port/firewall | تحقق من `ansible_ssh_private_key_file`، المنفذ 22، UFW |
| `Permission denied (publickey)` | مفتاح SSH خاطئ | تحقق من صلاحيات المفتاح (600)، `ssh-agent` |
| `Failed to connect to Docker` | Docker غير مشغّل/صلاحيات | تأكد من تشغيل `docker.service`، المستخدم في مجموعة `docker` |
| `Vault password incorrect` | كلمة مرور Vault خاطئة | تحقق من `--vault-password-file` أو `--ask-vault-pass` |
| `Container health check failed` | التطبيق لم يبدأ بعد | زد `start_period` في `healthcheck` |
| `Traefik certificate error` | DNS challenge فاشل | تحقق من Cloudflare API token، سجلات DNS |
| `Odoo database connection failed` | PostgreSQL غير جاهز/كلمة مرور | تحقق من `healthcheck` PostgreSQL، متغيرات البيئة |
| `Idempotency check failed` | مهمة غير مساوية للذات | استخدم `changed_when`، `check_mode`، أو أصلح المهمة |

---

## 18. المراجع والروابط المفيدة

### الوثائق الرسمية:
- [Ansible Documentation](https://docs.ansible.com/)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_best_practices.html)
- [Community Docker Collection](https://docs.ansible.com/ansible/latest/collections/community/docker/)
- [Community PostgreSQL Collection](https://docs.ansible.com/ansible/latest/collections/community/postgresql/)

### أدوات مساعدة:
- [Ansible Lint](https://ansible-lint.readthedocs.io/) — فحص جودة اللعبات
- [Molecule](https://molecule.readthedocs.io/) — اختبار الأدوار
- [Ansible Navigator](https://ansible-navigator.readthedocs.io/) — واجهة TUI
- [ARA Records Ansible](https://ara.recordsansible.org/) — تسجيل وعرض نتائج التشغيل

### المراجع الخاصة بالمشروع:
- `../INSTALLATION_REPORT.md` — تقرير تثبيت المرحلة 1
- `../VERSION_INFO.md` — إصدارات الأدوات المثبتة
- `docs/IMPLEMENTATION_REPORT.md` — تقرير تنفيذ المرحلة 2
- `CHANGELOG.md` — سجل التغييرات

---

## 19. قائمة التحقق النهائية (Checklist) قبل الإنتاج

### ما قبل النشر:
- [ ] جميع اللعبات تمر بـ `--syntax-check`
- [ ] جميع اللعبات تمر بـ `--check --diff` في staging
- [ ] جميع اللعبات **مُساوية للذات** (تشغيل مرتين = لا تغييرات)
- [ ] جميع الأسرار في Ansible Vault (لا نصوص واضحة في Git)
- [ ] مفاتيح SSH مخزنة بأمان، غير مشاركة
- [ ] مخزون الإنتاج منفصل ومقيد الوصول
- [ ] خطة استعادة مختبرة وموثقة
- [ ] مراقبة وتنبيهات مهيأة (Prometheus/Grafana/Alertmanager)

### بعد النشر:
- [ ] فحوصات الصحة تمر بنجاح
- [ ] النسخ الاحتياطي الأول تم وتحقق منه
- [ ] شهادات SSL صالحة ومجدولة للتجديد
- [ ] السجلات نظيفة، لا أخطاء حرجة
- [ ] توثيق النشر محدث في `CHANGELOG.md`
- [ ] الفريق مطلع على إجراءات الطوارئ

---

## 20. الدعم والمساهمة

### للإبلاغ عن مشكلة:
1. تحقق من `docs/IMPLEMENTATION_REPORT.md` للأخطاء المعروفة
2. شغّل اللعبات مع `-vvv` للتصحيح التفصيلي
3. أنشئ issue مع: اللعبية، البيئة، المخرجات، خطوات الاستنساخ

### للمساهمة:
1. Fork المستودع
2. أنشئ branch للميزة/الإصلاح
3. أضف اختبارات (Molecule للعبورات)
4. تأكد من مرور `ansible-lint`
5. أرسل Pull Request مع وصف واضح

---

**ملاحظة أخيرة:** هذا الدليل يغطي جميع جوانب المرحلة 2. تأكد من تنفيذ **المرحلة 1 بنجاح أولاً** (راجع `../INSTALLATION_REPORT.md`) قبل البدء بأي عمل في هذا المجلد.

---

*آخر تحديث: 2024 | الإصدار: 1.0 | المشروع: Odoo Docker Deployment with Ansible*