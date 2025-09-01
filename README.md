# cPanel WordPress Deployer

## 🚀 Overview

An enterprise-grade automation tool that revolutionizes WordPress deployment on cPanel hosting platforms. This Python-based solution reduces deployment time from 30+ minutes to just 3-5 minutes while ensuring security best practices and seamless Elementor Pro integration.

📖 **For full comprehensive project details and live demo, visit: [damilareadekeye.com/works/software/cpanel-wordpress-deployer](https://damilareadekeye.com/works/software/cpanel-wordpress-deployer)**

## ✨ Key Features

### **Automated Deployment Pipeline**
- Complete WordPress installation in 3-5 minutes
- Database creation with secure credentials
- Automatic Elementor Pro activation
- Essential plugin bundle installation
- Security hardening out of the box

### **Advanced Integration**
- **cPanel UAPI**: Direct API integration for hosting control
- **WP-CLI**: Command-line WordPress management
- **Elementor Pro**: Automatic license activation and setup
- **Database Management**: Automated MySQL setup with optimal configuration

### **Security Features**
- Cryptographically secure password generation
- Proper file permissions (644/755)
- Database prefix randomization
- Automatic security plugin installation
- SSL/HTTPS configuration support

## 🛠️ Technical Architecture

### Core Components
- **Python 3.8+** runtime environment
- **Requests library** for API communication
- **MySQL connector** for database operations
- **Base64 encoding** for secure file transfers
- **JSON configuration** management

### API Integrations
- cPanel UAPI v2 for hosting operations
- WordPress REST API for site configuration
- Elementor licensing API for activation
- WP-CLI for advanced WordPress management

## 📋 Prerequisites

- Python 3.8 or higher
- cPanel hosting account with API access
- Valid Elementor Pro license
- MySQL database access
- Required Python packages:
  ```bash
  pip install requests mysql-connector-python
  ```

## 🚀 Quick Start

### Installation
```bash
# Clone the repository
git clone https://github.com/damilareadekeye/cpanel-wordpress-deployer.git
cd cpanel-wordpress-deployer

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage
```python
from cpanel_wordpress_deployer import CPanelWordPressDeployer

# Initialize deployer
deployer = CPanelWordPressDeployer(
    hostname="your-server.com",
    username="cpanel_user",
    auth_type="token",
    auth_value="your_api_token"
)

# Deploy WordPress with Elementor
result = deployer.deploy_wordpress_with_elementor(
    domain="example.com",
    path="/home/username/public_html",
    db_name="wp_database",
    db_user="wp_user",
    db_password="secure_password_123",
    site_title="My WordPress Site",
    admin_user="admin",
    admin_password="admin_pass_456",
    admin_email="admin@example.com",
    elementor_pro_key="YOUR_LICENSE_KEY",
    elementor_pro_local_path="/path/to/elementor-pro.zip"
)

print(f"Site deployed successfully!")
print(f"Admin URL: {result['admin_url']}")
```

## 🔧 Configuration

### Authentication Methods

**Basic Authentication:**
```python
deployer = CPanelWordPressDeployer(
    hostname="server.com",
    username="user",
    auth_type="password",
    auth_value="your_password"
)
```

**Token Authentication (Recommended):**
```python
deployer = CPanelWordPressDeployer(
    hostname="server.com",
    username="user",
    auth_type="token",
    auth_value="api_token"
)
```

### Deployment Options
```python
# Full deployment with custom settings
deployer.deploy_wordpress_with_elementor(
    domain="site.com",
    path="/home/username/public_html",
    db_name="wp_corp",
    db_user="wp_user",
    db_password="secure_db_pass",
    site_title="Corporate Website",
    admin_user="wp_admin",
    admin_password="custom_pass_123",
    admin_email="admin@company.com",
    elementor_pro_key="LICENSE_KEY",
    elementor_pro_local_path="/path/to/elementor-pro.zip",
    kit_local_path="/path/to/template-kit.zip",  # Optional
    install_plugins=[
        'wordfence',
        'yoast-seo',
        'contact-form-7'
    ]
)
```

## 📊 Performance Metrics

| Operation | Manual Process | Automated |
|-----------|---------------|-----------|
| Database Setup | 5-10 min | 30 sec |
| WordPress Installation | 10-15 min | 1-2 min |
| Elementor Setup | 5-10 min | 30 sec |
| Security Configuration | 10-15 min | 45 sec |
| **Total Deployment** | **30-50 min** | **3-5 min** |

## 🔐 Security Best Practices

The deployer implements several security measures:

1. **Secure Password Generation**: 16-character passwords with mixed case, numbers, and symbols
2. **Database Security**: Unique prefixes and restricted user privileges
3. **File Permissions**: Proper Unix permissions (644 for files, 755 for directories)
4. **API Security**: Token-based authentication support
5. **Error Handling**: Comprehensive error catching without exposing sensitive data

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
```bash
# Clone the repo
git clone https://github.com/damilareadekeye/cpanel-wordpress-deployer.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Damilare Lekan Adekeye**
- Portfolio: [damilareadekeye.com](https://damilareadekeye.com)
- GitHub: [@damilareadekeye](https://github.com/damilareadekeye)
- LinkedIn: [@damilareadekeye](https://linkedin.com/in/damilareadekeye)

## 🙏 Acknowledgments

- cPanel for their comprehensive UAPI documentation
- WordPress community for WP-CLI
- Elementor team for their excellent page builder
- All contributors and users of this tool

## 📞 Support

For issues, questions, or suggestions, please open an issue on the [GitHub repository](https://github.com/damilareadekeye/cpanel-wordpress-deployer/issues) or contact via [portfolio website](https://damilareadekeye.com/contact).

---

**Note**: This tool requires valid cPanel hosting credentials and appropriate API access. Always test in a development environment before production use.
