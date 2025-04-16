import { Execution, JobResult } from "../types";

export const fetchTestResults = async (jobId: string): Promise<JobResult> => {
  const response = await fetch(`http://localhost:5000/api/jenkins/job-results/${jobId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch test results");
  }
  return response.json();
};

export const fetchRecentExecutions = async (): Promise<Execution[]> => {
  const response = await fetch("http://localhost:5000/api/executions/recent");
  if (!response.ok) {
    throw new Error("Failed to fetch recent executions");
  }

  const data: Execution[] = await response.json();
  return data;
};
