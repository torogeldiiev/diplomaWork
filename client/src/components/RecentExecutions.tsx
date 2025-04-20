// src/components/RecentExecutions.tsx
import React, { useEffect, useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  TableContainer,
  Button,
  CircularProgress
} from '@mui/material';
import { fetchRecentExecutions, fetchTestResults, triggerJob } from '../api/api';
import { Execution } from '../types';

interface RecentExecutionsProps {
  onSelectExecution: (exec: Execution) => void;
}

const RecentExecutions: React.FC<RecentExecutionsProps> = ({ onSelectExecution }) => {
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [loading, setLoading] = useState(true);
  const [buttonLoading, setButtonLoading] = useState<{ [key: string]: boolean }>({});

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const data = await fetchRecentExecutions();
        setExecutions(data);
      } catch (err) {
        console.error('Failed to load recent executions', err);
      } finally {
        setLoading(false);
      }
    };

    load();
    // you could also poll periodically here if desired
  }, []);

  const handleCheck = async (exec: Execution) => {
    setButtonLoading(b => ({ ...b, [exec.buildNumber]: true }));
    try {
      const res = await fetchTestResults(exec.jobName, Number(exec.buildNumber));
      if (res.success) {
        onSelectExecution(exec);
      } else {
        console.error('Fetch test results failed', res);
      }
    } catch (err) {
      console.error('Error fetching test results', err);
    } finally {
      setButtonLoading(b => ({ ...b, [exec.buildNumber]: false }));
    }
  };

  const handleRestart = async (exec: Execution) => {
    setButtonLoading(b => ({ ...b, [exec.buildNumber]: true }));
    try {
      const res = await triggerJob(exec.jobName, exec.parameters);
      console.log('Restart result', res);
      // Optionally: refresh the list
    } catch (err) {
      console.error('Error restarting job', err);
    } finally {
      setButtonLoading(b => ({ ...b, [exec.buildNumber]: false }));
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
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
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {executions.map(exec => (
              <TableRow key={exec.id}>
                <TableCell>{exec.jobName}</TableCell>
                <TableCell>{exec.status}</TableCell>
                <TableCell>{new Date(exec.startTime).toLocaleString()}</TableCell>
                <TableCell align="right">
                  <Box display="flex" gap={1} justifyContent="flex-end">
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => handleCheck(exec)}
                      disabled={buttonLoading[exec.buildNumber]}
                    >
                      {buttonLoading[exec.buildNumber]
                        ? <CircularProgress size={16}/>
                        : 'Check Results'}
                    </Button>
                    <Button
                      size="small"
                      variant="outlined"
                      color="secondary"
                      onClick={() => handleRestart(exec)}
                      disabled={buttonLoading[exec.buildNumber]}
                    >
                      {buttonLoading[exec.buildNumber]
                        ? <CircularProgress size={16}/>
                        : 'Restart'}
                    </Button>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

export default RecentExecutions;
