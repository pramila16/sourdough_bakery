import click
import os
import yaml
from pathlib import Path
from autoremediate.autoremediateflow.AutoFix.AutoFix import AutoFix
@click.command()
@click.option('--project-root', default='.', help='Path to the project root')
@click.option('--disable-telemetry', is_flag=True, help='Disable telemetry')
@click.option('--sarif-file-path', help='Override default SARIF path')
@click.argument('paths', nargs=-1)
def main(project_root, disable_telemetry, sarif_file_path, paths):
    """CLI that uses ONLY default.yml for credentials"""
    if project_root:
        os.chdir(project_root)

    config = {}
    defaults_path = Path(__file__).parent / "defaults.yml"
    if defaults_path.exists():
        with open(defaults_path) as f:
            config = yaml.safe_load(f) or {}

    inputs = {
        'project_root': project_root,
        '__disable_telemetry': disable_telemetry,
        'sarif_file_path': sarif_file_path,
        'paths': list(paths),
        **config
    }

    try:
        AutoFix(inputs=inputs).run()
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    main()