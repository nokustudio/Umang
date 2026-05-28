import subprocess
import sys
import datetime
import os

def run_command(cmd):
    print(f"\nRunning: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing command: {' '.join(cmd)}")
        print(result.stderr)
        return False, result.stdout, result.stderr
    print(result.stdout)
    return True, result.stdout, result.stderr

def main():
    print("=== Noku Pitch Sync Script ===")
    
    # Get base directory of the script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    
    # 1. Compile website
    print("\n[Step 1/3] Compiling website with update_site.py...")
    success, stdout, stderr = run_command([sys.executable, "update_site.py"])
    if not success:
        print("Site compilation failed. Aborting sync.")
        sys.exit(1)
        
    # 2. Stage changes
    print("\n[Step 2/3] Staging changes in Git...")
    success, _, _ = run_command(["git", "add", "-A"])
    if not success:
        print("Staging failed. Aborting sync.")
        sys.exit(1)
        
    # Check status
    _, status_out, _ = run_command(["git", "status", "-s"])
    if not status_out.strip():
        print("\nNo changes to commit. Working tree is clean.")
        return
        
    # 3. Commit changes
    print("\n[Step 3/3] Committing and pushing changes...")
    
    # Prompt for commit message
    commit_msg = ""
    if len(sys.argv) > 1:
        commit_msg = " ".join(sys.argv[1:])
    else:
        try:
            if sys.stdin.isatty():
                commit_msg = input("Enter commit message (leave blank for auto-timestamp): ").strip()
            else:
                commit_msg = ""
        except (EOFError, KeyboardInterrupt):
            commit_msg = ""
            print() # Print newline after interrupt/EOF
            
    if not commit_msg:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"Auto-update: {timestamp}"
        
    success, _, _ = run_command(["git", "commit", "-m", commit_msg])
    if not success:
        print("Commit failed. Aborting sync.")
        sys.exit(1)
        
    # Push changes
    success, _, _ = run_command(["git", "push", "origin", "main"])
    if not success:
        print("Push failed.")
        sys.exit(1)
        
    print("\nSuccess! Website compiled, committed, and pushed to GitHub successfully.")

if __name__ == "__main__":
    main()
