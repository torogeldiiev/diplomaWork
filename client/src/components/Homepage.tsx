import React, { useEffect, useState } from 'react';
import {Container, Typography, Box, Paper, Grid, CircularProgress
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import TestResults from './TestResults';
import JobHistory from './JobHistory';
import JobTrigger from './JobTrigger';
import RecentExecutions from './RecentExecutions';
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
            <JobTrigger onJobTriggered={exec => setTriggeredExecution(exec)} />
          </Grid>
          <Grid item xs={12} md={6}>
            <JobHistory />
          </Grid>
          {/* Execution Monitoring Section */}
          <Grid item xs={12}>
            <RecentExecutions onSelectExecution={exec => setTriggeredExecution(exec)} />
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
