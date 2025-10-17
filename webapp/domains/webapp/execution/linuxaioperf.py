"""
Linux AIO Performance Checker - Refactored Version
Author: Samuel Matildes
Description: Linux AIO Perf Checker HTML report generator
using domain-based architecture
Requirements: Python 3.6 or higher
Version: 2.1.2
Date: 15/05/2025
"""

import os
import logging
import datetime
from typing import List, Any, Optional

from domains.factory import ProcessorFactory
from domains.htmlgeneration import generate_report


def setup_logging() -> logging.Logger:
    """Setup logging configuration."""
    logger = logging.getLogger('linuxaioperf')
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def log_message(message: str, log_level: str = 'Info',
                logger: Optional[logging.Logger] = None):
    """Log a message with timestamp."""
    if logger:
        if log_level.lower() == 'error':
            logger.error(message)
        elif log_level.lower() == 'warning':
            logger.warning(message)
        else:
            logger.info(message)
    else:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{current_time}: [{log_level}] [linuxaioperf_v2.py] {message}")


def print_banner(logger: logging.Logger):
    """Print the script banner."""
    log_message(
        "===> LINUX AIO PERFORMANCE CHECKER EXECUTION INITIATED",
        logger=logger)


class PerformanceReportGenerator:
    """
    Main class for generating Linux AIO performance reports.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or setup_logging()
        self.processors = {}
        self.results = {}

    def process_cpu_data(self) -> List[Any]:
        """Process CPU performance data."""
        self.logger.info("Processing CPU Data")

        try:
            processor = ProcessorFactory.create_processor(
                'cpu', 'mpstat.txt', logger=self.logger
            )
            df, figures = processor.process()
            self.results['cpu'] = {'data': df, 'figures': figures}
            return figures
        except Exception as e:
            self.logger.error(f"Failed to process CPU data: {e}")
            return []

    def process_disk_data(self) -> tuple[List[Any], List[Any]]:
        """Process disk performance data."""
        self.logger.info("Processing Disk Data 1/2")

        # Process per-device disk data
        try:
            processor = ProcessorFactory.create_processor(
                'diskiostat', 'iostat-data.out', logger=self.logger
            )
            df, figures = processor.process()
            self.results['disk_per_device'] = {'data': df, 'figures': figures}
            disk_pd_figs = figures
        except Exception as e:
            self.logger.error(f"Failed to process disk per-device data: {e}")
            disk_pd_figs = []

        self.logger.info("Processing Disk Data 2/2")

        # Process per-metric disk data
        try:
            processor = ProcessorFactory.create_processor(
                'diskmetrics', 'iostat-data.out', logger=self.logger
            )
            df, figures = processor.process()
            self.results['disk_per_metric'] = {'data': df, 'figures': figures}
            disk_pm_figs = figures
        except Exception as e:
            self.logger.error(f"Failed to process disk per-metric data: {e}")
            disk_pm_figs = []

        return disk_pd_figs, disk_pm_figs

    def process_diskstats_data(self) -> List[Any]:
        """Process high-resolution disk statistics."""
        self.logger.info("Processing High Resolution Diskstats Data")

        if not os.path.exists("diskstats_log.txt"):
            self.logger.warning(
                "No diskstats_log.txt found, skipping diskstats")
            return []

        try:
            processor = ProcessorFactory.create_processor(
                'diskhighres', 'diskstats_log.txt', logger=self.logger
            )
            df, figures = processor.process()
            self.results['diskstats'] = {'data': df, 'figures': figures}
            return figures
        except Exception as e:
            self.logger.error(f"Failed to process diskstats data: {e}")
            return []

    def process_memory_data(self) -> List[Any]:
        """Process memory performance data."""
        self.logger.info("Processing Memory Data")

        try:
            processor = ProcessorFactory.create_processor(
                'memory', 'vmstat-data.out', logger=self.logger
            )
            df, figures = processor.process()
            self.results['memory'] = {'data': df, 'figures': figures}
            return figures
        except Exception as e:
            self.logger.error(f"Failed to process memory data: {e}")
            return []

    def process_network_data(self) -> List[Any]:
        """Process network performance data."""
        self.logger.info("Processing Network Data")

        if not os.path.exists("sarnetwork.txt"):
            self.logger.warning("No sarnetwork.txt found, skipping network")
            return []

        try:
            processor = ProcessorFactory.create_processor(
                'network', 'sarnetwork.txt', logger=self.logger
            )
            df, figures = processor.process()
            self.results['network'] = {'data': df, 'figures': figures}
            return figures
        except Exception as e:
            self.logger.error(f"Failed to process network data: {e}")
            return []

    def generate_report(self,
                        mpstat_figs: List[Any],
                        iostat_pd_figs: List[Any],
                        iostat_pm_figs: List[Any],
                        vmstat_figs: List[Any],
                        sarnet_figs: List[Any],
                        diskstats_figs: List[Any]):
        """Generate the final HTML report."""
        self.logger.info("Generating HTML Report")

        try:
            generate_report(
                mpstat_figs, iostat_pd_figs, iostat_pm_figs,
                vmstat_figs, sarnet_figs, diskstats_figs
            )
            self.logger.info("HTML report generated successfully")
        except Exception as e:
            self.logger.error(f"Failed to generate HTML report: {e}")
            raise

    def run(self):
        """Main execution method."""
        print_banner(self.logger)

        try:
            # Process all data types
            mpstat_figs = self.process_cpu_data()
            iostat_pd_figs, iostat_pm_figs = self.process_disk_data()
            diskstats_figs = self.process_diskstats_data()
            vmstat_figs = self.process_memory_data()
            sarnet_figs = self.process_network_data()

            # Generate final report
            self.generate_report(
                mpstat_figs, iostat_pd_figs, iostat_pm_figs,
                vmstat_figs, sarnet_figs, diskstats_figs
            )

            self.logger.info("Report generation completed successfully")

        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            raise


def main():
    """Main function."""
    logger = setup_logging()
    generator = PerformanceReportGenerator(logger)
    generator.run()


if __name__ == "__main__":
    main()
