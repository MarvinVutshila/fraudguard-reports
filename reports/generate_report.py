# generate_report.py
import os
import json
import psycopg2
import psycopg2.extras
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")
    conn = psycopg2.connect(DATABASE_URL)
    logger.info("Connected to database.")
    return conn

def fetch_all(conn, sql, params=None):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params or ())
        return cur.fetchall()

def fetch_one(conn, sql, params=None):
    rows = fetch_all(conn, sql, params)
    return rows[0] if rows else None

def clean_value(value):
    """Clean data for presentation"""
    if value is None:
        return 0
    if isinstance(value, float):
        return round(value, 4)
    if isinstance(value, str):
        return value.strip()
    return value

def get_transaction_summary(conn, since, label=""):
    sql = """
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE decision = 'BLOCK') as blocked,
            COUNT(*) FILTER (WHERE decision = 'REVIEW') as reviewed,
            COUNT(*) FILTER (WHERE decision = 'APPROVE') as approved,
            COALESCE(AVG(probability), 0) as avg_risk,
            COALESCE(SUM(amount), 0) as total_amount,
            COALESCE(SUM(CASE WHEN decision = 'BLOCK' THEN amount ELSE 0 END), 0) as blocked_amount,
            COALESCE(SUM(CASE WHEN decision = 'APPROVE' THEN amount ELSE 0 END), 0) as approved_amount
        FROM transactions
        WHERE timestamp >= %s
    """
    result = fetch_one(conn, sql, (since,))
    if result:
        for key in result:
            result[key] = clean_value(result[key])
    return result

def get_daily_transactions(conn):
    sql = """
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE decision = 'BLOCK') as blocked,
            COUNT(*) FILTER (WHERE decision = 'REVIEW') as reviewed,
            COUNT(*) FILTER (WHERE decision = 'APPROVE') as approved,
            COALESCE(AVG(probability), 0) as avg_risk,
            COALESCE(SUM(amount), 0) as total_amount,
            COALESCE(SUM(CASE WHEN decision = 'BLOCK' THEN amount ELSE 0 END), 0) as blocked_amount,
            COALESCE(SUM(CASE WHEN decision = 'APPROVE' THEN amount ELSE 0 END), 0) as approved_amount
        FROM transactions
        WHERE timestamp > NOW() - INTERVAL '7 days'
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
    """
    results = fetch_all(conn, sql)
    for row in results:
        for key in row:
            row[key] = clean_value(row[key])
    return results

def get_risk_distribution(conn):
    sql = """
        SELECT 
            risk_level,
            COUNT(*) as count,
            COALESCE(AVG(probability), 0) as avg_probability,
            ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions WHERE timestamp > NOW() - INTERVAL '30 days')), 2) as percentage
        FROM transactions
        WHERE timestamp > NOW() - INTERVAL '30 days'
        GROUP BY risk_level
        ORDER BY 
            CASE risk_level
                WHEN 'LOW' THEN 1
                WHEN 'MEDIUM' THEN 2
                WHEN 'HIGH' THEN 3
                WHEN 'CRITICAL' THEN 4
                ELSE 5
            END
    """
    results = fetch_all(conn, sql)
    for row in results:
        for key in row:
            row[key] = clean_value(row[key])
    return results

def get_top_users(conn):
    try:
        sql = """
            SELECT 
                username,
                COUNT(*) as login_count,
                COUNT(*) FILTER (WHERE success = true) as successful,
                COUNT(*) FILTER (WHERE success = false) as failed,
                ROUND((COUNT(*) FILTER (WHERE success = true) * 100.0 / COUNT(*)), 2) as success_rate
            FROM login_logs
            WHERE timestamp > NOW() - INTERVAL '30 days'
            GROUP BY username
            ORDER BY login_count DESC
            LIMIT 10
        """
        results = fetch_all(conn, sql)
        for row in results:
            for key in row:
                row[key] = clean_value(row[key])
        return results
    except Exception as e:
        logger.warning(f"Could not fetch top users: {e}")
        return []

def get_override_activity(conn):
    try:
        sql = """
            SELECT 
                overridden_by as analyst,
                COUNT(*) as override_count,
                COUNT(*) FILTER (WHERE new_decision = 'APPROVE') as approved_overrides,
                COUNT(*) FILTER (WHERE new_decision = 'BLOCK') as blocked_overrides,
                ROUND((COUNT(*) FILTER (WHERE new_decision = 'APPROVE') * 100.0 / COUNT(*)), 2) as approve_rate
            FROM transaction_overrides
            WHERE timestamp > NOW() - INTERVAL '30 days'
            GROUP BY overridden_by
            ORDER BY override_count DESC
        """
        results = fetch_all(conn, sql)
        for row in results:
            for key in row:
                row[key] = clean_value(row[key])
        return results
    except Exception as e:
        logger.warning(f"Could not fetch override activity: {e}")
        return []

