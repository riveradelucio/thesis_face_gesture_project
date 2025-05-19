import os
import json

# Path to the roles JSON file
ROLES_FILE = os.path.join("data", "roles.json")
os.makedirs("data", exist_ok=True)  # Make sure folder exists

# Default roles if file is missing
DEFAULT_ROLES = {
    "lucia": "Elderly user",
    "daniel": "Family member",
    "nurse_ana": "Caregiver"
}

# Load roles from JSON or initialize defaults
def load_roles():
    if os.path.exists(ROLES_FILE):
        with open(ROLES_FILE, "r") as f:
            return json.load(f)
    else:
        save_roles(DEFAULT_ROLES)
        return DEFAULT_ROLES.copy()

# Save roles to JSON
def save_roles(roles_dict):
    with open(ROLES_FILE, "w") as f:
        json.dump(roles_dict, f, indent=4)

# Global dictionary used by other parts of the app
USER_ROLES = load_roles()
