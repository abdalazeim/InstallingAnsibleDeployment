# build inventory

Used for installation verification (`installation/verify.sh`) and the optional
Semaphore smoke template (`system.verify`).

- On a bare-metal Ubuntu host, `localhost` is the supported Ubuntu target.
- Inside the containerized Semaphore runner, `localhost` is the runner
  container, not an Ubuntu server. Replace this host with the target server
  over SSH before using the build environment for real operations.

An empty inventory is refused by `playbooks/_guard.yml`; a skipped play is not
treated as success.
