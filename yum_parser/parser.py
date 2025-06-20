import createrepo_c


def parse_package(pkg_name):
    repo = 'os'
    repo_url = 'https://repo1.red-soft.ru/redos/8.0/x86_64/' + repo + '/'
    repodata = createrepo_c.Metadata()
    repodata.locate_and_load_xml(repo_url)

    info = {
    'name': 'unk',
    'nevra': 'unk',
    'version': 'unk',
    'release': 'unk',
    'url': 'unk',
    }

    for key in repodata.keys():
        pkg = repodata.get(key)

        if (pkg.name == pkg_name):
            info = {
                'name': pkg_name,
                'nevra': pkg.nevra(),
                'version': pkg.version,
                'release': pkg.release,
                'url': pkg.url,
            }
            print(pkg.name)
            print(pkg.nevra())
            print(pkg.version)
            print(pkg.release)
            print(pkg.url)
            return info
       
    return info

    