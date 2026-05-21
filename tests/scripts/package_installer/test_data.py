from scripts.package_installer.data.packages import packages


def test_packages_are_sorted_by_identifier():
    actual_identifiers = [str(pkg.name).split("/")[-1].lower() for pkg in packages]
    expected_identifiers = sorted(actual_identifiers)

    assert actual_identifiers == expected_identifiers, (
        "The packages list is not sorted alphabetically by identifier!"
    )
