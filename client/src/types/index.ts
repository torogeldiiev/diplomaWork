export interface TestCase {
  name: string;
  status: 'PASSED' | 'FAILED';
  duration: number;
  errorDetails?: string;
  errorStackTrace?: string;
}

export interface TestResultsProps {
  jobType: string;
  buildNumber: number;
}

export interface JobResult {
  success: boolean;
  data: {
    status: string;
    test_cases: TestCase[];
  };
}

export interface Execution {
  id: number;
  jobName: string;
  status: string;
  buildNumber: string;
  startTime: string;
  parameters: Record<string, string>;
}

export interface Job {
  id: string;
  name: string;
  parameters: Record<string, string>;
}

export interface Cluster {
  id: string;
  name: string;
  release_version: string;
}

export interface JobHistoryData {
  totalRuns: number;
  successRate: number;
  avgExecutionTime: number | null;
  executions: JobExecutionSummary[];
}


export interface JobExecutionSummary {
  id: number | string;
  startTime: string;
  status: string;
  totalTests: number;
  passed: number;
  failed: number;
  buildNumber: string | number;
}