#!/usr/bin/python3

from argparse import ArgumentParser
from pathlib import Path
import subprocess
import git
import yaml
from jinja2 import Environment, FileSystemLoader

output_dir = Path.cwd() / 'output'
env = Environment(loader=FileSystemLoader('templates'))

parser = ArgumentParser()
parser.add_argument('-s', '--scheme', default='default-light',
                    help='use given scheme', metavar='SCHEME')
parser.add_argument('-l', '--list', action='store_true',
                    help='list available schemes')
parser.add_argument('-r', '--random', action='store_true',
                    help='set random Base16 scheme')
args = parser.parse_args()

schemes_list = Path('base16/schemes/list.yaml')
if not schemes_list.exists():
    try:
        print('Cloning base16 schemes...')
        git.Repo.clone_from('https://github.com/chriskempson/base16-schemes-source.git',
                            'base16/schemes')
    except git.GitCommandError as e:
        # already present
        pass

    with open("base16/schemes/list.yaml") as lst:
        schemes = yaml.safe_load(lst)

    for name, repo in schemes.items():
        try:
            print(f'Cloning {repo}...')
            git.Repo.clone_from(repo, f'base16/themes/{name}')
        except git.GitCommandError as e:
            # already present
            pass

schemes = []
for p in Path().glob('base16/themes/**/*.yaml'):
    schemes.append(p)

scheme = None
if args.list:
    stems = []
    for i in schemes:
        stems.append(i.stem)
    for i in sorted(stems):
        print(i)
else:
    if args.random:
        import random
        scheme_file = schemes[random.randint(0, len(schemes))]
        with open(scheme_file) as file:
            scheme = yaml.safe_load(file)
            print(f'Random Base16 pick: {scheme["scheme"]}')
    else:
        for f in schemes:
            if str(f).endswith('/' + args.scheme + '.yaml'):
                with open(f) as file:
                    scheme = yaml.safe_load(file)
                break
    if not scheme:
        print(f'No such scheme: {args.scheme}')
    else:
        template = env.get_template('css.j2')
        css = template.render(scheme=scheme)

        with open(f'{output_dir}/opr.css', 'w') as f:
            f.write(css)

        dest = Path(f'{output_dir}/reset.css')
        src = Path('static/reset.css')
        dest.write_text(src.read_text())

        print('Generating OPR...')
        subprocess.run([
            'pandoc',
            'content/header.yaml',
            'content/header.md',
            'content/content.md',
            'content/sidebar.md',
            '--standalone',
            '--css', 'reset.css',
            '--css', 'opr.css',
            '--from', 'markdown-auto_identifiers',
            '--output', f'{output_dir}/index.html',
            '--template', 'templates/template.html5'
        ], check=True)

        print('Verifying OPR...')
        subprocess.run([
            'tidy',
            '-quiet',
            '-errors',
            f'{output_dir}/index.html'
        ], check=True)

        if Path('/usr/bin/chromium').exists():
            chromium_binary = 'chromium'
        else:
            chromium_binary = 'chromium-browser'

        print('Generating PDF...')
        subprocess.run([
            chromium_binary,
            '--use-gl=swiftshader',
            '--headless',
            '--incognito',
            '--no-sandbox',
            '--print-to-pdf',
            f'file://{output_dir}/index.html'
        ], check=True, cwd=output_dir)
