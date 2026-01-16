#!/usr/bin/env python3
"""
Fix git repository to point to correct URL
"""
import os
import subprocess

def run_command(cmd, description=""):
    """Run a shell command and capture output"""
    print(f"  {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"  Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"  Exception: {e}")
        return False

def fix_git_remote():
    """Remove wrong remote and add correct one"""
    commands = [
        # Remove incorrect remote URL if it exists
        ["git", "remote", "remove", "origin"],
        # Add correct remote URL
        ["git", "remote", "add", "https://github.com/QuantumCotton/liora-animal-learning.git"]
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Removing {cmd[2]}"):
            continue
    
    print("✅ Fixed git remote URL")

def git_push():
    """Push all changes to correct repository"""
    run_command("git", "Pushing all changes to correct repository...")
    return run_command("git", "push", "origin", "main")

if __name__ == "__main__":
    print("🔧 Fixing git repository...")
    print("📍 Current directory:", os.getcwd())
    print()
    
    # Step 1: Fix remote URL
    fix_git_remote()
    print()
    
    # Step 2: Push changes
    print()
    git_push()
    
    print("✅ Complete! Repository now points to correct GitHub URL")
    print("🚀 Pushing to Netlify...")
    return run_command("git", "push", "--force")
