"""
This module initializes a `.env` file for a Django project if one does not already exist.

Constants:
    SECRET_KEY_BYTES (int): The number of bytes to use when generating the
        Django secret key.
    DATABASE_PASSWORD_BYTES (int): The number of bytes to use when generating
        the database password.
    OWNER_PERMISSIONS_MODE (int): The file mode to apply to the `.env` file,
        restricting access to the file owner.

"""

import os
import secrets
from pathlib import Path
from typing import Final

SECRET_KEY_BYTES: Final[int] = 64
DATABASE_PASSWORD_BYTES: Final[int] = 32
OWNER_PERMISSIONS_MODE: Final[int] = 0o600

def main():
    """
    Generates and writes a `.env` file with updated secret keys and passwords.

    This function reads a template `.env.example` file from the project root directory,
    replaces placeholders for `DJANGO_SECRET_KEY` and `POSTGRES_PASSWORD` with new,
    securely generated secrets, and writes the updated content to a new `.env` file.
    The function ensures that the `.env` file is created only if it does not already
    exist.

    :raises FileExistsError: If the `.env` file already exists when attempting
        to create it.

    :return: None
    """
    # get project root
    root = Path(__file__).resolve().parents[1]
    example_env_file = (root / ".env.example").read_text(encoding="utf-8")

    # update django secret key and postgres password
    new_secret_key = f"DJANGO_SECRET_KEY={secrets.token_urlsafe(SECRET_KEY_BYTES)}"
    new_postgres_pw = f"POSTGRES_PASSWORD={secrets.token_urlsafe(DATABASE_PASSWORD_BYTES)}"
    updated_file_content = example_env_file.replace("DJANGO_SECRET_KEY=\n", new_secret_key)
    updated_file_content = updated_file_content.replace("POSTGRES_PASSWORD=local-development-only", new_postgres_pw)

    # only create .env file if it does not exist and write to it the updated content
    file_descriptor = os.open(root / ".env", os.O_WRONLY | os.O_CREAT | os.O_EXCL, OWNER_PERMISSIONS_MODE)
    with os.fdopen(file_descriptor, "w", encoding="utf-8") as environment_file:
        environment_file.write(updated_file_content)


if __name__ == "__main__":
    main()