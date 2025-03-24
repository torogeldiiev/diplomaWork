import React, { useState } from 'react';
import {
  Container,
  Typography,
  Button,
  Box,
  Paper,
  Grid,
  CircularProgress
} from '@mui/material';

const Dashboard = () => {
  const [executionData, setExecutionData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleJobTrigger = async (jobType: string) => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/jenkins/trigger', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_type: jobType,
          parameters: {}, // Add job parameters if needed
        }),
      });
      const data = await response.json();
      setExecutionData(data);
    } catch (error) {
      console.error('Error triggering job:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Job Trigger Dashboard
        </Typography>
        <Typography variant="body1" sx={{ mb: 3 }}>
          Choose a job to trigger:
        </Typography>

        <Grid container spacing={2} sx={{ mb: 4 }}>
          <Grid item>
            <Button
              variant="contained"
              onClick={() => handleJobTrigger('Config Diff')}
              disabled={isLoading}
              sx={{ minWidth: 200 }}
            >
              {isLoading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                'Trigger Config Diff'
              )}
            </Button>
          </Grid>
          <Grid item>
            <Button
              variant="contained"
              onClick={() => handleJobTrigger('Platform Test')}
              disabled={isLoading}
              sx={{ minWidth: 200 }}
            >
              {isLoading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                'Trigger Platform Test'
              )}
            </Button>
          </Grid>
        </Grid>

        <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
          Execution Data:
        </Typography>
        <Paper elevation={2} sx={{ p: 3, backgroundColor: '#f5f5f5' }}>
          {executionData ? (
            <Box
              component="pre"
              sx={{
                margin: 0,
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                fontFamily: 'monospace'
              }}
            >
              {JSON.stringify(executionData, null, 2)}
            </Box>
          ) : (
            <Typography color="text.secondary">No job triggered yet</Typography>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default Dashboard;
