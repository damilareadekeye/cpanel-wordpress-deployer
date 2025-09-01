#!/usr/bin/env python3
"""
cPanel WordPress Deployer with Elementor Integration
=====================================================
Enterprise-Grade WordPress Automation Tool for cPanel Hosting
Author: Damilare Lekan Adekeye
"""

import os
import base64
import requests
import json
import time
import random
import string

class CPanelWordPressDeployer:
    """
    A class to automate WordPress deployment on cPanel hosting via the cPanel API.
    Includes support for Elementor and Elementor Pro integration.

    This class handles the entire deployment process including:
    - Database creation and user setup
    - WordPress core installation
    - Configuration and file permission management
    - Elementor and Elementor Pro installation
    - Template kit import
    """

    def __init__(self, hostname, username, auth_type="password", auth_value=None, port=2083):
        """
        Initialize the deployer with cPanel credentials.

        Args:
            hostname (str): cPanel hostname (e.g., 'example.com')
            username (str): cPanel username
            auth_type (str): 'password' or 'token'
            auth_value (str): Either the password or API token
            port (int): cPanel port (default: 2083 for HTTPS)
        """
        # Store basic connection details
        self.hostname = hostname
        self.username = username
        self.port = port

        # Construct the base URL for all API requests
        # The "/execute/" endpoint is part of cPanel's UAPI structure
        self.base_url = f"https://{hostname}:{port}/execute/"

        # Set up authentication headers based on auth type
        if auth_type == "password":
            # For password auth: encode username:password in Base64 (Basic Auth)
            auth_string = base64.b64encode(f"{username}:{auth_value}".encode()).decode()
            self.headers = {
                "Authorization": f"Basic {auth_string}",
                "Content-Type": "application/json"
            }
        else:  # token authentication
            # For token auth: use cPanel API token format
            self.headers = {
                "Authorization": f"cpanel {username}:{auth_value}",
                "Content-Type": "application/json"
            }

    def make_api_request(self, module, function, params=None):
        """
        Make a request to the cPanel API.
        This is the core method for interacting with cPanel's API.

        Args:
            module (str): API module (e.g., 'Mysql', 'SubDomain')
            function (str): API function (e.g., 'create_database')
            params (dict): Parameters for the API call

        Returns:
            dict: API response with standardized format
        """
        # Construct the full URL for the API endpoint
        url = f"{self.base_url}{module}/{function}"

        try:
            # Send POST request to the API endpoint with authentication and parameters
            response = requests.post(url, headers=self.headers, json=params or {}, verify=True)

            # Raise an exception for 4xx/5xx status codes
            response.raise_for_status()

            # Parse and return the JSON response
            return response.json()
        except requests.exceptions.RequestException as e:
            # Handle any request-related exceptions with standardized error format
            return {"status": 0, "errors": [str(e)], "data": None}

    # Database management methods
    def create_database(self, db_name, charset="utf8"):
        """
        Create a MySQL database for WordPress.

        Args:
            db_name (str): Database name (without username prefix)
            charset (str): Character set for the database

        Returns:
            dict: API response
        """
        # cPanel automatically prefixes database names with the username
        # Store the full name for reference
        full_db_name = f"{self.username}_{db_name}"

        # Call the MySQL API to create the database
        return self.make_api_request(
            "Mysql", "create_database",
            {"name": db_name, "charset": charset}
        )

    def create_db_user(self, user_name, password):
        """
        Create a database user for WordPress.

        Args:
            user_name (str): Username (without prefix)
            password (str): User password

        Returns:
            dict: API response
        """
        # cPanel automatically prefixes usernames with the account username
        full_user_name = f"{self.username}_{user_name}"

        # Call the MySQL API to create the user with the provided password
        return self.make_api_request(
            "Mysql", "create_user",
            {"name": user_name, "password": password}
        )

    def assign_user_to_db(self, db_name, user_name, privileges="ALL PRIVILEGES"):
        """
        Assign user privileges to a database.
        WordPress needs full access to its database.

        Args:
            db_name (str): Database name (without prefix)
            user_name (str): Username (without prefix)
            privileges (str): MySQL privileges to grant

        Returns:
            dict: API response
        """
        # Call the API to set user privileges on the database
        # Use the full prefixed names for both database and user
        return self.make_api_request(
            "Mysql", "set_privileges_on_database",
            {
                "database": f"{self.username}_{db_name}",
                "user": f"{self.username}_{user_name}",
                "privileges": privileges
            }
        )

    # WordPress installation methods
    def download_wordpress(self, destination_path):
        """
        Download and extract WordPress to the specified directory.

        Args:
            destination_path (str): Server path to install WordPress

        Returns:
            dict: API response
        """
        # Execute shell commands to:
        # 1. Change to the destination directory
        # 2. Download the latest WordPress zip
        # 3. Extract the zip file
        # 4. Move all files from wordpress/ to current directory
        # 5. Remove the empty folder and zip file
        return self.make_api_request(
            "Execute", "exec",
            {
                "command": f"cd {destination_path} && wget https://wordpress.org/latest.zip && unzip latest.zip && mv wordpress/* . && rm -rf wordpress latest.zip"
            }
        )

    def create_wp_config(self, path, db_name, db_user, db_password, db_host="localhost"):
        """
        Create WordPress configuration file with database connection details
        and security keys.

        Args:
            path (str): Path to WordPress installation
            db_name (str): Database name (without prefix)
            db_user (str): Database username (without prefix)
            db_password (str): Database password
            db_host (str): Database host

        Returns:
            dict: API response
        """
        # Fetch WordPress salts from WordPress.org API
        # These are unique security keys for each WP installation
        try:
            salts_response = requests.get("https://api.wordpress.org/secret-key/1.1/salt/")
            salts = salts_response.text
        except:
            # Fallback if WordPress API is unreachable
            # Generate random string for security keys
            chars = string.ascii_letters + string.digits + string.punctuation
            random_string = ''.join(random.choice(chars) for _ in range(64))
            salts = f"""
define('AUTH_KEY',         '{random_string}');
define('SECURE_AUTH_KEY',  '{random_string}');
define('LOGGED_IN_KEY',    '{random_string}');
define('NONCE_KEY',        '{random_string}');
define('AUTH_SALT',        '{random_string}');
define('SECURE_AUTH_SALT', '{random_string}');
define('LOGGED_IN_SALT',   '{random_string}');
define('NONCE_SALT',       '{random_string}');
"""

        # Create wp-config.php content with database details and salts
        wp_config = f""" {path}/wp-config.php << 'EOL'\n{wp_config}\nEOL"
        return self.make_api_request("Execute", "exec", {"command": cmd})

    def set_file_permissions(self, path):
        """
        Set proper file permissions for WordPress security.

        Args:
            path (str): Path to WordPress installation

        Returns:
            dict: API response
        """
        # Execute commands to set proper permissions:
        # - Directories: 755 (rwxr-xr-x) - owner can write, everyone can read/execute
        # - Files: 644 (rw-r--r--) - owner can write, everyone can read
        # - wp-config.php: 600 (rw-------) - only owner can read/write (for security)
        commands = f"""
