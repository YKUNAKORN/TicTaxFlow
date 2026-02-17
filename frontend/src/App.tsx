import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import LandingPage from './pages/LandingPage';
import DashboardPage from './pages/DashboardPage';
import TransactionsPage from './pages/TransactionsPage';
import TaxRulesPage from './pages/TaxRulesPage';
import SignInPage from './pages/SignInPage';
import SignUpPage from './pages/SignUpPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import AgentPage from './pages/AgentPage';

function App() {
    return (
        <Router>
            <Routes>
                {/* Landing Page (No Shell) */}
                <Route path="/" element={<LandingPage />} />
                <Route path="/signin" element={<SignInPage />} />
                <Route path="/signup" element={<SignUpPage />} />
                <Route path="/forgot-password" element={<ForgotPasswordPage />} />

                {/* Protected App Routes (With Shell) */}
                <Route path="/dashboard" element={
                    <Layout>
                        <DashboardPage />
                    </Layout>
                } />

                <Route path="/transactions" element={
                    <Layout>
                        <TransactionsPage />
                    </Layout>
                } />

                <Route path="/tax-rules" element={
                    <Layout>
                        <TaxRulesPage />
                    </Layout>
                } />

                <Route path="/agent" element={
                    <Layout>
                        <AgentPage />
                    </Layout>
                } />

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </Router>
    );
}

export default App;
