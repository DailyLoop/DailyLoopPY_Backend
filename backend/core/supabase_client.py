#!/usr/bin/env python3
"""
Centralized Supabase Client Singleton

Provides a single shared Supabase client using the service role key,
which bypasses RLS for all server-side operations.

Import pattern for all modules:
    from backend.core.supabase_client import supabase
"""

from supabase import create_client, Client
from backend.core.config import Config
import logging

logger = logging.getLogger(__name__)

if not Config.SUPABASE_URL or not Config.SUPABASE_SERVICE_ROLE_KEY:
    raise EnvironmentError(
        "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment."
    )

supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
logger.info("Supabase singleton client initialized (service role)")
