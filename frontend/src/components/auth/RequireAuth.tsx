import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { storage } from '../../lib/storage';

interface RequireAuthProps {
    children: React.ReactNode;
}

/**
 * Route guard for the authenticated app shell. Redirects to /signin when no
 * token is present, remembering where the user was headed so the sign-in
 * flow can send them back.
 *
 * This is a client-side convenience only — every data endpoint independently
 * derives the user from the bearer token (backend `core/security.py`), so a
 * missing or forged token fails server-side regardless of this check.
 */
const RequireAuth: React.FC<RequireAuthProps> = ({ children }) => {
    const location = useLocation();
    const token = storage.getToken();

    if (!token) {
        return <Navigate to="/signin" state={{ from: location.pathname }} replace />;
    }

    return <>{children}</>;
};

export default RequireAuth;
