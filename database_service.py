import os
from supabase import create_client, Client
from datetime import datetime

# Initialize Supabase client
def get_supabase_client() -> Client:
    """Initialize and return Supabase client"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        raise ValueError('SUPABASE_URL and SUPABASE_ANON_KEY must be set')
    
    return create_client(url, key)

def init_database():
    """Initialize users table in Supabase"""
    try:
        supabase = get_supabase_client()
        
        # Check if table exists by trying to select from it
        result = supabase.table('users').select('user_id').limit(1).execute()
        print('Users table already exists.')
        
    except Exception as e:
        print(f'Note: You need to create the users table in Supabase dashboard')
        print(f'Error: {e}')

def log_user_to_supabase(user):
    """Log user to Supabase database"""
    try:
        supabase = get_supabase_client()
        
        user_data = {
            'user_id': user.id,
            'username': user.username or '',
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'created_at': datetime.now().isoformat()
        }
        
        # Use upsert to handle conflicts (insert or ignore if exists)
        result = supabase.table('users').upsert(
            user_data, 
            on_conflict='user_id'
        ).execute()
        
        print(f'User {user.id} logged to Supabase successfully.')
        
    except Exception as e:
        print(f'Error logging user to Supabase: {e}')

# Alternative: Using raw SQL if you prefer (similar to your original approach)
def log_user_to_supabase_sql(user):
    """Log user using raw SQL approach"""
    try:
        supabase = get_supabase_client()
        
        # Supabase doesn't support raw SQL execution through Python client
        # So we'll use the table operations instead
        user_data = {
            'user_id': user.id,
            'username': user.username or '',
            'first_name': user.first_name or '',
            'last_name': user.last_name or ''
        }
        
        # Check if user exists first
        existing = supabase.table('users').select('user_id').eq('user_id', user.id).execute()
        
        if not existing.data:
            # Insert new user
            result = supabase.table('users').insert(user_data).execute()
            print(f'New user {user.id} logged to Supabase.')
        else:
            print(f'User {user.id} already exists in Supabase.')
            
    except Exception as e:
        print(f'Error logging user to Supabase: {e}')

# For testing the connection
def test_supabase_connection():
    """Test Supabase connection"""
    try:
        supabase = get_supabase_client()
        result = supabase.table('users').select('count').execute()
        print('✅ Supabase connection successful!')
        return True
    except Exception as e:
        print(f'❌ Supabase connection failed: {e}')
        return False