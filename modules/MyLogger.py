import json
from datetime import datetime
import os
from pathlib import Path
import traceback

class MyLogger:
    def __init__(self):
        pass

    def log_and_save(self, msg):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M")
            print(f"{timestamp}: {msg}")
            self._save_log_to_json({"timestamp": datetime.now().strftime("%Y-%m-%d_%H:%M"), "log": msg})
        except Exception as error:
            print(f"Error to save log: {error}")
            print(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Error to save log: {error}")

    def _save_log_to_json(self, log_record):
        name_log = f'case-search-mn_{datetime.now().strftime("%Y-%m-%d")}.json'
        filepath = os.path.join(Path(__file__).parent.parent, name_log)
        if os.path.exists(filepath):
            with open(filepath, 'a') as f:
                f.write(f'{json.dumps(log_record)}\n')
        else:
            with open(filepath, 'w') as f:
                json.dump(log_record, f)
                f.write('\n')

logger = MyLogger()