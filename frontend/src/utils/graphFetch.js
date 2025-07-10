import { fetchGraphApi } from './requestApi';

export async function fetchGraph({ packageName, selectedRepos, setMessage, setIsLoading }) {
  if (!packageName || selectedRepos.length === 0) return;

  setMessage('');
  setIsLoading(true);

  const data = await fetchGraphApi(packageName, selectedRepos);
  setIsLoading(false);

  return data;
}

export async function showGraphFromTracked({ pkg, repos, repoSource, setPackageName, setSelectedRepos, fetchGraph }) {
  setPackageName(pkg);

  const selected = repos.map(r => {
    if (typeof r === 'string') {
      for (const [baseUrl, repoNames] of Object.entries(repoSource)) {
        if (r.startsWith(baseUrl)) {
          const repoName = r.slice(baseUrl.length).replace(/\/$/, '');
          if (repoNames.includes(repoName)) {
            return {
              name: repoName,
              full: r,
              base_url: baseUrl,
            };
          }
        }
      }
      return null;
    }
    return r;
  }).filter(Boolean);

  setSelectedRepos(selected);
  await fetchGraph();
}

export function transformRepoList(repoList) {
  const repoSource = {};

  repoList.forEach(fullRepoPath => {
    const trimmedPath = fullRepoPath.endsWith('/') && fullRepoPath.length > 1
      ? fullRepoPath.slice(0, -1)
      : fullRepoPath;

    const lastSlashIndex = trimmedPath.lastIndexOf('/');
    const baseUrl = trimmedPath.slice(0, lastSlashIndex + 1);
    const repoName = trimmedPath.slice(lastSlashIndex + 1);

    if (!repoSource[baseUrl]) {
      repoSource[baseUrl] = [];
    }
    repoSource[baseUrl].push(repoName);
  });

  return repoSource;
}