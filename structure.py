from pathlib import Path

def print_tree(directory, prefix=""):
    path = Path(directory)

    items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))

    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        connector = "└── " if is_last else "├── "

        print(prefix + connector + item.name)

        if item.is_dir():
            extension = "    " if is_last else "│   "
            print_tree(item, prefix + extension)

project_root = Path.cwd()

print(project_root.name + "/")
print_tree(project_root)