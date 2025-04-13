import React, { useEffect, useState } from 'react';
import {
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Box,
} from '@mui/material';

interface TestCase {
  name: string;
  status: 'PASSED' | 'FAILED';
  duration: number;
  errorDetails?: string;
  errorStackTrace?: string;
}

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
        const response = await fetch(`http://localhost:5000/api/jenkins/job-results/${jobId}`);
        const data = await response.json();
        if (data.success) {
          setResults(data.data.test_cases);
          if (data.data.test_cases.length > 0 || data.data.status !== 'RUNNING') {
            clearInterval(interval);
          }
        } else {
          setError(data.message);
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
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Typography color="error">{error}</Typography>
    );
  }

  return (
    <Box>
      {!error && results.length > 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Test Name</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell>Details</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {results.map((test, index) => (
                <TableRow key={index}>
                  <TableCell>{test.name}</TableCell>
                  <TableCell>
                    <Chip 
                      label={test.status}
                      color={test.status === 'PASSED' ? 'success' : 'error'}
                    />
                  </TableCell>
                  <TableCell>{test.duration}s</TableCell>
                  <TableCell>
                    {test.errorDetails && (
                      <Typography color="error" variant="body2">
                        {test.errorDetails}
                      </Typography>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
      {!error && results.length === 0 && !loading && (
        <Typography>No test results available yet. Tests might still be running.</Typography>
      )}
    </Box>
  );
};

export default TestResults; 