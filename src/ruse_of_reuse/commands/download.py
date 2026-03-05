
def add_parser(subparsers):
    parser = subparsers.add_parser(
        "download",
        help="Download required hackathon data.",
    )

    parser.set_defaults(func=run_download)


def run_download(args):
    from ruse_of_reuse.utils import download_data

    download_data()

    print("Done.")
    return 0
