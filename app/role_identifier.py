from app.role_database import USER_ROLES

def get_user_role(name: str) -> str:
    """
    Return the role of a user based on their name.

    Args:
        name (str): The string name identified from face recognition.

    Returns:
        str: The role of the user ("Elderly user", "Family member", "Caregiver"),
             or "Unknown role" if the name is not in the database.
    """
    normalized_name = name.strip().lower()
    return USER_ROLES.get(normalized_name, "Unknown role")

# Optional test
if __name__ == "__main__":
    test_names = ["Lucia", "nurse_ana", "random_guy"]
    for name in test_names:
        role = get_user_role(name)
        print(f"{name} → {role}")
