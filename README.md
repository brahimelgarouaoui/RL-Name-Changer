# RL Name Changer

A minimalistic tool to change your display name in Rocket League. This project is based on [RL-Spoofer-GUI](https://github.com/Kakapo-Labs/RL-Spoofer-GUI) but with a focus on simplicity and ease of use.

## Features

- 🎮 Change your Rocket League display name without modifying game files
- 🔧 Simple, user-friendly GUI interface
- 🛡️ Safe and reversible - no permanent changes to your system
- ⚡ Automatic proxy management
- 🎯 Minimal resource usage
- 📝 Comprehensive logging for troubleshooting

## How It Works

The application uses a local proxy server (mitmproxy) to intercept and modify HTTP responses from Rocket League's servers. When the game requests your player information, the proxy modifies the display name in the response before it reaches the game client.

## Prerequisites

- Windows 10/11 (64-bit)
- Python 3.7+ (for running from source)
- Administrator privileges (required for certificate installation and system proxy settings)

## Installation

### Install from Source

1. **Clone the repository:**
   ```bash
   git clone https://github.com/borgox/rl-name-changer.git
   cd rl-name-changer
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up mitmproxy certificates:**
   ```bash
   # Run as Administrator
   python scripts/setup_mitmproxy_cert.py
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

## Usage

### Initial Setup

1. **Install mitmproxy certificate** (one-time setup):
   - Run `scripts\setup_mitmproxy_cert.bat` as Administrator
   - The script will automatically download, install, and configure the mitmproxy certificate
   - This is required for HTTPS interception to work properly

2. **Start the application:**
   - Run `python src/main.py` 

### Changing Your Name

1. **Enter your desired display name** in the text field
2. **Click "ACTIVATE"** to start the proxy
3. **Launch Rocket League** 
4. **Your new name should appear in-game**

### Important Notes

- **Close Rocket League before changing names** - The name change only takes effect when the game requests fresh player data
- **The proxy must be active** while playing for the name change to persist
- **Click "DEACTIVATE"** when done to restore normal network settings
- **Auto-attach option** (future feature) will automatically detect when Rocket League is running

### Troubleshooting Name Changes

If your name isn't changing:

1. Make sure the proxy is **ACTIVATED** (green status)
2. **Completely close and restart Rocket League**
3. Try going to a menu that refreshes player data (Main Menu -> Play -> Back)
4. Check the application logs for any error messages

## Project Structure

```
rl-name-changer/
├── src/
│    main.py                       # Legacy entry point (backward compatibility)
│    rl_name_changer/          # Main application package
│       ├── __init__.py
│       ├── main.py               # Application entry point
│       ├── gui.py                # GUI components
│       ├── proxy.py              # mitmproxy addon and controller
│       ├── config.py             # Configuration constants
│       ├── config_manager.py     # Configuration file management
│       ├── system_utils.py       # System utilities (proxy, process detection)
│       ├── logging_setup.py      # Logging configuration
│       └── cleanup.py            # Cleanup and exception handling
├── scripts/
│   ├── setup_mitmproxy_cert.bat  # Certificate setup (Windows batch)
│   ├── setup_mitmproxy_cert.py   # Certificate setup (Python)
├── requirements.txt              # Python dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Technical Details

### Security Considerations

- The application only modifies display name responses from specific game-related domains
- No game files are modified
- All changes are temporary and reversible
- The proxy only runs when explicitly activated
- Certificates are properly managed and can be uninstalled

### Network Configuration

- **Proxy Address:** `127.0.0.1:8080`
- **Target Domains:** `*.epicgames.com`, `*.psyonix.com`, `*.live.psynet.gg`
- **Excluded from Proxy:** `<local>`, Epic Games launcher domains

### Logging

- Application logs are saved to: `%APPDATA%\RLNameChanger\mitmproxy_app_log.txt`
- Console output includes colored log levels for easy debugging
- Both file and console logging are enabled by default

## Common Issues and Solutions

### "Port 8080 is already in use"
- Close any other applications using port 8080
- Wait 30 seconds and try again (Windows TIME_WAIT)
- Check for other proxy applications

### "Permission denied while setting proxy"
- Run the application as Administrator
- Ensure your user account has proxy configuration permissions

### "Failed to import mitmproxy modules"
- Install mitmproxy: `pip install mitmproxy`
- Check Python installation and PATH

### "Certificate not trusted" / SSL errors
- Re-run the certificate setup script as Administrator
- Check Windows certificate store (run `certmgr.msc`)
- Restart your browser/applications after certificate installation

### Name not changing in-game
- Ensure Rocket League is completely closed before activating
- Try restarting Rocket League after activation
- Check that the status shows "Proxy: Active"
- Verify your entered name is within character limits

## Development

### Setting up Development Environment

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
4. Install development dependencies: `pip install -r requirements.txt`

### Code Style

The project uses Black for code formatting and follows PEP 8 guidelines.

```bash
# Format code
black src/
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and ensure code follows style guidelines
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational and personal use only. Use at your own risk. The developers are not responsible for any consequences resulting from the use of this software. Always respect game terms of service and community guidelines.

## Acknowledgments

- Based on [RL-Spoofer-GUI](https://github.com/Kakapo-Labs/RL-Spoofer-GUI) by Kakapo Labs
- Built with [mitmproxy](https://mitmproxy.org/) for HTTP interception
- GUI powered by [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)

## Support

If you encounter issues:

1. Check the [Common Issues](#common-issues-and-solutions) section
2. Look at the application logs in `%APPDATA%\RLNameChanger\mitmproxy_app_log.txt`
3. Create an issue on GitHub with:
   - Your operating system and version
   - Python version (if running from source)
   - Complete error message
   - Steps to reproduce the problem
   - Log file contents (remove any personal information)

---

**Happy gaming!** 🚗⚽