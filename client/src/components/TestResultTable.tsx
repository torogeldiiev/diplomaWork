import React from 'react';
import {Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Typography,
} from '@mui/material';
import { TestCase } from '../types';

interface TestResultTableProps {
  results: TestCase[];
}

const TestResultTable: React.FC<TestResultTableProps> = ({ results }) => (
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
);

export default TestResultTable;
