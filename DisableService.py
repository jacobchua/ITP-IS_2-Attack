import subprocess

service_name = "MyService"

# Stop the service if it's currently running
subprocess.run(["sc", "stop", service_name], check=False)

# Disable the service
subprocess.run(["sc", "config", service_name, "start=", "disabled"], check=True)
