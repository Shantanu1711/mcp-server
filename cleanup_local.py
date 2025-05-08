import subprocess
import sys
import pkg_resources

def uninstall_local_packages():
    # Get list of installed packages
    installed_packages = [f"{dist.key}=={dist.version}" for dist in pkg_resources.working_set]
    
    print("Starting cleanup of local Python packages...")
    print("The following packages will be uninstalled:")
    for package in installed_packages:
        print(f"- {package}")
    
    # Ask for confirmation
    confirm = input("\nDo you want to proceed with uninstallation? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Cleanup cancelled.")
        return
    
    # Uninstall each package
    for package in installed_packages:
        try:
            print(f"\nUninstalling {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", package])
        except subprocess.CalledProcessError as e:
            print(f"Error uninstalling {package}: {str(e)}")
    
    print("\nCleanup completed!")

if __name__ == "__main__":
    uninstall_local_packages() 