find {path} -type d -exec chmod 755 {{}} \\;
find {path} -type f -exec chmod 644 {{}} \\;
chmod 600 {path}/wp-config.php
"""
        return self.make_api_request("Execute", "exec", {"command": commands})

    def run_wp_installation(self, path, site_url, title, admin_user, admin_password, admin_email):
        """
        Run WordPress installation using WP-CLI.
        This sets up the WordPress database tables and creates the admin user.

        Args:
            path (str): Path to WordPress installation
            site_url (str): Site URL (e.g., 'https://example.com')
            title (str): Site title
            admin_user (str): Admin username
            admin_password (str): Admin password
            admin_email (str): Admin email

        Returns:
            dict: API response
        """
        # Execute WP-CLI command to install WordPress
        # --skip-email prevents sending admin email notification
        command = f"""
cd {path} &&
wp core install --url='{site_url}' --title='{title}' --admin_user='{admin_user}' --admin_password='{admin_password}' --admin_email='{admin_email}' --skip-email
"""
        return self.make_api_request("Execute", "exec", {"command": command})

    # Elementor-related methods
    def install_elementor(self, path):
        """
        Install and activate Elementor free plugin from WordPress repository.

        Args:
            path (str): Path to WordPress installation

        Returns:
            dict: API response
        """
        # Use WP-CLI to install and activate Elementor from the WordPress plugin repository
        command = f"""
