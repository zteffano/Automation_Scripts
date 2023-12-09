import subprocess
import os





def run_command(command):
    """ Run a shell command and return its output """
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {' '.join(command)}\n{result.stderr}")
        return False
    else:
        print(f"Command output: {result.stdout}")
        return True

def build_webapi_to_hub():
    # Step 1: Navigate to Project Directory
    project_directory = r"C:\Users\z\source\repos\HSS_WEBAPI_MICROSERVICE"
    os.chdir(project_directory)

    # Step 2: Build the Docker Image
    if not run_command(f'docker build -t hsswebapi_scripted -f HSS_WEBAPI_MICROSERVICE/Dockerfile .'):
        return

    # Step 3: Tag the Image
    if not run_command('docker tag hsswebapi_scripted zteffano/hsswebapi_test:latest'):
        return

    # Step 3.5: Docker login
    # Note: Docker login might require interactive input. This step may need to be done manually
    # if not run_command('docker login'):
    #     return

    # Step 4: Push the Image to Docker Hub
    if not run_command('docker push zteffano/hsswebapi_test:latest'):
        return

    print("Docker Script execution completed.")

if __name__ == "__main__":
    build_webapi_to_hub()
