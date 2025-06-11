import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import ChangeChatStylePage from "./component/ChangeChatStylePage";
import Sidebar from './component/SideBar';
import VectorStorePage from "./component/VectorStorePage";
import "./index.css";

export default function App() {
  return (
    <Router>
      <div style={{ display: "flex", height: "100vh" }}>
        <Sidebar />
        <div style={{ flex: 1, overflow: "auto" }}>
          <Routes>
            <Route path="/convert" element={<ChangeChatStylePage />} />
            <Route path="/collections" element={<VectorStorePage />} />
            <Route path="/*" element={<ChangeChatStylePage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}