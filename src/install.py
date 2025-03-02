from packages import Package, PackageManager, Yay

packages = [
    Package(
        id_map={"git": []},
        description="a distributed version control system",
        tags=["terminal"],
    ),
    Package(
        id_map={"alacritty": [Yay]},
        description="a cross-platform, GPU-accelerated terminal emulator",
        tags=["terminal"],
    ),
    Package(
        id_map={"firefox": []}, description="a private & safe web browser", tags=["gui"]
    ),
    Package(
        id_map={"fzf": []},
        description="a fuzzy finder in the terminal",
        tags=["terminal"],
    ),
]

if __name__ == "__main__":
    available_package_managers = PackageManager.available_managers()

    print(available_package_managers)

    for package in packages:
        package_id, pm = PackageManager.choose_package_manager(
            package, available_package_managers
        )
        print(package_id, pm)

        if package_id and pm:
            pm.install(package_id)
