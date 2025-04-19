import React, { useEffect, useState } from 'react';
import {Container, Typography, Button, Box, Paper, Grid, TextField, Select, MenuItem, FormControl, InputLabel,
  CircularProgress, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import TestResults from './TestResults';
import JobHistory from './JobHistory';
import { fetchJobs, fetchClusters, fetchRecentExecutions, triggerJob, fetchTestResults } from '../api/api';
import { Execution, Job, Cluster } from '../types';

const Homepage = () => {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [selectedJob, setSelectedJob] = useState<string>('');
  const [parameters, setParameters] = useState<Record<string, string>>({});
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [loading, setLoading] = useState(true);
  const [triggerStatus, setTriggerStatus] = useState<{ success?: boolean; message?: string } | null>(null);
  const [triggeredExecution, setTriggeredExecution] = useState<Execution | null>(null);
  const [isJobLoading, setIsJobLoading] = useState(false);
  const [executionLoadingStates, setExecutionLoadingStates] = useState<{ [key: string]: boolean }>({});
  const [jobStats, setJobStats] = useState<null | { totalRuns: number; successRate: number; avgExecutionTime: number }>(null);
  const [selectedStatsJob, setSelectedStatsJob] = useState<string>('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const jobsData = await fetchJobs();
        setJobs(jobsData);

        const clustersData = await fetchClusters();
        setClusters(clustersData);

        const executionsData = await fetchRecentExecutions();
        setExecutions(executionsData);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleJobSelect = (jobName: string) => {
    setSelectedJob(jobName);
    const job = jobs.find(j => j.name === jobName);
    if (job) {
      setParameters(job.parameters);
    }
    setTriggerStatus(null);
  }


  const handleParameterChange = (paramName: string, value: string) => {
    setParameters(prev => ({
      ...prev,
      [paramName]: value
    }));
  };

  const formatStartTime = (startTime: string): string => {
    console.log('Start Time:', startTime);
    if (!startTime) {
      return 'Empty';  // Return a fallback string when startTime is invalid
    }

    const formattedTime = startTime.split('.')[0] + startTime.slice(-6);
    const date = new Date(formattedTime);

    // Check if the date is valid
    if (isNaN(date.getTime())) {
      return 'Invalid Date';  // Return a fallback string when the date is invalid
    }

    return date.toLocaleString();
  };

  const handleTriggerJob = async () => {
    setIsJobLoading(true);
    setTriggerStatus(null);
    try {
      const data = await triggerJob(selectedJob, parameters);
      if (data.success) {
        setTriggeredExecution({id: Date.now(),  jobName: selectedJob, status: 'QUEUED', buildNumber: data.data.queue_number.toString(),
        startTime: new Date().toISOString(),
        parameters: parameters
      });
        setTriggerStatus({ success: true, message: 'Job triggered successfully!' });
      } else {
        throw new Error(data.message || 'Failed to trigger job');
      }
    } catch (error) {
      console.error('Error triggering job:', error);
      setTriggerStatus({ success: false, message: error instanceof Error ? error.message : 'Error connecting to server' });
    } finally {
      setIsJobLoading(false);
    }
  };

  const handleCheckTestResults = async (buildNumber: string) => {
    setExecutionLoadingStates(prev => ({ ...prev, [buildNumber]: true }));
    try {
      const exec = executions.find(e => e.buildNumber === buildNumber);
      if (!exec) throw new Error("Execution not found");

      const data = await fetchTestResults(exec.jobName, Number(exec.buildNumber));
      if (data.success) {
        setTriggeredExecution(exec); // ✅ Store the whole execution
        setTriggerStatus({ success: true, message: 'Test results fetched successfully!' });
      } else {
        throw new Error(data.data.status || 'Failed to fetch test results');
      }
    } catch (error) {
      console.error('Error fetching test results:', error);
      setTriggerStatus({ success: false, message: error instanceof Error ? error.message : 'Error connecting to server' });
    } finally {
      setExecutionLoadingStates(prev => ({ ...prev, [buildNumber]: false }));
    }
  };


  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 4 }}>
      <Container maxWidth="lg">
        <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ mb: 4 }}>
          Jenkins Job Management
        </Typography>

        <Grid container spacing={4}>
          {/* Job Triggering Section */}
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Trigger Job
              </Typography>
              
              {triggerStatus && (
                <Alert 
                  severity={triggerStatus.success ? "success" : "error"} 
                  sx={{ mb: 2 }}
                >
                  {triggerStatus.message}
                </Alert>
              )}

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Select Job</InputLabel>
                <Select
                  value={selectedJob}
                  label="Select Job"
                  onChange={(e) => handleJobSelect(e.target.value)}
                >
                  {jobs.map((job) => (
                    <MenuItem key={job.name} value={job.name}>
                      {job.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {selectedJob && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Job Parameters:
                  </Typography>
                  {Object.entries(parameters).map(([key, value]) => (
                    key === 'source' || key === 'target' ? (
                      <FormControl key={key} fullWidth sx={{ mb: 1 }}>
                        <InputLabel>{key}</InputLabel>
                        <Select
                          value={value}
                          label={key}
                          onChange={(e) => handleParameterChange(key, e.target.value)}
                        >
                          {clusters.map((cluster) => (
                            <MenuItem key={cluster.id} value={cluster.name}>
                              {cluster.name} ({cluster.release_version})
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    ) : (
                      <TextField
                        key={key}
                        fullWidth
                        label={key}
                        value={value}
                        onChange={(e) => handleParameterChange(key, e.target.value)}
                        sx={{ mb: 1 }}
                      />
                    )
                  ))}
                </Box>
              )}

              <Button
                variant="contained"
                color="primary"
                fullWidth
                onClick={handleTriggerJob}
                disabled={!selectedJob || isJobLoading}
              >
                {isJobLoading ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  'Trigger Job'
                )}
              </Button>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <JobHistory />
          </Grid>
          {/* Execution Monitoring Section */}
          <Grid item xs={12}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Recent Executions
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Job Name</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Start Time</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {executions.map((execution) => (
                      <TableRow key={execution.id}>
                        <TableCell>{execution.jobName}</TableCell>
                        <TableCell>{execution.status}</TableCell>
                        <TableCell>{formatStartTime(execution.startTime)}</TableCell>
                        <TableCell>
                          <Button
                            variant="contained"
                            color="primary"
                            onClick={() => handleCheckTestResults(execution.buildNumber)}
                            disabled={executionLoadingStates[execution.buildNumber] || isJobLoading}
                          >
                            {executionLoadingStates[execution.buildNumber] ? (
                              <CircularProgress size={24} color="inherit" />
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
            </Paper>
          </Grid>

          {/* Render TestResults component for the selected job ID */}
          {triggeredExecution && (
            <Grid item xs={12}>
              <Paper elevation={3} sx={{ p: 3, mt: 4 }}>
                <Typography variant="h6" gutterBottom>
                  Test Results
                </Typography>
                <TestResults
                  jobType={triggeredExecution.jobName}
                  buildNumber={Number(triggeredExecution.buildNumber)}
                />
              </Paper>
            </Grid>
          )}
        </Grid>
      </Container>
    </Box>
  );
};

export default Homepage;
