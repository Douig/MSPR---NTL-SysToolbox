import subprocess

def get_service_status():
    
    
    try:
        command1 = ["powershell", "-Command", "(Get-Service -Name 'DNS' -ErrorAction SilentlyContinue).Status"]
        command2 = ["powershell", "-Command", "(Get-Service -Name 'NTDS' -ErrorAction SilentlyContinue).Status"]

        result1 = subprocess.run(command1, capture_output=True, text=True)
        result2 = subprocess.run(command2, capture_output=True, text=True)


        status_dns = result1.stdout.strip() if result1.stdout.strip() else "Not installed"
        status_ntds = result2.stdout.strip() if result2.stdout.strip() else "Not installed"

        return status_dns, status_ntds

    except Exception as e:
        return "Not installed", "Not installed"



  #status_dns, status_ntds = get_service_status()
  #print(f"Status DNS: {status_dns}")
  #print(f"Status NTDS: {status_ntds}") 
