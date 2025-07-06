import createrepo_c
from typing import Dict, List, Any

def parse_packages(packages: Dict[str, List[Any]], repos: List[str]) -> Dict[str, List[Any]]:
    for repo in repos:
        repo_url = 'https://repo1.red-soft.ru/redos/8.0/x86_64/' + repo + '/'
        repodata = createrepo_c.Metadata()
        repodata.locate_and_load_xml(repo_url)

        for key in repodata.keys():
            pkg = repodata.get(key)
            
            pkg_info = [
                pkg.requires,
                pkg.provides,
                pkg.obsoletes,
                pkg.conflicts,
                pkg.nevra(),
                pkg.version,
                pkg.release,
                pkg.url
            ]

            packages[pkg.name] = pkg_info

    return packages
