// src/components/JobTrigger.tsx
import React, { useState, useEffect } from 'react';
import {Paper, Typography, Box, FormControl, InputLabel, Select, MenuItem, TextField, Button, CircularProgress, Alert,
} from '@mui/material';
import { fetchJobs, fetchClusters, triggerJob } from '../api/api';
import { Job, Cluster } from '../types';

interface JobTriggerProps {
  onJobTriggered: (exec: {
    id: number;
    jobName: string;
    status: string;
    buildNumber: string;
    startTime: string;
    parameters: Record<string, string>;
  }) => void;
}

const JobTrigger: React.FC<JobTriggerProps> = ({ onJobTriggered }) => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [selectedJob, setSelectedJob] = useState<string>('');
  const [parameters, setParameters] = useState<Record<string, string>>({});
  const [isJobLoading, setIsJobLoading] = useState(false);
  const [triggerStatus, setTriggerStatus] = useState<{ success?: boolean; message?: string } | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const [jobsData, clustersData] = await Promise.all([
          fetchJobs(),
          fetchClusters(),
        ]);
        setJobs(jobsData);
        setClusters(clustersData);
      } catch (err) {
        console.error('Error loading jobs or clusters', err);
      }
    })();
  }, []);

  const handleJobSelect = (jobName: string) => {
    setSelectedJob(jobName);
    const job = jobs.find(j => j.name === jobName);
    setParameters(job ? job.parameters : {});
    setTriggerStatus(null);
  };

  const handleParameterChange = (key: string, val: string) => {
    setParameters(p => ({ ...p, [key]: val }));
  };

  const handleTrigger = async () => {
    setIsJobLoading(true);
    setTriggerStatus(null);
    try {
      const res = await triggerJob(selectedJob, parameters);
      if (res.success) {
        const exec = {
          id: Date.now(),
          jobName: selectedJob,
          status: 'QUEUED',
          buildNumber: res.data.queue_number.toString(),
          startTime: new Date().toISOString(),
          parameters,
        };
        onJobTriggered(exec);
        setTriggerStatus({ success: true, message: 'Job triggered successfully!' });
      } else {
        throw new Error(res.message || 'Trigger failed');
      }
    } catch (err: any) {
      console.error(err);
      setTriggerStatus({ success: false, message: err.message || 'Error' });
    } finally {
      setIsJobLoading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>Trigger Job</Typography>
      {triggerStatus && (
        <Alert severity={triggerStatus.success ? 'success' : 'error'} sx={{ mb: 2 }}>
          {triggerStatus.message}
        </Alert>
      )}
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Select Job</InputLabel>
        <Select
          value={selectedJob}
          onChange={e => handleJobSelect(e.target.value)}
          label="Select Job"
        >
          {jobs.map(j => (
            <MenuItem key={j.name} value={j.name}>{j.name}</MenuItem>
          ))}
        </Select>
      </FormControl>
      {selectedJob && Object.entries(parameters).map(([key, val]) =>
        ['source','target', 'cluster'].includes(key) ? (
          <FormControl key={key} fullWidth sx={{ mb: 1 }}>
            <InputLabel>{key === 'cluster' ? 'Cluster' : key}</InputLabel>
            <Select
              value={val}
              label={key}
              onChange={e => handleParameterChange(key, e.target.value)}
            >
              {clusters.map(c => (
                <MenuItem key={c.id} value={c.name}>
                  {c.name} ({c.release_version})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        ) : (
          <TextField
            key={key}
            fullWidth
            label={key}
            value={val}
            onChange={e => handleParameterChange(key, e.target.value)}
            sx={{ mb: 1 }}
          />
        )
      )}
      <Button
        variant="contained"
        fullWidth
        onClick={handleTrigger}
        disabled={!selectedJob || isJobLoading}
      >
        {isJobLoading
          ? <CircularProgress size={24} color="inherit"/>
          : 'Trigger Job'}
      </Button>
    </Paper>
  );
};

export default JobTrigger;
