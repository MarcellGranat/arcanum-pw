from src.__main__ import download_archive


def main() -> None:
    landing_url = input("Enter the Arcanum collection landing page URL: ").strip()
    download_archive(landing_url)

if __name__ == "__main__":
    main()
