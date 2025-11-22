import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ComponentPreviewRouter } from './components/ComponentPreview';

/*-krisspy-code-start*/
// Auto-generated imports from manifest
import DesignSystemTest from '/src/pages/DesignSystemTest.tsx';
import RetroRainbowDesignSystem from '/src/pages/RetroRainbowDesignSystem.tsx';
import LandingPage from './pages/LandingPage';
import SignUp from './pages/SignUp';
import Login from './pages/Login';
import DemoAccess from './pages/DemoAccess';
import EmailVerification from './pages/EmailVerification';
import OnboardingAssessment from './pages/OnboardingAssessment';
import Dashboard from './pages/Dashboard';
import NoviceLearningPath from './pages/NoviceLearningPath';
import IntermediateLearningPath from './pages/IntermediateLearningPath';
import AdvancedLearningPath from './pages/AdvancedLearningPath';
import LearningModulesHub from './pages/LearningModulesHub';
import DemoModules from './pages/DemoModules';

// Auth guard component
function AuthGuard({ children, requiresAuth = false }: { children: React.ReactNode, requiresAuth?: boolean }) {
  if (requiresAuth) {
    const isAuthenticated = false; // This would come from your auth context/store
    
    if (!isAuthenticated) {
      return (
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <h1>Authentication Required</h1>
          <p>You need to be logged in to access this page</p>
          <button style={{ 
            padding: '0.5rem 1rem', 
            backgroundColor: '#3b82f6', 
            color: 'white', 
            border: 'none', 
            borderRadius: '0.25rem',
            cursor: 'pointer'
          }}>
            Sign In
          </button>
        </div>
      );
    }
  }
  
  return <>{children}</>;
}

// Layout wrapper component
function PageWithLayout({ 
  page: Page, 
  layouts = [] 
}: { 
  page: React.ComponentType, 
  layouts?: React.ComponentType<{ children: React.ReactNode }>[] 
}) {
  if (!layouts.length) {
    return <Page />;
  }
  
  // Render nested layouts from outermost to innermost
  return layouts.reduceRight(
    (acc, Layout) => <Layout>{acc}</Layout>, 
    <Page />
  );
}
/*-krisspy-code-end*/

export default function App() {
  return (
    <Router>
      <Routes>
        {/*-krisspy-code-start*/}
        {/* Auto-generated routes from manifest */}
        <Route path="/" element={
          <AuthGuard requiresAuth={false}>
            <PageWithLayout page={LandingPage} layouts={[]} />
          </AuthGuard>
        } />
        <Route path="/signup" element={
          <AuthGuard requiresAuth={false}>
            <PageWithLayout page={SignUp} layouts={[]} />
          </AuthGuard>
        } />
        <Route path="/login" element={
          <AuthGuard requiresAuth={false}>
            <PageWithLayout page={Login} layouts={[]} />
          </AuthGuard>
        } />
        <Route path="/demo-access" element={
          <AuthGuard requiresAuth={false}>
            <PageWithLayout page={DemoAccess} layouts={[]} />
          </AuthGuard>
        } />
        <Route path="/email-verification" element={
          <AuthGuard requiresAuth={false}>
            <PageWithLayout page={EmailVerification} layouts={[]} />
          </AuthGuard>
        } />
        <Route path="/onboarding-assessment" element={
          <AuthGuard requiresAuth={false}>
            <PageWithLayout page={OnboardingAssessment} layouts={[]} />
          </AuthGuard>
        } />
        <Route path="/dashboard" element={
          <AuthGuard requiresAuth={false}>
            <PageWithLayout page={Dashboard} layouts={[]} />
          </AuthGuard>
        } />
        <Route path="/learning-path/novice" element={
          <AuthGuard requiresAuth={false}>
            <PageWithLayout page={NoviceLearningPath} layouts={[]} />
          </AuthGuard>
        } />
        <Route path="/learning-path/intermediate" element={
          <AuthGuard requiresAuth={false}>
            <PageWithLayout page={IntermediateLearningPath} layouts={[]} />
          </AuthGuard>
        } />
        <Route path="/learning-path/advanced" element={
          <AuthGuard requiresAuth={false}>
            <PageWithLayout page={AdvancedLearningPath} layouts={[]} />
          </AuthGuard>
        } />
        <Route path="/modules" element={
          <AuthGuard requiresAuth={false}>
            <PageWithLayout page={LearningModulesHub} layouts={[]} />
          </AuthGuard>
        } />
        <Route path="/demo-modules" element={
          <AuthGuard requiresAuth={false}>
            <PageWithLayout page={DemoModules} layouts={[]} />
          </AuthGuard>
        } />
        <Route path="/design-system" element={
          <AuthGuard requiresAuth={false}>
            <PageWithLayout page={DesignSystemTest} layouts={[]} />
          </AuthGuard>
        } />
        <Route path="/design" element={
          <AuthGuard requiresAuth={false}>
            <PageWithLayout page={RetroRainbowDesignSystem} layouts={[]} />
          </AuthGuard>
        } />
        {/*-krisspy-code-end*/}
        
        <Route path="/_component/*" element={<ComponentPreviewRouter />} />
        <Route path="*" element={
          <div style={{ padding: '2rem', textAlign: 'center' }}>
            <h1>404 - Page Not Found</h1>
            <a href="/" style={{ color: 'blue', textDecoration: 'underline' }}>
              Go back to home
            </a>
          </div>
        } />
      </Routes>
    </Router>
  );
}