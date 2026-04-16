#!/usr/bin/env python3
"""Enable or disable AWI client submodules.

Usage:
    python3 toggle_client.py enable <name>    # init + checkout submodule
    python3 toggle_client.py disable <name>   # deinit submodule (keeps registration)
    python3 toggle_client.py status           # show all clients and their state
    python3 toggle_client.py enable all       # enable all registered clients
    python3 toggle_client.py disable all      # disable all registered clients
"""

import argparse
import subprocess
import sys
from pathlib import Path

AWI_ROOT = Path(__file__).resolve().parents[4]
CLIENTS_DIR = AWI_ROOT / "_clients"


def get_registered_clients() -> list[str]:
    """Return list of client names registered in .gitmodules."""
    result = subprocess.run(
        ["git", "submodule", "status"],
        cwd=AWI_ROOT,
        capture_output=True,
        text=True,
    )
    clients = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            path = parts[1]
            if path.startswith("_clients/"):
                clients.append(path.removeprefix("_clients/"))
    return clients


def is_active(name: str) -> bool:
    """True if submodule working directory has content (is initialized)."""
    client_path = CLIENTS_DIR / name
    return client_path.exists() and any(client_path.iterdir())


def enable(name: str) -> int:
    """Initialize and checkout a client submodule."""
    registered = get_registered_clients()
    if name not in registered:
        print(f"Error: '{name}' not registered in .gitmodules.")
        print(f"Registered clients: {', '.join(registered) or 'none'}")
        return 1

    if is_active(name):
        print(f"'{name}' already active.")
        return 0

    print(f"Enabling '{name}'...")
    result = subprocess.run(
        ["git", "submodule", "update", "--init", "--recursive", f"_clients/{name}"],
        cwd=AWI_ROOT,
    )
    if result.returncode == 0:
        print(f"'{name}' enabled.")
    return result.returncode


def disable(name: str) -> int:
    """Deinit a client submodule (removes working dir, keeps registration)."""
    registered = get_registered_clients()
    if name not in registered:
        print(f"Error: '{name}' not registered in .gitmodules.")
        print(f"Registered clients: {', '.join(registered) or 'none'}")
        return 1

    if not is_active(name):
        print(f"'{name}' already inactive.")
        return 0

    print(f"Disabling '{name}'...")
    result = subprocess.run(
        ["git", "submodule", "deinit", "-f", f"_clients/{name}"],
        cwd=AWI_ROOT,
    )
    if result.returncode == 0:
        print(f"'{name}' disabled.")
    return result.returncode


def status() -> int:
    """Print active/inactive state for all registered clients."""
    registered = get_registered_clients()
    if not registered:
        print("No clients registered.")
        return 0

    print("Client submodule status:\n")
    for name in registered:
        state = "active  " if is_active(name) else "inactive"
        print(f"  {state}  _clients/{name}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Enable or disable AWI client submodules."
    )
    parser.add_argument(
        "action",
        choices=["enable", "disable", "status"],
        help="Action to perform",
    )
    parser.add_argument(
        "name",
        nargs="?",
        help="Client name (e.g. CSR1, newhaze) or 'all'",
    )
    args = parser.parse_args()

    if args.action == "status":
        return status()

    if not args.name:
        parser.error(f"'name' required for action '{args.action}'")

    fn = enable if args.action == "enable" else disable

    if args.name == "all":
        clients = get_registered_clients()
        if not clients:
            print("No clients registered.")
            return 0
        codes = [fn(c) for c in clients]
        return max(codes)

    return fn(args.name)


if __name__ == "__main__":
    sys.exit(main())
