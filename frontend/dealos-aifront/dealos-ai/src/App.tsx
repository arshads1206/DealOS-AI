import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { PremiumCursor } from "@/components/ui/PremiumCursor";
import { AppShell } from "@/components/layout/AppShell";
import { DashboardPage } from "@/features/dashboard/DashboardPage";
import { CompaniesPage } from "@/features/companies/CompaniesPage";
import { CompanyWorkspacePage } from "@/features/workspace/CompanyWorkspacePage";
import { OverviewTab } from "@/features/workspace/tabs/OverviewTab";
import { DocumentsTab } from "@/features/workspace/tabs/DocumentsTab";
import { FinancialsTab } from "@/features/workspace/tabs/FinancialsTab";
import { RisksTab } from "@/features/workspace/tabs/RisksTab";
import { AIAnalystTab } from "@/features/workspace/tabs/AIAnalystTab";
import { ReportsTab } from "@/features/workspace/tabs/ReportsTab";
import { TimelineTab } from "@/features/workspace/tabs/TimelineTab";
import { ActivityTab } from "@/features/workspace/tabs/ActivityTab";
import { SearchPage } from "@/features/search/SearchPage";
import { DocumentLibraryPage } from "@/features/documents/DocumentLibraryPage";
import { InvestmentReportsPage } from "@/features/reports/InvestmentReportsPage";
import { FinancialAnalysisPage } from "@/features/financial-analysis/FinancialAnalysisPage";
import { RiskAnalysisPage } from "@/features/risk-analysis/RiskAnalysisPage";
import { SettingsPage } from "@/features/settings/SettingsPage";
import { ProfilePage } from "@/features/profile/ProfilePage";
import { NotificationsPage } from "@/features/notifications/NotificationsPage";
import { AdminPage } from "@/features/admin/AdminPage";
import { AuthPage } from "@/features/auth/AuthPage";

function App() {
  return (
    <ErrorBoundary>
      <PremiumCursor />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<AuthPage />} />
          <Route element={<AppShell />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/companies" element={<CompaniesPage />} />
            <Route path="/companies/:id" element={<CompanyWorkspacePage />}>
              <Route index element={<Navigate to="overview" replace />} />
              <Route path="overview" element={<OverviewTab />} />
              <Route path="documents" element={<DocumentsTab />} />
              <Route path="financials" element={<FinancialsTab />} />
              <Route path="risks" element={<RisksTab />} />
              <Route path="ai-analyst" element={<AIAnalystTab />} />
              <Route path="reports" element={<ReportsTab />} />
              <Route path="timeline" element={<TimelineTab />} />
              <Route path="activity" element={<ActivityTab />} />
            </Route>
            <Route path="/search" element={<SearchPage />} />
            <Route path="/documents" element={<DocumentLibraryPage />} />
            <Route path="/reports" element={<InvestmentReportsPage />} />
            <Route path="/financial-analysis" element={<FinancialAnalysisPage />} />
            <Route path="/risk-analysis" element={<RiskAnalysisPage />} />
            <Route path="/ai-analyst" element={<Navigate to="/companies" replace />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/notifications" element={<NotificationsPage />} />
            <Route path="/admin" element={<AdminPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
