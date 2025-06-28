import createrepo_c


#Парсим нужную информацию о пакетах из определеннго репозитория (по выбору(добавить))
def parse_packages():
    packages = {}
    repo = 'os'
    repo_url = 'https://repo1.red-soft.ru/redos/8.0/x86_64/' + repo + '/'
    repodata = createrepo_c.Metadata()
    repodata.locate_and_load_xml(repo_url)

    for key in repodata.keys():
        pkg = repodata.get(key)

        pkg_info = [
            pkg.requires,
            pkg.provides,
            pkg.nevra(),
            pkg.version,
            pkg.release,
            pkg.url
        ]
        packages[pkg.name] = pkg_info

    return packages
