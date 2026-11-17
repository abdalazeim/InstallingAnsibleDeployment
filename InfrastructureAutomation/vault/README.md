# Ansible Vault - Secrets Storage
## NEVER commit real secrets here. Use placeholder values.

## Required secrets:
1. vault_odoo_admin_password - Odoo admin password
2. vault_odoo_db_password - Odoo database password
3. vault_postgresql_admin_password - PostgreSQL admin password
4. vault_jenkins_token - Jenkins API token
5. vault_cf_api_token - Cloudflare API token (for Traefik DNS challenge)
6. django_secret_key - Django secret key
7. django_db_password - Django database password

## Usage:
```bash
# Create encrypted file
ansible-vault create vault/secrets.yml

# Edit encrypted file
ansible-vault edit vault/secrets.yml

# Decrypt to view
ansible-vault view vault/secrets.yml
```

## Never commit:
- Real passwords
- API tokens
- Private keys
- Any production credentials