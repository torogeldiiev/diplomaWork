// components/TestResults.tsx
import React, { useEffect, useState } from 'react';
import { Box, Typography } from '@mui/material';
import TestResultTable from './TestResultTable';
import LoadingIndicator from './LoadingIndicator';
import ErrorDisplay from './ErrorDisplay';
import { fetchTestResults } from '../api/api';
import { JobResult, TestCase } from '../types';

interface TestResultsProps {
  jobId: string;
}

const TestResults: React.FC<TestResultsProps> = ({ jobId }) => {
  const [results, setResults] = useState<TestCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const data: JobResult = await fetchTestResults(jobId);
        if (data.success) {
          setResults(data.data.test_cases);
        } else {
          setError(data.data.status);
        }
      } catch (err) {
        setError('Failed to fetch test results');
      } finally {
        setLoading(false);
      }
    };

    fetchResults();

    const interval = setInterval(fetchResults, 30000);
    return () => clearInterval(interval);
  }, [jobId]);

  if (loading) {
    return <LoadingIndicator />;
  }

  if (error) {
    return <ErrorDisplay message={error} />;
  }

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
