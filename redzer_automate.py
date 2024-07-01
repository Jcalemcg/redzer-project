import shutil
import os
import subprocess
import logging
import yaml
import argparse
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration
def load_config(config_file):
    if not os.path.exists(config_file):
        logging.error(f'Configuration file not found: {config_file}')
        exit(1)
    
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

# Helper functions
def write_file(filepath, content):
    with open(filepath, 'w') as file:
        file.write(content)
    logging.info(f'Created {filepath}')

def read_file(filepath):
    with open(filepath, 'r') as file:
        return file.read()

def run_command(command, env=None):
    try:
        result = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        logging.info(f'Command succeeded: {command}')
        logging.info(result.stdout.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        logging.error(f'Command failed: {command}')
        logging.error(e.stderr.decode('utf-8'))

# Create necessary directories
def create_directories(project_dir, template_dir):
    if project_dir.exists():
        logging.info(f'Removing existing project directory: {project_dir}')
        shutil.rmtree(project_dir)

    project_dir.mkdir(parents=True)
    (project_dir / 'modules').mkdir()
    (project_dir / 'services').mkdir()
    (project_dir / 'caching').mkdir()
    (project_dir / 'tests').mkdir()
    (project_dir / 'templates').mkdir()
    logging.info('Created project directory structure')

    # Create template files
    setup_content = '''\
from setuptools import setup, find_packages

setup(
    name='Redzer',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'python-nmap',
        'pytest',
        'numpy',
        'scikit-learn',
        'scapy',
        'tkinter',
        'PyQt5',
        'metasploit-py',
        'johnny',
    ],
    entry_points={{
        'console_scripts': [
            'redzer-cli = cli:main',
        ],
    }},
    description='A Red Teaming Automation Tool',
    long_description="""Redzer is a Python-based tool designed to automate various tasks commonly used during Red Team engagements. 
    It provides functionalities for network scanning, vulnerability assessment, exploitation, and post-exploitation activities. 
    This tool is intended for educational purposes and penetration testing professionals. 
    Use it responsibly and ethically.""",
    long_description_content_type="text/markdown",
    author='Your Name',
    author_email='youremail@example.com',
    url='https://github.com/yourusername/redzer',
    license='MIT',
    keywords='redteam security automation pentest',
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Security Professionals',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Security :: Penetration Testing',
    ],
)
'''
    redzer_spec_content = '''\
# redzer.spec
block_cipher = None

a = Analysis(['cli.py'],
       pathex=['.'],
       binaries=[],
       datas=[('config.yaml', '.')],
       hiddenimports=[],
       hookspath=[],
       runtime_hooks=[],
       excludes=[],
       winnoexcludes=[],
       cipher=block_cipher,
       noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
       cipher=block_cipher)
exe = EXE(pyz,
     a.scripts,
     a.binaries,
     a.zipfiles,
     a.datas,
     [],
     name='redzer',
     debug=False,
     bootloader_ignore_signals=False,
     strip=False,
     upx=True,
     upx_exclude=[],
     runtime_tmpdir=None,
     console=True, icon='icon.ico')
coll = COLLECT(exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None)
'''
    redzer_installer_content = '''\
; redzer_installer.iss
[Setup]
AppName=Redzer
AppVersion=0.1
DefaultDirName={pf}\\Redzer
DefaultGroupName=Redzer
OutputBaseFilename=redzer_installer
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
Source: "dist\\redzer.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.yaml"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\Redzer"; Filename: "{app}\\redzer.exe"
Name: "{commondesktop}\\Redzer"; Filename: "{app}\\redzer.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\\redzer.exe"; Description: "{cm:LaunchProgram,Redzer}"; Flags: nowait postinstall skipifsilent
'''

    template_files = {
        template_dir / 'setup_template.py': setup_content,
        template_dir / 'redzer_template.spec': redzer_spec_content,
        template_dir / 'redzer_installer_template.iss': redzer_installer_content
    }

    for path, content in template_files.items():
        write_file(path, content)

# Initialize and run the automation script
def initialize_project(config):
    project_name = config['project_name']
    project_dir = Path(config['project_dir']) / project_name
    template_dir = project_dir / 'templates'
    venv_dir = project_dir / config['venv_dir']

    logging.info('Initializing project...')
    create_directories(project_dir, template_dir)

    # Write setup.py
    setup_path = project_dir / 'setup.py'
    setup_content = read_file(template_dir / 'setup_template.py')
    write_file(setup_path, setup_content)

    # Write PyInstaller spec file
    spec_path = project_dir / 'redzer.spec'
    spec_content = read_file(template_dir / 'redzer_template.spec')
    write_file(spec_path, spec_content)

    # Write Inno Setup script
    inno_setup_path = project_dir / 'redzer_installer.iss'
    inno_setup_content = read_file(template_dir / 'redzer_installer_template.iss')
    write_file(inno_setup_path, inno_setup_content)

    # Create virtual environment
    run_command(f'python -m venv {venv_dir}')

    # Activate virtual environment and install requirements
    activate_env = f'{venv_dir / "Scripts" / "activate"}'
    pip_install = f'{venv_dir / "Scripts" / "pip"} install -r {project_dir / config["requirements_file"]}'
    pyinstaller_install = f'{venv_dir / "Scripts" / "pip"} install pyinstaller'
    env = os.environ.copy()
    env['VIRTUAL_ENV'] = str(venv_dir)
    env['PATH'] = f'{venv_dir / "Scripts"};{env["PATH"]}'
    
    run_command(f'{activate_env} && {pip_install}', env=env)
    run_command(f'{activate_env} && {pyinstaller_install}', env=env)

    # Package with PyInstaller
    run_command(f'{venv_dir / "Scripts" / "pyinstaller"} {spec_path}', env=env)

    # Create installer with Inno Setup
    run_command(f'ISCC {inno_setup_path}')

    logging.info('Project initialization complete')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Automate Redzer setup, packaging, and distribution.')
    parser.add_argument('config_file', nargs='?', default='config.yaml', help='Path to the configuration file (default: config.yaml)')
    args = parser.parse_args()

    config = load_config(args.config_fileTo ensure that your `redzer_automate.py` script runs successfully, follow these steps:
