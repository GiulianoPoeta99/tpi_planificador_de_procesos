import os
import logging
import string
from datetime import datetime

class CustomLogger:
    def __init__(self, policy_name):
        self.policy_name_format = policy_name.lower().translate(str.maketrans('', '', string.punctuation)).replace(' ', '_')
        self.log_dir = self._create_log_directory()

        # Parameters logger
        self.param_logger = logging.getLogger(f"{self.policy_name_format}_parameters")
        self.param_logger.setLevel(logging.INFO)
        param_handler = logging.FileHandler(os.path.join(self.log_dir, 'parameters.log'))
        param_handler.setLevel(logging.INFO)
        self.param_logger.addHandler(param_handler)
        
        # Summary logger
        self.summary_logger = logging.getLogger(f"{self.policy_name_format}_summary")
        self.summary_logger.setLevel(logging.INFO)
        summary_handler = logging.FileHandler(os.path.join(self.log_dir, 'summary.log'))
        summary_handler.setLevel(logging.INFO)
        self.summary_logger.addHandler(summary_handler)
        
        # Processes logger
        self.processes_logger = logging.getLogger(f"{self.policy_name_format}_processes")
        self.processes_logger.setLevel(logging.DEBUG)
        processes_handler = logging.FileHandler(os.path.join(self.log_dir, 'processes.log'))
        processes_handler.setLevel(logging.DEBUG)
        self.processes_logger.addHandler(processes_handler)

    def _create_log_directory(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = os.path.join('src/logs', f"{timestamp}_{self.policy_name_format}")
        os.makedirs(log_dir, exist_ok=True)
        return log_dir

    def log_parameters(self, scheduler):
        self.param_logger.info(f"Parameters:\n{str(scheduler)}")

    def log_summary(self, result):
        self.summary_logger.info(f"Summary:\n{str(result)}")

    def log_process_state(self, time_unit, process_info):
        self.processes_logger.debug(f"Time Unit: {time_unit}, Process: {process_info}")