def get_hourly_pattern(conn):
    sql = """
        SELECT 
            EXTRACT(HOUR FROM timestamp) as hour,
            COUNT(*) as count,
            COALESCE(AVG(probability), 0) as avg_risk
        FROM transactions
        WHERE timestamp > NOW() - INTERVAL '7 days'
        GROUP BY EXTRACT(HOUR FROM timestamp)
        ORDER BY hour
    """
    results = fetch_all(conn, sql)
    for row in results:
        for key in row:
            row[key] = clean_value(row[key])
    return results

def get_decision_breakdown(conn):
    sql = """
        SELECT 
            decision,
            COUNT(*) as count,
            COALESCE(AVG(probability), 0) as avg_probability,
            ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions WHERE timestamp > NOW() - INTERVAL '30 days')), 2) as percentage
        FROM transactions
        WHERE timestamp > NOW() - INTERVAL '30 days'
        GROUP BY decision
        ORDER BY count DESC
    """
    results = fetch_all(conn, sql)
    for row in results:
        for key in row:
            row[key] = clean_value(row[key])
    return results

def get_system_stats(conn):
    stats = {}
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = cur.fetchone()[0]
        cur.close()
    except:
        stats['total_users'] = 0
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(DISTINCT username) 
            FROM login_logs 
            WHERE timestamp > NOW() - INTERVAL '7 days'
        """)
        stats['active_users_7d'] = cur.fetchone()[0]
        cur.close()
    except:
        stats['active_users_7d'] = 0
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM transactions 
            WHERE timestamp > NOW() - INTERVAL '30 days'
        """)
        stats['total_transactions_30d'] = cur.fetchone()[0]
        cur.close()
    except:
        stats['total_transactions_30d'] = 0
    
    return stats

def build_report(conn):
    logger.info("Aggregating transaction summaries for daily / weekly / monthly...")
    
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    report = {
        "generated_at": now.isoformat(),
        "period": {
            "week_start": week_ago.isoformat(),
            "month_start": month_ago.isoformat()
        },
        "daily": {
            "transactions": get_daily_transactions(conn)
        },
        "weekly": get_transaction_summary(conn, week_ago, "Weekly"),
        "monthly": get_transaction_summary(conn, month_ago, "Monthly"),
        "summary": {
            "risk_distribution": get_risk_distribution(conn),
            "top_users": get_top_users(conn),
            "override_activity": get_override_activity(conn),
            "hourly_pattern": get_hourly_pattern(conn),
            "decision_breakdown": get_decision_breakdown(conn),
            **get_system_stats(conn)
        }
    }
    
    # Convert Decimal objects to float
    def convert(obj):
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'item'):  # Decimal
            return float(obj)
        else:
            return obj
    
    return convert(report)

def save_report(report_data, filename="data/reports.json"):
    os.makedirs("data", exist_ok=True)
    with open(filename, "w") as f:
        json.dump(report_data, f, indent=2, default=str)
    logger.info(f"Report saved to {filename}")

def main():
    logger.info("=" * 60)
    logger.info("FraudGuard Report Generation Starting")
    logger.info("=" * 60)
    
    try:
        if not DATABASE_URL:
            logger.error("DATABASE_URL is not set. Please create .env file.")
            return False
        
        conn = get_connection()
        report = build_report(conn)
        conn.close()
        
        save_report(report)
        
        # Print summary
        weekly = report.get('weekly', {})
        logger.info("")
        logger.info("📊 Report Summary:")
        logger.info(f"   📅 Generated: {report['generated_at'][:10]}")
        logger.info(f"   📈 Weekly Transactions: {weekly.get('total', 0):,}")
        logger.info(f"   🚫 Blocked: {weekly.get('blocked', 0)}")
        logger.info(f"   ⏳ Review: {weekly.get('reviewed', 0)}")
        logger.info(f"   ✅ Approved: {weekly.get('approved', 0)}")
        logger.info(f"   💰 Total Amount: ${weekly.get('total_amount', 0):,.2f}")
        logger.info(f"   📊 Avg Risk: {(weekly.get('avg_risk', 0) * 100):.2f}%")
        logger.info("")
        logger.info("✅ Report generation completed successfully!")
        logger.info("📊 Report available at: data/reports.json")
        logger.info("🌐 Open index.html to view the dashboard")
        return True
        
    except Exception as e:
        logger.error(f"❌ Report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)