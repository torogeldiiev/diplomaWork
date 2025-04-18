export interface TestCase {
  name: string;
  status: 'PASSED' | 'FAILED';
  duration: number;
  errorDetails?: string;
  errorStackTrace?: string;
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