import React, { useEffect, useState } from 'react';
import { Box, Typography } from '@mui/material';
import TestResultTable from './TestResultTable';
import LoadingIndicator from './LoadingIndicator';
import ErrorDisplay from './ErrorDisplay';
import { fetchTestResults } from '../api/api';
import { JobResult, TestCase, TestResultsProps } from '../types';

const TestResults: React.FC<TestResultsProps> = ({ jobType, buildNumber }) => {
  const [results, setResults] = useState<TestCase[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
  const fetchResults = async () => {
    setLoading(true);
    try {
      const res: any = await fetchTestResults(buildNumber);
      console.log("raw job-results payload:", res);
      if (!res.success) {
        setError(res.message ?? "Unknown error");
        setResults([]);
        return;
      }
      const list: TestCase[] = Array.isArray(res.data)
        ? res.data
        : Array.isArray(res.data?.test_cases)
          ? res.data.test_cases
          : [];

      setResults(list);
      setError(null);
    } catch (err) {
      setError("Failed to fetch test results");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  fetchResults();
  const iv = setInterval(fetchResults, 30_000);
  return () => clearInterval(iv);
}, [jobType, buildNumber]);


  if (loading) return <LoadingIndicator />;
  if (error) return <ErrorDisplay message={error} />;

  return (
    <Box>
      {results.length > 0 ? (
        <TestResultTable results={results} />
      ) : (
        <Typography>No test results available yet. Tests might still be running.</Typography>
      )}
    </Box>
  );
};

export default TestResults;
