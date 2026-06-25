# run_report.py
import os
import subprocess
import logging
from datetime import datetime
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def generate_report():
    """Run the report generator and handle errors"""
    try:
        logger.info("🔄 Generating report...")
        result = subprocess.run(
            ["python", "generate_report.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ Report generated successfully")
            logger.info(result.stdout)
        else:
            logger.error(f"❌ Report generation failed: {result.stderr}")
        
        # Write log file
        with open("logs/report.log", "a") as f:
            f.write(f"{datetime.now()}: {'✅ Success' if result.returncode == 0 else '❌ Failed'}\n")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    generate_report()