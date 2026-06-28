from flask import jsonify
from backend.api.routes import api_bp
from backend.core.db import jobs_col, USE_POSTGRES, get_db_connection
import json

@api_bp.route('/history', methods=['GET'])
def get_history():
    """Get history of all image conversions"""
    if USE_POSTGRES:
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT id, status, progress, total, results, error FROM jobs ORDER BY id DESC LIMIT 50")
                rows = cur.fetchall()
                history_list = []
                for row in rows:
                    results_data = row[4]
                    results = results_data if isinstance(results_data, list) else json.loads(results_data or '[]')
                    history_list.append({
                        'job_id': row[0],
                        'status': row[1],
                        'progress': row[2],
                        'total': row[3],
                        'results': results,
                        'error': row[5]
                    })
                return jsonify(history_list)
        except Exception as e:
            print(f"Error fetching history from PostgreSQL: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            if conn:
                conn.close()
    else:
        try:
            # Access internal dict for in-memory fallback
            jobs_data = jobs_col.data
            history_list = []
            for job_id, doc in sorted(jobs_data.items(), key=lambda x: x[0], reverse=True)[:50]:
                history_list.append({
                    'job_id': job_id,
                    'status': doc.get('status'),
                    'progress': doc.get('progress'),
                    'total': doc.get('total'),
                    'results': doc.get('results', []),
                    'error': doc.get('error')
                })
            return jsonify(history_list)
        except Exception as e:
            print(f"Error fetching history from in-memory DB: {e}")
            return jsonify({'error': str(e)}), 500
