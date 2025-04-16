import React from 'react';
import { Typography } from '@mui/material';

interface ErrorDisplayProps {
  message: string;
}

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ message }) => (
  <Typography color="error">{message}</Typography>
);

export default ErrorDisplay;
