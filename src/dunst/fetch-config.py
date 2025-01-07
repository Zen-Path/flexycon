import requests
from bs4 import BeautifulSoup
import re


def fetch_webpage(url):
    """Fetches the webpage content."""
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def infer_type(values, default_value, format_value):
    """Infers the type of the option based on its values, default, and format."""
    if values:
        return f"option({', '.join(map(lambda x: f"'{x}'", values))})"
    if default_value in ["true", "false"]:
        return f"boolean(default={default_value})"
    if default_value and default_value.isdigit():
        return f"integer(default={default_value})"
    if format_value:
        return f"format({format_value})"
    return "string"


def parse_documentation(html_content):
    """Parses the HTML content of the documentation to extract options."""
    soup = BeautifulSoup(html_content, "html.parser")
    configspec = {}
    spec_details = []

    # Locate the first <dl> element which contains options
    dl_element = soup.find("dl")

    if dl_element:
        # Find all direct child <dt> and <dd> pairs within the <dl>
        dt_elements = dl_element.find_all("dt", recursive=False)
        dd_elements = dl_element.find_all("dd", recursive=False)

        for dt, dd in zip(dt_elements, dd_elements):
            # Extract the NAME of the option (within <b>)
            option_name_tag = dt.find("b")
            option_name = (
                option_name_tag.get_text(strip=True) if option_name_tag else None
            )

            # Extract the BRIEF (everything after the name)
            brief = (
                dt.get_text(strip=True).replace(option_name, "", 1).strip()
                if option_name
                else ""
            )

            # Extract DEFAULT, VALUES, and FORMAT from BRIEF
            default_match = re.search(r"default: ([^,\)]+)", brief)
            values_match = re.search(r"values: \[([^\]]+)\]", brief)
            format_match = re.search(r"format: \(([^\)]+)\)", brief)

            default_value = default_match.group(1) if default_match else None
            values_list = values_match.group(1).split("/") if values_match else []
            format_value = format_match.group(1) if format_match else None

            # Extract DESC (from <dd>)
            description = dd.get_text(strip=True, separator=" ")

            # Determine the type dynamically
            option_type = infer_type(values_list, default_value, format_value)

            # Build configspec and spec details
            if option_name:
                configspec.setdefault("global", {})[option_name] = option_type

                spec_details.append(
                    {
                        "option": option_name,
                        "default": default_value,
                        "values": values_list,
                        "format": format_value,
                        "description": description,
                    }
                )

    return configspec, spec_details


def set_option(group, key, value, comments):
    """Helper function to simulate setting a configuration option."""
    print(f"Setting option: [{group}] {key} = {value}")
    print("Comments:")
    for comment in comments:
        print(f"  {comment}")


def main():
    url = "https://dunst-project.org/documentation/"
    print(f"Fetching webpage: {url}")

    try:
        html_content = fetch_webpage(url)
        configspec, spec_details = parse_documentation(html_content)

        # Write configspec
        print("\nConfigspec:")
        print(configspec)

        # Write spec details
        print("\nSpec Details:")
        for detail in spec_details:
            print(
                f"""set_option(
'global',
"{detail["option"]}",
"{detail["default"] if detail["default"] else "None"}",
{[
    detail["description"]
]}
)"""
            )

    except requests.exceptions.RequestException as e:
        print(f"Error fetching webpage: {e}")


if __name__ == "__main__":
    main()
