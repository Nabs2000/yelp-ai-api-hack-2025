import json
from supabase import create_client, Client

with open("config.json") as config_file:
    config = json.load(config_file)

supabase_url = config["SUPABASE_URL"]
supabase_key = config["SUPABASE_API_KEY"]

supabase: Client = create_client(supabase_url, supabase_key)
print("Supabase initialized successfully:", supabase)