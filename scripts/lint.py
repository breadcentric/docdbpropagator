import subprocess


def main() -> None:
    commands = [["black", "."], ["isort", "."], ["flake8", "."], ["mypy", "."]]

    for cmd in commands:
        print(f"Running {' '.join(cmd)}...")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            exit(result.returncode)


if __name__ == "__main__":
    main()
