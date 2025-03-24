import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Button,
  Box,
  Paper,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';

interface Job {
  id: string;
  name: string;
  parameters: Record<string, string>;
}

interface Execution {
  id: string;
  jobName: string;
  status: string;
  startTime: string;
  endTime?: string;
}

interface Cluster {
  id: number;
  name: string;
  release_version: string;
}

const Homepage = () => {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [selectedJob, setSelectedJob] = useState<string>('');
  const [parameters, setParameters] = useState<Record<string, string>>({});
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [loading, setLoading] = useState(true);
  const [triggerStatus, setTriggerStatus] = useState<{ success?: boolean; message?: string } | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch jobs
        const jobsResponse = await fetch('http://localhost:5000/api/jobs');
        const jobsData = await jobsResponse.json();
        setJobs(jobsData);

        // Fetch clusters
        const clustersResponse = await fetch('http://localhost:5000/api/clusters');
        const clustersData = await clustersResponse.json();
        setClusters(clustersData);

        // Fetch executions
        const executionsResponse = await fetch('http://localhost:5000/api/executions');
        const executionsData = await executionsResponse.json();
        setExecutions(executionsData);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleJobSelect = (jobId: string) => {
    setSelectedJob(jobId);
    const job = jobs.find(j => j.id === jobId);
    if (job) {
      setParameters(job.parameters);
    }
    setTriggerStatus(null);
  };

  const handleParameterChange = (paramName: string, value: string) => {
    setParameters(prev => ({
      ...prev,
      [paramName]: value
    }));
  };

  const handleTriggerJob = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/jenkins/trigger', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_type: selectedJob,
          parameters: parameters
        }),
      });
      
      if (response.ok) {
        setTriggerStatus({ success: true, message: 'Job triggered successfully!' });
        // Refresh executions after triggering
        const executionsResponse = await fetch('http://localhost:5000/api/executions');
        const executionsData = await executionsResponse.json();
        setExecutions(executionsData);
      } else {
        setTriggerStatus({ success: false, message: 'Failed to trigger job' });
      }
    } catch (error) {
      console.error('Error triggering job:', error);
      setTriggerStatus({ success: false, message: 'Error triggering job' });
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
                    <MenuItem key={job.id} value={job.id}>
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
                disabled={!selectedJob}
              >
                Trigger Job
              </Button>
            </Paper>
          </Grid>

          {/* Job Parameters Section */}
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Job Parameters
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Job Name</TableCell>
                      <TableCell>Parameters</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {jobs.map((job) => (
                      <TableRow key={job.id}>
                        <TableCell>{job.name}</TableCell>
                        <TableCell>
                          {Object.keys(job.parameters).join(', ')}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
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
                      <TableCell>End Time</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {executions.map((execution) => (
                      <TableRow key={execution.id}>
                        <TableCell>{execution.jobName}</TableCell>
                        <TableCell>{execution.status}</TableCell>
                        <TableCell>{new Date(execution.startTime).toLocaleString()}</TableCell>
                        <TableCell>
                          {execution.endTime
                            ? new Date(execution.endTime).toLocaleString()
                            : 'In Progress'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Homepage;
