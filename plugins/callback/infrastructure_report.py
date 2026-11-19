"""Write only aggregate statistics: never task results, variables or credentials."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import uuid
from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    CALLBACK_VERSION=2.0
    CALLBACK_TYPE='aggregate'
    CALLBACK_NAME='infrastructure_report'
    CALLBACK_NEEDS_ENABLED=True

    def v2_playbook_on_stats(self,stats):
        default=Path('/reports') if Path('/reports').is_dir() else Path.cwd()/'reports'
        folder=Path(os.environ.get('INFRASTRUCTURE_REPORT_DIR',str(default)))
        run_id=os.environ.get('INFRASTRUCTURE_RUN_ID',uuid.uuid4().hex)
        if not re.fullmatch(r'[A-Za-z0-9_-]+',run_id):
            self._display.warning('Invalid report ID; report not written')
            return
        report={'run_id':run_id,'finished_at':datetime.now(timezone.utc).isoformat(),
                'operation':os.environ.get('INFRASTRUCTURE_OPERATION','ansible'),
                'hosts':{host:stats.summarize(host) for host in sorted(stats.processed)}}
        try:
            folder.mkdir(parents=True,exist_ok=True,mode=0o700)
            fd=os.open(folder/(run_id+'.stats.json'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'w') as stream: json.dump(report,stream,indent=2)
        except OSError:
            self._display.warning('Cannot persist infrastructure statistics; check protected report directory permissions')
