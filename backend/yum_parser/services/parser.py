import createrepo_c

def parse_packages(packages, repos):
    for repo in repos:
        repo_url = 'https://repo1.red-soft.ru/redos/8.0/x86_64/' + repo + '/'
        repodata = createrepo_c.Metadata()
        repodata.locate_and_load_xml(repo_url)

        for key in repodata.keys():
            pkg = repodata.get(key)

            if pkg.name in packages.keys():
                continue
            
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

        del repodata

    return packages
