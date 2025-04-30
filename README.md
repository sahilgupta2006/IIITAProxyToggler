# 🚀 IIITAProxyToggler

Tired of manually toggling proxies every time you switch between the **IIITA college network** and a regular, non-proxied network?

Annoyed by having to run `fixwifi.it` every hour just to survive on campus WiFi?

This tool is **made for you**.

---

### Works on: Windows

### Setup Instructions

1. **Download** the `.exe` from the `dist/` directory.
2. **Create** a folder named `ProxyToggler` in `C:\`.
3. **Place** the `config.ini` file inside `C:\ProxyToggler\`.
4. **Edit** the config file with your IIITA credentials
5. **Run** the proxy_toggler.exe file once and then done. Dont delete the file, that's not a setup file.

### After setup
It runs automatically and in ideal scenario if not hindered by NTVirus, it should run in the background as soon as you bootup the PC.

```ini
# C:\ProxyToggler\config.ini

[creds]
uname=<your-enrolment-number>
pwd=<your-ldap-password>
