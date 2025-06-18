import { Sheet, Stack, Typography } from '@mui/joy';
import { FaDatabase, FaExchangeAlt } from "react-icons/fa";
import { NavLink } from 'react-router-dom';

export default function Sidebar() {
  return (
    <Sheet
      component="nav"
      sx={{
        width: 250,
        height: '100vh',
        bgcolor: 'neutral.800',
        color: 'common.white',
        py: 4,
        px: 2,
        boxShadow: 'md',
      }}
    >
      <Stack spacing={2}>
        <Typography level="h4" textColor="neutral.50" mb={2} textAlign="center">Menu</Typography>
        <NavLink to="/convert" style={({ isActive }) => ({
          background: isActive ? '#1976d2' : 'transparent',
          borderRadius: 8,
          padding: 12,
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          fontWeight: 500,
          fontSize: 16,
          color: 'inherit',
          textDecoration: 'none',
        })}>
          <FaExchangeAlt/> Change Chat Style
        </NavLink>
        <NavLink to="/collections" style={({ isActive }) => ({
          background: isActive ? '#1976d2' : 'transparent',
          borderRadius: 8,
          padding: 12,
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          fontWeight: 500,
          fontSize: 16,
          color: 'inherit',
          textDecoration: 'none',
        })}>
          <FaDatabase/> Manage Collections
        </NavLink>
        <NavLink to="/swagger" style={({ isActive }) => ({
          background: isActive ? '#1976d2' : 'transparent',
          borderRadius: 8,
          padding: 12,
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          fontWeight: 500,
          fontSize: 16,
          color: 'inherit',
          textDecoration: 'none',
        })}>
          <FaDatabase/> Swagger
        </NavLink>
      </Stack>
    </Sheet>
  );
}