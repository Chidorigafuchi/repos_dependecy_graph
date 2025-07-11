import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export async function getAvailabelRepos() {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/available_repos/`);
    return response.data
  }
  catch (error){
    return []
  }
}

export async function fetchGraphApi(packageName, repoList) {
  if (!packageName || repoList.length === 0) return null;

  try {
    const response = await axios.post(`${API_BASE_URL}/api/package/`, {
      name: packageName,
      repos: repoList
    }, 
    {
      withCredentials: true
    });
    return response.data;
  } 
  catch (error) {
    return {}
  }
}

export async function trackPackageApi(packageName, repoList) {
  if (!packageName || repoList.length === 0) return null;

  try {
    const response = await axios.post(`${API_BASE_URL}/api/track_package/`, {
      name: packageName,
      repos: repoList
    }, 
    {
      withCredentials: true
    });
    return response.data;
  } 
  catch (error) {
    return {};
  }
}

export async function fetchPackageInfoApi(packageId) {
  if (!packageId) return null;

  try {
    const response = await axios.get(`${API_BASE_URL}/api/package_info/`, {
      params: { name: packageId }, 
      withCredentials: true
    });
    return response.data;
  } 
  catch (error) {
    return null
  }
}

export async function fetchTrackedPackagesApi() {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/tracked_packages_list/`, {
      withCredentials: true
    });
    return response.data;
  } 
  catch (error) {
    return [];
  }
}

export async function deleteRepoGroupApi(packageName, repoList) {
  if (!packageName || !Array.isArray(repoList) || repoList.length === 0) return null;

  try {
    const response = await axios.delete(`${API_BASE_URL}/api/tracked_packages_list/`, {
      data: {
        package: packageName,
        repos: repoList
      },
      withCredentials: true
    });
    return response.data;
  } 
  catch (error) {
    return null;
  }
}

export async function fetchPackageVersionsApi(packageName, repos) {
  if (!packageName || !Array.isArray(repos) || repos.length === 0) return null;

  try {
    const response = await axios.get(`${API_BASE_URL}/api/version_diff/`, {
      params: {
        name: packageName,
        repos: repos
      },
      withCredentials: true
    });
    return response.data;
  } catch (error) {
    return null;
  }
}

export async function fetchVersionDiffApi(packageName, repos, nevra) {
  if (!packageName || !nevra || !Array.isArray(repos) || repos.length === 0) return null;

  try {
    const response = await axios.post(`${API_BASE_URL}/api/version_diff/`, {
      name: packageName,
      repos: repos,
      nevra: nevra
    }, 
    {
      withCredentials: true
    });
    return response.data;
  } 
  catch (error) {
    return null;
  }
}