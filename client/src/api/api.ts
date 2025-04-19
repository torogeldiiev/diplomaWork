import { Execution, Job, Cluster, JobResult } from "../types";

export const fetchJobs = async (): Promise<Job[]> => {
  const response = await fetch('http://localhost:5000/api/jobs');
  if (!response.ok) {
    throw new Error("Failed to fetch jobs");
  }
  return response.json();
};

export const fetchClusters = async (): Promise<Cluster[]> => {
  const response = await fetch('http://localhost:5000/api/clusters');
  if (!response.ok) {
    throw new Error("Failed to fetch clusters");
  }
  return response.json();
};

export const fetchRecentExecutions = async (): Promise<Execution[]> => {
  const response = await fetch("http://localhost:5000/api/executions/recent");
  if (!response.ok) {
    throw new Error("Failed to fetch recent executions");
  }
  return response.json();
};

export const triggerJob = async (jobType: string, parameters: Record<string, string>) => {
  const response = await fetch('http://localhost:5000/api/jenkins/trigger', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      job_type: jobType,
      parameters: parameters
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

export const fetchTestResults = async (jobType: string, buildNumber: number) => {
  const response = await fetch(`http://localhost:5000/api/jenkins/job-results/${jobType}/${buildNumber}`);
  if (!response.ok) {
    throw new Error("Failed to fetch test results");
  }
  return response.json();
};


export const fetchJobHistory = async (jobId: string, days: number) => {
  const response = await fetch(`http://localhost:5000/api/job-history?jobId=${jobId}&days=${days}`);
  if (!response.ok) {
    throw new Error('Failed to fetch job history');
  }

  const data = await response.json();
  if (!data.success) {
    throw new Error(data.message || 'Unknown error');
  }

  return data.data;
};


