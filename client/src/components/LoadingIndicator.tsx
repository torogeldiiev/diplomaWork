import React from 'react';
import { Box, CircularProgress } from '@mui/material';

const LoadingIndicator: React.FC = () => (
  <Box display="flex" justifyContent="center" p={3}>
    <CircularProgress />
  </Box>
);

export default LoadingIndicator;
