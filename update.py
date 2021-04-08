#!/usr/bin/env python3
from dataclasses import dataclass, field
from os import path
from pathlib import Path
from typing import List, Tuple

from git import Repo
from git.refs.tag import Tag
import shutil

curDir = path.dirname(path.abspath(__file__))

repositoryUrl = 'https://github.com/python/cpython.git'
buildDir = path.sep.join([curDir, 'build', 'src'])
dockerfilesDir = path.sep.join([curDir, 'docker'])
buildDirPath = Path(buildDir)

if not path.exists(buildDir):
    print('Downloading Python repository...')
    buildDirPath.mkdir(parents=True, exist_ok=True)
    # 1. clone the Python git repository
    gitRepo = Repo.clone_from(url=repositoryUrl, to_path=buildDir)
else:
    # 1. set the Python git repository
    gitRepo = Repo(path=buildDir)

pythonMajor = 3
pythonMinMinor = 6


@dataclass
class PythonVersion:
    tag: str
    major: int
    minor: int
    patch: int
    rank: int = field(default=0)


gpgKeys = {
    '3': {
        # gpg: key AA65421D: public key "Ned Deily (Python release signing key) <nad@acm.org>" imported
        # https://www.python.org/dev/peps/pep-0494/#release-manager-and-crew
        '6': '0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D',
        # gpg: key AA65421D: public key "Ned Deily (Python release signing key) <nad@acm.org>" imported
        # https://www.python.org/dev/peps/pep-0537/#release-manager-and-crew
        '7': '0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D',
        # gpg: key B26995E310250568: public key "\xc5\x81ukasz Langa (GPG langa.pl) <lukasz@langa.pl>" imported
        # https://www.python.org/dev/peps/pep-0569/#release-manager-and-crew
        '8': 'E3FF2839C048B25C084DEBE9B26995E310250568',
        # gpg: key B26995E310250568: public key "\xc5\x81ukasz Langa (GPG langa.pl) <lukasz@langa.pl>" imported
        # https://www.python.org/dev/peps/pep-0596/#release-manager-and-crew
        '9': 'E3FF2839C048B25C084DEBE9B26995E310250568',
        # gpg: key 64E628F8D684696D: public key "Pablo Galindo Salgado <pablogsal@gmail.com>" imported
        # https://www.python.org/dev/peps/pep-0619/#release-manager-and-crew
        '10': 'A035C8C19219BA821ECEA86B64E628F8D684696D',
    },


}
pythonVersions = {}
tagsToProcess: List[str] = []

# Clean up destination folder
shutil.rmtree(path=dockerfilesDir, ignore_errors=True)

for tag in gitRepo.tags:
    tag: Tag = tag
    numbers = tag.name.split('.')
    if len(numbers) != 3:
        continue
    [major, minor, patch] = numbers
    major = major.replace(r'v', '')
    try:
        patch = int(patch)

        if int(major) == pythonMajor and int(minor) >= pythonMinMinor and int(patch):
            if major not in pythonVersions:
                pythonVersions[major] = {}

            current = pythonVersions[major][minor] if minor in pythonVersions[major] else None
            if current is None or current.patch < patch:
                pythonVersions[major][minor] = PythonVersion(
                    tag.name, major, minor, patch)
    except ValueError:
        pass

outputMatrix = []
with open(path.sep.join([curDir, 'Dockerfile.template']), 'r') as templateFile:
    template = templateFile.read()

    for major in pythonVersions.keys():
        for minor, version in pythonVersions[major].items():
            pythonVersion = version.tag
            gpgKey = gpgKeys[major][minor]
            outputMatrix.append(f'"{major}.{minor}.{version.patch}"')

            print(pythonVersion, gpgKey)

            destDir = path.sep.join([dockerfilesDir, pythonVersion])
            shutil.rmtree(path=destDir, ignore_errors=True)
            Path(destDir).mkdir(parents=True)

            dockerContent = template.replace(
                '{{PYTHON_VERSION}}', pythonVersion.replace('v', ''))
            dockerContent = dockerContent.replace('{{GPG_KEY}}', gpgKey)

            with open(path.sep.join([destDir, 'Dockerfile']), 'w') as dockerFile:
                dockerFile.write(dockerContent)

print(f'::set-output name=matrix::[{",".join(outputMatrix)}]')