cd {path} &&
wp plugin install elementor --activate
"""
        return self.make_api_request("Execute", "exec", {"command": command})

    def install_elementor_pro(self, path, license_key=None, pro_zip_path=None):
        """
        Install and activate Elementor Pro from a zip file.

        Args:
            path (str): Path to WordPress installation
            license_key (str): Elementor Pro license key
            pro_zip_path (str): Path to Elementor Pro zip file on server

        Returns:
            dict: API response
        """
        # Validate required parameters
        if not license_key:
            return {"status": 0, "errors": ["No Elementor Pro license key provided"]}

        if not pro_zip_path:
            return {"status": 0, "errors": ["No Elementor Pro zip file path provided"]}

        # Execute commands to:
        # 1. Install Elementor Pro from the uploaded zip file
        # 2. Activate the plugin
        # 3. Activate the license key
        command = f"""
cd {path} &&
wp plugin install {pro_zip_path} --activate &&
wp elementor license activate {license_key}
"""
        return self.make_api_request("Execute", "exec", {"command": command})

    def import_elementor_kit(self, path, kit_url=None, kit_file=None):
        """
        Import Elementor kit (template) from URL or local file.

        Args:
            path (str): Path to WordPress installation
            kit_url (str): URL to Elementor kit file
            kit_file (str): Path to Elementor kit file on server

        Returns:
            dict: API response
        """
        # Determine import source (URL or file) and create appropriate command
        if kit_url:
            # Import kit from URL
            command = f"""
cd {path} &&
wp elementor kit import {kit_url} --yes
"""
        elif kit_file:
            # Import kit from local file on server
            command = f"""
cd {path} &&
wp elementor kit import {kit_file} --yes
"""
        else:
            return {"status": 0, "errors": ["No kit URL or file provided"]}

        # Execute the import command (--yes automatically confirms any prompts)
        return self.make_api_request("Execute", "exec", {"command": command})

    def upload_kit_file(self, local_path, server_path):
        """
        Upload Elementor kit file from local system to server using cPanel API.

        Args:
            local_path (str): Local path to kit file
            server_path (str): Server path to upload kit file

        Returns:
            dict: API response
        """
        try:
            # Read the local file and encode it in Base64 for transmission
            with open(local_path, 'rb') as file:
                file_content = file.read()
                file_content_base64 = base64.b64encode(file_content).decode()
        except Exception as e:
            return {"status": 0, "errors": [f"Failed to read local file: {str(e)}"]}

        # Prepare parameters for the file manager API
        # Split the server path into directory and filename
        params = {
            "dir": os.path.dirname(server_path),
            "file": os.path.basename(server_path),
            "content": file_content_base64
        }

        # Use cPanel's File Manager API to save the file
        return self.make_api_request("Fileman", "save_file_content", params)

    def upload_elementor_pro_zip(self, local_path, server_path):
        """
        Upload Elementor Pro zip file from local system to server.

        Args:
            local_path (str): Local path to Elementor Pro zip
            server_path (str): Server path to upload zip file

        Returns:
            dict: API response
        """
        try:
            # Read the Elementor Pro zip file and encode in Base64
            with open(local_path, 'rb') as file:
                file_content = file.read()
                file_content_base64 = base64.b64encode(file_content).decode()
        except Exception as e:
            return {"status": 0, "errors": [f"Failed to read Elementor Pro zip: {str(e)}"]}

        # Prepare parameters for file upload
        params = {
            "dir": os.path.dirname(server_path),
            "file": os.path.basename(server_path),
            "content": file_content_base64
        }

        # Upload the file using cPanel's File Manager API
        return self.make_api_request("Fileman", "save_file_content", params)

    # Main deployment methods
    def deploy_wordpress(self, domain, path, db_name, db_user, db_password,
                         site_title, admin_user, admin_password, admin_email,
                         install_theme=None, install_plugins=None):
        """
        Deploy a basic WordPress site with all necessary components.

        Args:
            domain (str): Site domain (e.g., 'example.com')
            path (str): Server path to install WordPress
            db_name (str): Database name (without prefix)
            db_user (str): Database username (without prefix)
            db_password (str): Database password
            site_title (str): Site title
            admin_user (str): Admin username
            admin_password (str): Admin password
            admin_email (str): Admin email
            install_theme (str): Theme to install (optional)
            install_plugins (list): Plugins to install (optional)

        Returns:
            dict: Deployment results with status of each operation
        """
        # Initialize results dictionary to track status of each step
        results = {
            "database_creation": None,
            "database_user_creation": None,
            "user_privileges": None,
            "wordpress_download": None,
            "wp_config_creation": None,
            "permissions": None,
            "installation": None,
            "theme_installation": None,
            "plugin_installation": None,
            "success": False,
            "admin_url": f"https://{domain}/wp-admin/"  # Admin URL for reference
        }

        # Step 1: Create database
        results["database_creation"] = self.create_database(db_name)
        if not results["database_creation"].get("status", 0):
            # Return early if database creation failed
            return results

        # Step 2: Create database user
        results["database_user_creation"] = self.create_db_user(db_user, db_password)
        if not results["database_user_creation"].get("status", 0):
            # Return early if user creation failed
            return results

        # Step 3: Assign user to database
        results["user_privileges"] = self.assign_user_to_db(db_name, db_user)
        if not results["user_privileges"].get("status", 0):
            # Return early if privilege assignment failed
            return results

        # Step 4: Download WordPress
        results["wordpress_download"] = self.download_wordpress(path)
        if not results["wordpress_download"].get("status", 0):
            # Return early if WordPress download failed
            return results

        # Step 5: Create wp-config.php
        results["wp_config_creation"] = self.create_wp_config(path, db_name, db_user, db_password)
        if not results["wp_config_creation"].get("status", 0):
            # Return early if config creation failed
            return results

        # Step 6: Set file permissions
        results["permissions"] = self.set_file_permissions(path)
        if not results["permissions"].get("status", 0):
            # Return early if setting permissions failed
            return results

        # Step 7: Install WordPress
        results["installation"] = self.run_wp_installation(
            path, domain, site_title, admin_user, admin_password, admin_email
        )
        if not results["installation"].get("status", 0):
            # Return early if WordPress installation failed
            return results

        # Step 8: Install theme if specified
        if install_theme and results["installation"].get("status", 0):
            results["theme_installation"] = self.make_api_request(
                "Execute", "exec",
                {"command": f"cd {path} && wp theme install {install_theme} --activate"}
            )

        # Step 9: Install plugins if specified
        if install_plugins and results["installation"].get("status", 0):
            # Build a command string with all plugins
            # Join with " && " to create a chain of install commands
            plugin_commands = " && ".join([f"wp plugin install {p} --activate" for p in install_plugins])
            results["plugin_installation"] = self.make_api_request(
                "Execute", "exec",
                {"command": f"cd {path} && {plugin_commands}"}
            )

        # Determine overall success by checking all critical operations
        results["success"] = all(r.get("status", 0) for r in [
            results["database_creation"],
            results["database_user_creation"],
            results["user_privileges"],
            results["wordpress_download"],
            results["wp_config_creation"],
            results["permissions"],
            results["installation"]
        ])

        return results

    def deploy_wordpress_with_elementor(self, domain, path, db_name, db_user, db_password,
                                       site_title, admin_user, admin_password, admin_email,
                                       elementor_pro_key=None, elementor_pro_local_path=None,
                                       kit_url=None, kit_local_path=None,
                                       install_plugins=None):
        """
        Deploy WordPress with Elementor and Elementor Pro.
        This is the main method for a complete deployment with Elementor integration.

        Args:
            domain (str): Site domain (e.g., 'example.com')
            path (str): Server path to install WordPress
            db_name (str): Database name (without prefix)
            db_user (str): Database username (without prefix)
            db_password (str): Database password
            site_title (str): Site title
            admin_user (str): Admin username
            admin_password (str): Admin password
            admin_email (str): Admin email
            elementor_pro_key (str): Elementor Pro license key
            elementor_pro_local_path (str): Local path to Elementor Pro zip file
            kit_url (str): URL to Elementor kit
            kit_local_path (str): Local path to Elementor kit file
            install_plugins (list): Additional plugins to install

        Returns:
            dict: Deployment results with status of each operation
        """
        # Step 1: Deploy the basic WordPress site
        # This handles database, WordPress installation, and basic plugins
        results = self.deploy_wordpress(
            domain, path, db_name, db_user, db_password,
            site_title, admin_user, admin_password, admin_email,
            install_plugins=install_plugins or []
        )

        # If WordPress deployment failed, return early
        if not results["success"]:
            return results

        # Add Elementor-specific result fields to track status
        results.update({
            "elementor_installation": None,
            "elementor_pro_upload": None,
            "elementor_pro_installation": None,
            "kit_upload": None,
            "kit_import": None
        })

        # Step 2: Install free Elementor plugin
        results["elementor_installation"] = self.install_elementor(path)

        # Step 3: Handle Elementor Pro if provided
        server_pro_path = None
        if elementor_pro_key and elementor_pro_local_path:
            # Upload Elementor Pro zip to server
            server_pro_path = f"{path}/wp-content/uploads/elementor-pro.zip"
            results["elementor_pro_upload"] = self.upload_elementor_pro_zip(elementor_pro_local_path, server_pro_path)

            # Install and activate Elementor Pro if upload was successful
            if results["elementor_pro_upload"].get("status", 0):
                results["elementor_pro_installation"] = self.install_elementor_pro(
                    path, license_key=elementor_pro_key, pro_zip_path=server_pro_path
                )

        # Step 4: Handle Elementor kit if provided
        kit_server_path = None
        if kit_local_path:
            # Upload kit file to server
            kit_server_path = f"{path}/wp-content/uploads/elementor-kit.zip"
            results["kit_upload"] = self.upload_kit_file(kit_local_path, kit_server_path)

        # Step 5: Import the kit if Elementor was installed successfully
        if (kit_url or kit_server_path) and results["elementor_installation"].get("status", 0):
            results["kit_import"] = self.import_elementor_kit(
                path,
                kit_url=kit_url,
                kit_file=kit_server_path
            )

        # Determine Elementor success by checking each Elementor-related operation
        elementor_success = results["elementor_installation"].get("status", 0)

        # Check if Pro was supposed to be installed and if it was successful
        if elementor_pro_key and elementor_pro_local_path:
            pro_success = (
                results["elementor_pro_upload"].get("status", 0) and
                results["elementor_pro_installation"].get("status", 0)
            )
            elementor_success = elementor_success and pro_success

        # Check if kit was supposed to be imported and if it was successful
        if kit_url or kit_local_path:
            if kit_local_path:
                kit_success = (
                    results["kit_upload"].get("status", 0) and
                    results["kit_import"].get("status", 0)
                )
            else:
                kit_success = results["kit_import"].get("status", 0)
            elementor_success = elementor_success and kit_success

        # Update the overall success flag to include Elementor operations
        results["success"] = results["success"] and elementor_success

        return results


# ==========================
# EXAMPLE USAGE
# ==========================

if __name__ == "__main__":
    # Create a deployer instance with cPanel credentials
    deployer = CPanelWordPressDeployer(
        hostname="example.com",
        username="cpanelusername",
        auth_type="password",  # or "token"
        auth_value="your_password_or_token"
    )

    # Deploy WordPress with Elementor and kit
    results = deployer.deploy_wordpress_with_elementor(
        # Basic site information
        domain="yourdomain.com",
        path="/home/username/public_html",

        # Database details
        db_name="wordpress",
        db_user="wpuser",
        db_password="secure_password",

        # WordPress admin details
        site_title="My WordPress Site",
        admin_user="admin",
        admin_password="admin_password",
        admin_email="admin@example.com",

        # Elementor details
        elementor_pro_key="your_elementor_pro_license",
        elementor_pro_local_path="/path/to/elementor-pro.zip",
        kit_local_path="/path/to/elementor-kit.zip",

        # Additional plugins to install
        install_plugins=["contact-form-7", "yoast-seo", "wordfence"]
    )

    # Print the results in a readable format
    print(json.dumps(results, indent=2))
