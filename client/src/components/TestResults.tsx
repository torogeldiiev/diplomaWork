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
      try {
        const data: JobResult = await fetchTestResults(jobType, buildNumber);
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
