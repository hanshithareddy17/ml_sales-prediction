import React, { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import SalesChart from "../components/SalesChart";
import SalesTable from "../components/SalesTable";
import SummaryCards from "../components/SummaryCards";

import {
  getActualSales,
  getThisYearAnalysis,
  getSalesForecast,
} from "../api/api";

const Dashboard = () => {
  const [data, setData] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [title, setTitle] = useState("");
  const [mode, setMode] = useState("actual");
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      setError(null);

      try {
        if (mode === "actual") {
          const res = await getActualSales();
          setData(res.data);
          setAnalysis(null);
          setTitle("Actual Sales");
        }

        if (mode === "analysis") {
          const res = await getThisYearAnalysis();
          setAnalysis(res.analysis);
          setData([]);
          setTitle("This Year Analysis");
        }

        if (mode === "1year") {
          const res = await getSalesForecast(12);
          setData(
            res.predictions.map((p) => {
              const d = new Date(p.date);
              return {
                month: d.toLocaleString("default", { month: "short" }),
                year: d.getFullYear(),
                amount: Math.round(p.forecast),
                type: "Predicted",
              };
            })
          );
          setAnalysis(null);
          setTitle("Next 1 Year Prediction");
        }

        if (mode === "2year") {
          const res = await getSalesForecast(24);
          setData(
            res.predictions.map((p) => {
              const d = new Date(p.date);
              return {
                month: d.toLocaleString("default", { month: "short" }),
                year: d.getFullYear(),
                amount: Math.round(p.forecast),
                type: "Predicted",
              };
            })
          );
          setAnalysis(null);
          setTitle("Next 2 Years Prediction");
        }
      } catch (err) {
        console.error("Failed to load data", err);

        let message = "Unable to reach the backend API.";
        if (err.response) {
          message += ` Server responded with status ${err.response.status}: ${err.response.statusText}`;
        } else if (err.request) {
          message += " No response received (network error).";
        } else if (err.message) {
          message += ` ${err.message}`;
        }

        setError(message);
        setData([]);
        setAnalysis(null);
      }
    };

    loadData();
  }, [mode]);

  return (
    <>
      <Navbar onSelect={setMode} />

      <div className="container mt-4">
        {error && (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        )}

        {analysis && <SummaryCards data={analysis} />}

        {data.length > 0 && (
          <div className="row">
            <div className="col-md-7 mb-4">
              <SalesChart data={data} title={title} />
            </div>
            <div className="col-md-5 mb-4">
              <SalesTable data={data} />
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default Dashboard;
