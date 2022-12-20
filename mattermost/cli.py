"""Console script for mattermost."""

import click


@click.command()
def main():
    """Main entrypoint."""
    click.echo("mattermost-python-sdk")
    click.echo("=" * len("mattermost-python-sdk"))
    click.echo("Skeleton project created by Cookiecutter PyPackage")


if __name__ == "__main__":
    main()  # pragma: no cover
