from supabase import create_client, Client

from app.core.config import settings

if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")

# Shared client for DB operations (table queries). Never use this for auth
# sign_in / sign_out because it pollutes the internal postgrest headers.
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def get_auth_client() -> Client:
    """Create a fresh Supabase client for auth operations.
    
    Auth operations like sign_in_with_password mutate the client's internal
    state (postgrest headers, session). Using a throwaway client prevents
    the shared DB client from being corrupted.
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)