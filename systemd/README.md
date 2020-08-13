## Running via systemd

A service file for running the Keystone bot automatically.

## How to setup

This assumes you have the correct privileges to create systemd services

1. Edit the keystone.service file to set the WorkingDirectory 
   `WorkingDirectory=/opt/keystone`
2. Create a symlink to the keystone.service file
   `systemctl link /opt/keystone/systemd/keystone.service`
3. Reload the systemd configuration
   `systemctl daemon-reload`
4. Enable the service to start automatically
   `systemctl enable keystone.service`
5. Start the service 
   `systemctl start keystone.service`
6. Check the service status
   `systemctl status keystone.service`
