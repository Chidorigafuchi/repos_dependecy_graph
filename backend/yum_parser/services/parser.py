import createrepo_c
from typing import Dict, List, Any
from pickle import dumps, loads
from zlib import compress, decompress
from repos_dependency_graph.services.redis import redis_cache


def parse_packages():
    repos = ['os', 'updates', 'debuginfo', 'kernel-rt', 'kernel-testing']
    repos_packages_dependencies = {}
    repos_packages_info = {}

    length = 0
    
    for repo in repos:
        repo_url = 'https://repo1.red-soft.ru/redos/8.0/x86_64/' + repo + '/'
        repodata = createrepo_c.Metadata()
        repodata.locate_and_load_xml(repo_url)
        
        packages_dependencies = {}
        packages_info = {}

        for key in repodata.keys():
            pkg = repodata.get(key)

            pkg_dependencies = {
                'requires': pkg.requires,
                'provides': pkg.provides,
            }
        
            pkg_info = {
                'obsoletes': get_names(pkg.obsoletes),
                'conflicts': get_names(pkg.conflicts),
                'nevra': pkg.nevra(),
                'version': pkg.version,
                'release': pkg.release,
                'url': pkg.url
            }
            
            # new_package_name = pkg.name + '_' + repo
            new_package_name = pkg.name

            packages_dependencies[new_package_name] = pkg_dependencies
            packages_info[new_package_name] = pkg_info

        repos_packages_dependencies[repo] = packages_dependencies
        repos_packages_info.update(packages_info)

    compressed_dependencies = compress(dumps(repos_packages_dependencies))
    compressed_info = compress(dumps(repos_packages_info))

    redis_cache.set('repos_dependencies:compressed', compressed_dependencies, ex=60 * 60 * 24)
    redis_cache.set('repos_info:compressed', compressed_info, ex=60 * 60 * 24)
    
def repos_union(repos: List[str]) -> Dict[str, List[Any]]:
    cached_packages_data = redis_cache.get('repos_dependencies:compressed')
    packages = {}
    repos_packages = {}

    if cached_packages_data:
        decompressed_data = decompress(cached_packages_data)
        repos_packages = loads(decompressed_data)
    else:
        parse_packages()
        decompressed_data = decompress(redis_cache.get('repos_dependencies:compressed'))
        repos_packages = loads(decompressed_data)

    for repo in repos:
        packages.update(repos_packages[repo])

    return packages

def get_names(dependecies: List[List[str]]) -> List[str]:
    if dependecies:
        dependecies = list(zip(*dependecies))[0]
    return dependecies