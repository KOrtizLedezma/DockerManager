import os
import shutil
import subprocess

BASE_DIR = os.path.dirname(__file__)
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
CONTAINERS_DIR = os.path.join(BASE_DIR, 'containers')

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Error:", result.stderr)
    return result

def list_templates():
    return [f for f in os.listdir(TEMPLATES_DIR)
            if os.path.isdir(os.path.join(TEMPLATES_DIR, f)) and not f.startswith("generic-")]

def generate_dockerfile(target_dir, entry_file="index.js"):
    dockerfile_content = f"""\
        FROM node:20-alpine
        WORKDIR /app
        COPY . .
        RUN npm install
        EXPOSE 3000
        CMD [\"node\", \"{entry_file}\"]
        """
    with open(os.path.join(target_dir, "Dockerfile"), "w") as f:
        f.write(dockerfile_content)

def detect_entry_file(target_dir):
    for f_name in ["server.js", "index.js", "app.js"]:
        if os.path.exists(os.path.join(target_dir, f_name)):
            return f_name
    return "index.js"

def prompt_env_file(target_dir):
    env_choice = input("Do you want to (1) provide or (2) create a .env file? (1/2/n): ".strip().lower())
    dest_env_path = os.path.join(target_dir, ".env")

    if env_choice == "1":
        env_source_path = input("Enter the path of the .env file: ".strip())
        try:
            shutil.copy(env_source_path, dest_env_path)
            print(f"The .env file has been copied to {dest_env_path}")
        except Exception as e:
            print(f"Failed to copy the .env file: {e}")

    elif env_choice == "2":
        print("Enter key=value pairs for your .env file. Type 'done' to finish:")
        env_lines = []
        while True:
            line = input("→ ")
            if line.strip().lower() == "done":
                break
            if '=' in line:
                env_lines.append(line)
            else:
                print("Invalid format. Use key=value")

        try:
            with open(os.path.join(target_dir, ".env"), "w") as f:
                f.write("\n".join(env_lines))
            print(f".env file created at {dest_env_path}")
        except Exception as e:
            print(f"Failed to create .env file: {e}")


def clone_github_repo(name):
    repo_url = input("Enter GitHub repo URL (HTTPS): ").strip()
    target_dir = os.path.join(CONTAINERS_DIR, name)
    print(f"Cloning {repo_url} into {target_dir}...")
    run_cmd(f"git clone {repo_url} {target_dir}")

    server_path = os.path.join(target_dir, "Server")
    if os.path.exists(os.path.join(server_path, "package.json")):
        print("Detected nested 'Server/' folder. Moving contents to root...")
        for item in os.listdir(server_path):
            shutil.move(os.path.join(server_path, item), target_dir)
        shutil.rmtree(server_path)

    prompt_env_file(target_dir)

    entry_file = detect_entry_file(target_dir)
    print(f"Detected entry file: {entry_file}")
    generate_dockerfile(target_dir, entry_file)
    return target_dir, "3000"

def use_template(name):
    print("\nAvailable templates:")
    templates = list_templates()
    for i, t in enumerate(templates):
        print(f"{i + 1}. {t}")
    choice = input("Select template: ")
    try:
        template = templates[int(choice) - 1]
    except (IndexError, ValueError):
        print("Invalid template selection.")
        return None, None

    target_dir = os.path.join(CONTAINERS_DIR, name)
    shutil.copytree(os.path.join(TEMPLATES_DIR, template), target_dir)

    internal_port = "5000"
    if template == "django":
        internal_port = "8000"
    elif template == "node":
        internal_port = "3000"

    return target_dir, internal_port

def create_container():
    print("\n--- Create Container ---")
    use_github = input("Use a GitHub repo instead of a template? (y/n): ").lower().strip() == "y"

    name = input("Container name: ")
    port = input("Port to expose: ")
    target_dir = os.path.join(CONTAINERS_DIR, name)

    if os.path.exists(target_dir):
        print("Container with that name already exists.")
        return

    if use_github:
        target_dir, internal_port = clone_github_repo(name)
    else:
        target_dir, internal_port = use_template(name)
        if not target_dir:
            return

    env_file = os.path.join(target_dir, ".env")
    if os.path.exists(env_file):
        print("Using .env file for environment variables.")
    else:
        print("No .env file found. Continuing without it.")

    image_name = f"{name}_image"

    print("\nBuilding Docker image...")
    run_cmd(f"docker build -t {image_name} {target_dir}")

    print("\nRunning Docker container...")
    if os.path.exists(env_file):
        run_cmd(f"docker run -d -p {port}:{internal_port} --env-file {env_file} --name {name} {image_name}")
    else:
        run_cmd(f"docker run -d -p {port}:{internal_port} --name {name} {image_name}")

def delete_container():
    name = input("Container name to delete: ")
    run_cmd(f"docker rm -f {name}")
    target_dir = os.path.join(CONTAINERS_DIR, name)
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    print("Container deleted.")

def list_all_containers():
    print("\n--- All Containers ---")
    run_cmd("docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'")

def show_logs():
    name = input("Container name to view logs: ")
    os.system(f"docker logs -f {name}")

def manage_container():
    name = input("Container name: ").strip()
    print("\nAvailable actions:")
    print("1. Restart")
    print("2. Stop")
    print("3. Start")
    print("4. Pause")
    print("5. Unpause")

    action = input("Select action: ").strip()

    cmd_map = {
        "1": f"docker restart {name}",
        "2": f"docker stop {name}",
        "3": f"docker start {name}",
        "4": f"docker pause {name}",
        "5": f"docker unpause {name}"
    }

    if action in cmd_map:
        run_cmd(cmd_map[action])
    else:
        print("Invalid action.")


def main():
    os.makedirs(CONTAINERS_DIR, exist_ok=True)
    while True:
        print("\n--- Docker Manager ---")
        print("1. Create container")
        print("2. Delete container")
        print("3. List all containers")
        print("4. Monitor logs")
        print("5. Manage container (start/stop/restart/pause)")
        print("6. Exit")
        choice = input("Select an option: ")
        if choice == "1":
            print("\n")
            create_container()
        elif choice == "2":
            print("\n")
            delete_container()
        elif choice == "3":
            print("\n")
            list_all_containers()
        elif choice == "4":
            print("\n")
            show_logs()
        elif choice == "5":
            print("\n")
            manage_container()
        elif choice == "6":
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()