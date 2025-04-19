import React, { useEffect, useState } from 'react';
import {
  Paper,
  Typography,
  CircularProgress,
  Box,
  FormControl,
  Select,
  MenuItem,
  InputLabel,
  Alert,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  TableContainer,
  Button,
} from '@mui/material';
import { fetchJobHistory, fetchJobs, fetchTestResults } from '../api/api';
import { Job, JobHistoryData } from '../types';

const JobHistory = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState('');
  const [selectedDays, setSelectedDays] = useState(7); // Default to last 7 days
  const [history, setHistory] = useState<JobHistoryData | null>(null);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [executionLoadingStates, setExecutionLoadingStates] = useState<{ [key: string]: boolean }>({});

  useEffect(() => {
    const loadJobs = async () => {
      try {
        const jobList = await fetchJobs();
        setJobs(jobList);
      } catch (err) {
        console.error('Failed to load jobs:', err);
      } finally {
        setInitialLoading(false);
      }
    };

    loadJobs();
  }, []);

  const handleLoadHistory = async (jobId: string, days: number) => {
    setLoading(true);
    setHistory(null);
    try {
      const data = await fetchJobHistory(jobId, days);
      setHistory(data);
    } catch (error) {
      console.error('Error fetching job history:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckResults = async (executionId: string) => {
    setExecutionLoadingStates(prev => ({ ...prev, [executionId]: true }));
    try {
      console.log('Button clicked for execution:', executionId);
      const exec = history?.executions.find(e => e.id.toString() === executionId);
      if (!exec) return;

      const data = await fetchTestResults(selectedJob, Number(exec.buildNumber)); // ✅ Store result
      console.log('Test results:', data);

    // You can redirect, show modal, or pass `data.data.test_cases` to a TestResult component
    } catch (error) {
      console.error('Failed to fetch test results', error);
    } finally {
      setExecutionLoadingStates(prev => ({ ...prev, [executionId]: false }));
    }
  };


  useEffect(() => {
    if (selectedJob) {
      handleLoadHistory(selectedJob, selectedDays);
    }
  }, [selectedJob, selectedDays]);

  if (initialLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Job History
      </Typography>

      <Box display="flex" gap={2} mb={2}>
        <FormControl fullWidth>
          <InputLabel>Select Job</InputLabel>
          <Select
            value={selectedJob}
            label="Select Job"
            onChange={(e) => setSelectedJob(e.target.value)}
          >
            {jobs.map((job) => (
              <MenuItem key={job.name} value={job.name}>
                {job.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>Days</InputLabel>
          <Select
            value={selectedDays}
            label="Days"
            onChange={(e) => setSelectedDays(Number(e.target.value))}
          >
            {[1, 3, 7, 14, 30].map(days => (
              <MenuItem key={days} value={days}>
                Last {days} day{days > 1 ? 's' : ''}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {loading && (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="80px">
          <CircularProgress />
        </Box>
      )}

      {!loading && selectedJob && !history && (
        <Alert severity="info">No statistics available for this job in the selected period.</Alert>
      )}

      {!loading && history && (
        <>
          <Box mb={2}>
            <Typography>Total Runs: {history.totalRuns}</Typography>
            {history.successRate !== null && (
              <Typography>Success Rate: {history.successRate.toFixed(2)}%</Typography>
            )}
            {history.avgExecutionTime !== null ? (
              <Typography>Average Execution Time: {history.avgExecutionTime.toFixed(2)} seconds</Typography>
            ) : (
              <Typography>Average Execution Time: N/A</Typography>
            )}
          </Box>

          <Typography variant="subtitle1" gutterBottom>
            Executions:
          </Typography>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Start Time</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Total Tests</TableCell>
                  <TableCell>Passed</TableCell>
                  <TableCell>Failed</TableCell>
                  <TableCell>Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {history.executions.map((exec) => (
                  <TableRow key={exec.id}>
                    <TableCell>{new Date(exec.startTime).toLocaleString()}</TableCell>
                    <TableCell>{exec.status}</TableCell>
                    <TableCell>{exec.totalTests}</TableCell>
                    <TableCell>{exec.passed}</TableCell>
                    <TableCell>{exec.failed}</TableCell>
                    <TableCell>
                      <Button
                        variant="outlined"
                        onClick={() => handleCheckResults(exec.id.toString())}
                        disabled={executionLoadingStates[exec.id.toString()]}
                      >
                        {executionLoadingStates[exec.id.toString()] ? (
                          <CircularProgress size={16} color="inherit" />
                        ) : (
                          'Check Test Results'
                        )}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </>
      )}
    </Paper>
  );
};

export default JobHistory;
