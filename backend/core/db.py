import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from backend.config import Config

class MockCollection:
    """In-memory fallback collection replicating basic MongoDB/PostgreSQL operations"""
    def __init__(self):
        self.data = {}
        
    def find_one(self, query):
        if '_id' in query:
            return self.data.get(query['_id'])
        # Basic match query
        for val in self.data.values():
            match = True
            for k, v in query.items():
                if val.get(k) != v:
                    match = False
                    break
            if match:
                return val.copy() if isinstance(val, dict) else val
        return None
        
    def insert_one(self, doc):
        _id = doc.get('_id')
        self.data[_id] = doc.copy() if isinstance(doc, dict) else doc
        return doc
        
    def update_one(self, query, update):
        doc = self.find_one(query)
        if doc:
            ref = self.data.get(doc['_id'])
            if '$set' in update:
                ref.update(update['$set'])
            if '$push' in update:
                for k, v in update['$push'].items():
                    if k not in ref:
                        ref[k] = []
                    ref[k].append(v)
        return doc
        
    def replace_one(self, query, doc, upsert=False):
        _id = query.get('_id') or doc.get('_id')
        self.data[_id] = doc.copy() if isinstance(doc, dict) else doc
        return doc


class PostgresCollection:
    """Wrapper that mimics MongoDB collection API but queries PostgreSQL instead"""
    def __init__(self, table_name, connection_factory):
        self.table_name = table_name
        self.get_conn = connection_factory
        
    def find_one(self, query):
        conn = None
        try:
            conn = self.get_conn()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if self.table_name == 'config':
                    _id = query.get('_id')
                    cur.execute("SELECT data FROM config WHERE id = %s", (_id,))
                    row = cur.fetchone()
                    if row:
                        # Convert to dict if not already
                        res = row['data'] if isinstance(row['data'], dict) else json.loads(row['data'])
                        res['_id'] = _id
                        return res
                    return None
                    
                elif self.table_name == 'files':
                    if '_id' in query:
                        cur.execute("SELECT id, path, name, size, output_path FROM files WHERE id = %s", (query['_id'],))
                    elif 'path' in query:
                        cur.execute("SELECT id, path, name, size, output_path FROM files WHERE path = %s", (str(query['path']),))
                    else:
                        return None
                    row = cur.fetchone()
                    if row:
                        res = {
                            '_id': row['id'],
                            'path': row['path'],
                            'name': row['name'],
                            'size': row['size']
                        }
                        if row['output_path'] is not None:
                            res['output_path'] = row['output_path']
                        return res
                    return None
                    
                elif self.table_name == 'jobs':
                    _id = query.get('_id')
                    cur.execute("SELECT id, status, progress, total, results, error FROM jobs WHERE id = %s", (_id,))
                    row = cur.fetchone()
                    if row:
                        res = {
                            '_id': row['id'],
                            'status': row['status'],
                            'progress': row['progress'],
                            'total': row['total'],
                            # Parse JSONB array
                            'results': row['results'] if isinstance(row['results'], list) else json.loads(row['results'] or '[]')
                        }
                        if row['error'] is not None:
                            res['error'] = row['error']
                        return res
                    return None
        except Exception as e:
            print(f"Error in find_one for {self.table_name}: {e}")
        finally:
            if conn:
                conn.close()
        return None
        
    def insert_one(self, doc):
        conn = None
        try:
            conn = self.get_conn()
            with conn.cursor() as cur:
                if self.table_name == 'files':
                    cur.execute(
                        "INSERT INTO files (id, path, name, size, output_path) VALUES (%s, %s, %s, %s, %s)",
                        (doc['_id'], doc['path'], doc['name'], doc['size'], doc.get('output_path'))
                    )
                elif self.table_name == 'jobs':
                    cur.execute(
                        "INSERT INTO jobs (id, status, progress, total, results, error) VALUES (%s, %s, %s, %s, %s, %s)",
                        (doc['_id'], doc['status'], doc['progress'], doc['total'], json.dumps(doc['results']), doc.get('error'))
                    )
                conn.commit()
        except Exception as e:
            print(f"Error in insert_one for {self.table_name}: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
        return doc
        
    def update_one(self, query, update):
        conn = None
        try:
            conn = self.get_conn()
            with conn.cursor() as cur:
                _id = query.get('_id')
                
                if self.table_name == 'files':
                    if '$set' in update:
                        sets = update['$set']
                        if 'output_path' in sets:
                            cur.execute("UPDATE files SET output_path = %s WHERE id = %s", (sets['output_path'], _id))
                            
                elif self.table_name == 'jobs':
                    # Lock the row for update to prevent concurrent race conditions
                    cur.execute("SELECT status, progress, total, results, error FROM jobs WHERE id = %s FOR UPDATE", (_id,))
                    row = cur.fetchone()
                    if row:
                        status, progress, total, results_str, error = row
                        results = results_str if isinstance(results_str, list) else json.loads(results_str or '[]')
                        
                        if '$push' in update:
                            for k, v in update['$push'].items():
                                if k == 'results':
                                    results.append(v)
                                    
                        if '$set' in update:
                            sets = update['$set']
                            if 'status' in sets:
                                status = sets['status']
                            if 'progress' in sets:
                                progress = sets['progress']
                            if 'error' in sets:
                                error = sets['error']
                                
                        cur.execute(
                            "UPDATE jobs SET status = %s, progress = %s, total = %s, results = %s, error = %s WHERE id = %s",
                            (status, progress, total, json.dumps(results), error, _id)
                        )
                conn.commit()
        except Exception as e:
            print(f"Error in update_one for {self.table_name}: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
        return None
        
    def replace_one(self, query, doc, upsert=False):
        conn = None
        try:
            conn = self.get_conn()
            with conn.cursor() as cur:
                _id = query.get('_id') or doc.get('_id')
                data = doc.copy()
                data.pop('_id', None)
                
                if self.table_name == 'config':
                    cur.execute(
                        "INSERT INTO config (id, data) VALUES (%s, %s) ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data",
                        (_id, json.dumps(data))
                    )
                conn.commit()
        except Exception as e:
            print(f"Error in replace_one for {self.table_name}: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
        return doc


def get_db_connection():
    """Create a new PostgreSQL connection"""
    return psycopg2.connect(
        host=Config.POSTGRES_HOST,
        port=int(Config.POSTGRES_PORT),
        database=Config.POSTGRES_DB,
        user=Config.POSTGRES_USER,
        password=Config.POSTGRES_PASSWORD,
        connect_timeout=3
    )

USE_MONGO = False
USE_POSTGRES = False
files_col = None
jobs_col = None
config_col = None

try:
    # Attempt to connect to PostgreSQL
    conn = get_db_connection()
    
    # Initialize tables
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id VARCHAR(32) PRIMARY KEY,
                path TEXT NOT NULL,
                name TEXT NOT NULL,
                size BIGINT NOT NULL,
                output_path TEXT
            );
            CREATE TABLE IF NOT EXISTS jobs (
                id VARCHAR(32) PRIMARY KEY,
                status VARCHAR(20) NOT NULL,
                progress INTEGER NOT NULL,
                total INTEGER NOT NULL,
                results JSONB NOT NULL DEFAULT '[]'::jsonb,
                error TEXT
            );
            CREATE TABLE IF NOT EXISTS config (
                id VARCHAR(20) PRIMARY KEY,
                data JSONB NOT NULL
            );
        """)
        conn.commit()
    conn.close()
    
    USE_POSTGRES = True
    print("Database Connection: Successfully connected to PostgreSQL and initialized tables.")
    
    # Create PostgreSQL collections
    files_col = PostgresCollection('files', get_db_connection)
    jobs_col = PostgresCollection('jobs', get_db_connection)
    config_col = PostgresCollection('config', get_db_connection)

except Exception as e:
    print(f"Database Connection: PostgreSQL not available ({e}). Falling back to In-Memory mode.")
    USE_POSTGRES = False
    
    # In-memory fallback mock collections
    files_col = MockCollection()
    jobs_col = MockCollection()
    config_col = MockCollection()
