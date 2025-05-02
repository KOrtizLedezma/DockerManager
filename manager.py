import os
import shutil
import subprocess
from dotenv import load_dotenv

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
        CMD ["node", "{entry_file}"]
        """
    with open(os.path.join(target_dir, "Dockerfile"), "w") as f:
        f.write(dockerfile_content)


def detect_entry_file(target_dir):
    for fname in ["server.js", "index.js", "app.js"]:
        if os.path.exists(os.path.join(target_dir, fname)):
            return fname
    return "index.js"  # fallback


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
        repo_url = input("Enter GitHub repo URL (HTTPS): ").strip()
        print(f"Cloning {repo_url} into {target_dir}...")
        run_cmd(f"git clone {repo_url} {target_dir}")

        # Check for nested Server directory (case-sensitive match)
        server_path = os.path.join(target_dir, "Server")
        if os.path.exists(os.path.join(server_path, "package.json")):
            print("Detected nested 'Server/' folder. Moving contents to root...")
            for item in os.listdir(server_path):
                shutil.move(os.path.join(server_path, item), target_dir)
            shutil.rmtree(server_path)

        entry_file = detect_entry_file(target_dir)
        print(f"Detected entry file: {entry_file}")
        generate_dockerfile(target_dir, entry_file)
        internal_port = "3000"
    else:
        print("\nAvailable templates:")
        templates = list_templates()
        for i, t in enumerate(templates):
            print(f"{i + 1}. {t}")
        choice = input("Select template: ")
        try:
            template = templates[int(choice) - 1]
        except (IndexError, ValueError):
            print("Invalid template selection.")
            return

        shutil.copytree(os.path.join(TEMPLATES_DIR, template), target_dir)

        internal_port = "5000"
        if template == "django":
            internal_port = "8000"
        elif template == "node":
            internal_port = "3000"

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


def list_containers():
    run_cmd("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'")


def show_logs():
    name = input("Container name to view logs: ")
    os.system(f"docker logs -f {name}")


def main():
    os.makedirs(CONTAINERS_DIR, exist_ok=True)
    while True:
        print("\n--- Docker Manager ---")
        print("1. Create container")
        print("2. Delete container")
        print("3. List running containers")
        print("4. Monitor logs")
        print("5. Exit")
        choice = input("Select an option: ")
        if choice == "1":
            create_container()
        elif choice == "2":
            delete_container()
        elif choice == "3":
            list_containers()
        elif choice == "4":
            show_logs()
        elif choice == "5":
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()
